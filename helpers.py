import string
from typing import List


class Token:


    def __init__(self, original, corrected):
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
        self.original = original
        self.correction = correction
        self.candidates = candidates

        self.original_tokens = [token for token in self.original.split(" ")]
        self.mistake_tokens = [token for token in self.correction.split(" ")]


    def _clean_token(self, token: str) -> str:
        # Remove symbol characters from the token like '!' or ','.
        for char in string.punctuation:
            token = token.replace(char, '')
        return token.strip()


    @property
    def corrected_tokens(self) -> List[Token]:
        container = []
        for index, original_token in enumerate(self.original_tokens):
            mistake_token = self._clean_token(self.mistake_tokens[index])
            original_token = self._clean_token(original_token)
            if mistake_token.lower() != original_token.lower():
                token = Token(original_token, mistake_token)
                container.append(token)
        return container


    def __str__(self):
        return self.correction
