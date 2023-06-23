import vs
import math 
from honeybee.config import folders as hb_folders
#from .config import tolerance
from ladybug_vectorworks.color import color_to_color, gray

try:
	from ladybug_geometry.geometry2d.line import LineSegment2D
except ImportError as e:
	raise ImportError('Failed to import ladybug_geometry.\n{}'.format(e))
from ladybug_geometry.geometry3d.mesh import Mesh3D
from honeybee.config import folders as hb_folders
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
	p2 = (pts.x,pts.y,0)
	vs.Locus3D(p2)
	vs.SetPlanarRef(vs.LNewObj(), -1)
	return vs.LNewObj()

'''
def from_ray2d(ray, z=0):
	return rg.Ray3d(from_point2d(ray.p, z), from_vector2d(ray.v))
'''

def from_linesegment2d(line, z=0):
	vs.MoveTo(line.p1.x,line.p1.y)
	vs.LineTo(line.p2.x,line.p2.y)
	obj = vs.LNewObj()
	vs.Move3DObj(obj,0,0,z)
	vs.SetPlanarRef(obj, -1)
	return obj


def from_arc2d(arc, z=0):
	if arc.is_circle:
		(cx,cy) =arc.c
		vs.ArcByCenter(cx,cy,arc.r,360,360)
		obj = vs.LNewObj()
		vs.Move3DObj(obj,0,0,z)
		vs.SetFPat(obj, 0)
		vs.SetPlanarRef(obj, -1)
		return obj
	else: 
		r1 = math.degrees(arc.a1)
		r2 = math.degrees(arc.a2)
		(cx,cy)=arc.c
		vs.ArcByCenter(cx,cy,r1-90,(r2-r1))
		obj = vs.LNewObj() 
		vs.SetFPat(obj, 0)
		vs.SetPlanarRef(obj, -1)
		return obj


def from_polygon2d(polygon, z=0):
	pts = [pt for pt in polygon.vertices]
	vs.Poly(*pts)
	obj = vs.LNewObj()
	vs.SetFPat(obj, 0)
	vs.SetPlanarRef(obj, -1)
	return obj
	
		
'''
	return rg.PolylineCurve(
		[from_point2d(pt, z) for pt in polygon.vertices] + [from_point2d(polygon[0], z)])
'''

def from_polyline2d(polyline, z=0):
	if polyline.interpolated:
		d=3
	else:
		d=1
	pts = [pt for pt in polyline.vertices]
	p = pts.pop(0)
	if len(p) == 2:
		p = (p[0], p[1], z)
	nC = vs.CreateNurbsCurve(p[0], p[1], z, True,d)
	for p in pts:
		if len(p) == 2:
			p = (p[0], p[1], z)
		vs.AddVertex3D(nC, p[0] , p[1], z)
	vs.SetFPat(nC, 0)
	vs.SetPlanarRef(nC, -1)
	return nC


def from_mesh2d(mesh, z=0):
	if isinstance(z, tuple) :
		if len(z)<3:
			pt_function = 0
		else :
			pt_function = z[2]
	else:
		pt_function = z
	h = _translate_mesh(mesh, pt_function)
	vs.Move3DObj(h,0,0,z)
	vs.SetPlanarRef(h, -1)
	return h

