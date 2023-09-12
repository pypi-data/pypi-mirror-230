from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
    name="dvoryan",
    version="0.0.2",
    description="Reproducible and efficient diffusion kurtosis imaging in Python.",
    url="https://github.com/kerkelae/dkmri",
    author="Leevi Kerkelä",
    author_email="leevi.kerkela@protonmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "jax>=0.2.28",
        "jaxlib>=0.1.76",
        "matplotlib>=3.5.1",
        "nibabel>=3.2.1",
        "numba>=0.55.1",
        "numpy>=1.21.5",
        "scikit-learn>=1.0.2",
    ],
    scripts=["dvoryan/dvoryan.py"],
    long_description=readme(),
    long_description_content_type="text/markdown",
)
