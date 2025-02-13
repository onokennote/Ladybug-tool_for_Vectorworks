
import math
import array as specializedarray
import vs

from ladybug_vectorworks.togeometry import to_face3d
from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.mesh import Mesh3D
from ladybug_geometry.geometry3d.ray import Ray3D
from ladybug_geometry.geometry3d.pointvector import Vector3D, Point3D


from ladybug_vectorworks.config import tolerance, angle_tolerance

from concurrent.futures import ThreadPoolExecutor



def join_geometry_to_mesh(geometry):
	obj = geometry

	faces = []
	cobj = []
	for ob in obj:
		f1 = vs.ConvertTo3DPolys(ob)
		cobj.append(f1)
		h = vs.FInGroup(f1)
		while h != None:
			faces.append(h)
			h = vs.NextObj(h)


	vs.BeginMesh()
	for h in faces:
		vs.CreateDuplicateObject(h,vs.Handle(0))
	vs.EndMesh()
	mesh = vs.LNewObj()

	for h in cobj:
		vs.Marionette_DisposeObj(h)
	for h in obj:
		vs.Marionette_DisposeObj(h)


	return mesh

	'''
	joined_mesh = rg.Mesh()
	for geo in geometry:
		if isinstance(geo, rg.Brep):
			meshes = rg.Mesh.CreateFromBrep(geo, rg.MeshingParameters.Default)
			for mesh in meshes:
				joined_mesh.Append(mesh)
		elif isinstance(geo, rg.Mesh):
			joined_mesh.Append(geo)
		else:
			raise TypeError('Geometry must be either a Brep or a Mesh. '
							'Not {}.'.format(type(geo)))
	return joined_mesh
	'''

def join_geometry_to_brep(geometry):
	"""Convert an array of Rhino Breps and/or Meshes into a single Rhino Brep.

	This is a typical pre-step before using the ray tracing functions.

	Args:
		geometry: An array of Rhino Breps or Rhino Meshes.
	"""
	joined_mesh = join_geometry_to_mesh(geometry)
	return joined_mesh




def vec3D_angle(va,vb):
	(ax,ay,az) = va
	(bx,by,bz) = vb
	vcos = (ax*bx+ay*by+az*bz)/((ax**2+ay**2+az**2)**0.5*(bx**2+by**2+bz**2)**0.5)
	return math.acos(vcos)

def int_check(faces,ray):

	rep = 1
	for face in faces:
			re = face.intersect_line_ray(ray)
			if re != None:
				rep = 0
				break
	return rep

