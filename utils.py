import json
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import openai
import os
from dotenv import load_dotenv

# Get the API key from the environment
api_key = os.getenv("OPENAI_API_KEY")

def get_solution(exercise_number, file_name):
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002",openai_api_key=api_key)

    # Load the vector store
    vector_store = FAISS.load_local("exercise_solution_store", embeddings,allow_dangerous_deserialization=True)

    # Student's attempt
    student_attempt = f"Get solution for exercise {exercise_number}"

    #Retrieve relevant exercises for a specific course and lab
    filters = {
        "file_name": file_name,
        'exercise_number': exercise_number
    }

    retrieved_docs = vector_store.similarity_search(student_attempt, k=1, filter=filters)
    return retrieved_docs


# Function to complete chat input using OpenAI's GPT-3.5 Turbo

def chatcompletion(prompt, messages = [], temperature = 0.7, model="gpt-4o"):
    messages.append({"role": "user", "content": prompt})
    openai_response = openai.chat.completions.create(
        model = model,
        temperature = temperature,
        messages = messages
    )
    #print(openai_response)
    response_content = openai_response.choices[0].message.content
    #print("Raw response content:", response_content)

    try:
        result = json.loads(response_content)
    except json.JSONDecodeError:
        result = response_content  # If response is not JSON, return it as plain text
    return result