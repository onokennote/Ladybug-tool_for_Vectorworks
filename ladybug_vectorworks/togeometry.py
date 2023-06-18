try:
	from ladybug_geometry.geometry2d.pointvector import Vector2D, Point2D
	from ladybug_geometry.geometry2d.ray import Ray2D
	from ladybug_geometry.geometry2d.line import LineSegment2D
	from ladybug_geometry.geometry2d.polyline import Polyline2D
	from ladybug_geometry.geometry2d.polygon import Polygon2D
	from ladybug_geometry.geometry2d.mesh import Mesh2D
	from ladybug_geometry.geometry3d.pointvector import Vector3D, Point3D
	from ladybug_geometry.geometry3d.ray import Ray3D
	from ladybug_geometry.geometry3d.line import LineSegment3D
	from ladybug_geometry.geometry3d.polyline import Polyline3D
	from ladybug_geometry.geometry3d.plane import Plane
	from ladybug_geometry.geometry3d.mesh import Mesh3D
	from ladybug_geometry.geometry3d.face import Face3D
	from ladybug_geometry.geometry3d.polyface import Polyface3D
except ImportError as e:
	raise ImportError(
		"Failed to import ladybug_geometry.\n{}".format(e))


try:
	import ladybug.color as lbc
except ImportError as e:
	raise ImportError("Failed to import ladybug.\n{}".format(e))

import vs
import math
import itertools
import operator

#from .VW_fromgeometry import from_face3ds_to_joined_brep
from .config import tolerance


"""____________2D GEOMETRY TRANSLATORS____________"""


def to_vector2d(vector):
	if len(vector)== 3:
		(px,py,pz) = vector
	else:
		(px,py) = vector
	return Vector2D(px,py)


def to_point2d(point):
	if len(point)== 3:
		(px,py,pz) = point
	else:
		(px,py) = point
	return Point2D(px,py)


def to_ray2d(ray):
	
	return Ray2D(to_point2d(ray.Position), to_vector2d(ray.Direction))


def to_linesegment2d(line):
	
	return LineSegment2D.from_end_points(
		to_point2d(line.PointAtStart), to_point2d(line.PointAtEnd))



def to_polyline2d(polyline):
	pts = [to_point2d(polyline.Point(i)) for i in range(polyline.PointCount)]
	return Polyline2D(pts) if len(pts) != 2 else LineSegment2D.from_end_points(*pts)



def to_polygon2d(polygon):
	assert polygon.IsClosed, \
		'Rhino PolyLineCurve must be closed to make a Ladybug Polygon2D.'
	return Polygon2D(
		[to_point2d(polygon.Point(i)) for i in range(polygon.PointCount - 1)])



def to_mesh2d(mesh, color_by_face=True):
	
	lb_verts = tuple(to_point2d(pt) for pt in mesh.Vertices)
	lb_faces, colors = _extract_mesh_faces_colors(mesh, color_by_face)
	return Mesh2D(lb_verts, lb_faces, colors)


"""____________3D GEOMETRY TRANSLATORS____________"""


def to_vector3d(vector):
	if len(vector)==3:
		(px,py,pz) =vector
		return Vector3D(px,py,pz)
	else:
		(px,py) = vector
		return Vector3D(px,py,0)	


def to_point3d(point):
	if len(point)==3:
		(px,py,pz) = point
		return Point3D(px,py,pz)
	else:
		(px,py) = point
		return Point3D(px,py,0)	

'''
def to_ray3d(ray):
	
	return Ray3D(to_point3d(ray.Position), to_vector3d(ray.Direction))
'''

'''
def to_linesegment3d(line):
	
	return LineSegment3D.from_end_points(
		to_point3d(line.PointAtStart), to_point3d(line.PointAtEnd))
'''

'''
def to_polyline3d(polyline):
	pts = [to_point3d(polyline.Point(i)) for i in range(polyline.PointCount)]
	return Polyline3D(pts) if len(pts) != 2 else LineSegment3D.from_end_points(*pts)
'''

'''
def to_plane(pl):
	return Plane(
		to_vector3d(pl.ZAxis), to_point3d(pl.Origin), to_vector3d(pl.XAxis))
'''


