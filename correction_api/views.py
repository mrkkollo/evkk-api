from django.shortcuts import render
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

# Create your views here.
from correction_api.serializer import TextCorrectionSerializer
from jamspell_corrector import JamspellCorrector


corrector = None


class TextCorrectionView(APIView):
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    serializer_class = TextCorrectionSerializer


    def _load_corrector(self):
        logging.debug("Loading the Jamspell Corrector!")
        global corrector
        if corrector is None:
            corrector = JamspellCorrector(
                model_path="models/estonski.bin",
                correction_mapping_path="texts/training_texts/word_mapping.csv",
                stanza_model_path="/home/mkollo/PycharmProjects/texta-rest/data/models/stanza"
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
