from setuptools import setup, find_packages

setup(
    name='Entratools',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        'console_scripts': [
        'Entratools=Entratools.cli_commands:app',
      ],
    },
    author='Your Name',
    description='Description of your package',
)
