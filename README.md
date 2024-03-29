# Installation

1. Clone this repository and move inside it with a terminal.
1. Install g++ and gcc on a system level, on Debian based systems  ```sudo apt update && sudo apt install gcc g++```
   should be sufficient.
1. Run ```conda env create -f environment.yaml``` to create the Python environment.
1. Create a directory called "models" inside the root of this repository.
1. If you posess a different model you wish to use, add the model inside the models/ directory and change the value "
   model_name" inside conf.json. Otherwise, without the existence of a preset model, one is downloaded for the user.
1. Users can also directly edit the file with the pre-made token replacements under texts/dependencies/word_mapping.




# Usage

1. If using a custom JamSpell model, create a "models directory", send the model binary into that folder and change the "model_name" value inside conf.json. If this is not done, it will download the model from the web in case it is not already inside the folder. Said model is put into an automatically created "models" folder.
1. Access the environment with ```conda activate evkk```
1. Inside the environment, run ```python manage.py migrate```, this will populate a simple sqlite database
   with the DB schema.
1. Run the application with ```python manage.py runserver```. Please note that this is just a plain development server
   and is not appropriate for a full production setting.
1. Access http://localhost:8000 to view the API, from there you can use the visual Browsable API to make request.

NB! Please note that on first requests, it might take a while for the models to be loaded into memory in the global
namespace. This might take up to a few minutes, additional requests will be processed much faster.

NB! Since the model is  loaded into memory inside the global namespace, any web server configurations that create
multiple workers should take into account increased memory usage.


# Jamspell


Source: https://habr.com/en/post/346618/ (In Russian)

This application uses Jamspell as a method of text correction. Jamspell is a heavily modified version of the Symspell algorithm, implemented by the use of 3-grams for language
modeling, [Kneser–Ney smoothing](https://u.cs.biu.ac.il/~yogo/courses/mt2013/papers/chen-goodman-99.pdf) to fix the
issue of a never-before met 3-gram creating 0 candidates and 0
probability, [Perfect Hashing](https://en.wikipedia.org/wiki/Perfect_hash_function) to keep the impact on RAM into
useable levels and a [Bloom Filter](https://habr.com/en/post/112069/) to further reduce the memory inprint the model
has.

This application downloads a Jamspell model trained using a subset of
the [Estonian National Corpus 2019](https://metashare.ut.ee/repository/browse/estonian-national-corpus-2019/cd9633fab22e11eaa6e4fa163e9d4547b71a2df64d1f43f1ac26dbd8508ea951/) (
etnc19_balanced_corpus.prevert). Sadly, the entirety of the national corpus ended up being too memory heavy for my
machine so I was forced to limit it only to a subset of 126109243 words (calculated using a Linux ```wc -w``` command)
which is only 8% of the corpus' word size.

# Training Jamspell model

1. Place the new line delimited full-text training material inside model_training/training_texts.txt.
1. Inside this repository run ```docker build -f docker/jamspell_dockerfile -t jamspell .``` to build the Jamspell
   image.
1. Run the command ```docker run -it jamspell bash``` to start the docker image and log into it.
1. Run the
   command ```./main/jamspell train alphabet_et.txt training_texts.txt {{model name of your choosing, nice to have a timestamp here for bookkeeping}}.bin```
1. Wait until the model is done training.
1. Outside the jamspell image, run ```docker ps``` In a terminal to find the Docker container name that was randomly
   generated for the JamSpell image that you created.
1. In an outside terminal,
   execute ```docker cp {{container name}}:/JamSpell/build/{{name you set for the model}} ./{{name you set for the model}}```
   , this will copy the model from the Docker image to the same path where you launched the command.

### If creating the model for this API:
1. Create a models dir inside this repository.
1. Move the model into said directory.
1. Change the "model_name" inside conf.json to match the file name of the model.

# API Docker

Since this package depends on external system dependencies to compile itself (installation is very platform dependent),
I've created a Dockerfile which users can use to guarantee a working environment.

1. Inside this repository run ```docker build -f docker/api_dockerfile -t jamspell-rest .``` to install the image.
1. To access the installed image, run ```docker run -p 8000:8000 jamspell-rest```, this will "put" you inside the
   isolated image.
1. You can then access the page through ```http://localhost:8000```


# Links:
* JamSpell Model - https://drive.google.com/file/d/1AVO7H1v6SaQ9Eom50ZmFZoW6Q17SUzm2/view?usp=sharing
* Original Training Text Subset - https://drive.google.com/file/d/1uAGbD6mLjy1U46ZrMzXTUbQdZ8kjslCG/view?usp=sharing
