import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from langchain_community.callbacks.manager import get_openai_callback
from langchain.globals import set_verbose, get_verbose
from src.utils import read_file, get_table_data
from src.MCQGenerator import generate_evaluate_chain
from src.logger import logging

# Load the JSON file
with open('Response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# Set the page config with a custom icon and title
st.set_page_config(
    page_title="MCQ Generator 📝",
    page_icon="📚",
    layout="centered"
)

# Create a title for the app with emojis
st.title("MCQs Application Generator with LangChain 🦜⛓️")

# Add a description and instructions for users
st.markdown("""
    Welcome to the **MCQ Generator**! 🚀
    
    Upload a PDF or text file and generate multiple-choice questions (MCQs) with ease.  
    Customize the number of questions, subject, and difficulty level to create the perfect quiz. 🎯
""")

# Create a form using st.form
with st.form("user_inputs"):
    # File Upload with a file uploader message
    st.header("Upload Your Content 📄")
    uploaded_file = st.file_uploader("Upload a PDF or txt file", type=["pdf", "txt"])

    # Input Fields
    st.header("Customize Your Quiz 🎨")
    mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=50, help="Select the number of questions you'd like to generate.")
    subject = st.text_input("Insert Subject", max_chars=20, help="Specify the subject of the quiz.")
    tone = st.text_input("Difficulty Level Of Questions", max_chars=20, placeholder="Simple", help="Define the difficulty level of the questions (e.g., Easy, Medium, Hard).")

    # Add a submit button
    button = st.form_submit_button("Create MCQs ✨")

    # Check if the button is clicked and all fields have input
    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("Generating your quiz... ⏳"):
            try:
                text = read_file(uploaded_file)
                # Count tokens and the cost of API call
                with get_openai_callback() as cb:
                    response = generate_evaluate_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }
                    )

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Oops! Something went wrong while reading the file. 😕")

            else:
                # Display token usage and cost
                st.success("Quiz Generated Successfully! 🎉")
                st.write(f"**Total Tokens Used:** {cb.total_tokens}")
                st.write(f"**API Call Cost:** ${cb.total_cost:.4f}")

                if isinstance(response, dict):
                    # Extract the quiz data from the response
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            # Display the review in a text area as well
                            st.text_area(label="Quiz Review 📝", value=response["review"], height=150)
                        else:
                            st.error("Error in processing the table data. 😓")
                else:
                    st.write(response)

# Add a footer with contact information or credits
st.markdown("""
    ---
    *Developed by [Abraham Owodunni](https://www.linkedin.com/in/abrahamowodunni/) | Powered by LangChain*  
    *Need help? [Contact us](abrahamowodunni) 💬*
""")
