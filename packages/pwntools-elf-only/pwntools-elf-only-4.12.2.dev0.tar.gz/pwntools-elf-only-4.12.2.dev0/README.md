# pwntools - CTF toolkit

[![PyPI](https://img.shields.io/pypi/v/pwntools-elf-only?style=flat)](https://pypi.org/project/pwntools-elf-only/)

Fork of the Main-Project with:
 
- reduced dependencies for windows & 32-bit ARM Linux distros
- only focussed on ELF-features (other parts get removed or altered when causing trouble)

How to publish at pypi:

- increment .version and setup.py -> 4.12.#dev
- push to dev

Changes: 

- make compatible with newest pyelftools v0.30
- remove dependencies: mako, ropgadget, pyserial, pip, zstandard, pathlib2, paramiko, capstone, pysocks, unicorn
- clean readme.md, pyproject.toml and .github-directory
