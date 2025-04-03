import io
from typing import Any, List, Dict
import pymupdf as fitz
from PIL import Image
import pytesseract
from reportlab.lib import pagesizes
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def query_llm(model: Any, prompt: str) -> str:
    """Query a LLM with a given prompt and return the response.

    Args:
        model: The LLM to query.
        prompt: The input prompt to send to the model.

    Returns:
        The model's response text or an error message if the query fails.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


def extract_text_from_pdf(pdf_file: io.BytesIO) -> str:
    """Extract text from a PDF file using PyMuPDF and OCR for images.

    Args:
        pdf_file: A file-like object containing the PDF data.

    Returns:
        Extracted text from the PDF, including OCR text from images.
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""

    for page in doc:
        text += page.get_text("text") + "\n"
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            img_pil = Image.open(io.BytesIO(image_data))
            ocr_text = pytesseract.image_to_string(img_pil)
            text += f"\n[Image {img_index + 1} OCR Text]:\n{ocr_text}"

    doc.close()
    return text


def create_questions_pdf(topic: str, questions_text: str) -> io.BytesIO:
    """Create a professional PDF containing only questions.

    Args:
        topic: The topic or title of the test.
        questions_text: Text containing questions in the format:
            Multiple Choice Questions (MCQ)
            1. Question 1
            a) Option 1
            b) Option 2
            c) Option 3
            d) Option 4

            Open-Ended Written Questions
            1. Question 1
            2. Question 2

            True or False
            1. Statement 1
            2. Statement 2

    Returns:
        A PDF file in BytesIO format containing the formatted questions.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.letter,
        topMargin=50,
        bottomMargin=50,
        leftMargin=30,
        rightMargin=30
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=1,
        spaceAfter=20
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        spaceBefore=20,
        spaceAfter=10
    )
    question_style = ParagraphStyle(
        "Question",
        parent=styles["BodyText"],
        leftIndent=10,
        spaceAfter=5
    )
    option_style = ParagraphStyle(
        "Option",
        parent=styles["BodyText"],
        leftIndent=20
    )

    story: List[Any] = []

    # Header with topic
    story.append(Paragraph(f"Test Questions: {topic}", title_style))
    story.append(Spacer(1, 20))

    # Parse questions
    lines = questions_text.split("\n")
    current_section = None
    sections: Dict[str, List[str]] = {"MCQ": [], "Written": [], "T&F": []}
    question_counter: Dict[str, int] = {"MCQ": 0, "Written": 0, "T&F": 0}

    for line in lines:
        line = line.strip()
        if "Multiple Choice Questions (MCQ)" in line:
            current_section = "MCQ"
        elif "Open-Ended Written Questions" in line or "Written Questions" in line:
            current_section = "Written"
        elif "True or False" in line or "True/False" in line:
            current_section = "T&F"
        elif line and current_section and "Answer Key" not in line:
            sections[current_section].append(line)

    # Build PDF content
    for section, questions in sections.items():
        if questions:
            story.append(Paragraph(f"{section} Section", section_style))
            for question in questions:
                if (section == "MCQ" and 
                    not any(question.startswith(x) for x in ["a)", "b)", "c)", "d)"])):
                    question_counter[section] += 1
                    story.append(Paragraph(
                        f"{question_counter[section]}. {question}",
                        question_style
                    ))
                elif section == "MCQ":
                    story.append(Paragraph(question, option_style))
                else:
                    question_counter[section] += 1
                    story.append(Paragraph(
                        f"{question_counter[section]}. {question}",
                        question_style
                    ))
                story.append(Spacer(1, 8))
            story.append(Spacer(1, 20))

    doc.build(story)
    buffer.seek(0)
    return buffer