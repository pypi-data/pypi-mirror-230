from setuptools import setup, find_packages

setup(
    name='Entratools',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        'console_scripts': [
            'my-cli-command = Entratools.Utils.cli_commands:cli_command',
        ],
    },
    author='Your Name',
    description='Description of your package',
)
