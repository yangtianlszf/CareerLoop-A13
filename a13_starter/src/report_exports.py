from __future__ import annotations

import html
import io
import os
import re
import struct
import zipfile
import zlib
from functools import lru_cache
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape


_PDF_PAGE_WIDTH = 595
_PDF_PAGE_HEIGHT = 842
_PDF_LEFT_MARGIN = 48
_PDF_TOP_MARGIN = 792
_PDF_BOTTOM_MARGIN = 56
_PDF_LINE_HEIGHT = 16
_PDF_FONT_SIZE = 11
_PDF_MAX_LINE_UNITS = 58
_PDF_FONT_CANDIDATES = (
    "/mnt/c/Windows/Fonts/simhei.ttf",
    "/mnt/c/Windows/Fonts/STSONG.TTF",
    "/mnt/c/Windows/Fonts/Deng.ttf",
)


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
    normalized_lines = _markdown_to_pdf_lines(markdown_text, title=title)
    pages = _paginate_pdf_lines(normalized_lines)
    font_info = _load_embedded_pdf_font()
    if font_info is None:
        return _build_cjk_pdf_document(pages)
    return _build_embedded_cjk_pdf_document(pages, font_info)


def build_export_bundle(analysis: dict[str, Any]) -> dict[str, bytes | str]:
    title = f"{analysis['student_profile'].get('name', '学生')}_职业规划报告"
    markdown_text = str(analysis["report_markdown"])
    return build_report_export_bundle(markdown_text, title=title)


def build_report_export_bundle(markdown_text: str, title: str = "职业规划报告") -> dict[str, bytes | str]:
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


@lru_cache(maxsize=1)
def _load_embedded_pdf_font() -> dict[str, Any] | None:
    candidates: list[Path] = []
    env_path = str(os.environ.get("A13_PDF_FONT_PATH", "")).strip()
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(Path(path) for path in _PDF_FONT_CANDIDATES)

    for path in candidates:
        if not path.is_file():
            continue
        try:
            return _parse_ttf_font(path.read_bytes(), base_name=path.stem)
        except Exception:
            continue
    return None