def intersect_mesh_rays(mesh, points, vectors, normals=None, cpu_count=0, parallel=True,max_dist=None):
	faces = to_face3d(mesh)
	intersection_matrix = [0] * len(points)	 # matrix to be filled with results
	angle_matrix = [0] * len(normals) if normals is not None else None
	cutoff_angle = math.pi / 2	# constant used in all normal checks
	if not parallel:
		cpu_count = 1

	def intersect_point(i):
		"""Intersect all of the vectors of a given point without any normal check."""
		pt = points[i]
		int_list = []
		for vec in vectors:
			(px,py,pz) = pt
			p = Point3D(px,py,pz)
			(vx,vy,vz) = vec
			v = Vector3D(vx,vy,vz)
			ray = Ray3D(p, v)
			if max_dist is not None:
				if (vx**2+vy**2+vz**2)**0.5<max_dist:
					int_list.append(int_check(faces,ray))
				else:
					int_list.append(0)
			else:
				int_list.append(0)
		intersection_matrix[i] = int_list

	def intersect_point_normal_check(i):
		"""Intersect all of the vectors of a given point with a normal check."""
		pt, normal_vec = points[i], normals[i]
		int_list = []
		angle_list = []
		for vec in vectors:
			vec_angle = vec3D_angle(normal_vec, vec)
			angle_list.append(vec_angle)
			if vec_angle <= cutoff_angle:
				(px,py,pz) = pt
				p = Point3D(px,py,pz)
				(vx,vy,vz) = vec
				v = Vector3D(vx,vy,vz)
				ray = Ray3D(p, v)
				int_list.append(int_check(faces,ray))
			else:  # the vector is pointing behind the surface
				int_list.append(0)
		intersection_matrix[i] = specializedarray.array('B', int_list)
		angle_matrix[i] = specializedarray.array('d', angle_list)



	def intersect_each_point_group(worker_i):
		"""Intersect groups of points so that only the cpu_count is used."""
		start_i, stop_i = pt_groups[worker_i]
		for count in range(start_i, stop_i):
			intersect_point(count)

	def intersect_each_point_group_normal_check(worker_i):
		"""Intersect groups of points with distance check so only cpu_count is used."""
		start_i, stop_i = pt_groups[worker_i]
		for count in range(start_i, stop_i):
			intersect_point_normal_check(count)

	if cpu_count is not None and cpu_count > 1:
		# group the points in order to meet the cpu_count
		pt_count = len(points)
		worker_count = min((cpu_count, pt_count))
		i_per_group = int(math.ceil(pt_count / worker_count))
		pt_groups = [[x, x + i_per_group] for x in range(0, pt_count, i_per_group)]
		pt_groups[-1][-1] = pt_count  # ensure the last group ends with point count

	if normals is not None:

		if cpu_count is None:  # use all available CPUs
			with ThreadPoolExecutor() as executor:
				for i in range(len(points)):
					executor.submit(intersect_point_normal_check,i)
		elif cpu_count <= 1:  # run everything on a single processor
			for i in range(len(points)):
				intersect_point_normal_check(i)
		else:  # run the groups in a manner that meets the CPU count
			with ThreadPoolExecutor() as executor:
				for i in range(len(points)):
					executor.submit(intersect_each_point_group_normal_check,i)

	else:

		if cpu_count is None:  # use all available CPUs
			with ThreadPoolExecutor() as executor:
				for i in range(len(points)):
					executor.submit(intersect_point,i)

		elif cpu_count <= 1:  # run everything on a single processor
			for i in range(len(points)):
				intersect_point(i)
		else:  # run the groups in a manner that meets the CPU count
			with ThreadPoolExecutor() as executor:
				for i in range(len(points)):
					executor.submit(intersect_each_point_group,i)

	return intersection_matrix, angle_matrix

def intersect_mesh_lines(
		mesh, start_points, end_points, max_dist=None, cpu_count=None, parallel=True):
	vectors =[]
	for i ,ep in enumerate(end_points):
		(x1,y1,z1)=start_points[i]
		(x2,y2,z2)=ep
		vectors.append((x2-x1,y2-y1,z2-z1))
	intersection_matrix, angle_matrix = intersect_mesh_rays(mesh, start_points, vectors,\
		normals=None, cpu_count=cpu_count, parallel=parallel, max_dist=max_dist)
	return intersection_matrix
'''
	int_matrix = [0] * len(start_points)  # matrix to be filled with results
	if not parallel:
		cpu_count = 1

	def intersect_line(i):
		"""Intersect a line defined by a start and an end with the mesh."""
		pt = start_points[i]
		int_list = []
		for ept in end_points:
			lin = rg.Line(pt, ept)
			int_obj = rg.Intersect.Intersection.MeshLine(mesh, lin)
			is_clear = 1 if None in int_obj or len(int_obj) == 0 else 0
			int_list.append(is_clear)
		int_matrix[i] = int_list

	def intersect_line_dist_check(i):
		"""Intersect a line with the mesh with a distance check."""
		pt = start_points[i]
		int_list = []
		for ept in end_points:
			lin = rg.Line(pt, ept)
			if lin.Length > max_dist:
				int_list.append(0)
			else:
				int_obj = rg.Intersect.Intersection.MeshLine(mesh, lin)
				is_clear = 1 if None in int_obj or len(int_obj) == 0 else 0
				int_list.append(is_clear)
		int_matrix[i] = int_list

	def intersect_each_line_group(worker_i):
		"""Intersect groups of lines so that only the cpu_count is used."""
		start_i, stop_i = l_groups[worker_i]
		for count in range(start_i, stop_i):
			intersect_line(count)

	def intersect_each_line_group_dist_check(worker_i):
		"""Intersect groups of lines with distance check so only cpu_count is used."""
		start_i, stop_i = l_groups[worker_i]
		for count in range(start_i, stop_i):
			intersect_line_dist_check(count)

	if cpu_count is not None and cpu_count > 1:
		# group the lines in order to meet the cpu_count
		l_count = len(start_points)
		worker_count = min((cpu_count, l_count))
		i_per_group = int(math.ceil(l_count / worker_count))
		l_groups = [[x, x + i_per_group] for x in range(0, l_count, i_per_group)]
		l_groups[-1][-1] = l_count	# ensure the last group ends with line count

	if max_dist is not None:
		if cpu_count is None:  # use all available CPUs
			tasks.Parallel.ForEach(range(len(start_points)), intersect_line_dist_check)
		elif cpu_count <= 1:  # run everything on a single processor
			for i in range(len(start_points)):
				intersect_line_dist_check(i)
		else:  # run the groups in a manner that meets the CPU count
			tasks.Parallel.ForEach(
				range(len(l_groups)), intersect_each_line_group_dist_check)
	else:
		if cpu_count is None:  # use all available CPUs
			tasks.Parallel.ForEach(range(len(start_points)), intersect_line)
		elif cpu_count <= 1:  # run everything on a single processor
			for i in range(len(start_points)):
				intersect_line(i)
		else:  # run the groups in a manner that meets the CPU count
			tasks.Parallel.ForEach(
				range(len(l_groups)), intersect_each_line_group)
	return int_matrix
'''


