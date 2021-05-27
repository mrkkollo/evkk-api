# Installation

1. Clone this repository and move inside it with a terminal.
1. Install g++ and gcc on a system level, on Debian based systems  ```sudo apt update && sudo apt install gcc g++``` should be sufficient.
1. Run ```conda env create -f environment.yaml``` to create the Python environment.
1. Create a directory called "models" inside the root of this repository.
1. If you posess a different model you wish to use, add the model inside the models/ directory and change the value "model_name" inside conf.json. Otherwise, without the existence of a preset model, one is downloaded for the user.

# Usage

1. Access the environment with ```conda activate evkk```
1. Run the application with ```python manage.py runserver```. Please note that this is just a plain development server and is not appropriate for a full production setting.
1. Access http://localhost:8000 to view the API, from there you can use the visual Browsable API to make request.

NB! Please not that on first requests, it might take a while for the models to be loaded into memory in the global namespace. This might take up to a few minutes, additional requests will be processed much faster. 

NB! Since the model is loaded into memory inside the global namespace, any web server configurations that create multiple workers should take into account increased memory usage.


# Jamspell
Source: https://habr.com/en/post/346618/ (In Russian)

Jamspell is a heavily modified version of the Symspell algorithm, implemented by the use of 3-grams for language modeling, [Kneser–Ney smoothing](https://u.cs.biu.ac.il/~yogo/courses/mt2013/papers/chen-goodman-99.pdf) to fix the issue of a never-before met 3-gram creating 0 candidates and 0 probability, [Perfect Hashing](https://en.wikipedia.org/wiki/Perfect_hash_function) to keep the impact on RAM into useable levels and a [Bloom Filter](https://habr.com/en/post/112069/) to further reduce the memory inprint the model has.

# Estonian Jamspell
This application downloads a Jamspell model trained using a subset of the [Estonian National Corpus 2019](https://metashare.ut.ee/repository/browse/estonian-national-corpus-2019/cd9633fab22e11eaa6e4fa163e9d4547b71a2df64d1f43f1ac26dbd8508ea951/) (etnc19_balanced_corpus.prevert). Sadly, the entirety of the national corpus ended up being too memory heavy for my machine so I was forced to limit it only to a subset of 126109243 words (calculated using a Linux ```wc -w``` command) which is only 8% of the corpus' word size. 

# Docker

Since this package depends on external system dependencies to compile itself (installation is very platform dependent),
I've created a Dockerfile which users can use to guarantee a working environment.

1. Inside this repository run ```docker build -t jamspell-rest .``` to install the image.
1. To access the installed image, run ```docker run -p 8000:8000 jamspell-rest```, this will "put" you inside the isolated image.

