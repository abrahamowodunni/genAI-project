import os
import json
import traceback
import pandas as pd
from io import BytesIO
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

    Whether you're a teacher looking to craft the perfect quiz or a student preparing for your next exam, this tool has you covered. 🎓

    **For Teachers:** Generate tailored multiple-choice questions (MCQs) to inspire your quizzes and exams. Just upload your content, set the parameters, and let the generator do the rest! 📝

    **For Students:** Use this app to create customized quizzes that match your study needs. Revise effectively and test your knowledge with questions that challenge you at just the right level. 📚

    Ready to get started? Upload your file, adjust the settings, and create your quiz now! 🎯
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
                    
                    # Validate table_data before creating the DataFrame
                    if table_data and isinstance(table_data, list) and all(isinstance(row, dict) for row in table_data):
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1
                        st.table(df)
                        # Display the review in a text area as well
                        st.text_area(label="Quiz Review 📝", value=response["review"], height=150)
                        
                        # Move the download button outside the form
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Quiz as CSV 📥",
                            data=csv,
                            file_name='quiz.csv',
                            mime='text/csv',
                        )
                    else:
                        st.error("Error in processing the table data. 😓 Invalid or empty data.")
                else:
                    st.error("Quiz data not found in the response. 😕")
            else:
                st.write(response)

# Add a footer with contact information or credits
st.markdown("""
    ---
    *Developed by [Abraham Owodunni](https://github.com/abrahamowodunni/genAI-project) | Powered by LangChain*  
    *Need help? [Contact us](mailto:abrahamowodunni@gmail.com) 💬*
""")
