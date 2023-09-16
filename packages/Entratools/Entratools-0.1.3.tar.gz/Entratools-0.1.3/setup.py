from setuptools import setup, find_packages

setup(
    name='Entratools',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        'console_scripts': [
        'Entratools=Entratools.cli_commands:app',
      ],
    },
    author='Emiliano Fripp',
    description='Tools for easier development',
)
