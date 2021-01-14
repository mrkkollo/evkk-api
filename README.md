# Installation

* Run ```conda env create -f environment.yaml``` to create the Python environment.
* In case of gcc errors when installing jamspell, make sure you have gcc and g++ installed on your system, for
  Debian ```sudo apt update && sudo apt install gcc g++``` is sufficient.
* From http://tlu.ee/~mkollo/models download "estonski.bin" and put it into the models directory.

# Docker

Since this package depends on external system dependencies to compile itself (installation is very platform dependent),
I've created a Dockerfile which users can use to guarantee a working environment.

1. Inside this repository run ```docker build -t jamspell-rest .``` to install the image.
1. To access the installed image, run ```docker run -p 8000:8000 jamspell-rest```, this will "put" you inside the isolated image.


# Usage

Access http://localhost:8000 to view the API, from there you can use the visual Browsable API to make request.