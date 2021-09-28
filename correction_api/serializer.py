from rest_framework import serializers


class TextCorrectionSerializer(serializers.Serializer):
    text = serializers.CharField(help_text="Text you want to insert for correction.")
    use_preprocessing = serializers.BooleanField(default=True, help_text="Whether to run preprocessing - word replacement etc.")
    show_candidates = serializers.BooleanField(default=False, help_text="Whether to include the candidates of each word in the output, increases the output size significantly.")
