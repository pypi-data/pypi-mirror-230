from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
    name="dvoryan",
    version="0.0.3",
    description="Reproducible and efficient diffusion kurtosis imaging in Python.",
    url="https://github.com/kerkelae/dkmri",
    author="Leevi Kerkelä",
    author_email="leevi.kerkela@protonmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "jax",
        "jaxlib",
        "nibabel",
        "numba",
        "numpy",
        "scikit-learn",
    ],
    scripts=["dvoryan/dvoryan.py"],
    long_description=readme(),
    long_description_content_type="text/markdown",
)
