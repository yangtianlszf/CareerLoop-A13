from __future__ import annotations

import io
import zipfile
from pathlib import Path
from xml.etree import ElementTree


class ResumeFileParseError(RuntimeError):
    pass


def parse_resume_file(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix in {".txt", ".md"}:
        return _decode_text_bytes(content)
    if suffix == ".docx":
        return _parse_docx(content)
    if suffix == ".pdf":
        return _parse_pdf(content)
    raise ResumeFileParseError("当前仅支持 txt、md、docx、pdf 文件。")


def _decode_text_bytes(content: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "gbk"):
        try:
            text = content.decode(encoding)
        except UnicodeDecodeError:
            continue
        cleaned = text.strip()
        if cleaned:
            return cleaned
    raise ResumeFileParseError("文本文件编码无法识别，请先转换为 UTF-8 再上传。")


def _parse_docx(content: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as docx:
            document_xml = docx.read("word/document.xml")
    except KeyError as error:
        raise ResumeFileParseError("DOCX 文件缺少正文内容，无法解析。") from error
    except zipfile.BadZipFile as error:
        raise ResumeFileParseError("DOCX 文件格式损坏，无法解析。") from error

    root = ElementTree.fromstring(document_xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:body/w:p", namespace):
        texts = [node.text for node in paragraph.findall(".//w:t", namespace) if node.text]
        merged = "".join(texts).strip()
        if merged:
            paragraphs.append(merged)
    extracted = "\n".join(paragraphs).strip()
    if not extracted:
        raise ResumeFileParseError("DOCX 文件里没有识别到文本内容。")
    return extracted


def _parse_pdf(content: bytes) -> str:
    reader = None
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(io.BytesIO(content))
    except Exception:
        try:
            from PyPDF2 import PdfReader  # type: ignore

            reader = PdfReader(io.BytesIO(content))
        except Exception as error:
            raise ResumeFileParseError(
                "当前环境没有安装 PDF 解析依赖，建议优先上传 txt、md 或 docx 简历。"
            ) from error

    texts: list[str] = []
    for page in reader.pages:
        page_text = (page.extract_text() or "").strip()
        if page_text:
            texts.append(page_text)
    extracted = "\n".join(texts).strip()
    if not extracted:
        raise ResumeFileParseError("PDF 文件中没有识别到可用文本。")
    return extracted
