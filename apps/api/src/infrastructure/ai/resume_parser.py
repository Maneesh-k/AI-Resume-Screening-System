from __future__ import annotations

import asyncio
import io
from pathlib import Path

import structlog

from src.infrastructure.ai.openai_client import chat_completion

log = structlog.get_logger()

_RESUME_PARSE_PROMPT = (Path(__file__).parent / "prompts" / "resume_parse.txt").read_text()
_SCORE_PROMPT = (Path(__file__).parent / "prompts" / "candidate_score.txt").read_text()
_SUMMARY_PROMPT = (Path(__file__).parent / "prompts" / "summary_generate.txt").read_text()
_QUESTIONS_PROMPT = (Path(__file__).parent / "prompts" / "question_generate.txt").read_text()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF."""
    try:
        import fitz  # pymupdf
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = [page.get_text() for page in doc]
        doc.close()
        return "\n".join(text_parts).strip()
    except Exception as e:
        log.warning("pdf_text_extraction_failed", error=str(e))
        return ""


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        log.warning("docx_text_extraction_failed", error=str(e))
        return ""


def extract_text_via_ocr(file_bytes: bytes) -> str:
    """Fallback OCR extraction for scanned PDFs."""
    try:
        import fitz
        import pytesseract
        from PIL import Image

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        texts = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            texts.append(pytesseract.image_to_string(img))
        doc.close()
        return "\n".join(texts).strip()
    except Exception as e:
        log.warning("ocr_extraction_failed", error=str(e))
        return ""


def extract_text(file_bytes: bytes, content_type: str) -> str:
    """Extract text from resume file. Falls back to OCR for PDFs."""
    if "pdf" in content_type:
        text = extract_text_from_pdf(file_bytes)
        if len(text.strip()) < 100:
            log.info("falling_back_to_ocr")
            text = asyncio.get_event_loop().run_until_complete(
                asyncio.to_thread(extract_text_via_ocr, file_bytes)
            )
        return text
    elif "word" in content_type or "docx" in content_type:
        return extract_text_from_docx(file_bytes)
    return ""


async def parse_resume(resume_text: str) -> dict:
    """Use LLM to structure resume text into JSON."""
    user_prompt = f"Parse the following resume:\n\n{resume_text[:15000]}"
    return await chat_completion(_RESUME_PARSE_PROMPT, user_prompt, json_mode=True)


async def score_candidate(resume_text: str, job_description: str, required_skills: list[str]) -> dict:
    """Score candidate against job description using LLM."""
    user_prompt = f"""
JOB DESCRIPTION:
{job_description[:5000]}

REQUIRED SKILLS: {", ".join(required_skills)}

CANDIDATE RESUME:
{resume_text[:8000]}
"""
    return await chat_completion(_SCORE_PROMPT, user_prompt, json_mode=True)


async def generate_summary(resume_text: str, job_title: str, job_description: str) -> str:
    """Generate a professional AI summary for the candidate."""
    user_prompt = f"""
JOB TITLE: {job_title}

JOB DESCRIPTION (excerpt):
{job_description[:3000]}

CANDIDATE RESUME:
{resume_text[:8000]}
"""
    result = await chat_completion(_SUMMARY_PROMPT, user_prompt, json_mode=True, temperature=0.4)
    return result.get("summary", "")


async def generate_interview_questions(resume_text: str, job_title: str, job_description: str) -> list[dict]:
    """Generate targeted interview questions for the candidate."""
    user_prompt = f"""
JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_description[:3000]}

CANDIDATE RESUME:
{resume_text[:8000]}
"""
    result = await chat_completion(_QUESTIONS_PROMPT, user_prompt, json_mode=True, temperature=0.5)
    return result.get("questions", [])
