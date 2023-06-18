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
	horizontal_alignment += 1
	if vertical_alignment==5:
		vertical_alignment=4
	vs.SetWorkingPlaneN((plane.o.x,plane.o.y,plane.o.z),(plane.n.x,plane.n.y,plane.n.z),(plane.x.x,plane.x.y,plane.x.z),)
	pl_id = vs.GetCurrentPlanarRefID()
	tex = text.split('\n')
	obj = []
	LayerScale  = vs.GetLScale(vs.ActLayer())
	(fraction, display, format, upi, name, squareName) =  vs.GetUnits()
	for i in range(0,len(tex)):
		vs.MoveTo(0,-i*height*1.2)
		vs.CreateText(tex[i])
		tx = vs.LNewObj()
		vs.SetTextSize( tx ,0,1000,72*height/LayerScale/upi)
		vs.SetTextJust( tx , horizontal_alignment)
		vs.SetTextVerticalAlign(tx,vertical_alignment)
		vs.SetFPat(tx, 0)
		vs.SetPlanarRef(tx, pl_id)
		obj.append(tx)
	vs.SetWorkingPlaneN( (0,0,0),(0,0,1),(1,0,0) )
	return obj

