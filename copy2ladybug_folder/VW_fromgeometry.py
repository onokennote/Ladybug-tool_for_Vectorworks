import vs
import math 

#from .config import tolerance
from .VW_color import color_to_color, gray

try:
	from ladybug_geometry.geometry2d.line import LineSegment2D
except ImportError as e:
	raise ImportError('Failed to import ladybug_geometry.\n{}'.format(e))


'''
def obj2plane(obj , plane ):
	(ax,ay,az ) =plane.o
	vx = plane.x
	vy = plane.y
	vs.Move3DObj(obj,ax,ay,az)
	return obj
'''	

"""____________2D GEOMETRY TRANSLATORS____________"""


def from_vector2d(pts):
	p2 = (pts.x,pts.y,0)
	return p2

def from_point2d(pts):
	p2 = (pts.x,pts.y)
	vs.Locus(p2)
	return vs.LNewObj()

'''
def from_ray2d(ray, z=0):
	return rg.Ray3d(from_point2d(ray.p, z), from_vector2d(ray.v))
'''

def from_linesegment2d(line, z=0):
	vs.MoveTo(line.p1.x,line.p1.y)
	vs.LineTo(line.p2.x,line.p2.y)
	vs.Move3DObj(vs.LNewObj(),0,0,z)
	return vs.LNewObj()


def from_arc2d(arc, z=0):
	if arc.is_circle:
		(cx,cy) =arc.c
		vs.ArcByCenter(cx,cy,arc.r,360,360)
		vs.Move3DObj(vs.LNewObj(),0,0,z)
		return vs.LNewObj()
	else: 
		r1 = math.degrees(arc.a1)
		r2 = math.degrees(arc.a2)
		(cx,cy)=arc.c
		vs.ArcByCenter(cx,cy,r1-90,(r2-r1))
		obj = vs.LNewObj() 
		return obj


def from_polygon2d(polygon, z=0):
	pts = [pt for pt in polygon.vertices]
	vs.Poly(*pts)
	return vs.LNewObj()
	
		
'''
	return rg.PolylineCurve(
		[from_point2d(pt, z) for pt in polygon.vertices] + [from_point2d(polygon[0], z)])
'''

def from_polyline2d(polyline, z=0):
	if polyline.interpolated:
		d=3
	else:
		d=2
	pts = [pt for pt in polyline.vertices]
	p = pts.pop(0)
	if len(p) == 2:
		p = (p[0], p[1], 0)
	nC = vs.CreateNurbsCurve(p[0], p[1], z, True,d)
	for p in pts:
		if len(p) == 2:
			p = (p[0], p[1], 0)
		vs.AddVertex3D(nC, p[0] , p[1], z)
	return nC


def from_mesh2d(mesh, z=0):
	if isinstance(z, tuple) :
		if len(z)<3:
			pt_function = 0
		else :
			pt_function = z[2]
	else:
		pt_function = z
	return _translate_mesh(mesh, pt_function)


   

"""____________3D GEOMETRY TRANSLATORS____________"""


def from_vector3d(pts):
	p2 = (pts.x,pts.y,pts.z)
	return p2


def from_point3d(pts):
	p2 = (pts.x,pts.y,pts.z)
	vs.Locus3D(p2)
	return vs.LNewObj()

'''
def from_ray3d(ray):
	return rg.Ray3d(from_point3d(ray.p), from_vector3d(ray.v))
'''

'''
def from_linesegment3d(line):
	return rg.LineCurve(from_point3d(line.p1), from_point3d(line.p2))
'''

'''
def from_plane(pl):
	return rg.Plane(from_point3d(pl.o), from_vector3d(pl.x), from_vector3d(pl.y))
'''


def from_arc3d(arc):
	if arc.is_circle:
		(ax,ay,az ) =arc.plane.o
		(cx,cy,cz) =arc.c
		vs.ArcByCenter(cx,cy,arc.radius,360,360)
		vs.Move3DObj(vs.LNewObj(),0,0,cz)
		return vs.LNewObj()
	else:
		vs.SetWorkingPlaneN((arc.plane.o.x,arc.plane.o.y,arc.plane.o.z),(arc.plane.n.x,arc.plane.n.y,arc.plane.n.z),(arc.plane.y.x,arc.plane.y.y,arc.plane.y.z),)
		r1 = math.degrees(arc.a1)
		r2 = math.degrees(arc.a2)
		if arc.plane.o.z<0:
			vs.ArcByCenter(0,0,arc.radius,r1-90,(r2-r1))
		else:
			vs.ArcByCenter(0,0,arc.radius,r1-90,180+r2*2)
		obj = vs.LNewObj() 
		vs.SetWorkingPlaneN( (0,0,0),(0,0,1),(1,0,0) )
		return obj


