from setuptools import setup
from mypyc.build import mypycify

setup(
    name='nostril',
    packages=['nostril'],
    ext_modules=mypycify(['-p', 'nostril.nonsense_detector']),
)