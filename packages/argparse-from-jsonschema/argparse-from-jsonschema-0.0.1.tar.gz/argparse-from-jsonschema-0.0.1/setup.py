from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

name = 'argparse-from-jsonschema'
module = name.replace("-", "_")
setup(
    name=name,
    version='0.0.1',
    description='Parse Argument with JSON Schema',
    url=f'https://github.com/LeConTesteur/{name}',
    author='LeConTesteur',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='Argument Schema',
    entry_points={
        'console_scripts': [f'{name}={module}:main'],
    },
    py_modules=[f'{module}']
)
