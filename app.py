import os
import json
import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from utils import *


# Database Credentials
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', "5432")
DB_NAME = os.getenv('DB_NAME')
TABLE_NAME = "exercise_store"

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Create Database Engine
engine = create_engine(
    f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
    pool_size=10,
    max_overflow=5,
    pool_recycle=1800,
    pool_pre_ping=True
)

# Initialize FastAPI App
app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Model for API Request Validation
class FeedbackRequest(BaseModel):
    file_name: str
    exercise_number: str
    student_attempt: str

@app.get("/")
async def home():
    """ Home Route """
    return {"message": "Hello Pierrepont students!"}

@app.post("/feedback")
async def feedback_response(request: FeedbackRequest):
    """
    API endpoint to receive student attempts and provide feedback.

    Expected JSON Payload:
    {
        "file_name": "hw03",
        "exercise_number": "1",
        "student_attempt": "def student_code():\n    return None"
    }
    """
    try:
        file_name = request.file_name
        exercise_number = request.exercise_number
        student_attempt = request.student_attempt

        # Fetch question and correct answer from database
        context_question, answer = get_exercise_details(engine, file_name, exercise_number)
        
        if not context_question or not answer:
            raise HTTPException(status_code=404, detail="Exercise details not found")

        # Define user Prompt
        prompt = f"""
        A student was presented with the following question:
        ```
        {context_question}
        ```

        The correct solution to this question is:
        ```
        {answer}
        ```
        
        The student submitted the following function as their attempt:
        ```
        {student_attempt}
        ```
        
        Provide constructive feedback on the student's attempt:
        
        - If the student's solution is **functionally equivalent** to the correct solution, acknowledge that they are correct. Do not critique minor differences in style, naming, or structure.
        - If the student's solution is incorrect:
          - Identify the mistake and provide a helpful hint to guide them toward fixing it, without directly revealing the correct solution.
          - Recognize when their approach is close but flawed, and offer specific guidance on what needs adjustment.
          - Do not reference the correct solution—encourage them to refine their approach through subtle hints.
        - Accept alternative correct implementations, as long as they achieve the same result using valid logic.
        - Do not mention minor issues like indentation, formatting, or missing imports.
        - If the student's function still contains placeholders (e.g., `...`), assume they have not attempted the problem yet.
        - Avoid referring to any external document. Speak directly to the student as a tutor or reviewer, using first-person language.
        """

        feedback = chatcompletion(prompt)
        return {"response": feedback}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
