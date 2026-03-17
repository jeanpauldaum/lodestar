"""
PDF report generator for Lodestar.

Converts Markdown briefs to polished PDF reports using WeasyPrint.
"""

import logging
import os

logger = logging.getLogger(__name__)

try:
    import weasyprint

    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("weasyprint not installed — PDF generation unavailable")


PDF_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a2e;
    margin: 0;
    padding: 0;
}

@page {
    margin: 2cm;
    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
    }
}

h1 {
    font-size: 22pt;
    color: #0f3460;
    border-bottom: 3px solid #0f3460;
    padding-bottom: 8px;
    margin-top: 0;
}

h2 {
    font-size: 15pt;
    color: #16213e;
    margin-top: 24px;
    border-left: 4px solid #0f3460;
    padding-left: 10px;
}

h3 { font-size: 12pt; color: #0f3460; margin-top: 16px; }

table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 10pt;
}

th {
    background-color: #0f3460;
    color: white;
    padding: 8px 10px;
    text-align: left;
}

td {
    padding: 7px 10px;
    border-bottom: 1px solid #e0e0e0;
}

tr:nth-child(even) td { background-color: #f8f9fa; }

blockquote {
    background: #fff8e1;
    border-left: 4px solid #ffa000;
    margin: 12px 0;
    padding: 10px 16px;
    font-style: italic;
}

code { font-family: 'Courier New', monospace; background: #f5f5f5; padding: 2px 4px; }

hr { border: none; border-top: 1px solid #e0e0e0; margin: 20px 0; }
"""


def markdown_to_pdf(
    markdown_content: str,
    output_path: str,
    title: str = "Lodestar Policy Analysis",
) -> str:
    """
    Convert a Markdown brief to a PDF report.

    Args:
        markdown_content: Markdown string (from generate_markdown_brief).
        output_path: File path for the output PDF.
        title: Document title for PDF metadata.

    Returns:
        Absolute path to the generated PDF file.

    Raises:
        ImportError: If WeasyPrint is not installed.
        OSError: If the output path is not writable.
    """
    if not WEASYPRINT_AVAILABLE:
        raise ImportError(
            "weasyprint is required for PDF generation: pip install weasyprint"
        )

    try:
        import markdown as md_lib

        html_body = md_lib.markdown(
            markdown_content, extensions=["tables", "fenced_code"]
        )
    except ImportError:
        # Fallback: basic HTML wrapping without markdown conversion
        logger.warning("markdown package not available, using plain text in PDF")
        html_body = f"<pre>{markdown_content}</pre>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>{PDF_CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    logger.info("Generating PDF: %s", output_path)
    doc = weasyprint.HTML(string=html_content)
    doc.write_pdf(output_path)
    size_kb = os.path.getsize(output_path) / 1024
    logger.info("PDF generated: %s (%.1f KB)", output_path, size_kb)
    return os.path.abspath(output_path)
