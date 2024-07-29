import os
import pytest
from fastapi.testclient import TestClient
from main import app
from reportlab.pdfgen import canvas
from docx import Document
from tests.documents.content import pdf1_content, pdf2_content, word1_content, word2_content


def create_pdf(pdf_name: str, pdf_content: str):
    c = canvas.Canvas(pdf_name)
    c.drawString(100, 750, pdf_content)
    c.save()


def create_word(word_doc_name: str, word_doc_content: str):
    doc = Document()
    doc.add_paragraph(word_doc_content)
    doc.save(word_doc_name)


client = TestClient(app)

