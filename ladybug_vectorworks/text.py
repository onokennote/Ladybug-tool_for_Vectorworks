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

"""____________EXTRA HELPER OBJECTS____________"""

'''
class TextGoo(gh.Kernel.Types.GH_GeometricGoo[rh.Display.Text3d],
              gh.Kernel.IGH_BakeAwareData, gh.Kernel.IGH_PreviewData):
    """A Text object that can be baked and transformed in Grasshopper.

    The code for this entire class was taken from David Rutten and Giulio Piacentino's
    script described here:
    https://discourse.mcneel.com/t/creating-text-objects-and-outputting-them-as-normal-rhino-geometry/47834/7

    Args:
        text: A Rhino Text3d object.
    """

    def __init__(self, text):
        """Initialize Bake-able text."""
        self.m_value = text

    @staticmethod
    def DuplicateText3d(original):
        if original is None:
            return None
        text = rh.Display.Text3d(original.Text, original.TextPlane, original.Height)
        text.Bold = original.Bold
        text.Italic = original.Italic
        text.FontFace = original.FontFace
        return text

    def DuplicateGeometry(self):
        return TextGoo(TextGoo.DuplicateText3d(self.m_value))

    def get_TypeName(self):
        return "3D Text"

    def get_TypeDescription(self):
        return "3D Text"

    def get_Boundingbox(self):
        if self.m_value is None:
            return rh.Geometry.BoundingBox.Empty
        return self.m_value.BoundingBox

    def GetBoundingBox(self, xform):
        if self.m_value is None:
            return rh.Geometry.BoundingBox.Empty
        box = self.m_value.BoundingBox
        corners = xform.TransformList(box.GetCorners())
        return rh.Geometry.BoundingBox(corners)

    def Transform(self, xform):
        text = TextGoo.DuplicateText3d(self.m_value)
        if text is None:
            return TextGoo(None)

        plane = text.TextPlane
        point = plane.PointAt(1, 1)

        plane.Transform(xform)
        point.Transform(xform)
        dd = point.DistanceTo(plane.Origin)

        text.TextPlane = plane
        text.Height *= dd / math.sqrt(2)
        new_text = TextGoo(text)

        new_text.m_value.Bold = self.m_value.Bold
        new_text.m_value.Italic = self.m_value.Italic
        new_text.m_value.FontFace = self.m_value.FontFace
        return new_text

    def Morph(self, xmorph):
        return self.DuplicateGeometry()

    def get_ClippingBox(self):
        return self.get_Boundingbox()

    def DrawViewportWires(self, args):
        if self.m_value is None:
            return
        color = black() if black is not None else args.Color
        args.Pipeline.Draw3dText(self.m_value, color)

    def DrawViewportMeshes(self, args):
        # Do not draw in meshing layer.
        pass

    def BakeGeometry(self, doc, att, id):
        id = guid.Empty
        if self.m_value is None:
            return False, id
        if att is None:
            att = doc.CreateDefaultAttributes()
        original_plane = None
        d_txt = self.m_value.Text
        nl_count = len(d_txt.split('\n')) - 1
        if nl_count > 1 and str(self.m_value.VerticalAlignment) == 'Bottom':
            y_ax = rh.Geometry.Vector3d(self.m_value.TextPlane.YAxis)
            txt_h = self.m_value.Height * (3 / 2)
            m_vec = rh.Geometry.Vector3d.Multiply(y_ax, txt_h * -nl_count)
            original_plane = self.m_value.TextPlane
            new_plane = rh.Geometry.Plane(self.m_value.TextPlane)
            new_plane.Translate(m_vec)
            self.m_value.TextPlane = new_plane
        self.m_value.Height = self.m_value.Height * (2 / 3)
        id = doc.Objects.AddText(self.m_value, att)
        self.m_value.Height = self.m_value.Height * (3 / 2)
        if original_plane is not None:
            self.m_value.TextPlane = original_plane
        return True, id

    def ScriptVariable(self):
        """Overwrite Grasshopper ScriptVariable method."""
        return self

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        if self.m_value is None:
            return "<null>"
        return self.m_value.Text


class AlignmentTypes(object):
    """Enumeration of text alignment types."""

    _HORIZONTAL = (rh.DocObjects.TextHorizontalAlignment.Left,
                   rh.DocObjects.TextHorizontalAlignment.Center,
                   rh.DocObjects.TextHorizontalAlignment.Right)

    _VERTICAL = (rh.DocObjects.TextVerticalAlignment.Top,
                 rh.DocObjects.TextVerticalAlignment.MiddleOfTop,
                 rh.DocObjects.TextVerticalAlignment.BottomOfTop,
                 rh.DocObjects.TextVerticalAlignment.Middle,
                 rh.DocObjects.TextVerticalAlignment.MiddleOfBottom,
                 rh.DocObjects.TextVerticalAlignment.Bottom,
                 rh.DocObjects.TextVerticalAlignment.BottomOfBoundingBox)

    @classmethod
    def horizontal(cls, field_number):
        """Get a Rhino horizontal alignment object by its integer field number.

        * 0 - Left
        * 1 - Center
        * 2 - Right

        """
        return cls._HORIZONTAL[field_number]

    @classmethod
    def vertical(cls, field_number):
        """Get a Rhino vertical alignment object by its integer field number.

        * 0 - Top
        * 1 - MiddleOfTop
        * 2 - BottomOfTop
        * 3 - Middle
        * 4 - MiddleOfBottom
        * 5 - Bottom
        * 6 - BottomOfBoundingBox

        """
        return cls._VERTICAL[field_number]
'''