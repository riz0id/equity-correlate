import os
import platform
import re
import sys

from setuptools import Extension, setup

PLATFORMS = {"windows", "linux", "darwin", "cygwin", "android"}

target = platform.system().lower()

if "pydroid3" in sys.executable.lower():
    target = "android"

for known in PLATFORMS:
    if target.startswith(known):
        target = known

if target not in PLATFORMS:
    target = "linux"

libraries = {
    "windows": [],
    "linux": [],
    "cygwin": [],
    "darwin": [],
    "android": [],
}

extra_compile_args = {
    "windows": ["-fpermissive"],
    "linux": ["-fpermissive"],
    "cygwin": ["-fpermissive"],
    "darwin": ["-Wno-deprecated-declarations"],
    "android": ["-fpermissive"],
}

extra_linker_args = {
    "windows": [],
    "linux": [],
    "cygwin": [],
    "darwin": [],
    "android": [],
}

short_description = "Calculate correlation coefficients of prices between two or more equities."

with open("README.md") as f:
    long_description = re.sub(r"</?div[^>]*>|\r", "", f.read(), flags=re.M)

keywords = [
    "cryptography",
    "finance",
]

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "License :: OSI Approved",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Games/Entertainment",
    "Topic :: Multimedia :: Graphics",
    "Topic :: Multimedia :: Graphics :: 3D Rendering",
    "Topic :: Scientific/Engineering :: Visualization",
    "Programming Language :: Python :: 3 :: Only",
]

project_urls = {
#    "Documentation": "https://moderngl.readthedocs.io/",
#   "Source": "https://github.com/moderngl/moderngl/",
#    "Bug Tracker": "https://github.com/moderngl/moderngl/issues/",
}

setup(
    name="equity-correlate",
    version="1.0.0",
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/riz0id/equity-correlate",
    author="Jacob Leach",
    author_email="jacobleach@protonmail.com",
    license="MIT",
    project_urls=project_urls,
    classifiers=classifiers,
    keywords=keywords,
    include_package_data=True,
    package_data={},
    packages=["equity-correlate"],
    py_modules=[],
    ext_modules=[],
    platforms=[
      "any"
    ],
    extras_require={},
    install_requires=[
    ],
    python_requires=">=3.7",
)