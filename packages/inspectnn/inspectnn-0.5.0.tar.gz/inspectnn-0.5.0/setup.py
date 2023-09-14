try:
    import setuptools
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from codecs import open
from os import path

setup(
    name="inspectnn",
    version="0.5.0",
    description="Inference eNgine uSing aPproximate arithmEtic ComponenTs for Neural Networks",
    long_description="Inference eNgine uSing aPproximate arithmEtic ComponenTs for Neural Networks",
    url="https://github.com/SalvatoreBarone/inspect-nn",
    author="Salvatore Barone, Filippo Ferrandino",
    author_email="salvatore.barone@unina.it, fi.ferrandino@studenti.unina.it",
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.11"
    ],
    keywords="Neural Networks Approximate-Computing",
    packages=setuptools.find_packages(),#["inspectnn"],
    include_package_data=True,
    python_requires='>=3.11',#3.11 o 3.12
    #numba 0.57.0rc1 va con python 3.11 e numpy 1.24
    install_requires=["tensorflow==2.12", "protobuf","numpy==1.23.5","numba==0.57.1","scipy==1.10.1","scikit-learn"],#fare -U pymoo
    project_urls={
        "Bug Reports": "https://github.com/SalvatoreBarone/inspect-nn/issues",
        "Source": "https://github.com/SalvatoreBarone/inspect-nn",
    },
)