def trace_ray(ray, breps, bounce_count=1):
	"""Get a list of Rhino points for the path a ray takes bouncing through breps.

	Args:
		ray: A Rhino Ray whose path will be traced through the geometry.
		breps: An array of Rhino breps through with the ray will be traced.
		bounce_count: An positive integer for the number of ray bounces to trace
			the sun rays forward. (Default: 1).
	"""
	### vectorworksに要置き換え

	return rg.Intersect.Intersection.RayShoot(ray, breps, bounce_count)


'''
def normal_at_point(brep, point):
	"""Get a Rhino vector for the normal at a specific point that lies on a brep.

	Args:
		breps: A Rhino brep on which the normal direction will be evaluated.
		point: A Rhino point on the input brep where the normal will be evaluated.
	"""
	return brep.ClosestPoint(point, tolerance)[5]
'''
def bounding_box(geometry, high_accuracy=False):
	"""Get a Rhino bounding box around an input Rhino Mesh or Brep.

	This is a typical pre-step before using intersection functions.

	Args:
		geometry: A Rhino Brep or Mesh.
		high_accuracy: If True, a physically accurate bounding box will be computed.
			If not, a bounding box estimate will be computed. For some geometry
			types, there is no difference between the estimate and the accurate
			bounding box. Estimated bounding boxes can be computed much (much)
			faster than accurate (or "tight") bounding boxes. Estimated bounding
			boxes are always similar to or larger than accurate bounding boxes.
	"""
	oy,ox,oz = vs.Get3DInfo(geometry)
	(cx,cy),cz =  vs.Get3DCntr(geometry)

	p1x = cx - ox/2
	p1y = cy - oy/2
	p1z = cz - oz/2
	p2x = cx + ox/2
	p2y = cy + oy/2
	p2z = cz + oz/2
	return [(p1x,p1y,p1z),(p2x,p2y,p2z)]
	#return geometry.GetBoundingBox(high_accuracy)

def bounding_box_extents(geometry, high_accuracy=False):
	"""Get min and max points around an input Rhino Mesh or Brep

	Args:
		geometry: A Rhino Brep or Mesh.
		high_accuracy: If True, a physically accurate bounding box will be computed.
			If not, a bounding box estimate will be computed. For some geometry
			types, there is no difference between the estimate and the accurate
			bounding box. Estimated bounding boxes can be computed much (much)
			faster than accurate (or "tight") bounding boxes. Estimated bounding
			boxes are always similar to or larger than accurate bounding boxes.
	"""
	b_box = bounding_box(geometry, high_accuracy)
	return b_box[1], b_box[0]


