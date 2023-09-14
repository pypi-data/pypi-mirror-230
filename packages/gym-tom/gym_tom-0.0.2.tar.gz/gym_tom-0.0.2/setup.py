from setuptools import setup

setup(
    name="gym_tom",
    packages = ['gym_tom', 'gym_tom.envs'],
    version="0.0.2",
    license='unlicense',
    install_requires=["gym==0.26.0", "pygame==2.1.0"],

)