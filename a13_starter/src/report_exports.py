from __future__ import annotations

import html
import io
import re
import zipfile
from typing import Any
from xml.sax.saxutils import escape


def markdown_to_html(markdown_text: str, title: str = "职业规划报告") -> str:
    body_parts: list[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            body_parts.append("</ul>")
            in_list = False

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            close_list()
            continue

        if line.startswith("# "):
            close_list()
            body_parts.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
            continue
        if line.startswith("## "):
            close_list()
            body_parts.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
            continue
        if line.startswith("### "):
            close_list()
            body_parts.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
            continue
        if line.startswith("- "):
            if not in_list:
                body_parts.append("<ul>")
                in_list = True
            body_parts.append(f"<li>{html.escape(line[2:].strip())}</li>")
            continue

        close_list()
        body_parts.append(f"<p>{html.escape(line.strip())}</p>")

    close_list()
    body_html = "\n".join(body_parts)
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{html.escape(title)}</title>
    <style>
      :root {{
        --bg: #f7f1e8;
        --text: #2d241d;
        --muted: #6e6256;
        --line: rgba(90, 70, 50, 0.14);
        --accent: #8d3716;
      }}
      body {{
        margin: 0;
        font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
        color: var(--text);
        background: linear-gradient(180deg, #fcfaf6 0%, var(--bg) 100%);
      }}
      .sheet {{
        max-width: 900px;
        margin: 32px auto;
        padding: 40px 44px;
        background: white;
        border: 1px solid var(--line);
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(60, 40, 20, 0.08);
      }}
      h1, h2, h3 {{
        color: var(--accent);
        margin-top: 1.4em;
      }}
      h1 {{
        margin-top: 0;
        font-size: 32px;
      }}
      h2 {{ font-size: 24px; }}
      h3 {{ font-size: 18px; }}
      p, li {{
        line-height: 1.8;
        color: var(--text);
      }}
      ul {{
        padding-left: 22px;
      }}
      .print-tip {{
        margin-bottom: 20px;
        padding: 14px 16px;
        border-radius: 14px;
        background: #f7efe7;
        color: var(--muted);
      }}
      @media print {{
        body {{
          background: white;
        }}
        .sheet {{
          margin: 0;
          box-shadow: none;
          border: 0;
          border-radius: 0;
          max-width: none;
          padding: 0;
        }}
        .print-tip {{
          display: none;
        }}
      }}
    </style>
  </head>
  <body>
    <main class="sheet">
      <div class="print-tip">如果需要 PDF，请使用浏览器“打印”并选择“另存为 PDF”。</div>
      {body_html}
    </main>
  </body>
</html>
"""


def markdown_to_docx_bytes(markdown_text: str, title: str = "职业规划报告") -> bytes:
    paragraphs = _markdown_to_docx_paragraphs(markdown_text)
    document_xml = _build_docx_document_xml(title, paragraphs)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", _content_types_xml())
        docx.writestr("_rels/.rels", _rels_xml())
        docx.writestr("docProps/core.xml", _core_xml(title))
        docx.writestr("docProps/app.xml", _app_xml())
        docx.writestr("word/document.xml", document_xml)
        docx.writestr("word/styles.xml", _styles_xml())
        docx.writestr("word/_rels/document.xml.rels", _document_rels_xml())
    return buffer.getvalue()


def markdown_to_simple_pdf_bytes(markdown_text: str, title: str = "career_plan_report") -> bytes:
    lines = [title]
    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^#+\s*", "", line)
        lines.extend(_wrap_text_for_pdf(line, 48))

    content_lines = ["BT", "/F1 11 Tf", "40 800 Td", "14 TL"]
    first = True
    for line in lines:
        safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        if first:
            content_lines.append(f"({safe_line}) Tj")
            first = False
        else:
            content_lines.append(f"T* ({safe_line}) Tj")
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n",
        f"4 0 obj<< /Length {len(stream)} >>stream\n".encode("latin-1") + stream + b"\nendstream\nendobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]

    pdf = io.BytesIO()
    pdf.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(pdf.tell())
        pdf.write(obj)
    xref_position = pdf.tell()
    pdf.write(f"xref\n0 {len(offsets)}\n".encode("latin-1"))
    pdf.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.write(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.write(
        (
            f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_position}\n%%EOF"
        ).encode("latin-1")
    )
    return pdf.getvalue()


def build_export_bundle(analysis: dict[str, Any]) -> dict[str, bytes | str]:
    title = f"{analysis['student_profile'].get('name', '学生')}_职业规划报告"
    markdown_text = str(analysis["report_markdown"])
    return {
        "markdown": markdown_text,
        "html": markdown_to_html(markdown_text, title=title),
        "docx": markdown_to_docx_bytes(markdown_text, title=title),
        "pdf": markdown_to_simple_pdf_bytes(markdown_text, title=title),
    }


def _markdown_to_docx_paragraphs(markdown_text: str) -> list[tuple[str, str]]:
    paragraphs: list[tuple[str, str]] = []
    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            paragraphs.append(("Normal", ""))
            continue
        if line.startswith("# "):
            paragraphs.append(("Heading1", line[2:].strip()))
        elif line.startswith("## "):
            paragraphs.append(("Heading2", line[3:].strip()))
        elif line.startswith("### "):
            paragraphs.append(("Heading3", line[4:].strip()))
        elif line.startswith("- "):
            paragraphs.append(("ListParagraph", line.strip()))
        else:
            paragraphs.append(("Normal", line.strip()))
    return paragraphs


def _build_docx_document_xml(title: str, paragraphs: list[tuple[str, str]]) -> str:
    body = []
    for style, text in paragraphs:
        escaped = escape(text)
        if not text:
            body.append("<w:p/>")
            continue
        body.append(
            f"""
            <w:p>
              <w:pPr><w:pStyle w:val="{style}"/></w:pPr>
              <w:r><w:t xml:space="preserve">{escaped}</w:t></w:r>
            </w:p>
            """
        )
    body_xml = "\n".join(body)
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
 xmlns:o="urn:schemas-microsoft-com:office:office"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
 xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
 xmlns:v="urn:schemas-microsoft-com:vml"
 xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:w10="urn:schemas-microsoft-com:office:word"
 xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
 xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
 xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
 xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
 xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
 mc:Ignorable="w14 wp14">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Title"/></w:pPr>
      <w:r><w:t>{escape(title)}</w:t></w:r>
    </w:p>
    {body_xml}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>
    </w:sectPr>
  </w:body>
</w:document>
"""


def _content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


def _rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def _document_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>
"""


def _core_xml(title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{escape(title)}</dc:title>
  <dc:creator>A13 Career Planner</dc:creator>
  <cp:lastModifiedBy>A13 Career Planner</cp:lastModifiedBy>
</cp:coreProperties>
"""


def _app_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>A13 Career Planner</Application>
</Properties>
"""


def _styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="30"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="26"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:qFormat/>
    <w:rPr><w:b/><w:sz w:val="24"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph">
    <w:name w:val="List Paragraph"/>
    <w:qFormat/>
  </w:style>
</w:styles>
"""


def _wrap_text_for_pdf(text: str, width: int) -> list[str]:
    if len(text) <= width:
        return [text]
    return [text[i : i + width] for i in range(0, len(text), width)]
