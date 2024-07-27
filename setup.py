from setuptools import setup, Extension, find_packages
from codecs import open
# from Cython.Build import cythonize
import os

long_description = ""

# Load README.rst into long description. User can skip using README.rst as long description:
# GGWAVE_OMIT_README_RST=1 python setup.py install
OMIT_README_RST = os.getenv('GGWAVE_OMIT_README_RST', True)
if not OMIT_README_RST:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()

extension = [Extension("ggtransfer.ggwave",
                       ["src/ggtransfer/ggwave/ggwave.pyx", "src/ggtransfer/ggwave/ggwave/src/ggwave.cpp"],
                       include_dirs=["src/ggtransfer/ggwave", "src/ggtransfer/ggwave/ggwave/include", "src/ggtransfer/ggwave/ggwave/include/ggwave"],
                       depends=["src/ggtransfer/ggwave/ggwave/include/ggwave/ggwave.h", "src/ggtransfer/ggwave/cggwave.pxd"],
                       language="c++",
                       )]

# extension = cythonize(extension)

setup(
    # Information
    name="ggtransfer.ggwave",
    # description="Tiny data-over-sound library.",
    # long_description=long_description,
    # version="0.4.2",
    # url="https://github.com/ggerganov/ggwave",
    # author="Georgi Gerganov",
    # author_email="ggerganov@gmail.com",
    # license="MIT",
    # keywords="data-over-sound fsk ecc serverless pairing qrcode ultrasound",
    # packages=["ggtransfer.ggwave"],
    # packages=find_packages(where="src/ggtransfer", include=["ggwave"]),
    # Build instructions
    ext_modules=extension,
)
