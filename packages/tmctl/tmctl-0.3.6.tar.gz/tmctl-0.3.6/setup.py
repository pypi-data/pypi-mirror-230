from setuptools import setup, find_packages


setup(
    name="tmctl",
    version="0.3.6",
    packages=find_packages(),
    long_description="TMCtl",
    install_requires=["requests", "pyyaml", "fire"],
    description="TMCTL - Admin CLI for Trino Cluster Manager",
    entry_points={"console_scripts": "tmctl = tmctl:main"},
)
