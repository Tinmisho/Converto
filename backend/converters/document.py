"""
Document conversion strategy:
- LibreOffice (soffice) handles: docx, odt, rtf → pdf, docx, odt, html, txt
- Pandoc handles: md, html, epub ↔ md, html, epub, docx, txt, pdf(via html)
- For PDF input: LibreOffice export to target
"""
import subprocess
import shutil
import os
import tempfile


# Formats LibreOffice handles well as input
LIBREOFFICE_INPUT = {"doc", "docx", "odt", "rtf", "txt", "pdf"}

# Formats Pandoc handles well as input
PANDOC_INPUT = {"md", "html", "epub", "rst", "docx", "txt"}

# LibreOffice export filter names
LO_FILTERS = {
    "pdf":  "writer_pdf_Export",
    "docx": "MS Word 2007 XML",
    "odt":  "writer8",
    "html": "HTML (StarWriter)",
    "txt":  "Text",
    "rtf":  "Rich Text Format",
}

# Pandoc format names
PANDOC_FORMATS = {
    "md":   "markdown",
    "html": "html",
    "epub": "epub",
    "docx": "docx",
    "txt":  "plain",
    "pdf":  "pdf",
    "odt":  "odt",
    "rtf":  "rtf",
}


def convert_document(
    input_path: str,
    output_path: str,
    source_ext: str,
    target_ext: str,
):
    src = source_ext.lower()
    tgt = target_ext.lower()

    # Route to the best converter
    if _use_pandoc(src, tgt):
        _pandoc_convert(input_path, output_path, src, tgt)
    else:
        _libreoffice_convert(input_path, output_path, tgt)


def _use_pandoc(src: str, tgt: str) -> bool:
    """Prefer Pandoc for markup-to-markup and epub paths."""
    pandoc_preferred = {"md", "html", "epub", "rst"}
    return src in pandoc_preferred or tgt in pandoc_preferred


def _pandoc_convert(input_path: str, output_path: str, src: str, tgt: str):
    from_fmt = PANDOC_FORMATS.get(src, src)
    to_fmt = PANDOC_FORMATS.get(tgt, tgt)

    cmd = [
        "pandoc",
        input_path,
        "--from", from_fmt,
        "--to", to_fmt,
        "--output", output_path,
        "--standalone",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc error: {result.stderr}")


def _libreoffice_convert(input_path: str, output_path: str, target_ext: str):
    """
    LibreOffice CLI converts to a directory; we then move the result.
    It names the output file based on input filename, so we work in a temp dir.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        filter_name = LO_FILTERS.get(target_ext)
        if not filter_name:
            raise ValueError(f"No LibreOffice filter for .{target_ext}")

        cmd = [
            "soffice",
            "--headless",
            "--convert-to", target_ext,
            "--infilter", filter_name,
            "--outdir", tmpdir,
            input_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"LibreOffice error: {result.stderr}")

        # Find the output file LibreOffice created
        base = os.path.splitext(os.path.basename(input_path))[0]
        lo_output = os.path.join(tmpdir, f"{base}.{target_ext}")

        if not os.path.exists(lo_output):
            # LibreOffice sometimes uses different casing
            files = os.listdir(tmpdir)
            if not files:
                raise RuntimeError("LibreOffice produced no output file.")
            lo_output = os.path.join(tmpdir, files[0])

        shutil.move(lo_output, output_path)
