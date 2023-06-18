import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
	long_description = fh.read()
setuptools.setup(
	name="ladybug_vectorworks",
	use_scm_version=True,
	setup_requires=['setuptools_scm'],
	author="onokennote",
	author_email="info@onoken-web.com",
	description="A library for communicating between Ladybug Tools core libraries and Vectorwroks CAD.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/onokennote/Ladybug-tool_for_Vectorworks.git",
	packages=setuptools.find_packages(exclude=["tests"]),
	package_data={
		'ladybug_vectorworks': ['icon_set/*.png'],
<<<<<<< HEAD
		'ladybug_vectorworks': ['etc/*.vwx'],
		'ladybug_vectorworks': ['etc/*.pdf'],
		'ladybug_vectorworks': ['etc/*.epw'],
=======
>>>>>>> d83f573d3abec43a29c6633cddf7cc3da3fc9953
	},
	license="AGPL-3.0"
)
