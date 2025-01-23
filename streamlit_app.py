import streamlit as st
import json

# Load data from JSON file
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

SKILLS_INFO = data["skills_info"]
TRAIT_QUESTIONS = data["trait_questions"]
BACKGROUND_QUESTIONS = data["background_questions"]
COURSES = data["courses"]

# Helper Functions
def initialize_session_state():
    """Initialize session state variables."""
    if 'test_completed' not in st.session_state:
        st.session_state['test_completed'] = False
        st.session_state['question_index'] = 0
        st.session_state['score'] = {skill: 0 for skill in SKILLS_INFO.keys()}
        st.session_state['results'] = []
        st.session_state['level'] = "Beginner"  # Default level
        st.session_state['language'] = "Arabic"  # Default language
        st.session_state['background_completed'] = False

def apply_custom_styles():
    """Apply custom CSS styles."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
        html, body, [class*="st"] {
            font-family: 'Cairo', sans-serif;
            direction: rtl; /* Set direction to right-to-left */
        }
        .stRadio > label {
            text-align: right;
        }
        .stRadio > div > div > div {
            display: flex;
            flex-direction: row-reverse;
        }
        .logo-container {
            text-align: center;
            padding-bottom: 20px;
        }
        .logo-container img {
            max-width: 200px;
            height: auto;
        }
        .question-text {
            font-size: 1.8em; /* Larger font size for questions */
            font-weight: bold;
            color: #2c3e50; /* Dark blue color */
            margin-bottom: 30px; /* Add more space below the question */
            text-align: right; /* Align text to the right */
        }
        h2 {
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 10px;
            font-family: 'Cairo', sans-serif;
        }
        h3 {
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 8px;
            font-family: 'Cairo', sans-serif;
            color: Tomato; /* Tomato color for track name */
        }
        .option-button {
            display: block;
            margin: 5px auto;
            padding: 2px 2px;
            border: 2px solid #f1c40f;
            border-radius: 5px;
            background-color: white;
            color: black;
            cursor: pointer;
            text-align: right;
        }
        /* Larger font size for checkbox options */
        div.stCheckbox > label {
            text-align: right;
            font-size: 1.3em; /* Increased font size */
            padding: 4px 0; /* Reverted padding to original state */
        }
        div.stCheckbox > div > div > div {
            display: flex;
            flex-direction: row-reverse;
        }
        div.stCheckbox > div > div > div > div:nth-child(1) {
            margin-left: 20px;
        }
        /* Style the buttons */
        .stButton > button {
            font-family: 'Cairo', sans-serif;
            font-size: 1.3em; /* Larger font size for buttons */
            font-weight: bold; /* Bold text for buttons */
            background-color: #f1c40f;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            margin: 10px auto;
            width: 150px; /* Fixed width for both buttons */
            display: block;
        }
        /* Change hover color of the buttons */
        .stButton > button:hover {
            color: black !important;
        }
        /* Center the buttons */
        .stButton {
            text-align: center;
        }
        /* Add margin to the "إعادة الاختبار" button */
        .restart-button {
            margin-top: 30px;
        }
        /* Add a separating line */
        .separator {
            border-top: 2px solid #f1c40f;
            margin: 20px 0;
        }
        /* Style for the subtitle */
        .subtitle-text {
            font-size: 1.3em; /* Larger font size for subtitle */
            text-align: center;
            margin-bottom: 20px;
        }
        /* Add space between recommended track text and results */
        .results-section {
            margin-top: 20px;
        }
        /* Larger text for blue-highlighted sections */
        .results-section h3, .results-section p {
            font-size: 1.4em; /* Larger font size */
        }
        </style>
    """, unsafe_allow_html=True)

def display_question(q_data):
    """Display the current question and options."""
    question = q_data["question"]
    options = q_data["options"]
    st.markdown(f"<div class='question-text'>{question}</div>", unsafe_allow_html=True)
    
    responses_list = []
    for i, option in enumerate(options):
        selected = st.checkbox(option, key=f"option_{st.session_state['question_index']}_{i}")
        if selected:
            responses_list.append((option, q_data["responses"][i][1]))
    
    return responses_list

def update_scores(responses_list, current_question_key):
    """Update scores based on user responses."""
    weight = TRAIT_QUESTIONS[current_question_key].get("weight", 1)
    for _, skill in responses_list:
        st.session_state['score'][skill] += weight

def generate_course_hint(track, level, language):
    """Generate a result code based on track, level, and language."""
    # Generate 3-letter abbreviation for the track
   