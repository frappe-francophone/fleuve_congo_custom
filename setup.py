from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in fleuve_congo_custom/__init__.py
from fleuve_congo_custom import __version__ as version

setup(
	name="fleuve_congo_custom",
	version=version,
	description="Fleuve Congo Customization",
	author="Kossivi Amouzou",
	author_email="dodziamouzou@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
