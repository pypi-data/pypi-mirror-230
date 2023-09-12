from distutils.core import setup


VERSION = "0.1.0"
BASE_URL = "https://github.com/open-foil/xfoil-wrapper"

setup(
    name="xfoil_wrapper",  # How you named your package folder (MyLib)
    packages=["xfoil_wrapper"],  # Chose the same as "name"
    version=VERSION,  # Start with a small number and increase it with every change you make
    license="MIT",  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description="Wrapper for XFoil 6.99 by Marc Drela in Windows machine.",  # Give a short description about your library
    author="OpenFoil",  # Type in your name
    author_email="openfoil.project@gmail.com",  # Type in your E-Mail
    url="https://github.com/open-foil",  # Provide either the link to your github or to your website
    download_url=f"{BASE_URL}/archive/refs/tags/v{VERSION}.tar.gz",  # get link from Github Release
    keywords=[
        "xfoil",
        "wrapper",
        "aerodynamics",
        "airfoil",
    ],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        "numpy>=1.22.0",
        "matplotlib>=3.6.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",  # Define that your audience are developers
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",  # Again, pick a license
        "Programming Language :: Python :: 3",  # Specify which python versions that you want to support
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    include_package_data=True,
    package_data={"xfoil_wrapper": ["__exe__/*.exe", "__exe__/*.py"]},
)
