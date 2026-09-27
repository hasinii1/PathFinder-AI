import re


def clean_resume_text(text: str) -> str:
    """
    Clean extracted resume text before further processing.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove bullet characters
    text = re.sub(r"[•▪●○■□]", " ", text)

    # Remove unwanted special characters but keep useful symbols
    text = re.sub(r"[^\w\s@.+/#&'-]", " ", text)

    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n", text)

    # Remove spaces at the beginning/end of each line
    lines = [line.strip() for line in text.split("\n")]

    # Remove empty lines
    lines = [line for line in lines if line]

    # Join cleaned lines
    cleaned_text = "\n".join(lines)

    return cleaned_text.strip()


if __name__ == "__main__":
    print("Resume preprocessing module is ready.")