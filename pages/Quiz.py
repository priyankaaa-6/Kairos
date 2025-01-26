# Import required libraries
import streamlit as st  # Framework for building web applications
import json  # Library for handling JSON files
import time  # Provides functions to manage and calculate time

# Page Configurations
st.set_page_config(page_title="Kairos", layout="wide")  # Sets the page title and layout configuration
st.header("AI-Powered Learning Companion - Kairos!")  # App header

# Function to fetch questions from a JSON file
def Que_Fetch(file_path):
    with open(file_path, 'r') as file:  # Open the JSON file in read mode
        quiz_data = json.load(file)  # Load and parse the JSON data
    return quiz_data  # Return the parsed data

# Function to display questions with time tracking and submission
def Que_Display(button_number, line):
    # Create session state variables for tracking time and storing answers
    state = st.session_state
    if 'start_times' not in state:  # Dictionary to store start times for questions
        state.start_times = {}
    if 'selected_option' not in state:  # Dictionary to store selected options for each question
        state.selected_option = {}
    if 'answers' not in state:  # Dictionary to store answers and time taken
        state.answers = {}

    # Key for checkbox for current question
    checkbox_key = f"Checkbox {button_number}"
    # Checkbox for showing/hiding the question
    checkbox_state = st.checkbox(f"Question number {button_number + 1}")

    # If checkbox is ticked, display the question and start timing
    if checkbox_state:
        question = line['question']  # Extract the question text
        st.write(f"**Question:** {question}")  # Display the question

        options = line['options']  # Extract options for the current question
        # Dropdown to select an option
        selected_option_key = f"Selected Option {button_number}"
        state.selected_option[selected_option_key] = st.selectbox(f"Select an option for {button_number + 1}:", options)

        # Key for tracking start time for the current question
        start_time_checkbox_key = f"Start Time Checkbox {button_number}"
        if start_time_checkbox_key not in state.start_times:
            state.start_times[start_time_checkbox_key] = None

        # Start timer when the checkbox is ticked for the first time
        if state.start_times[start_time_checkbox_key] is None:
            state.start_times[start_time_checkbox_key] = time.time()

        # Submit button to finalize the answer
        if st.button(f"Submit Ans: {button_number + 1}"):
            start_time = state.start_times[start_time_checkbox_key]  # Retrieve start time
            if start_time is not None:
                end_time = time.time()  # Record end time when the answer is submitted
                elapsed_time = end_time - start_time  # Calculate time taken to answer

                selected_option = state.selected_option[selected_option_key]  # Retrieve selected option
                st.write('Submitted')  # Confirmation message

                # Store the answer and time taken in the session state
                answer_sheet = {
                    'answer': selected_option,
                    'time_taken': elapsed_time
                }
                state.answers[button_number] = answer_sheet

                # Save the answers to a JSON file
                save_answers_to_json(state.answers)

# Function to save answers and their timings to a JSON file
def save_answers_to_json(answers):
    file_path = r"Jsons\answer_sheet.json"  # File path to save answers
    with open(file_path, "w") as json_file:  # Open the file in write mode
        json.dump(answers, json_file)  # Write the answers dictionary to the file

# Main function to run the application
def main():
    st.title("All the best")  # Application title
    quiz_data = Que_Fetch(r'Jsons\ques.json')  # Fetch questions from JSON file

    # Loop through all questions and display them
    for qnum, line in enumerate(quiz_data):
        Que_Display(qnum, line)  # Call the question display function for each question
        
    # Footer with Project Description
    st.markdown(
        """
    <div style="position: fixed; bottom: 20px; right: 20px; font-size: 12px; color: grey; text-align: right;">
        <b>About Kairos:</b> An AI-powered educational tool for PDF analysis, quiz generation, and enhanced learning.
    </div>
    """,
        unsafe_allow_html=True
    )

# Entry point for the program
if __name__ == "__main__":
    main()  # Run the main function