def to_face3d(geo, meshing_parameters=None):
	grpPoly = vs.ConvertTo3DPolys(geo)
	poly = []
	faces = []
	h = vs.FInGroup(grpPoly)
	
	while h != None:
		poly.append(h)
		h = vs.NextObj(h)
	for h in poly:
		pt = []
		for iii in range(0,vs.GetVertNum(h)):
			(px,py,pz) = vs.GetPolyPt3D(h,iii)
			pt.append(Point3D(px,py,pz))
		face = Face3D(pt)
		faces.append(face)
	for h in poly:
		vs.Marionette_DisposeObj(h)
	
	return faces
	'''
	faces = []	# list of Face3Ds to be populated and returned
	if vs.GetType(geo)==40:#if isinstance(geo, rg.Mesh):  # convert each Mesh face to a Face3D
		pts = tuple(to_point3d(pt) for pt in geo.Vertices)
		for face in geo.Faces:
			if face.IsQuad:
				all_verts = (pts[face[0]], pts[face[1]], pts[face[2]], pts[face[3]])
				lb_face = Face3D(all_verts)
				if lb_face.area != 0:
					for _v in lb_face.vertices:
						if lb_face.plane.distance_to_point(_v) >= tolerance:
							# non-planar quad split the quad into two planar triangles
							verts1 = (pts[face[0]], pts[face[1]], pts[face[2]])
							verts2 = (pts[face[3]], pts[face[0]], pts[face[1]])
							faces.append(Face3D(verts1))
							faces.append(Face3D(verts2))
							break
					else:
						faces.append(lb_face)
			else:
				all_verts = (pts[face[0]], pts[face[1]], pts[face[2]])
				lb_face = Face3D(all_verts)
				if lb_face.area != 0:
					faces.append(lb_face)
	else:  # convert each Brep Face to a Face3D
		meshing_parameters = meshing_parameters #or rg.MeshingParameters.Default
		for b_face in geo.Faces:
			if b_face.IsPlanar(tolerance):
				try:
					bf_plane = to_plane(b_face.FrameAt(0, 0)[-1])
				except Exception:  # failed to extract the plane from the geometry
					bf_plane = None	 # auto-calculate the plane from the vertices
				all_verts = []
				for count in range(b_face.Loops.Count):	 # Each loop is a boundary/hole
					success, loop_pline = \
						b_face.Loops.Item[count].To3dCurve().TryGetPolyline()
					if not success:	 # Failed to get a polyline; there's a curved edge
						loop_verts = _planar.planar_face_curved_edge_vertices(
							b_face, count, meshing_parameters)
					else:  # we have a polyline representing the loop
						loop_verts = tuple(to_point3d(loop_pline.Item[i])
										   for i in range(loop_pline.Count - 1))
					all_verts.append(_remove_dup_verts(loop_verts))
				if len(all_verts[0]) >= 3:
					if len(all_verts) == 1:	 # No holes in the shape
						faces.append(Face3D(all_verts[0], plane=bf_plane))
					else:  # There's at least one hole in the shape
						hls = [hl for hl in all_verts[1:] if len(hl) >= 3]
						faces.append(Face3D(
							boundary=all_verts[0], holes=hls, plane=bf_plane))
			else:  # curved face must be meshed into planar Face3D objects
				faces.extend(_planar.curved_surface_faces(b_face, meshing_parameters))
	return faces
	'''


def to_polyface3d(geo, meshing_parameters=None):
	return Polyface3D.from_faces(to_face3d(geo, meshing_parameters), tolerance)
'''	
	mesh_par = meshing_parameters or rg.MeshingParameters.Default  # default
	if vs.GetType(geo)!=40: and _planar.has_curved_face(geo):  # keep solidity
		new_brep = from_face3ds_to_joined_brep(_planar.curved_solid_faces(geo, mesh_par))
		return Polyface3D.from_faces(to_face3d(new_brep[0], mesh_par), tolerance)
	return Polyface3D.from_faces(to_face3d(geo, mesh_par), tolerance)
'''


