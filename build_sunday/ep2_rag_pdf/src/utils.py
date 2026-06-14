import time
import re
from functools import wraps

def time_it(func):
    """
    Decorator to measure and display the execution time of functions.
    Crucial for analyzing bottlenecks (e.g. PDF parsing vs. Embedding Generation).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        print(f"⏱️ [{func.__name__}] took {elapsed:.4f} seconds to execute.")
        return result
    return wrapper

def clean_text(text: str) -> str:
    """
    Cleans raw extracted PDF text to improve indexing and retrieval quality.
    Removes excessive spaces, duplicate newlines, and normalized whitespace.
    """
    if not text:
        return ""
    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Replace three or more newlines with two newlines (keeps paragraph separation)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespaces
    return text.strip()

def count_words(text: str) -> int:
    """
    Quickly counts words in a text block as a proxy for token count.
    On average, 1 token ≈ 0.75 words, so: Tokens ≈ Words / 0.75
    """
    return len(text.split())

def format_citation(metadata: dict) -> str:
    """
    Formats metadata dict into a standardized user-friendly source citation.
    """
    doc_name = metadata.get("document_name", "Unknown Document")
    page_num = metadata.get("page_number", "N/A")
    # If page number is 0-indexed, display it as 1-indexed for humans
    if isinstance(page_num, int):
        page_num = page_num + 1
    return f"[{doc_name}, Page {page_num}]"

def print_section_header(title: str):
    """Prints a styled separator header for readability in command line outputs."""
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)
