import pymupdf
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from all pages of a PDF resume.
    """

    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"Resume not found: {pdf_file}")

    if pdf_file.suffix.lower() != ".pdf":
        raise ValueError("The provided file must be a PDF.")

    document = pymupdf.open(pdf_file)

    extracted_text = []

    for page in document:
        text = page.get_text("text")

        if text.strip():
            extracted_text.append(text.strip())

    document.close()

    final_text = "\n\n".join(extracted_text)

    if not final_text:
        print("Warning: No selectable text was found in this PDF.")

    return final_text


if __name__ == "__main__":
    print("Resume text extraction module is ready.")