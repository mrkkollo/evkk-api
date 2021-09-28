import string
from typing import List


class Token:

    def __init__(self, original: str, corrected: str):
        """
        Helper class for everything related to tokens.
        :param original: String value of the original token.
        :param corrected: String value of the original tokens correction.
        """
        self.original = original
        self.corrected = corrected


    def to_json(self):
        return {
            "original": self.original,
            "corrected": self.corrected
        }


    def __str__(self):
        return "Original: {} - Corrected: {}".format(self.original, self.corrected)


class Correction:

    def __init__(self, original: str, correction: str, candidates: dict):
        """
        Helper class for containing functions related to corrections.
        :param original: Original text in its unprocessed form.
        :param correction: Correction of the original text.
        :param candidates: Dictionary which contains the possible candidates of tokens offered by the corrector.
        """
        self.original = original
        self.correction = correction
        self.candidates = candidates

        self.original_tokens = [token for token in self.original.split(" ")]
        self.correction_tokens = [token for token in self.correction.split(" ")]


    def _clean_token(self, token: str) -> str:
        """
        Remove symbol characters from the token like '!' or ','.
        """
        for char in string.punctuation:
            token = token.replace(char, '')
        return token.strip()


    @property
    def corrected_tokens(self) -> List[Token]:
        container = []
        for index, original_token in enumerate(self.original_tokens):
            correction_token = self._clean_token(self.correction_tokens[index])
            original_token = self._clean_token(original_token)
            if correction_token.lower() != original_token.lower():
                token = Token(original_token, correction_token)
                container.append(token)
        return container


    def __str__(self):
        return self.correction