def draw_meshimage(mesh):
	facegroups = []
	fg_colors = []
	fg_normals = []		
	fg_vsets = []
	fg_ed1 = []
	fg_ed2 = []
	fg = []
	fgc = []
	vset = set()
	vts = [ (pt.x , pt.y , pt.z) for pt in mesh.vertices]
	path= hb_folders.python_package_path+"/ladybug_vectorworks/icon_set/LB ImportEPW.png"
	h0 = vs.ImportImageFileN(path, (0,0),1)
	vs.DelObject(h0)
	for i , face in enumerate(mesh.faces):
		ed1 = (vts[face[1]][0] - vts[face[0]][0] , vts[face[1]][1] - vts[face[0]][1] , vts[face[1]][2] - vts[face[0]][2] )
		ed2 = (vts[face[2]][0] - vts[face[1]][0] , vts[face[2]][1] - vts[face[1]][1] , vts[face[2]][2] - vts[face[1]][2] )
		if len(fg)==0:
			fg.append(face)
			fgc.append(mesh.colors[i])
			fg_normals.append(mesh.face_normals[i])
			fg_ed1.append(ed1)
			fg_ed2.append(ed2)
			for vv in face:
				vset.add(vv)
			edge1 = ed1
			edge2 = ed2
			gg = (ed1[0]**2+ed1[1]**2+ed1[2]**2)**0.5/20
		else:
			han = False
			if abs(edge1[0]-ed1[0]) < gg and abs(edge1[1]-ed1[1]) < gg and abs(edge1[2]-ed1[2]) < gg and abs(edge2[0]-ed2[0]) < gg and abs(edge2[1]-ed2[1]) < gg and abs(edge2[2]-ed2[2]) < gg:
				for p in face:
					if p in vset:
						han = True
						break
			if han==False:
				facegroups.append(fg)
				fg_colors.append(fgc)
				fg_vsets.append(vset)
				fg = []
				fgc = []
				vset = set()
				edge1 = ed1
				edge2 = ed2
				fg_normals.append(mesh.face_normals[i])
				fg_ed1.append(ed1)
				fg_ed2.append(ed2)
			fg.append(face)
			fgc.append(mesh.colors[i])
			for vv in face:
				vset.add(vv)
	facegroups.append(fg)
	fg_colors.append(fgc)
	fg_vsets.append(vset)
	
	vs.SetPrefInt(86,2)
	vw_mesh = []
	for kk , faces in enumerate(facegroups):
		x_co =  [vts[v][0] for v in fg_vsets[kk]] 
		y_co =  [vts[v][1] for v in fg_vsets[kk]]
		z_co =  [vts[v][2] for v in fg_vsets[kk]]
		x_min = min (x_co)
		x_max = max (x_co)
		y_min = min (y_co)
		y_max = max (y_co)
		z_min = min (z_co)
		z_max = max (z_co)
		cx = (x_max+ x_min)/2
		cy = (y_max+ y_min)/2
		cz = (z_max+ z_min)/2
		normal = fg_normals[kk]
		if normal[2] !=0:
			pv = [vts[face[0]][0] for face in faces] 
			pw = [vts[face[0]][1] for face in faces]
			v_dim = abs(vts[faces[0][2]][0]-vts[faces[0][0]][0])
			w_dim = abs(vts[faces[0][2]][1]-vts[faces[0][0]][1])
			if normal[2]<0:
				pv.reverse()
			if normal[0] != 0:
				pv , pw = pw , pv
				v_dim , w_dim = w_dim , v_dim
				pw.reverse()
		elif normal[1] ==0:
			pv = [vts[face[0]][1] for face in faces] 
			pw = [vts[face[0]][2] for face in faces]
			v_dim = abs(vts[faces[0][2]][1]-vts[faces[0][0]][1])
			w_dim = abs(vts[faces[0][2]][2]-vts[faces[0][0]][2])
			pw.reverse()
			if normal[0]<0:
				pv.reverse()
		else:
			pv = [vts[face[0]][0] for face in faces] 
			pw = [vts[face[0]][2] for face in faces]
			v_dim = abs(vts[faces[0][2]][0]-vts[faces[0][0]][0])
			w_dim = abs(vts[faces[0][2]][2]-vts[faces[0][0]][2])
			pw.reverse()
			if normal[1]<0:
				pv.reverse()
		v_min = min(pv)  
		v_max = max(pv)  
		w_min = min(pw)  
		w_max = max(pw)
		v_count = int((v_max-v_min)/v_dim)+1
		w_count = int((w_max-w_min)/w_dim)+1
		from PIL import Image,ImageDraw
		img = Image.new("RGBA",(v_count*2,w_count*2))
		draw = ImageDraw.Draw(img)
		(av,aw) = (v_min,w_min)
		
		for k ,face in enumerate(faces):
			ppv = round((pv[k]-av)/v_dim)
			ppw = round((pw[k]-aw)/w_dim)
			col = fg_colors[kk][k]
			draw.rectangle(((ppv*2,ppw*2),(ppv*2+1,ppw*2+1)),(col.r,col.g,col.b,255))
			
		img_path = hb_folders.default_simulation_folder+"/mashimg.png"
		img.save(img_path)
		
		msh = vs.ImportImageFile(img_path, (0,0))
		((b1x,b1y),(b2x,b2y)) = vs.GetBBox(msh)
		imw = b2x-b1x
		imh = b2y-b1y
		vs.DelObject(msh)
		
		igr = None
		igr = vs.BeginGroupN(igr)	
		(a1,a2,a3) = fg_ed1[kk]
		l = (a1**2+a2**2+a3**2)**0.5
		vs.SetWorkingPlaneN((cx,cy,cz),(normal.x,normal.y,normal.z),(a1/vv,a2/vv,a3/vv))
		pl_id = vs.GetCurrentPlanarRefID()
		msh = vs.ImportImageFileN(img_path, (0,0),1)
		vs.SetPlanarRef(msh, pl_id)
		
		vv = (fg_ed1[kk][0]**2+fg_ed1[kk][1]**2+fg_ed1[kk][2]**2)**0.5
		vw = (fg_ed2[kk][0]**2+fg_ed2[kk][1]**2+fg_ed2[kk][2]**2)**0.5
		vs.HScale2D(msh,cx,cy,vv*v_count/imw,vw*w_count/imh,False)
		#vs.HMove(msh,-icx,-icy)
		vs.SetWorkingPlaneN( (0,0,0),(0,0,1),(1,0,0) )
		vs.EndGroup()
		((icx,icy),icz) = vs.Get3DCntr(igr)
		vs.Move3DObj(igr , cx-icx, cy-icy,cz-icz)
		vs.HUngroup(igr)
		vw_mesh.append(msh)

	return vw_mesh
   