def _read_ushort(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def _read_short(data: bytes, offset: int) -> int:
    return struct.unpack_from(">h", data, offset)[0]


def _read_ulong(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def _parse_ttf_font(data: bytes, base_name: str) -> dict[str, Any]:
    tables = _read_ttf_tables(data)
    required = ("cmap", "head", "hhea", "hmtx", "maxp")
    for tag in required:
        if tag not in tables:
            raise ValueError(f"Missing TTF table: {tag}")

    head_offset, _ = tables["head"]
    units_per_em = _read_ushort(data, head_offset + 18)
    x_min = _read_short(data, head_offset + 36)
    y_min = _read_short(data, head_offset + 38)
    x_max = _read_short(data, head_offset + 40)
    y_max = _read_short(data, head_offset + 42)

    hhea_offset, _ = tables["hhea"]
    ascent = _read_short(data, hhea_offset + 4)
    descent = _read_short(data, hhea_offset + 6)
    num_h_metrics = _read_ushort(data, hhea_offset + 34)

    maxp_offset, _ = tables["maxp"]
    num_glyphs = _read_ushort(data, maxp_offset + 4)

    hmtx_offset, _ = tables["hmtx"]
    advances: list[int] = []
    last_advance = 0
    for index in range(num_glyphs):
        if index < num_h_metrics:
            last_advance = _read_ushort(data, hmtx_offset + index * 4)
        advances.append(last_advance)

    cmap = _read_best_unicode_cmap(data, tables["cmap"][0])
    font_name = _sanitize_pdf_font_name(base_name or "A13EmbeddedCJK")
    return {
        "data": data,
        "tables": tables,
        "units_per_em": units_per_em or 1000,
        "bbox": (x_min, y_min, x_max, y_max),
        "ascent": ascent,
        "descent": descent,
        "advances": advances,
        "cmap": cmap,
        "font_name": font_name,
    }


def _read_ttf_tables(data: bytes) -> dict[str, tuple[int, int]]:
    num_tables = _read_ushort(data, 4)
    offset = 12
    tables: dict[str, tuple[int, int]] = {}
    for _ in range(num_tables):
        tag = data[offset:offset + 4].decode("latin1")
        table_offset = _read_ulong(data, offset + 8)
        table_length = _read_ulong(data, offset + 12)
        tables[tag] = (table_offset, table_length)
        offset += 16
    return tables


def _read_best_unicode_cmap(data: bytes, cmap_table_offset: int) -> dict[str, Any]:
    num_tables = _read_ushort(data, cmap_table_offset + 2)
    best_score = -1
    best_cmap: dict[str, Any] | None = None

    for index in range(num_tables):
        record_offset = cmap_table_offset + 4 + index * 8
        platform_id = _read_ushort(data, record_offset)
        encoding_id = _read_ushort(data, record_offset + 2)
        subtable_offset = cmap_table_offset + _read_ulong(data, record_offset + 4)
        format_type = _read_ushort(data, subtable_offset)

        score = -1
        if format_type == 12 and platform_id == 3 and encoding_id == 10:
            score = 400
        elif format_type == 12 and platform_id == 0:
            score = 380
        elif format_type == 4 and platform_id == 3 and encoding_id in (1, 10):
            score = 300
        elif format_type == 4 and platform_id == 0:
            score = 280

        if score <= best_score:
            continue

        if format_type == 12:
            best_cmap = _parse_cmap_format12(data, subtable_offset)
            best_score = score
        elif format_type == 4:
            best_cmap = _parse_cmap_format4(data, subtable_offset)
            best_score = score

    if best_cmap is None:
        raise ValueError("No Unicode cmap found in font")
    return best_cmap


def _parse_cmap_format12(data: bytes, offset: int) -> dict[str, Any]:
    group_count = _read_ulong(data, offset + 12)
    groups: list[tuple[int, int, int]] = []
    cursor = offset + 16
    for _ in range(group_count):
        start_char = _read_ulong(data, cursor)
        end_char = _read_ulong(data, cursor + 4)
        start_glyph = _read_ulong(data, cursor + 8)
        groups.append((start_char, end_char, start_glyph))
        cursor += 12
    return {"format": 12, "groups": groups}


def _parse_cmap_format4(data: bytes, offset: int) -> dict[str, Any]:
    seg_count = _read_ushort(data, offset + 6) // 2
    end_count_offset = offset + 14
    start_count_offset = end_count_offset + 2 * seg_count + 2
    id_delta_offset = start_count_offset + 2 * seg_count
    id_range_offset_offset = id_delta_offset + 2 * seg_count

    end_counts = [_read_ushort(data, end_count_offset + i * 2) for i in range(seg_count)]
    start_counts = [_read_ushort(data, start_count_offset + i * 2) for i in range(seg_count)]
    id_deltas = [_read_short(data, id_delta_offset + i * 2) for i in range(seg_count)]
    id_range_offsets = [_read_ushort(data, id_range_offset_offset + i * 2) for i in range(seg_count)]

    return {
        "format": 4,
        "offset": offset,
        "seg_count": seg_count,
        "end_counts": end_counts,
        "start_counts": start_counts,
        "id_deltas": id_deltas,
        "id_range_offsets": id_range_offsets,
        "id_range_offset_offset": id_range_offset_offset,
        "data": data,
    }


def _lookup_glyph_id(font: dict[str, Any], char: str) -> int:
    codepoint = ord(char)
    cmap = font["cmap"]
    if cmap["format"] == 12:
        for start_char, end_char, start_glyph in cmap["groups"]:
            if start_char <= codepoint <= end_char:
                return start_glyph + (codepoint - start_char)
        return 0

    for index in range(cmap["seg_count"]):
        start_char = cmap["start_counts"][index]
        end_char = cmap["end_counts"][index]
        if not (start_char <= codepoint <= end_char):
            continue
        range_offset = cmap["id_range_offsets"][index]
        delta = cmap["id_deltas"][index]
        if range_offset == 0:
            return (codepoint + delta) & 0xFFFF

        glyph_offset = (
            cmap["id_range_offset_offset"]
            + index * 2
            + range_offset
            + 2 * (codepoint - start_char)
        )
        glyph_id = _read_ushort(cmap["data"], glyph_offset)
        if glyph_id == 0:
            return 0
        return (glyph_id + delta) & 0xFFFF
    return 0


def _glyph_width_1000(font: dict[str, Any], glyph_id: int) -> int:
    advances = font["advances"]
    units_per_em = font["units_per_em"] or 1000
    advance = advances[glyph_id] if 0 <= glyph_id < len(advances) else advances[0]
    return max(1, round(advance * 1000 / units_per_em))


def _sanitize_pdf_font_name(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9]+", "", value or "A13EmbeddedCJK")
    return safe or "A13EmbeddedCJK"


def _scale_font_metric(font: dict[str, Any], value: int) -> int:
    units_per_em = font["units_per_em"] or 1000
    return round(value * 1000 / units_per_em)


def _wrap_text_for_pdf(text: str, width: int) -> list[str]:
    normalized = str(text or "").replace("\r", "")
    if not normalized:
        return [""]

    lines: list[str] = []
    current: list[str] = []
    current_units = 0
    for char in normalized:
        units = _pdf_char_units(char)
        if current and current_units + units > width:
            lines.append("".join(current).rstrip())
            current = [char]
            current_units = units
            continue
        current.append(char)
        current_units += units

    if current:
        lines.append("".join(current).rstrip())
    return lines or [""]


def _pdf_char_units(char: str) -> int:
    if char == "\t":
        return 4
    if ord(char) < 128:
        return 1
    return 2


def _markdown_to_pdf_lines(markdown_text: str, title: str) -> list[str]:
    lines: list[str] = []
    clean_title = str(title or "").strip()
    if clean_title:
        lines.extend(_wrap_text_for_pdf(clean_title, _PDF_MAX_LINE_UNITS))
        lines.append("")

    for raw_line in str(markdown_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            if lines and lines[-1] != "":
                lines.append("")
            continue

        if line.startswith("# "):
            heading = line[2:].strip()
            if heading:
                if lines and lines[-1] != "":
                    lines.append("")
                lines.extend(_wrap_text_for_pdf(heading, _PDF_MAX_LINE_UNITS))
                lines.append("")
            continue

        if line.startswith("## "):
            heading = line[3:].strip()
            if heading:
                if lines and lines[-1] != "":
                    lines.append("")
                lines.extend(_wrap_text_for_pdf(f"[{heading}]", _PDF_MAX_LINE_UNITS))
            continue

        if line.startswith("### "):
            heading = line[4:].strip()
            if heading:
                lines.extend(_wrap_text_for_pdf(f"- {heading}", _PDF_MAX_LINE_UNITS))
            continue

        if line.startswith("- "):
            content = line[2:].strip()
            wrapped = _wrap_text_for_pdf(f"- {content}", _PDF_MAX_LINE_UNITS)
            lines.extend(wrapped)
            continue

        lines.extend(_wrap_text_for_pdf(line, _PDF_MAX_LINE_UNITS))

    while lines and lines[-1] == "":
        lines.pop()
    return lines or ["职业规划报告"]


def _paginate_pdf_lines(lines: list[str]) -> list[list[str]]:
    max_lines_per_page = max(1, (_PDF_TOP_MARGIN - _PDF_BOTTOM_MARGIN) // _PDF_LINE_HEIGHT)
    pages: list[list[str]] = []
    current_page: list[str] = []
    for line in lines:
        current_page.append(line)
        if len(current_page) >= max_lines_per_page:
            pages.append(current_page)
            current_page = []
    if current_page:
        pages.append(current_page)
    return pages or [["职业规划报告"]]


def _pdf_hex_text(text: str) -> str:
    safe_text = text if text else " "
    return "FEFF" + safe_text.encode("utf-16-be").hex().upper()


def _page_stream_bytes(lines: list[str]) -> bytes:
    commands = [
        "BT",
        f"/F1 {_PDF_FONT_SIZE} Tf",
        f"1 0 0 1 {_PDF_LEFT_MARGIN} {_PDF_TOP_MARGIN} Tm",
        f"{_PDF_LINE_HEIGHT} TL",
    ]
    first_line = True
    for line in lines:
        encoded = _pdf_hex_text(line)
        if first_line:
            commands.append(f"<{encoded}> Tj")
            first_line = False
        else:
            commands.append(f"T* <{encoded}> Tj")
    commands.append("ET")
    return "\n".join(commands).encode("ascii")


def _encode_pdf_text_with_embedded_font(text: str, font: dict[str, Any]) -> tuple[str, dict[int, str]]:
    safe_text = text if text else " "
    glyph_map: dict[int, str] = {}
    fallback_chars = ["?", "？", "□", " "]
    encoded_parts: list[str] = []

    for char in safe_text:
        glyph_id = _lookup_glyph_id(font, char)
        mapped_char = char
        if glyph_id == 0:
            for fallback in fallback_chars:
                glyph_id = _lookup_glyph_id(font, fallback)
                if glyph_id:
                    mapped_char = fallback
                    break
        encoded_parts.append(f"{glyph_id & 0xFFFF:04X}")
        if glyph_id and glyph_id not in glyph_map:
            glyph_map[glyph_id] = mapped_char

    return "".join(encoded_parts), glyph_map


def _build_embedded_page_stream_bytes(lines: list[str], font: dict[str, Any]) -> tuple[bytes, dict[int, str]]:
    commands = [
        "BT",
        f"/F1 {_PDF_FONT_SIZE} Tf",
        f"1 0 0 1 {_PDF_LEFT_MARGIN} {_PDF_TOP_MARGIN} Tm",
        f"{_PDF_LINE_HEIGHT} TL",
    ]
    glyph_map: dict[int, str] = {}
    first_line = True
    for line in lines:
        encoded, line_map = _encode_pdf_text_with_embedded_font(line, font)
        for glyph_id, char in line_map.items():
            glyph_map.setdefault(glyph_id, char)
        if first_line:
            commands.append(f"<{encoded}> Tj")
            first_line = False
        else:
            commands.append(f"T* <{encoded}> Tj")
    commands.append("ET")
    return "\n".join(commands).encode("ascii"), glyph_map


def _build_tounicode_cmap(glyph_map: dict[int, str]) -> bytes:
    lines = [
        "/CIDInit /ProcSet findresource begin",
        "12 dict begin",
        "begincmap",
        "/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> def",
        "/CMapName /A13ToUnicode def",
        "/CMapType 2 def",
        "1 begincodespacerange",
        "<0000> <FFFF>",
        "endcodespacerange",
    ]
    items = [
        (glyph_id, char)
        for glyph_id, char in sorted(glyph_map.items())
        if 0 < glyph_id <= 0xFFFF and char
    ]
    if not items:
        items = [(1, " ")]

    chunk_size = 100
    for start in range(0, len(items), chunk_size):
        chunk = items[start:start + chunk_size]
        lines.append(f"{len(chunk)} beginbfchar")
        for glyph_id, char in chunk:
            unicode_hex = char.encode("utf-16-be").hex().upper()
            lines.append(f"<{glyph_id:04X}> <{unicode_hex}>")
        lines.append("endbfchar")

    lines.extend(
        [
            "endcmap",
            "CMapName currentdict /CMap defineresource pop",
            "end",
            "end",
        ]
    )
    return "\n".join(lines).encode("ascii")


def _build_embedded_cjk_pdf_document(pages: list[list[str]], font: dict[str, Any]) -> bytes:
    page_streams: list[bytes] = []
    glyph_map: dict[int, str] = {}
    for page_lines in pages:
        stream, page_glyphs = _build_embedded_page_stream_bytes(page_lines, font)
        page_streams.append(stream)
        for glyph_id, char in page_glyphs.items():
            glyph_map.setdefault(glyph_id, char)

    used_glyph_ids = sorted(glyph_id for glyph_id in glyph_map if 0 < glyph_id <= 0xFFFF)
    widths_chunks: list[str] = []
    if used_glyph_ids:
        group: list[int] = [used_glyph_ids[0]]
        for glyph_id in used_glyph_ids[1:]:
            if glyph_id == group[-1] + 1:
                group.append(glyph_id)
                continue
            widths = " ".join(str(_glyph_width_1000(font, current)) for current in group)
            widths_chunks.append(f"{group[0]} [{widths}]")
            group = [glyph_id]
        widths = " ".join(str(_glyph_width_1000(font, current)) for current in group)
        widths_chunks.append(f"{group[0]} [{widths}]")

    widths_entry = "[ " + " ".join(widths_chunks) + " ]" if widths_chunks else "[]"

    font_file = font["data"]
    compressed_font_file = zlib.compress(font_file, level=9)
    tounicode_stream = _build_tounicode_cmap(glyph_map)
    compressed_tounicode = zlib.compress(tounicode_stream, level=9)

    x_min, y_min, x_max, y_max = font["bbox"]
    bbox = " ".join(
        str(_scale_font_metric(font, value))
        for value in (x_min, y_min, x_max, y_max)
    )
    ascent = _scale_font_metric(font, font["ascent"])
    descent = _scale_font_metric(font, font["descent"])
    cap_height = max(ascent, _scale_font_metric(font, y_max))
    missing_width = _glyph_width_1000(font, 0)
    font_name = font["font_name"]

    objects: dict[int, bytes] = {
        1: b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        3: (
            f"3 0 obj<< /Type /Font /Subtype /Type0 /BaseFont /{font_name} "
            f"/Encoding /Identity-H /DescendantFonts [4 0 R] /ToUnicode 7 0 R >>endobj\n"
        ).encode("ascii"),
        4: (
            f"4 0 obj<< /Type /Font /Subtype /CIDFontType2 /BaseFont /{font_name} "
            "/CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> "
            "/FontDescriptor 5 0 R "
            f"/DW {missing_width} /W {widths_entry} /CIDToGIDMap /Identity >>endobj\n"
        ).encode("ascii"),
        5: (
            f"5 0 obj<< /Type /FontDescriptor /FontName /{font_name} "
            f"/Flags 4 /FontBBox [{bbox}] /Ascent {ascent} /Descent {descent} "
            f"/CapHeight {cap_height} /ItalicAngle 0 /StemV 80 /MissingWidth {missing_width} "
            "/FontFile2 6 0 R >>endobj\n"
        ).encode("ascii"),
        6: (
            f"6 0 obj<< /Length {len(compressed_font_file)} /Filter /FlateDecode /Length1 {len(font_file)} >>stream\n".encode("ascii")
            + compressed_font_file
            + b"\nendstream\nendobj\n"
        ),
        7: (
            f"7 0 obj<< /Length {len(compressed_tounicode)} /Filter /FlateDecode >>stream\n".encode("ascii")
            + compressed_tounicode
            + b"\nendstream\nendobj\n"
        ),
    }

    page_ids: list[int] = []
    content_ids: list[int] = []
    next_object_id = 8
    for stream in page_streams:
        page_id = next_object_id
        content_id = next_object_id + 1
        page_ids.append(page_id)
        content_ids.append(content_id)
        objects[content_id] = (
            f"{content_id} 0 obj<< /Length {len(stream)} >>stream\n".encode("ascii")
            + stream
            + b"\nendstream\nendobj\n"
        )
        next_object_id += 2

    page_refs = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[2] = (
        f"2 0 obj<< /Type /Pages /Kids [{page_refs}] /Count {len(page_ids)} >>endobj\n"
    ).encode("ascii")

    for page_id, content_id in zip(page_ids, content_ids, strict=True):
        objects[page_id] = (
            f"{page_id} 0 obj<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 {_PDF_PAGE_WIDTH} {_PDF_PAGE_HEIGHT}] "
            f"/Contents {content_id} 0 R "
            "/Resources << /Font << /F1 3 0 R >> >> >>endobj\n"
        ).encode("ascii")

    pdf = io.BytesIO()
    pdf.write(b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n")
    offsets = [0]
    max_id = max(objects)
    for current_id in range(1, max_id + 1):
        payload = objects[current_id]
        offsets.append(pdf.tell())
        pdf.write(payload)

    xref_position = pdf.tell()
    pdf.write(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.write(
        (
            f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_position}\n%%EOF"
        ).encode("ascii")
    )
    return pdf.getvalue()


def _build_cjk_pdf_document(pages: list[list[str]]) -> bytes:
    objects: dict[int, bytes] = {
        1: b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
    }

    page_ids: list[int] = []
    content_ids: list[int] = []
    object_id = 3
    for page_lines in pages:
        page_id = object_id
        content_id = object_id + 1
        page_ids.append(page_id)
        content_ids.append(content_id)
        object_id += 2

        stream = _page_stream_bytes(page_lines)
        objects[content_id] = (
            f"{content_id} 0 obj<< /Length {len(stream)} >>stream\n".encode("ascii")
            + stream
            + b"\nendstream\nendobj\n"
        )

    font_id = object_id
    cid_font_id = object_id + 1

    page_refs = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[2] = f"2 0 obj<< /Type /Pages /Kids [{page_refs}] /Count {len(page_ids)} >>endobj\n".encode("ascii")

    for page_id, content_id in zip(page_ids, content_ids, strict=True):
        objects[page_id] = (
            f"{page_id} 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {_PDF_PAGE_WIDTH} {_PDF_PAGE_HEIGHT}] "
            f"/Contents {content_id} 0 R /Resources << /Font << /F1 {font_id} 0 R >> >> >>endobj\n"
        ).encode("ascii")

    objects[font_id] = (
        f"{font_id} 0 obj<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light "
        f"/Encoding /UniGB-UCS2-H /DescendantFonts [{cid_font_id} 0 R] >>endobj\n"
    ).encode("ascii")
    objects[cid_font_id] = (
        f"{cid_font_id} 0 obj<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light "
        "/CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 4 >> "
        "/DW 1000 >>endobj\n"
    ).encode("ascii")

    pdf = io.BytesIO()
    pdf.write(b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n")
    offsets = [0]
    max_id = max(objects)
    for current_id in range(1, max_id + 1):
        payload = objects[current_id]
        offsets.append(pdf.tell())
        pdf.write(payload)

    xref_position = pdf.tell()
    pdf.write(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.write(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.write(
        (
            f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_position}\n%%EOF"
        ).encode("ascii")
    )
    return pdf.getvalue()