def from_polyline3d(polyline):
	if polyline.interpolated:
		d=3
	else:
		d=2
	pts = [pt for pt in polyline.vertices]
	p = pts.pop(0)
	if len(p) == 2:
		p = (p[0], p[1], 0)
	nC = vs.CreateNurbsCurve(p[0], p[1], p[2], True,d)
	for p in pts:
		if len(p) == 2:
			p = (p[0], p[1], 0)
		vs.AddVertex3D(nC, p[0] , p[1], p[2])
	return nC	
	
def from_poly3d_record(poly,dat):
	vw_poly = []
	normals = poly.face_normals
	offset	= 13000/vs.GetLScale(vs.ActLayer())
	for i in range(0,len(poly.faces)):
		face = poly.faces[i]
		pts = []
		for pt in tuple(poly[i] for i in face):
			pts.append((pt.x,pt.y,pt.z))
		vs.Poly3D(*pts)
		po = vs.LNewObj()
		vs.SetPolyClosed( po , True)
		if poly.is_color_by_face and poly.colors is not None:
			col = color_to_color(poly.colors[i])
			vs.SetFillBack(po,col)
		(nx,ny,nz) = normals[i]
		vs.SetRecord(po,'ladybug')
		vs.SetRField(po,'ladybug', 'data',dat[i])
		vs.SetRField(po,'ladybug', 'offx',nx)
		vs.SetRField(po,'ladybug', 'offy',ny)
		vs.SetRField(po,'ladybug', 'offz',nz)
		vw_poly.append(po)
	return vw_poly



def from_mesh3d(mesh):
	return _translate_mesh(mesh, None)


def from_face3d(face):
	pts = face.vertices
	pts = [(pt.x,pt.y,pt.z) for pt in pts]
	vs.Poly3D(*pts)
	po = vs.LNewObj()
	vs.SetPolyClosed( po , True)
	return po
	'''
	segs = [from_linesegment3d(seg) for seg in face.boundary_segments]
	try:
		brep = rg.Brep.CreatePlanarBreps(segs, tolerance)[0]
	except TypeError:  # not planar in Rhino model tolerance; maybe from another model
		print('Brep not planar in Rhino model tolerance. Ignoring tolerance.')
		try:
			brep = rg.Brep.CreatePlanarBreps(segs, 1e6)[0]
		except TypeError:  # it must be a zero-area geometry
			return None
	if face.has_holes:
		for hole in face.hole_segments:
			trim_crvs = [from_linesegment3d(seg) for seg in hole]
			brep.Loops.AddPlanarFaceLoop(0, rg.BrepLoopType.Inner, trim_crvs)
	return brep
	'''


'''
def from_polyface3d(polyface):
	rh_faces = [from_face3d(face) for face in polyface.faces]
	brep = rg.Brep.JoinBreps(rh_faces, tolerance)
	if len(brep) == 1:
		return brep[0]
'''

'''
def from_sphere(sphere):
	
	return rg.Sphere(from_point3d(sphere.center), sphere.radius)
'''

'''
def from_cone(cone):
	
	plane = rg.Plane(from_point3d(cone.vertex), from_vector3d(cone.axis.normalize()))
	return rg.Cone(plane, cone.height, cone.radius)
'''

'''
def from_cylinder(cylinder):
	
	return rg.Cylinder(from_arc3d(cylinder.base_bottom), cylinder.height)
'''

"""________ADDITIONAL 3D GEOMETRY TRANSLATORS________"""

'''
def from_polyline2d_to_joined_polyline(polylines, z=0):
	
	line_crv = []
	for pl in polylines:
		if isinstance(pl, LineSegment2D):
			line_crv.append(from_linesegment2d(pl))
		else:
			line_crv.append(from_polyline2d(pl))
	return rg.Curve.JoinCurves(line_crv)[0]
'''

