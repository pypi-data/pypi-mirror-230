# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileCopyrightText: Czech Technical University in Prague

from setuptools import setup

setup(
    name="http-relay",
    version="2.1.3",
    description="Relay for HTTP messages (reverse proxy)",
    author="Martin Pecka",
    author_email="peci1@seznam.cz",
    maintainer="Martin Pecka",
    maintainer_email="peci1@seznam.cz",
    url="https://github.com/ctu-vras/http_relay",
    license="BSD 3-Clause",
    python_requires='>=2.7',
    packages=["http_relay"],
    package_dir={"": "src"},
    extras_require={"test": ['pytest']},
    entry_points={"console_scripts": ["http-relay = http_relay.__main__:main"]},
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Communications",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ],
    keywords=["http", "proxy"],
)
