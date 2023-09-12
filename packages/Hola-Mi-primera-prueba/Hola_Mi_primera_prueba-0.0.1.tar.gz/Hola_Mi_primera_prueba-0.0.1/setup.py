import setuptools
from pathlib import Path

long_desc =  Path('README.md').read_text()
setuptools.setup(

    name="Hola_Mi_primera_prueba",
    version="0.0.1",

    long_description=long_desc,

    packages=setuptools.find_packages(
        exclude=[
            "webium"
        ]
    )
)