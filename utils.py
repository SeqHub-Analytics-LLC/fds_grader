import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import openai

# Get the API key from the environment

TABLE_NAME = "exercise_store"
api_key = os.getenv("OPENAI_API_KEY")

def get_exercise_details(engine, file_name, exercise_number):
    """
    Queries PostgreSQL for context_question and answer based on file_name and exercise_number.
    
    Returns:
        tuple: (context_question, answer) if found, otherwise (None, None).
    """
    query = text(f"""
        SELECT context_question, answer 
        FROM {TABLE_NAME} 
        WHERE file_name = :file_name 
          AND exercise_number = :exercise_number
        LIMIT 1;
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"file_name": file_name, "exercise_number": exercise_number}).fetchone()
        return result if result else (None, None)
    except SQLAlchemyError as e:
        print(f"Database Error: {e}")
        return None, None

def chatcompletion(prompt, temperature=0.7, model="gpt-4o"):
    """
    Generates feedback for the student's response using OpenAI's GPT model.

    Args:
        prompt (str): The input prompt for the model.
        temperature (float, optional): Sampling temperature. Default is 0.7.
        model (str, optional): OpenAI model. Default is "gpt-4o".

    Returns:
        str: AI-generated feedback response.
    """
    messages = [{"role": "system",
                 "content": """You are a teacher tasked with providing constructive feedback to students. Given the question, the correct solution, and the student's attempt, your goal is to analyze their response, identify errors or areas for improvement, and offer clear, supportive guidance. Address the student directly using 'you'. Ensure your feedback is educational, encouraging, and tailored to help the student learn and improve."""},
                {"role": "user", "content": prompt}]
    try:
        openai_response = openai.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages
        )
        return openai_response.choices[0].message.content
    except Exception as e:
        return "An error occurred while generating feedback. Please try again later."
