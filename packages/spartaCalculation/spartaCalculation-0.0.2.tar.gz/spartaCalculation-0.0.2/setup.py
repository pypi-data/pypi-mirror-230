from setuptools import setup, find_packages

setup(
    name="spartaCalculation",
    py_modules=["spartaCalculation"],
    version="0.0.2",
    license="MIT",
    description="Calculation for Sparta",
    author="Arun Kumar",
    author_email="arun.kumar@swimming.org.au",
    packages=find_packages(),
    install_requires=["glom"],
    classifiers=["Topic :: Software Development :: Build Tools",],
)
