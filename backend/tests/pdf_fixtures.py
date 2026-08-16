import fitz


def make_pdf_bytes(pages: list[str]) -> bytes:
    document = fitz.open()
    try:
        for text in pages:
            page = document.new_page()
            page.insert_text((72, 72), text)
        return document.tobytes()
    finally:
        document.close()
