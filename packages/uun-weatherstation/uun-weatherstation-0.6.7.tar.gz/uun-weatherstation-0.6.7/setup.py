import setuptools
import shutil
import os
import re

name="uun-weatherstation"
name_=name.replace('-', '_')

# version from exported binary
pkg_path = os.path.abspath(os.path.dirname(__file__))
with open(f"{pkg_path}/bin/{name}", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setuptools.setup(
    name=name,
    version=version,
    author="(UUN) Tomáš Faikl",
    author_email="tomas.faikl@unicornuniversity.net",
    description="Get weather conditions from WeatherLink and send them to uuApp.",
    url="https://uuos9.plus4u.net/uu-bookkitg01-main/c145b7fe6d754775b71e196b3fbb9a6a/book/page?code=home",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
    install_requires=[
        "uun-iot>=0.9.3",
        "requests>=2.24.0"
    ],
    scripts=[
        "bin/" + name,
        "bin/" + name + "-install"
    ],
    package_data={
        name_: ["data/*"]
    }
)

