import logging
import pathlib

import jamspell
import stanza

from helpers import Correction


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', )


class JamspellCorrector:
    DEFAULT_MAPPING_PATH = "texts/training_texts/word_mapping.csv"
    DEFAULT_MODEL_PATH = "models/estonski.bin"
    DEFAULT_MODEL_DIRECTORY = "models/"


    def __init__(self, model_path: str = DEFAULT_MODEL_PATH, correction_mapping_path: str = DEFAULT_MAPPING_PATH, stanza_model_path=DEFAULT_MODEL_DIRECTORY, use_gpu=False):
        self.nlp = None
        self.corrector = jamspell.TSpellCorrector()
        self.word_mapping = JamspellCorrector.load_mapper_resources(correction_mapping_path)
        self.__load_corrector_resources(model_path)
        self.__load_lemmatizer_resources(stanza_model_path, use_gpu)


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


    def __load_lemmatizer_resources(self, model_folder: str, use_gpu=False):
        logging.debug("Starting loading the the Stanza models into the Pipeline!")
        self.nlp = stanza.Pipeline(lang='et', processors='tokenize,pos,lemma', dir=model_folder, use_gpu=use_gpu)
        logging.debug("Finished loading the stanza models!")


    def __load_corrector_resources(self, file_path: str):
        if pathlib.Path(file_path).exists():
            logging.debug("Loading the Jamspell model into memory! During first loads, this might take a while!")
            self.corrector.LoadLangModel(file_path)
            logging.debug("Finished the Jamspell model into memory!")
        else:
            raise FileNotFoundError("Could not find model with the path: {}!".format(file_path))


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

        preocessed_text = self.preprocess_text(original_text) if use_preprocessing else original_text

        logging.debug("Applying the Jamspell model on the preprocessed text!")
        corrected_text = self.corrector.FixFragment(preocessed_text)
        logging.debug("Finished applying the Jamspell model, final result!")

        logging.debug("Getting the candidates.")
        candidates = self._get_candidates_for_text(corrected_text)
        logging.debug("Finished getting the candidates!")

        return Correction(original=original_text, correction=corrected_text, candidates=candidates)


    def lemmatize(self, text: str, use_preprocessing=True):
        tokens = []
        corrected_text = self.correct_text(text, use_preprocessing)
        stanza_analysis = self.nlp(corrected_text.correction)
        for sentence in stanza_analysis.sentences:
            for word in sentence.words:
                tokens.append(word.lemma)
        return " ".join(tokens)


if __name__ == '__main__':
    c = JamspellCorrector(correction_mapping_path="texts/training_texts/word_mapping.csv")
    correction = c.correct_text("Ma kaisin poes!")
    pass
