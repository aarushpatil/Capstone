import fitz  # PyMuPDF

def extract_chapters_by_page_numbers(pdf_path, page_numbers):
    """
    Extracts chapters from a PDF based on provided page numbers.

    Args:
        pdf_path (str): The path to the PDF file.
        page_numbers (list): A list of page numbers indicating chapter ends.

    Returns:
        list: A list of strings, where each string represents a chapter.
    """
    try:
        doc = fitz.open(pdf_path)
        chapters = []
        start_page = 0

        for end_page in page_numbers:
            chapter_text = ""
            for page_num in range(start_page, end_page):
                if 0 <= page_num < doc.page_count: #prevent out of bounds errors.
                    page = doc[page_num]
                    chapter_text += page.get_text()
                else:
                    print(f"Warning: Page {page_num} out of bounds.")
            chapters.append(chapter_text)
            start_page = end_page

        if start_page < doc.page_count: #add any remaining pages.
            chapter_text = ""
            for page_num in range(start_page, doc.page_count):
                page = doc[page_num]
                chapter_text += page.get_text()
            chapters.append(chapter_text)

        doc.close()
        return chapters

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def getFirstManual():
    # Example usage:
    pdf_file = "../INTEGRATION_Manual_1.pdf"
    page_numbers = [1, 2, 4, 5, 8, 12, 30, 51, 59, 61]  # Example page numbers (chapter ends)
    chapter_strings = extract_chapters_by_page_numbers(pdf_file, page_numbers)
    return chapter_strings

def getSecondManual():
    # Example usage:
    pdf_file = "../INTEGRATION_Manual_2.pdf"
    page_numbers = [1, 2, 4, 5, 8, 12, 30, 51, 59, 61]  # NEED TO ACTUALLY FIX THESE VALUES!!
    chapter_strings = extract_chapters_by_page_numbers(pdf_file, page_numbers)
    return chapter_strings

def getManualChunks():
    return getFirstManual() + getSecondManual()