from setuptools import setup, find_packages
from os.path import join, dirname

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
    name="dkmri_WIN",
    version="0.1.3",
    description="Reproducible and efficient diffusion kurtosis imaging in Python.",
    url="https://github.com/kerkelae/dkmri",
    author="Leevi Kerkelä",
    author_email="leevi.kerkela@protonmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
	"jax",
        "jaxlib",
        "matplotlib",
        "nibabel",
        "numba",
        "numpy",
        "scikit-learn"
    ],
    long_description=readme(),
)
