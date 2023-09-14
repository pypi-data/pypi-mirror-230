import setuptools

with open("README.md", "r") as fh:
	description = fh.read()

setuptools.setup(
	name="count_app",
	version="0.0.1",
	author="FaithN",
	author_email="faithnchifor@gmail.com",
	packages=["count_app"],
	description="A sample test package",
	long_description=description,
	long_description_content_type="text/markdown",
	url="https://github.com/faith-nchifor/test-packagew",
	license='MIT',
	python_requires='>=3.8',
	install_requires=[]
)
