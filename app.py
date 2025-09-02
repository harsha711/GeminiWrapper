import os
from google import genai
from flask import Flask, render_template, request, session
# from dotenv import load_dotenv
import secrets


# load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

app.secret_key = secrets.token_hex(16)

# --- Configuration ---
# Vercel will set the API key from your project's Environment Variables
# Make sure you have set GEMINI_API_KEY in your Vercel project settings
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    # This error will be visible in the Vercel logs if the key is missing
    raise ValueError("GEMINI_API_KEY environment variable not set.")

client = genai.Client(api_key=api_key)
chat = client.chats.create(model='gemini-2.5-pro')

# --- Model Configuration ---
# Initialize the generative model
def to_serializable(history):
    """Converts Gemini chat history to a JSON-serializable format."""
    serializable_history = []
    for message in history:
        serializable_history.append({
            "role": message.role,
            "parts": [part.text for part in message.parts]
        })
    return serializable_history


@app.route('/', methods=['GET', 'POST'])
def index():
    gemini_response_text = ""

    if request.method == 'POST':
        if not client:
            gemini_response_text = "Error: The generative model is not initialized. Please check the server logs."
            return render_template('index.html', response=gemini_response_text)

        chat_history = session.get('chat_history', [])

        user_prompt = request.form.get('prompt', '').strip()

        if user_prompt:
            try:
                # Send the prompt to the Gemini API
                response = chat.send_message(user_prompt)
                session['chat_history'] = to_serializable(chat.get_history())

                gemini_response_text = chat.get_history()
            except Exception as e:
                # Handle potential errors from the API during generation
                gemini_response_text = f"An API error occurred: {e}"
        else:
            gemini_response_text = "Please enter a prompt."

    return render_template('index.html', response=gemini_response_text)

# if __name__ == '__main__':
#     app.run(debug=True)