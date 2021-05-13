import json
import logging
import pathlib
from typing import List

import jamspell
import stanza
import gdown
from helpers import Correction


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', )

DEFAULT_MAPPING_PATH = "texts/dependencies/word_mapping.csv"
DEFAULT_MODEL_DIRECTORY = "models/"
DEFAULT_STANZA_DIR_PATH = f"{DEFAULT_MODEL_DIRECTORY}/stanza"
DEFAULT_JAMSPELL_DIR_PATH = f"{DEFAULT_MODEL_DIRECTORY}/jamspell/"
DEFAULT_JAMSPELL_MODEL_PATH = "models/jamspell/jamspell_estonian_2021_05_13.bin"


class JamspellCorrector:


    def __init__(self, jamspell_model_path: str = DEFAULT_JAMSPELL_MODEL_PATH, correction_mapping_path: str = DEFAULT_MAPPING_PATH, stanza_model_dir_path=DEFAULT_STANZA_DIR_PATH, use_gpu=False):
        """
        :param jamspell_model_path: Relative or absolute path to the Jamspell binary model file.
        :param correction_mapping_path: Relative or absolute path to the CSV file which conducts word replacements.
        :param stanza_model_dir_path: Relative or absolute path to the directory IN WHICH the Estonian Stanza models reside in.
        :param use_gpu: Whether to use the GPU's CUDA support for Stanza operations.
        """
        self.nlp = None
        self.corrector = jamspell.TSpellCorrector()
        self.ensure_model_folders()
        self.word_mapping = self.load_mapper_resources(correction_mapping_path)
        self._load_corrector_resources(jamspell_model_path)
        self._load_lemmatizer_resources(stanza_model_dir_path, use_gpu)


    @staticmethod
    def ensure_model_folders(dirs: List[str] = (DEFAULT_JAMSPELL_DIR_PATH, DEFAULT_STANZA_DIR_PATH)):
        """
        Ensures the the directories in which the models are loaded from actually exist in case
        they should be deleted for whatever reason.
        :param dirs: Relative or absolute path of the folders whose existence you want to ensure.
        """
        for path in dirs:
            path = pathlib.Path(path)
            if path.exists() is False:
                path.mkdir(parents=True, exist_ok=True)


    @staticmethod
    def load_mapper_resources(file_path: str):
        path = pathlib.Path(file_path)
        if path.exists() and path.suffix == ".csv":
            logging.debug("Starting loading the word mapping for preprocessing!")
            mapping = []
            with open(file_path, "r", encoding="utf8") as fp:
                for line in fp:
                    mistake, correct = line.split(",")
                    mistake, correct = mistake.strip(), correct.strip()
                    mapping.append((mistake, correct))
            logging.debug("Finished loading the word mapping for preprocessing!")
            return mapping
        else:
            raise FileNotFoundError("Could not find the CSV file with the path: {}!".format(file_path))


    def __load_stanza_pipeline(self, model_folder: str, use_gpu: bool):
        logging.debug("Starting loading the the Stanza models into the Pipeline!")
        self.nlp = stanza.Pipeline(lang='et', processors='tokenize,pos,lemma', dir=model_folder, use_gpu=use_gpu)
        logging.debug("Finished loading the stanza models!")


    @staticmethod
    def download_stanza_model(model_dir, lang="et"):
        logging.debug("Downloading the missing Stanza models!")
        stanza.download(model_dir=model_dir, lang=lang)
        logging.debug("Finished downloading the missing Stanza models!")


    def _load_lemmatizer_resources(self, model_folder: str, use_gpu=False):
        does_exist = (pathlib.Path(model_folder) / "et").exists()
        if does_exist:
            self.__load_stanza_pipeline(model_folder, use_gpu)
        else:
            JamspellCorrector.download_stanza_model(model_folder, "et")
            self.__load_stanza_pipeline(model_folder, use_gpu)


    def __load_jampsell(self, file_path):
        logging.debug("Loading the Jamspell model into memory! During first loads, this might take a while (up to a few minutes)!")
        self.corrector.LoadLangModel(file_path)
        logging.debug("Finished the Jamspell model into memory!")


    def _load_corrector_resources(self, file_path: str):
        if pathlib.Path(file_path).exists():
            self.__load_jampsell(file_path)
        else:
            file_path = JamspellCorrector.download_missing_jamspell_model()
            self.__load_jampsell(file_path)


    @staticmethod
    def download_missing_jamspell_model():
        with open("conf.json", "r", encoding="utf8") as fp:
            config = json.load(fp)
            token = config.get("gdrive_file_id", None)
            model_name = config.get("model_name", None)
            if token and model_name:
                url = f"https://drive.google.com/uc?id={token}"
                path = f"{DEFAULT_JAMSPELL_DIR_PATH}{model_name}"
                gdown.download(url, output=path)
                return path
            else:
                raise ValueError("'model_name' and/or 'gdrive_file_id' are missing from the conf.json!")


    def _get_candidates_for_text(self, corrected_text: str):
        candidates = {}
        tokens = [token for token in corrected_text.split(" ")]
        for index, token in enumerate(tokens):
            if token not in candidates:
                candidates[token] = self.corrector.GetCandidates(tokens, index)
            else:
                candidates[token] += self.corrector.GetCandidates(tokens, index)
                candidates[token] = list(set(candidates[token]))
        return candidates


    def preprocess_text(self, original_text: str):
        logging.debug("Replacing the words in the text by the defined mappings from the file as a preprocessing step!")
        processed_text = original_text
        for mistake, correct in self.word_mapping:
            processed_text = processed_text.replace(mistake, correct)
        logging.debug("Finished replacing the words!")
        return processed_text


    def correct_text(self, original_text: str, use_preprocessing: bool = True):

        preprocessed_text = self.preprocess_text(original_text) if use_preprocessing else original_text

        logging.debug("Applying the Jamspell model on the preprocessed text!")
        corrected_text = self.corrector.FixFragment(preprocessed_text)
        logging.debug("Finished applying the Jamspell model, final result!")

        logging.debug("Getting the candidates.")
        candidates = self._get_candidates_for_text(corrected_text)
        logging.debug("Finished getting the candidates!")

        return Correction(original=original_text, correction=corrected_text, candidates=candidates)


    def lemmatize(self, text: str, use_preprocessing=True, correct_text=True):
        tokens = []
        if correct_text:
            text = self.correct_text(text, use_preprocessing).correction

        stanza_analysis = self.nlp(text)
        for sentence in stanza_analysis.sentences:
            for word in sentence.words:
                tokens.append(word.lemma)
        return " ".join(tokens)


if __name__ == '__main__':
    c = JamspellCorrector(correction_mapping_path="texts/dependencies/word_mapping.csv")
    correction = c.correct_text("Ma kaisin poes!")
    print(correction.correction)
    print(c.lemmatize(correction.correction, use_preprocessing=False))
    pass
