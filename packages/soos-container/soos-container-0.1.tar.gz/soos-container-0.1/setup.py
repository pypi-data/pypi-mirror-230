from setuptools import setup, find_packages

setup(
    name='soos-container',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'soos-container=soos_container.cli:main',
        ],
    },
)