def intersect_solids_parallel(solids, bound_boxes, cpu_count=None):
	"""Intersect the co-planar faces of an array of solids using parallel processing.

	Args:
		original_solids: An array of closed Rhino breps (polysurfaces) that do
			not have perfectly matching surfaces between adjacent Faces.
		bound_boxes: An array of Rhino bounding boxes that parallels the input
			solids and will be used to check whether two Breps have any potential
			for intersection before the actual intersection is performed.
		cpu_count: An integer for the number of CPUs to be used in the intersection
			calculation. The ladybug_rhino.grasshopper.recommended_processor_count
			function can be used to get a recommendation. If None, all available
			processors will be used. (Default: None).
		parallel: Optional boolean to override the cpu_count and use a single CPU
			instead of multiple processors.

	Returns:
		int_solids -- The input array of solids, which have all been intersected
		with one another.
	"""
	return intersect_solids(solids, bound_boxes)
	'''
	int_solids = solids[:]	# copy the input list to avoid editing it

	def intersect_each_solid(i):
		"""Intersect a solid with all of the other solids of the list."""
		bb_1 = bound_boxes[i]
		# intersect the solids that come after this one
		for j, bb_2 in enumerate(bound_boxes[i + 1:]):
			if not overlapping_bounding_boxes(bb_1, bb_2):
				continue  # no overlap in bounding box; intersection impossible
			split_brep1, int_exists = \
				intersect_solid(int_solids[i], int_solids[i + j + 1])
			if int_exists:
				int_solids[i] = split_brep1
		# intersect the solids that come before this one
		for j, bb_2 in enumerate(bound_boxes[:i]):
			if not overlapping_bounding_boxes(bb_1, bb_2):
				continue  # no overlap in bounding box; intersection impossible
			split_brep2, int_exists = intersect_solid(int_solids[i], int_solids[j])
			if int_exists:
				int_solids[i] = split_brep2

	def intersect_each_solid_group(worker_i):
		"""Intersect groups of solids so that only the cpu_count is used."""
		start_i, stop_i = s_groups[worker_i]
		for count in range(start_i, stop_i):
			intersect_each_solid(count)

	if cpu_count is None or cpu_count <= 1:	 # use all available CPUs
		tasks.Parallel.ForEach(range(len(solids)), intersect_each_solid)
	else:  # group the solids in order to meet the cpu_count
		solid_count = len(int_solids)
		worker_count = min((cpu_count, solid_count))
		i_per_group = int(math.ceil(solid_count / worker_count))
		s_groups = [[x, x + i_per_group] for x in range(0, solid_count, i_per_group)]
		s_groups[-1][-1] = solid_count	# ensure the last group ends with solid count
		tasks.Parallel.ForEach(range(len(s_groups)), intersect_each_solid_group)

	return int_solids
	'''

def intersect_solids(solids, bound_boxes):
	"""Intersect the co-planar faces of an array of solids.

	Args:
		original_solids: An array of closed Rhino breps (polysurfaces) that do
			not have perfectly matching surfaces between adjacent Faces.
		bound_boxes: An array of Rhino bounding boxes that parallels the input
			solids and will be used to check whether two Breps have any potential
			for intersection before the actual intersection is performed.

	Returns:
		int_solids -- The input array of solids, which have all been intersected
		with one another.
	"""
	int_solids = solids[:]	# copy the input list to avoid editing it

	for i, bb_1 in enumerate(bound_boxes):
		for j, bb_2 in enumerate(bound_boxes[i + 1:]):
			if not overlapping_bounding_boxes(bb_1, bb_2):
				continue  # no overlap in bounding box; intersection impossible

			# split the first solid with the second one
			split_brep1, int_exists = intersect_solid(
				int_solids[i], int_solids[i + j + 1])
			int_solids[i] = split_brep1

			# split the second solid with the first one if an intersection was found
			if int_exists:
				split_brep2, int_exists = intersect_solid(
					int_solids[i + j + 1], int_solids[i])
				int_solids[i + j + 1] = split_brep2

	return int_solids





def intersect_solid(solid, other_solid):
	"""Intersect the co-planar faces of one solid Brep using another.

	Args:
		solid: The solid Brep which will be split with intersections.
		other_solid: The other Brep, which will be used to split.

	Returns:
		A tuple with two elements

		-	solid -- The input solid, which has been split.

		-	intersection_exists -- Boolean to note whether an intersection was found
			between the solid and the other_solid. If False, there's no need to
			split the other_solid with the input solid.
	"""
	# variables to track the splitting process
	re , solid = vs.IntersectSolid(solid, other_solid)
	if re ==0 and solid is not None:
		intersection_exists = True
	else:
		intersection_exists = False
	return solid, intersection_exists
	'''intersection_exists = False	 # boolean to note whether an intersection exists
	temp_brep = solid.Split(other_solid, tolerance)
	if len(temp_brep) != 0:
		solid = rg.Brep.JoinBreps(temp_brep, tolerance)[0]
		solid.Faces.ShrinkFaces()
		intersection_exists = True
	return solid, intersection_exists
	'''