"""____________3D GEOMETRY TRANSLATORS____________"""



def from_vector3d(pts):
	p2 = (pts.x,pts.y,pts.z)
	return p2


def from_point3d(pts):
	p2 = (pts.x,pts.y,pts.z)
	#vs.Locus3D(p2)
	return p2

'''
def from_ray3d(ray):
	return rg.Ray3d(from_point3d(ray.p), from_vector3d(ray.v))
'''


def from_linesegment3d(line):
	vs.BeginPoly3D()
	vs.Add3DPt(line.p1.x,line.p1.y,line.p1.z)
	vs.Add3DPt(line.p2.x,line.p2.y,line.p2.z)
	vs.EndPoly3D()
	obj = vs.LNewObj()
	vs.SetFPat(obj, 0)
	return obj


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
		vs.SetWorkingPlaneN((arc.plane.o.x,arc.plane.o.y,arc.plane.o.z),(arc.plane.n.x,arc.plane.n.y,arc.plane.n.z),(arc.plane.y.x,arc.plane.y.y,arc.plane.y.z))
		pl_id = vs.GetCurrentPlanarRefID()
		r1 = math.degrees(arc.a1)
		r2 = math.degrees(arc.a2)
		if arc.plane.o.z<0:
			vs.ArcByCenter(0,0,arc.radius,r1-90,(r2-r1))
		else:
			vs.ArcByCenter(0,0,arc.radius,r1-90,180+r2*2)
		obj = vs.LNewObj() 
		vs.SetPlanarRef(obj, pl_id)
		vs.SetWorkingPlaneN( (0,0,0),(0,0,1),(1,0,0) )
		vs.SetFPat(obj, 0)
		return obj


def from_polyline3d(polyline):
	if polyline.interpolated:
		d=3
	else:
		d=1
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
	vs.ClosePoly()
	vw_poly = []
	normals = poly.face_normals
	offset = 13000/vs.GetLScale(vs.ActLayer())
	for i in range(0,len(poly.faces)):
		face = poly.faces[i]
		pts = []
		for pt in tuple(poly[i] for i in face):
			pts.append((pt.x,pt.y,pt.z))
		vs.Poly3D(*pts)
		po = vs.LNewObj()
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
	vs.ClosePoly()
	pts = face.vertices
	pts = [(pt.x,pt.y,pt.z) for pt in pts]
	vs.Poly3D(*pts)
	po = vs.LNewObj()
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


def from_polyline2d_to_joined_polyline(polylines, z=0):
	line_crv = []
	for pl in polylines:
		if isinstance(pl, LineSegment2D):
			line_crv.append(from_linesegment2d(pl))
		else:
			line_crv.append(from_polyline2d(pl))
	return line_crv
	'''### 線の合成の仕方が不明
	obj = line_crv[0]
	for i in range(0,len(line_crv)):
		vs.AddSurface(obj, line_crv[i])
	return obj
	'''


