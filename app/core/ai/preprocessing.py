import re
from typing import List, Dict, Any

class ContentPreprocessor:
    """
    Performs basic content preprocessing for AI analysis.
    Includes whitespace cleanup, case normalization, special char removal, etc.
    Extend as needed for more advanced NLP tasks.
    """
    def clean_text(self, text: str, to_lower: bool = True, remove_punct: bool = True) -> str:
        if to_lower:
            text = text.lower()
        text = re.sub(r"\s+", " ", text)
        if remove_punct:
            text = re.sub(r"[^\w\s]", "", text)
        return text.strip()

    def preprocess_batch(self, texts: List[str], **kwargs) -> List[str]:
        return [self.clean_text(t, **kwargs) for t in texts]