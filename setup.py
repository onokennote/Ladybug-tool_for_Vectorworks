import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
	long_description = fh.read()
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
setuptools.setup(
	name="ladybug_vectorworks",
	version="0.2.1",
	author="onokennote",
	author_email="info@onoken-web.com",
	description="A library for communicating between Ladybug Tools core libraries and Vectorwroks CAD.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/onokennote/Ladybug-tool_for_Vectorworks.git",
	packages=setuptools.find_packages(exclude=["tests"]),
	package_data={
		'ladybug_vectorworks': ['icon_set/*.png','etc/*.vwx','etc/*.pdf','etc/*.epw'],
	},
	install_requires=requirements,
	license="AGPL-3.0"
)
