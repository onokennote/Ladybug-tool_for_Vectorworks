import vs
import json
import math
import itertools
import operator

def color_to_color(color, alpha=255):
	co = vs.RGBToColorIndex(color.r,color.g,color.b)
	return (color.r*256,color.g*256,color.b*256)

def gray():
	return (200*256,200*256,200*256)
    
def black():
	return (0,0,0)