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

        The actual (correct) solution to the question is given below:
        ```
        {answer}
        ```

        To this end, they provided the following function as their response (attempt). Student's attempt:
        ```
        {student_attempt}
        ```

        Compare the students attempt to the correct solution and provide feedback to the student.
        - Explain the mistake and give a hint to help them fix it, without revealing the correct solution.
        - You can only claim that a student is yet to attempt the problem if the placeholders i.e ellipsis still exist in the function block instead of an answer attempt.
        - The correct answer must not be referenced if a student gets the answer wrong. Instead, prompt them to try again by highlighting subtle hints in the fault of their approach or response.
        - Don't refer to the document. The student doesn't need to know that you are sourcing from a document.
        - Speak in the first person to the student as a tutor or reviewer.
        """

        feedback = chatcompletion(prompt)
        return {"response": feedback}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