def from_polyline2d_to_offset_brep(polylines, offset, z=0):
	curve = from_polyline2d_to_joined_polyline(polylines, z)
	curve2 = []
	for c in curve:
		curve2.append(vs.OffsetPolyClosed(c, offset, False))
	for c in curve:
		vs.DelObject(c)
	return curve2
	'''
	curve2 = vs.OffsetPolyClosed(curve, offset, False)
	vs.DelObject(curve)
	return curve2
	'''


def from_face3d_to_wireframe(face):
	vs.ClosePoly()
	boundary = [_polyline_points(face.boundary)]
	for obj in boundary:
		vs.SetFPat(obj, 0)
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
			po = from_mesh3d(face.triangulated_mesh3d)
			col = color_to_color(color)
			vs.SetFillBack(po,col)
			joined_mesh.Append(po)
		except Exception:
			po = None  # failed to create a Rhino Mesh from the Face3D
		
	#joined_mesh.VertexColors.CreateMonotoneMesh(color_to_color(color))
	return joined_mesh



def from_mesh2d_to_outline(mesh, z=0):
	vs.ClosePoly()
	if isinstance(z, tuple) :
		if len(z)<3:
			pt_function = 0
		else :
			pt_function = z[2]
	else:
		pt_function = z
	h = _translate_mesh(mesh, pt_function)
	vs.Move3DObj(h,0,0,z)
	h = vs.MeshToGroup(h)
	obj = vs.FInGroup( h )
	while obj != None:
		vs.SetFPat(obj, 0)
		obj = vs.NextObj( obj )
	return [h]

def from_mesh3d_to_outline(mesh):
	mesh = mesh.offset_mesh( 100/vs.GetLScale(vs.ActLayer()) )
	rh_mesh = from_mesh3d_to_poly(mesh)
	'''
	r0 = vs.CreateDuplicateObject(rh_mesh[0],vs.Handle(0))
	r1 = vs.CreateDuplicateObject(rh_mesh[1],vs.Handle(0))
	re , outlines = vs.AddSolid(r0, r1)
	h0 = vs.FIn3D( outlines )
	for i in range(2,len(rh_mesh)):
		vs.CreateDuplicateObject(rh_mesh[i],vs.GetParent(h0))
	'''
	faces = []
	for obj in rh_mesh:
		faces.append(obj)
		obj = vs.NextObj( obj )
	outlines =[]
	outline = faces[0]
	for i in range(1,len(faces)):
		re ,outline2 = vs.AddSolid(outline, faces[i])
		if re>0:
			outlines.append(outline)
			outline = faces[i]
		else:
			outline = outline2
	outlines.append(outline)
	
	return rh_mesh,outlines


"""________________EXTRA HELPER FUNCTIONS________________"""


def _translate_mesh(mesh, z):
	vs.ClosePoly()
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
			if mesh.colors is not None:
				col = color_to_color(mesh.colors[face[0]])
				vs.SetFillBack(po,col)
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
	
def from_mesh3d_to_poly(mesh):
	vs.ClosePoly()
	if mesh.is_color_by_face:  # Mesh is constructed face-by-face
		vw_mesh = []
		for i in range(0,len(mesh.faces)):
			face = mesh.faces[i]
			pts = []
			for pt in tuple(mesh[i] for i in face):
				pts.append((pt.x,pt.y,pt.z))
			vs.Poly3D(*pts)
			po = vs.LNewObj()
			if mesh.colors is not None:
				col = color_to_color(mesh.colors[i])
				vs.SetFillBack(po,col)
			vw_mesh.append(po)

	else:  # Mesh is constructed vertex-by-vertex
		vw_mesh = []
		for i in range(0,len(mesh.faces)):
			face = mesh.faces[i]
			pts = []
			for pt in tuple(mesh[i] for i in face):
				pts.append((pt.x,pt.y,pt.z))
			vs.Poly3D(*pts)
			po = vs.LNewObj()
			if mesh.colors is not None:
				col = color_to_color(mesh.colors[face[0]])
				vs.SetFillBack(po,col)
			vw_mesh.append(po)

	return vw_mesh


def _polyline_points(tup):
	vs.ClosePoly()
	pts = []
	for pt in tup:
		pts.append((pt.x,pt.y,pt.z))
	vs.Poly3D(*pts)
	po = vs.LNewObj()
	return po 
