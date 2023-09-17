"""Azure Cognitive Services Tools."""

from langchaincoexpert.tools.azure_cognitive_services.form_recognizer import (
    AzureCogsFormRecognizerTool,
)
from langchaincoexpert.tools.azure_cognitive_services.image_analysis import (
    AzureCogsImageAnalysisTool,
)
from langchaincoexpert.tools.azure_cognitive_services.speech2text import (
    AzureCogsSpeech2TextTool,
)
from langchaincoexpert.tools.azure_cognitive_services.text2speech import (
    AzureCogsText2SpeechTool,
)

__all__ = [
    "AzureCogsImageAnalysisTool",
    "AzureCogsFormRecognizerTool",
    "AzureCogsSpeech2TextTool",
    "AzureCogsText2SpeechTool",
]
