from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.3'
DESCRIPTION = 'Sebuah pakej yang boleh menghasilkan pelbagai data berkenaan falak'
LONG_DESCRIPTION = 'Sebuah pakej python yang menggunakan ephemeris dari JPL Horizon bagi menghasilkan hitungan falak'

# Setting up
setup(
    name="EphemSahabatFalak",
    version=VERSION,
    author="cartcosine (izzatzubir)",
    author_email="<cart.cosine.0x@icloud.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    include_package_data = True,
    install_requires=['skyfield', 'pytz', 'datetime', 'DateTime', 'mpmath', 'pandas', 'timezonefinder',
                       'matplotlib', 'numpy', 'geopandas', 'geodatasets'],
    keywords=['falak', 'solat', 'hilal', 'waktu', 'matahari', 'bulan', 'kiblat'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)