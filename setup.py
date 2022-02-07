from pathlib import Path
from setuptools import find_packages, setup

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    fname="prose",
    version="0.9.61",
    author="Lionel J. Garcia",
    description="Reduction and analysis of FITS telescope observations",
    packages=find_packages("prose"),
    package_dir={"": "prose"},
    license="MIT",
    url="https://github.com/lgrcia/prose",
    # entry_points="""
    #     [console_scripts]
    #     prose=main:cli
    # """,
    long_description=README,
    long_description_content_type="text/markdown",
    install_requires=[
        "numpy",
        "scipy",
        "astropy",
        "matplotlib",
        "colorama",
        "scikit-image",
        "pandas>=1.1",
        "tqdm",
        "astroalign",
        "photutils",
        "astroquery",
        "pyyaml",
        "tabulate",
        "requests",
        "imageio",
        "sep",
        "xarray",
        "numba",
        "netcdf4",
        "celerite2",
        "jinja2",
        "tensorflow",
    ],
    extras_require={
        'dev': [
            "sphinx",
            "nbsphinx",
            "jupyter-sphinx",
            "sphinx_rtd_theme",
            "sphinx-copybutton",        
            "docutils",
            "jupyterlab",
            "twine",
        ]
    },
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