'''
def from_polyline2d_to_offset_brep(polylines, offset, z=0):
   
	curve = from_polyline2d_to_joined_polyline(polylines, z)
	crv_style = rg.CurveOffsetCornerStyle.Sharp
	all_curves = [curve]
	off_curves = curve.Offset(rg.Plane.WorldXY, -offset, tolerance, crv_style)
	if off_curves is not None:
		all_curves.extend(off_curves)
		offset_brep = rg.Brep.CreatePlanarBreps(all_curves)
		if len(offset_brep) == 1:
			if offset_brep[0].Loops.Count == 2:
				return offset_brep[0]
	return curve
'''


def from_face3d_to_wireframe(face):
	
	boundary = [_polyline_points(face.boundary)]
	if face.has_holes:
		return boundary + [_polyline_points(tup) for tup in face.holes]
	return boundary



def from_polyface3d_to_wireframe(polyface):
	
	return [f for face in polyface.faces for f in from_face3d_to_wireframe(face)]


'''
def from_face3d_to_solid(face, offset):
	
	srf_brep = from_face3d(face)
	return rg.Brep.CreateFromOffsetFace(
		srf_brep.Faces[0], offset, tolerance, False, True)
'''

'''
def from_face3ds_to_joined_brep(faces):
	"
	return rg.Brep.JoinBreps([from_face3d(face) for face in faces], tolerance)
'''


def from_face3ds_to_colored_mesh(faces, color):
	
	joined_mesh = []
	for face in faces:
		try:
			joined_mesh.Append(from_mesh3d(face.triangulated_mesh3d))
		except Exception:
			pass  # failed to create a Rhino Mesh from the Face3D
	#joined_mesh.VertexColors.CreateMonotoneMesh(color_to_color(color))
	return joined_mesh


'''
def from_mesh2d_to_outline(mesh, z=0):
	
	pt_function = _get_point2d_function(z)
	verts = [pt_function(pt) for pt in mesh.vertices]
	face_plines = []
	for face in mesh.faces:
		outline = [verts[f] for f in face] + [verts[face[0]]]
		face_plines.append(rg.PolylineCurve(outline))
	return face_plines
'''

'''
def from_mesh3d_to_outline(mesh):
	
	rh_mesh = from_mesh3d(mesh)
	return rh_mesh, rh_mesh.GetNakedEdges()
'''

"""________________EXTRA HELPER FUNCTIONS________________"""


def _translate_mesh(mesh, z):
	if mesh.is_color_by_face:  # Mesh is constructed face-by-face
		vs.BeginMesh()
		for i in range(0,len(mesh.faces)):
			face = mesh.faces[i]
			pts = []
			for pt in tuple(mesh[i] for i in face):
				if z==None:
					pts.append((pt.x,pt.y,pt.z))
				else :
					pts.append((pt.x, pt.y , z))
			vs.Poly3D(*pts)
			po = vs.LNewObj()
			vs.SetPolyClosed( po , True)
			if mesh.colors is not None:
				col = color_to_color(mesh.colors[i])
				vs.SetFillBack(po,col)
		vs.EndMesh()
		vw_mesh = vs.LNewObj()

	else:  # Mesh is constructed vertex-by-vertex
		vs.BeginMesh()
		for i in range(0,len(mesh.faces)):
			face = mesh.faces[i]
			pts = []
			for pt in tuple(mesh[i] for i in face):
				if z==None:
					pts.append((pt.x,pt.y,pt.z))
				else :
					pts.append((pt.x, pt.y , z))
			vs.Poly3D(*pts)
			po = vs.LNewObj()
			vs.SetPolyClosed( po , True)
			#if mesh.colors is not None:
			#	col = color_to_color(mesh.colors[i])
			#	vs.SetFillBack(po,col)
		vs.EndMesh()
		vw_mesh = vs.LNewObj()
		'''
		for pt in mesh.vertices:
			vw_mesh.Vertices.Add(pt_function(pt))
		for face in mesh.faces:
			vw_mesh.Faces.AddFace(*face)
		if mesh.colors is not None:
			vw_mesh.VertexColors.CreateMonotoneMesh(gray())
			for i, col in enumerate(mesh.colors):
				vw_mesh.VertexColors[i] = color_to_color(col)
		'''
	return vw_mesh


def _polyline_points(tup):
	
	pts = []
	for pt in tup:
		pts.append((pt.x,pt.y,pt.z))
	vs.Poly3D(*pts)
	po = vs.LNewObj()
	vs.SetPolyClosed( po , True)
	return po 