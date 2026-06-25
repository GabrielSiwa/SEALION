"""PDF/URL -> markdown via microsoft/markitdown.

This de-risks the data-normalization trap: we never hand-parse PDFs.
"""

import io

from markitdown import MarkItDown

_md = MarkItDown()


def convert_url(url: str) -> str:
    """Fetch a paper at `url` and convert it to markdown."""
    result = _md.convert(url)
    return result.text_content


def convert_bytes(data: bytes, filename: str = "upload.pdf") -> str:
    """Convert uploaded file bytes to markdown."""
    result = _md.convert_stream(io.BytesIO(data), file_extension=".pdf")
    return result.text_content
