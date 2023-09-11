import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="limitlessled_rf",
	version="0.15",
	author="Roy Keene",
	author_email="pypi@rkeene.org",
	description="Python LimitlessLED via RF",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://chiselapp.com/user/rkeene/repository/limitlessled_rf/",
	packages=["limitlessled_rf"],
	package_dir={"":"."},
	license="MIT License",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6'
)
