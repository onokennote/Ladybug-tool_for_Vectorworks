
import math
import vs

from ladybug_vectorworks.fromgeometry import from_mesh3d, from_arc2d, from_linesegment2d
from ladybug_vectorworks.text import text_objects

try:
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
    from ladybug_geometry.geometry3d.plane import Plane
except ImportError as e:
    raise ImportError("Failed to import ladybug_geometry.\n{}".format(e))


def legend_objects(legend):
		_height = legend.legend_parameters.text_height
		_font = legend.legend_parameters.font
		legend_mesh = from_mesh3d(legend.segment_mesh)
		legend_title = text_objects(legend.title, legend.title_location, _height, _font)
		if legend.legend_parameters.continuous_legend is False:
			legend_text = [text_objects(txt, loc, _height, _font, 0, 5) for txt, loc in
						   zip(legend.segment_text, legend.segment_text_location)]
		elif legend.legend_parameters.vertical is True:
			legend_text = [text_objects(txt, loc, _height, _font, 0, 3) for txt, loc in
						   zip(legend.segment_text, legend.segment_text_location)]
		else:
			legend_text = [text_objects(txt, loc, _height, _font, 1, 5) for txt, loc in
						   zip(legend.segment_text, legend.segment_text_location)]
		return [legend_mesh] + [legend_title] + legend_text


def compass_objects(compass, z=0, custom_angles=None, projection=None, font='Arial'):
	# set default variables based on the compass properties
	maj_txt = compass.radius / 20
	min_txt = maj_txt / 2
	
	xaxis = Vector3D(1, 0, 0).rotate_xy(math.radians(compass.north_angle))
	#r = math.radians(compass.north_angle)
	#xaxis = ( math.cos(r) , math.sin(r) ,0)

	result = []  # list to hold all of the returned objects
	for circle in compass.all_boundary_circles:
		result.append(from_arc2d(circle, z))

	# generate the labels and tick marks for the azimuths
	if custom_angles is None:
		for line in compass.major_azimuth_ticks:
			result.append(from_linesegment2d(line, z))
		for txt, pt in zip(compass.MAJOR_TEXT, compass.major_azimuth_points):
			(px,py)=pt
			txt_pln = Plane(o=Point3D(px, py, z), x=xaxis)
			result.append(text_objects(txt, txt_pln, maj_txt, font, 1, 3))
		for line in compass.minor_azimuth_ticks:
			result.append(from_linesegment2d(line, z))
		for txt, pt in zip(compass.MINOR_TEXT, compass.minor_azimuth_points):
			(px,py)=pt
			txt_pln = Plane(o=Point3D(px, py, z), x=xaxis)
			result.append(text_objects(txt, txt_pln, min_txt, font, 1, 3))
	else:
		for line in compass.ticks_from_angles(custom_angles):
			result.append(from_linesegment2d(line, z))
		for txt, pt in zip(
				custom_angles, compass.label_points_from_angles(custom_angles)):
			txt_pln = Plane(o=Point3D(pt.x, pt.y, z), x=xaxis)
			result.append(text_objects(str(txt), txt_pln, maj_txt, font, 1, 3))

	# generate the labels and tick marks for the altitudes
	if projection is not None:
		if projection.title() == 'Orthographic':
			for circle in compass.orthographic_altitude_circles:
				result.append(from_arc2d(circle, z))
			for txt, pt in zip(compass.ALTITUDES, compass.orthographic_altitude_points):
				txt_pln = Plane(o=Point3D(pt.x, pt.y, z), x=xaxis)
				result.append(text_objects(str(txt), txt_pln, min_txt, font, 1, 0))
		elif projection.title() == 'Stereographic':
			for circle in compass.stereographic_altitude_circles:
				result.append(from_arc2d(circle, z))
			for txt, pt in zip(compass.ALTITUDES, compass.stereographic_altitude_points):
				txt_pln = Plane(o=Point3D(pt.x, pt.y, z), x=xaxis)
				result.append(text_objects(str(txt), txt_pln, min_txt, font, 1, 0))

	return result
