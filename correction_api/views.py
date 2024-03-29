import logging
from typing import Optional

from rest_framework.generics import GenericAPIView
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response

# Create your views here.
from correction_api.serializer import TextCorrectionSerializer
from jamspell_corrector import JamspellCorrector


corrector: Optional[JamspellCorrector] = None


class TextCorrectionView(GenericAPIView):
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    serializer_class = TextCorrectionSerializer


    def _load_corrector(self):
        logging.debug("Loading the Jamspell Corrector!")
        global corrector
        if corrector is None:
            corrector = JamspellCorrector(
                correction_mapping_path="texts/dependencies/word_mapping.csv",
            )
        logging.debug("Finished loading the Jamspell Corrector!")


    def post(self, request):
        self._load_corrector()
        serializer = TextCorrectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        text = serializer.validated_data["text"]
        use_preprocessing = serializer.validated_data["use_preprocessing"]
        show_candidates = serializer.validated_data["show_candidates"]

        correction = corrector.correct_text(text, use_preprocessing)
        response = {
            "original": correction.original,
            "corrected": correction.correction,
            "mistake_tokens": [token.to_json() for token in correction.corrected_tokens],
        }
        if show_candidates:
            response["candidates"] = correction.candidates

        return Response(response)
