# Smart Teacher Assistant

## Project Overview
Smart Teacher Assistant is an AI-powered application designed to help teachers automate and enhance various classroom tasks. The application uses Google's Gemini AI model to generate lesson plans, create test questions, and provide assistance to students.

## Files in this Project

- **app.py**: The main Streamlit application file that creates the user interface and handles user interactions. It contains the three main tools (Generate Lesson Plan, Create Test Questions, Help Students) and connects the UI to the backend functions.

- **functions.py**: Contains all the helper functions that power the application:
  - `query_llm()`: Communicates with the Gemini AI model
  - `extract_text_from_pdf()`: Extracts text and performs OCR on images in PDF files
  - `create_questions_pdf()`: Generates professionally formatted PDF files containing test questions

## Features

- **Generate Lesson Plans**: Create customized lesson plans based on subject, topic, grade level, and student proficiency
- **Create Test Questions**: Generate multiple-choice, written, and true/false questions with answer keys
- **Help Students**: Provide simple explanations to student questions

## Setup & Usage

1. Install required dependencies:
```bash
pip install streamlit google-generativeai pymupdf pillow pytesseract reportlab
```

2. Set up Google Gemini API key in the code

3. Run the application:
```bash
streamlit run app.py
```

## Technologies Used
- Streamlit for the web interface
- Google Gemini AI for content generation
- PyMuPDF and Tesseract OCR for PDF processing
- ReportLab for PDF creation
