import setuptools
from io import open

with open(r'C:\Users\TT\Desktop\PyAlphabet\README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

version = '1.1'
setuptools.setup(
	name='PyAlphabet',
	version=version,
	author='Scrambler',
	author_email='vagifhalilov02@gmail.com',
	description='',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/Shedrjoinzz/Scrambler-PyAlphabet',
	download_url="https://github.com/Shedrjoinzz/Scrambler-PyAlphabet/zipball/master/",
	packages=['PyAlphabet'],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.6'
)