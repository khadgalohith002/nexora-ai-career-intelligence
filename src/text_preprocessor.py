import re


def clean_text(text):
    """
    Clean extracted resume text while preserving useful information.
    """

    if not text:
        return ""

    # Remove null characters
    text = text.replace("\x00", " ")

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove unnecessary spaces
    text = re.sub(r"[ ]+", " ", text)

    # Remove spaces before new lines
    text = re.sub(r" +\n", "\n", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_text(text):
    """
    Create normalized text for NLP/ML comparison.
    """

    if not text:
        return ""

    text = text.lower()

    # Replace URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Replace email addresses
    text = re.sub(r"\S+@\S+", " ", text)

    # Keep useful characters such as +, #, . and -
    # because skills can contain C++, C#, Node.js, etc.
    text = re.sub(r"[^a-z0-9+#.\-\s]", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def preprocess_resume(text):
    """
    Return both readable and ML-ready versions of resume text.
    """

    cleaned_text = clean_text(text)

    normalized_text = normalize_text(cleaned_text)

    return {"cleaned_text": cleaned_text, "normalized_text": normalized_text}