def overlapping_bounding_boxes(bound_box1, bound_box2):
	"""Check if two Rhino bounding boxes overlap within the tolerance.

	This is particularly useful as a check before performing computationally
	intense intersection processes between two bounding boxes. Checking the
	overlap of the bounding boxes is extremely quick given this method's use
	of the Separating Axis Theorem. This method is built into the intersect_solids
	functions in order to improve its calculation time.

	Args:
		bound_box1: The first bound_box to check.
		bound_box2: The second bound_box to check.
	"""
	# Bounding box check using the Separating Axis Theorem
	(p11x,p11y,p11z),(p12x,p12y,p12z) = bound_box1
	(p21x,p21y,p21z),(p22x,p22y,p22z) = bound_box1

	bb1_width = p12x-p11x #bound_box1.Max.X - bound_box1.Min.X
	bb2_width = p22x-p21x #bound_box2.Max.X - bound_box2.Min.X
	dist_btwn_x = abs((p11x+p12x)/2 - (p21x+p22x)/2) #abs(bound_box1.Center.X - bound_box2.Center.X)
	x_gap_btwn_box = dist_btwn_x - (0.5 * bb1_width) - (0.5 * bb2_width)

	bb1_depth = p12y-p11y #bound_box1.Max.Y - bound_box1.Min.Y
	bb2_depth = p22y-p21y #bound_box2.Max.Y - bound_box2.Min.Y
	dist_btwn_y = abs((p11y+p12y)/2 - (p21y+p22y)/2) #abs(bound_box1.Center.Y - bound_box2.Center.Y)
	y_gap_btwn_box = dist_btwn_y - (0.5 * bb1_depth) - (0.5 * bb2_depth)

	bb1_height = p12z-p11z #bound_box1.Max.Z - bound_box1.Min.Z
	bb2_height = p22z-p21z #bound_box2.Max.Z - bound_box2.Min.Z
	dist_btwn_z = abs((p11z+p12z)/2 - (p21z+p22z)/2) #abs(bound_box1.Center.Z - bound_box2.Center.Z)
	z_gap_btwn_box = dist_btwn_z - (0.5 * bb1_height) - (0.5 * bb2_height)

	if x_gap_btwn_box > tolerance or y_gap_btwn_box > tolerance or \
			z_gap_btwn_box > tolerance:
		return False  # no overlap
	return True	 # overlap exists


'''
def split_solid_to_floors(building_solid, floor_heights):
	"""Extract a series of planar floor surfaces from solid building massing.

	Args:
		building_solid: A closed brep representing a building massing.
		floor_heights: An array of float values for the floor heights, which
			will be used to generate planes that subdivide the building solid.

	Returns:
		floor_breps -- A list of planar, horizontal breps representing the floors
		of the building.
	"""
	# get the floor brep at each of the floor heights.
	floor_breps = []
	for hgt in floor_heights:
		story_breps = []
		floor_base_pt = rg.Point3d(0, 0, hgt)
		section_plane = rg.Plane(floor_base_pt, rg.Vector3d.ZAxis)
		floor_crvs = rg.Brep.CreateContourCurves(building_solid, section_plane)
		try:  # Assume a single contour curve has been found
			floor_brep = rg.Brep.CreatePlanarBreps(floor_crvs, tolerance)
		except TypeError:  # An array of contour curves has been found
			floor_brep = rg.Brep.CreatePlanarBreps(floor_crvs)
		if floor_brep is not None:
			story_breps.extend(floor_brep)
		floor_breps.append(story_breps)

	return floor_breps
'''

'''
def geo_min_max_height(geometry):
	"""Get the min and max Z values of any input object.

	This is useful as a pre-step before the split_solid_to_floors method.
	"""
	# intersection functions changed in Rhino 7.15 such that we now need 2* tolerance
	add_val = tolerance * 2 if (7, 15) <= rhino_version < (7, 17) else 0
	bound_box = geometry.GetBoundingBox(rg.Plane.WorldXY)
	return bound_box.Min.Z + add_val, bound_box.Max.Z
'''