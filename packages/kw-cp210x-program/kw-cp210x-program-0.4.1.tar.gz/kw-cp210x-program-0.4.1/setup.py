# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="kw-cp210x-program",
    description="Provides access to the EEPROM in an Silabs CP210x",
    long_description="""
The goal of this library is to provide access to the EEPROM of an Silabs CP210x
under Linux.

The CP210x is an USB-to-serial chip used in a lot of USB devices (similar to
FTDIs and PL2303). The CP210x has a EEPROM on the chip which can be programmed
via USB. Silabs provides already a library and gui programm to program this
EEPROM, but only for windows.

For more information see:
* http://www.silabs.com/tgwWebApp/public/web_content/products/Microcontrollers/Interface/en/interface.htm
* http://www.silabs.com/public/documents/tpub_doc/anote/Microcontrollers/Interface/en/an144.pdf

Requires:
* libusb: http://libusb.sourceforge.net/
* ctypes: http://starship.python.net/crew/theller/ctypes/
""",
    long_description_content_type="text/x-rst",
    author="Johannes Hölzl",
    author_email="johannes.hoelzl@gmx.de",
    url="https://github.com/VCTLabs/cp210x-program",
    platforms="POSIX",
    classifiers=[
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Intended Audience :: Manufacturing",
        "Development Status :: 4 - Beta",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Programming Language :: Python",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: MacOS :: MacOS X",
    ],
    packages=[
        'cp210x'
    ],
    scripts=[
        'scripts/cp210x-program.py'
    ],
)
