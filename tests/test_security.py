"""Basic security tests."""
from app.utils.security import sanitize_filename


def test_sanitize_path_traversal():
    assert "../" not in sanitize_filename("../../../etc/passwd")
    assert sanitize_filename("../../../etc/passwd") == "passwd.pdf" or "passwd" in sanitize_filename("../../../etc/passwd")


def test_sanitize_normal():
    assert sanitize_filename("kwitansi-001.pdf") == "kwitansi-001.pdf"


def test_sanitize_empty():
    assert sanitize_filename("") == "unnamed.pdf"
