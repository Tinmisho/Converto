"""
Format support matrix.
Each entry defines accepted input extensions and valid output targets.
"""

DOCUMENT_FORMATS = {
    "pdf":      {"label": "PDF",      "group": "document"},
    "docx":     {"label": "DOCX",     "group": "document"},
    "odt":      {"label": "ODT",      "group": "document"},
    "rtf":      {"label": "RTF",      "group": "document"},
    "epub":     {"label": "EPUB",     "group": "document"},
    "html":     {"label": "HTML",     "group": "document"},
    "md":       {"label": "Markdown", "group": "document"},
    "txt":      {"label": "TXT",      "group": "document"},
}

IMAGE_FORMATS = {
    "png":  {"label": "PNG",  "group": "image"},
    "jpg":  {"label": "JPG",  "group": "image"},
    "jpeg": {"label": "JPG",  "group": "image"},
    "webp": {"label": "WEBP", "group": "image"},
    "avif": {"label": "AVIF", "group": "image"},
    "heic": {"label": "HEIC", "group": "image"},
    "tiff": {"label": "TIFF", "group": "image"},
    "gif":  {"label": "GIF",  "group": "image"},
    "bmp":  {"label": "BMP",  "group": "image"},
}

ALL_FORMATS = {**DOCUMENT_FORMATS, **IMAGE_FORMATS}

# What each format can be converted TO
CONVERSION_TARGETS = {
    # Documents (via LibreOffice / Pandoc)
    "pdf":  ["docx", "odt", "html", "txt"],
    "docx": ["pdf", "odt", "html", "txt", "md", "rtf", "epub"],
    "odt":  ["pdf", "docx", "html", "txt"],
    "rtf":  ["pdf", "docx", "odt", "txt"],
    "epub": ["pdf", "docx", "html", "txt", "md"],
    "html": ["pdf", "docx", "md", "txt"],
    "md":   ["pdf", "docx", "html", "txt", "epub"],
    "txt":  ["pdf", "docx", "html", "md"],
    # Images (via libvips)
    "png":  ["jpg", "webp", "avif", "tiff", "bmp", "pdf"],
    "jpg":  ["png", "webp", "avif", "tiff", "bmp", "pdf"],
    "jpeg": ["png", "webp", "avif", "tiff", "bmp", "pdf"],
    "webp": ["png", "jpg", "avif", "tiff"],
    "avif": ["png", "jpg", "webp"],
    "heic": ["jpg", "png", "webp"],
    "tiff": ["png", "jpg", "webp", "pdf"],
    "gif":  ["png", "jpg", "webp"],
    "bmp":  ["png", "jpg", "webp", "tiff"],
}


def get_group(ext: str) -> str:
    ext = ext.lower().lstrip(".")
    if ext in DOCUMENT_FORMATS:
        return "document"
    if ext in IMAGE_FORMATS:
        return "image"
    return "unknown"


def is_supported(ext: str) -> bool:
    return ext.lower().lstrip(".") in ALL_FORMATS


def get_targets(ext: str) -> list[str]:
    return CONVERSION_TARGETS.get(ext.lower().lstrip("."), [])
