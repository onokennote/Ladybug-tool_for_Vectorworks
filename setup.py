import setuptools

with open("README.md", "r") as fh:
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
	url="https://github.com/onokennote/ladybug_vectorworks",
	packages=setuptools.find_packages(exclude=["tests"]),
	packages=find_packages(),
    package_data={
        'ladybug_vectorworks.icon_set': ['*.png'],
    },
	license="AGPL-3.0"
)