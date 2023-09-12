import os

from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

with open('requirements.txt') as f:
    install_reqs = f.readlines()
    reqs = [str(ir) for ir in install_reqs]

setup(
    name="blockcerts-merkletools",
    install_requires=reqs,
    version="1.0.3",
    description="Merkle Tools",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="https://github.com/blockchain-certificates/blockcerts-pymerkletools",
    author='Blockcerts',
    author_email='info@blockcerts.org',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords="merkle tree, blockchain",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
)
