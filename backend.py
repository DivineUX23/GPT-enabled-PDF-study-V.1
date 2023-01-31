"""My Python module.

This module contains functions and classes for performing various tasks.
"""

#from cmd import PROMPT
import sys
import os
import fitz
from flask import Flask, render_template, flash, request
import tempfile
import shutil, re
import openai
from flask import jsonify
print(sys.version)


app = Flask(__name__, template_folder='templates')
app = Flask(__name__)
app.secret_key = 'divine'


# Use your own API key
openai.api_key = "XXXXXXXXXXXXXXXX"

# Initialize an empty list to store the extracted text
extracted_text = []

# Initialize an empty list to store the extracted text
extracting_text = []

conversation_history = []


chatbot_response = None
page_number = None
@app.route('/', methods=['GET', 'POST'])
def extract_pdf_text():
    """
    Extracts text from specific pages of a PDF file and returns it as a string.

    Args:
        pdf_file (FileStorage): The uploaded PDF file.
        page_numbers (list): A list of integers representing the page numbers to extract.

    Returns:
        str: The extracted text.
    """

    if request.method == 'GET':
        flash("Please don't upload a pdf file of over 10 pages. We're still making improvemnts.")
        return render_template('frontend.html')

    if request.method == 'POST':
        global page_number
        pdf_data = None
        # Get the uploaded PDF file and page numbers from the form data
        pdf_file = request.files['pdf_file']


        # Save the PDF file to a temporary location on the filesystem
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = f"{temp_dir}/temp.pdf"
            pdf_file.save(pdf_path)

            flash("File uploaded successfully")


            # Open the PDF file using PyMuPDF
            pdf_doc = fitz.Document(pdf_path)

        # Iterate through all pages in the PDF document
        for page_number in range(pdf_doc.page_count):

            # Load the page from the PDF document
            page = pdf_doc.load_page(page_number)

            # Extract the text from the page
            text = page.get_text()

            # Add the extracted text and page number to the list
            extracting_text.append((text, page_number))

        return render_template('frontend.html', summary=extracting_text)


    else:
        # Render the HTML template for the GET request
        return render_template('frontend.html')

@app.route('/conversation', methods=['POST'])
def handle_conversation():

    global chatbot_response
    global page_number

    #User input
    user_input = request.form['user_input']

    # To engage in a conversation with the user about the summarized text
    prompt = f"From {extracting_text}. {user_input} specify the page you got the answer. if the answer is not in the book say so and provide your answer.  If no book was provide, say so and ask if I'll like to know anything else keep it simple and straight to the point."

    # Use GPT-3 to generate a esponse based on the user's input
    completions = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.0,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    bot_response = completions.choices[0].text

    conversation_history.append(f"You: {user_input}")
    conversation_history.append(f"AI: {bot_response}")


    return render_template('frontend.html', bot_response = bot_response, conversation_history=conversation_history)

#for deleting temp file

@app.route('/clear_data', methods=['DELETE'])
def clear_data():
        # code to delete the data
        extracted_text.clear()
        extracting_text.clear()
        shutil.rmtree(temp_dir)

        return jsonify(message="cleared successfully"),200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
