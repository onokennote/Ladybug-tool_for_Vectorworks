from __future__ import division
import math
import vs

def obj2plane(obj , plane ):
	(ax,ay,az ) =plane.o
	vx = plane.x
	vy = plane.y
	vs.Move3DObj(obj,ax,ay,az)
	return obj


def text_objects(text, plane, height, font='Arial',
	horizontal_alignment=1, vertical_alignment=4):
	if horizontal_alignment==0:
		horizontal_alignment=1
	if vertical_alignment==5:
		vertical_alignment=4
	vs.SetWorkingPlaneN((plane.o.x,plane.o.y,plane.o.z),(plane.n.x,plane.n.y,plane.n.z),(plane.x.x,plane.x.y,plane.x.z),)
	tex = text.split('\n')
	obj = []
	LayerScale  = vs.GetLScale(vs.ActLayer())
	for i in range(0,len(tex)):
		vs.MoveTo(0,-i*height*1.2)
		vs.CreateText(tex[i])
		vs.SetTextSize(vs.LNewObj(),0,1000,height/0.3528/LayerScale)
		vs.SetTextJust(vs.LNewObj(), horizontal_alignment)
		vs.SetTextVerticalAlign(vs.LNewObj(),vertical_alignment)
		obj.append(vs.LNewObj() )
	vs.SetWorkingPlaneN( (0,0,0),(0,0,1),(1,0,0) )
	return obj
