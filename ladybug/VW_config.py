
import os

try:
	from ladybug.config import folders as lb_folders
except ImportError as e:
	raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

import vs

tolerance = 0.01
angle_tolerance = 1.0  

#from .ghpath import find_grasshopper_userobjects, find_grasshopper_libraries


def conversion_to_meters():
	return 0.001


def units_system():
	(fraction, display, format, upi, name, squareName) =  vs.GetUnits()
	re = 'Meters'
	if name == 'mm':
		re = 'Millimeters'
	if name == 'cm':
		re = 'Centimeters'
	if name == "'":
		re = 'Feet'
	if name == "''":
		re = 'Inches'
	return re
	#try:  # Try to import units from the active Rhino document
	#	 import scriptcontext
	#	 return str(scriptcontext.doc.ModelUnitSystem).split('.')[-1]
	#except ImportError:  # No Rhino doc available. Default to the greatest of all units
	

def units_abbreviation():
	(fraction, display, format, upi, name, squareName) =  vs.GetUnits()
	return name
	'''"""Get text for the current Rhino doc units abbreviation (eg. 'm', 'ft')"""
	try:  # Try to import units from the active Rhino document
		import scriptcontext
		units = str(scriptcontext.doc.ModelUnitSystem).split('.')[-1]
	except ImportError:	 # No Rhino doc available. Default to the greatest of all units
		units = 'Meters'

	if units == 'Meters':
		return 'm'
	elif units == 'Millimeters':
		return 'mm'
	elif units == 'Feet':
		return 'ft'
	elif units == 'Inches':
		return 'in'
	elif units == 'Centimeters':
		return 'cm'
	else:
		raise ValueError(
			"You're kidding me! What units are you using?" + units + "?\n"
			"Please use Meters, Millimeters, Centimeters, Feet or Inches.")
	'''
'''
class Folders(object):
	"""Ladybug-rhino folders.

	Properties:
		* uo_folder
		* gha_folder
		* lbt_grasshopper_version
		* lbt_grasshopper_version_str
	"""

	def __init__(self):
		# find the location where the Grasshopper user objects are stored
		self._uo_folder = find_grasshopper_userobjects()[-1]
		self._gha_folder = find_grasshopper_libraries()[-1]
		if os.name == 'nt':
			# test to see if components live in the core installation
			lbt_components = os.path.join(lb_folders.ladybug_tools_folder, 'grasshopper')
			if os.path.isdir(lbt_components):
				user_dir = os.path.join(self._uo_folder, 'ladybug_grasshopper')
				if not os.path.isdir(user_dir):
					self._uo_folder = lbt_components
					self._gha_folder = lbt_components
		self._lbt_grasshopper_version = None
		self._lbt_grasshopper_version_str = None

	@property
	def uo_folder(self):
		"""Get the path to the user object folder."""
		return self._uo_folder

	@property
	def gha_folder(self):
		"""Get the path to the GHA Grasshopper component folder."""
		return self._gha_folder

	@property
	def lbt_grasshopper_version(self):
		"""Get a tuple for the version of lbt-grasshopper (eg. (3, 8, 2)).

		This will be None if the version could not be sensed.
		"""
		if self._lbt_grasshopper_version is None:
			self._lbt_grasshopper_version_from_txt()
		return self._lbt_grasshopper_version

	@property
	def lbt_grasshopper_version_str(self):
		"""Get text for the full version of python (eg."3.8.2").

		This will be None if the version could not be sensed.
		"""
		if self._lbt_grasshopper_version_str is None:
			self._lbt_grasshopper_version_from_txt()
		return self._lbt_grasshopper_version_str

	def _lbt_grasshopper_version_from_txt(self):
		"""Get the LBT-Grasshopper version from the requirements.txt file in uo_folder.
		"""
		req_file = os.path.join(self._uo_folder, 'requirements.txt')
		if os.path.isfile(req_file):
			with open(req_file) as rf:
				for row in rf:
					if row.startswith('lbt-grasshopper=='):
						lbt_ver = row.split('==')[-1].strip()
						try:
							self._lbt_grasshopper_version = \
								tuple(int(i) for i in lbt_ver.split('.'))
							self._lbt_grasshopper_version_str = lbt_ver
						except Exception:
							pass  # failed to parse the version into values
						break
'''

'''
folders = Folders()
'''
