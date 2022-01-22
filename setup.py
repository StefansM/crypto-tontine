from setuptools import setup, find_packages

setup(
    name='tontine',
    version="0.0.1",
    description="",
    author="Stefans Mezulis",
    author_email="stefans.mezulis@gmail.com",
    url="https://github.com/stefansm/crypto-tontine",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "click",
        "python-gnupg",
        "electrum @ git+https://github.com/spesmilo/electrum.git@4.1.5",
        "cryptography"
    ],
)
