import setuptools
import os
import re

lib_path = os.path.abspath(os.path.dirname(__file__))
with open(f"{lib_path}/uun_iot/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setuptools.setup(
    name="uun-iot",
    version=version,
    author="(UUN) Tomáš Faikl",
    author_email="tomas.faikl@unicornuniversity.net",
    description="Modular framework for communication with UuApp and utility functionality",
    url="https://uuapp.plus4u.net/uu-bookkit-maing01/38c7532545984b3797c5719390b523a8/book/page?code=71150832",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        "requests>=2.24.0",
        "requests_toolbelt>=0.9.1",
        "psutil>=5.7.0"
    ],
    python_requires='>=3.6'
)