def to_mesh3d(mesh, color_by_face=True):
	return to_gridded_mesh3d(mesh, 1000000)
	'''
	lb_verts = []
	for i in range(0,vs.GetMeshVertNum(h)):
		lb_verts.append.vs.GetMeshVertex(h,i)
	lb_verts = tuple(to_point3d(pt) for pt in mesh.Vertices)
	lb_faces, colors = _extract_mesh_faces_colors(mesh, color_by_face)
	return Mesh3D(lb_verts, lb_faces, colors)
	'''


"""________ADDITIONAL 3D GEOMETRY TRANSLATORS________"""


def to_gridded_mesh3d(brep, grid_size, offset_distance=0):
	grpPoly = vs.ConvertTo3DPolys(brep)
	poly = []
	mesh_grids = []
	
	h = vs.FInGroup(grpPoly)
	
	while h != None:
		poly.append(h)
		h = vs.NextObj(h)
	for h in poly:
		pt = []
		for i in range(0,vs.GetVertNum(h)):
			(px,py,pz) = vs.GetPolyPt3D(h,i)
			pt.append(Point3D(px,py,pz))
		face = Face3D(pt)
		mesh_grids.append(face.mesh_grid(grid_size,grid_size,offset_distance))	
	
	for h in poly:
		vs.Marionette_DisposeObj(h)
		
	return Mesh3D.join_meshes(mesh_grids)
	
	'''
	meshing_param = rg.MeshingParameters.Default
	meshing_param.MaximumEdgeLength = grid_size
	meshing_param.MinimumEdgeLength = grid_size
	meshing_param.GridAspectRatio = 1
	mesh_grids = rg.Mesh.CreateFromBrep(brep, meshing_param)#brep_to_3Dpolys(mesh)
	if len(mesh_grids) == 1:  # only one mesh was generated
		mesh_grid = mesh_grids[0]
	else:  # join the meshes into one
		mesh_grid = rg.Mesh()
		for m_grid in mesh_grids:
			mesh_grid.Append(m_grid)
	if offset_distance != 0:
		temp_mesh = rg.Mesh()
		mesh_grid.Normals.UnitizeNormals()
		for pt, vec in zip(mesh_grid.Vertices, mesh_grid.Normals):
			temp_mesh.Vertices.Add(pt + (rg.Vector3f.Multiply(vec, offset_distance)))
		for face in mesh_grid.Faces:
			temp_mesh.Faces.AddFace(face)
		mesh_grid = temp_mesh
	return to_mesh3d(mesh_grid)
	'''


def to_joined_gridded_mesh3d(geometry, grid_size, offset_distance=0):
	
	lb_meshes = []
	for geo in geometry:
		lb_meshes.append(to_gridded_mesh3d(geo, grid_size, offset_distance))
		#tp = vs.GetType(geo)
		#if tp==24 or tp==25 or tp==34 or tp==38:
		#	lb_meshes.append(to_gridded_mesh3d(geo, grid_size, offset_distance))
		#else:	# assume that it's a Mesh
		#	lb_meshes.append(to_mesh3d(geo))
	if len(lb_meshes) == 1:
		return lb_meshes[0]
	else:
		return Mesh3D.join_meshes(lb_meshes)



"""________________EXTRA HELPER FUNCTIONS________________"""


def _extract_mesh_faces_colors(mesh, color_by_face):
	colors = None
	lb_faces = []
	for face in mesh.Faces:
		if face.IsQuad:
			lb_faces.append((face[0], face[1], face[2], face[3]))
		else:
			lb_faces.append((face[0], face[1], face[2]))

	if len(mesh.VertexColors) != 0:
		colors = []
		if color_by_face is True:
			for face in mesh.Faces:
				col = mesh.VertexColors[face[0]]
				colors.append(lbc.Color(col.R, col.G, col.B))
		else:
			for col in mesh.VertexColors:
				colors.append(lbc.Color(col.R, col.G, col.B))
	return lb_faces, colors


'''
def _remove_dup_verts(vertices):
	
	return [pt for i, pt in enumerate(vertices)
			if not pt.is_equivalent(vertices[i - 1], tolerance)]
'''