import streamlit as st
import json

# Load data from JSON file
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

SKILLS_INFO = data["skills_info"]
TRAIT_QUESTIONS = data["trait_questions"]
LEVEL_QUESTIONS = data["level_questions"]
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
        st.session_state['level_determined'] = False
        st.session_state['recommended_track'] = None

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
    track_abbr = track[:3].upper()  # Take the first 3 letters of the track name
    
    # Map level to a numeric value
    level_mapping = {"Beginner": "1", "Intermediate": "2", "Advanced": "3"}
    level_code = level_mapping.get(level, "0")  # Default to "0" if level is not found
    
    # Map language to a letter
    language_mapping = {"Arabic": "A", "English": "E"}
    language_code = language_mapping.get(language, "U")  # Default to "U" (Unknown) if language is not found
    
    # Combine all parts into the result code
    result_code = f"{track_abbr}{level_code}{language_code}"
    return result_code

def show_results():
    """Display the results of the assessment."""
    ranked_skills = sorted(st.session_state['score'].items(), key=lambda item: item[1], reverse=True)
    st.session_state['results'] = ranked_skills
    
    if ranked_skills:
        top_skill, _ = ranked_skills[0]
        skill_data = SKILLS_INFO[top_skill]
        
        # Determine level and language based on user's session state
        level = st.session_state.get('level', 'Beginner')
        language = st.session_state.get('language', 'Arabic')
        
        # Find recommended course
        recommended_course = next((course for course in COURSES if course["track"] == top_skill and course["level"] == level and course["language"] == language), None)
        
        # Generate result code
        result_code = generate_course_hint(top_skill, level, language)
        
        # Use inline styles for the results section
        st.markdown(
            f"""
            <div class='results-section'>
                <h2 style='font-family: Cairo, sans-serif;'>التراك المقترح ليك : <span style='color: tomato;'>{top_skill}</span></h2>
                <h3 style='font-family: Cairo, sans-serif;'>الكورس اللى هتبدأ فيه:</h3>
                <p>- {recommended_course['name'] if recommended_course else 'No course found'}</p>
                <h3 style='font-family: Cairo, sans-serif;'> حاجات هتساعدك جنب الكورس:</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Display additional resources
        for resource_type in ["Books", "Podcasts"]:
            if skill_data["resources"].get(resource_type):
                st.markdown(
                    f"<div style='font-family: Cairo, sans-serif; font-size: 1.2em; direction: rtl;'>- {skill_data['resources'][resource_type][0]} ({resource_type})</div>",
                    unsafe_allow_html=True
                )
        
        # Display the result code
        st.markdown(
            f"""
            <div class='results-section'>
                <h3 style='font-family: Cairo, sans-serif;'>رمز الكورس:</h3>
                <p style='font-family: Cairo, sans-serif; font-size: 1.4em;'>{result_code}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Main Application
def main():
    """Main function to run the Streamlit app."""
    initialize_session_state()
    apply_custom_styles()

    # Add logo
    st.markdown(
        """
        <div class="logo-container">
            <img src="https://i.imgur.com/L5vmEv9.png" alt="App Logo">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(f"<h2 class='h2' style='text-align: center;'>Skill Path Assessment</h2>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle-text'> اختار الاجابات اللى تعبر عنك فى كل سؤال عشان نحدد التراك المناسب ليك  </p>", unsafe_allow_html=True)

    # Add a separating line
    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

    # Calculate total number of questions (trait + background)
    total_questions = len(TRAIT_QUESTIONS) + 2  # 2 additional questions for work nature and language

    if not st.session_state['test_completed']:
        # Display trait questions
        question_keys = list(TRAIT_QUESTIONS.keys())
        current_question_key = question_keys[st.session_state['question_index']]
        q_data = TRAIT_QUESTIONS[current_question_key]

        responses_list = display_question(q_data)

        # Add "التالي" and "السابق" buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("التالي", key=f"next_button_{st.session_state['question_index']}"):
                if responses_list:
                    update_scores(responses_list, current_question_key)
                    if st.session_state['question_index'] < len(TRAIT_QUESTIONS) - 1:
                        st.session_state['question_index'] += 1
                    else:
                        st.session_state['test_completed'] = True
                    st.rerun()
                else:
                    st.warning("برجاء اختيار إجابة واحدة على الأقل قبل المتابعة.")
        with col2:
            if st.session_state['question_index'] > 0:
                if st.button("السابق", key=f"prev_button_{st.session_state['question_index']}"):
                    st.session_state['question_index'] -= 1
                    st.rerun()

        # Update progress bar
        progress = (st.session_state['question_index'] + 1) / total_questions
        st.progress(progress)
        st.write(f"Question {st.session_state['question_index'] + 1} of {total_questions}")

    elif st.session_state['test_completed'] and not st.session_state.get('background_completed', False):
        # Display work nature question
        st.markdown("<h2 style='text-align: center;'>أسئلة إضافية</h2>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle-text'>من فضلك أجب على هذه الأسئلة لتحديد مستوى الخبرة واللغة المناسبة لك.</p>", unsafe_allow_html=True)

        # Ask work nature question
        work_nature_data = TRAIT_QUESTIONS["Work Nature"]
        question = work_nature_data["question"]
        options = work_nature_data["options"]
        st.markdown(f"<div class='question-text'>{question}</div>", unsafe_allow_html=True)
        
        selected_option = st.radio("", options, key="work_nature")
        
        # Store the selected response in session state
        for option, value in work_nature_data["responses"]:
            if option == selected_option:
                st.session_state['work_nature'] = value
                break

        # Ask language preference and usage questions
        language_data = TRAIT_QUESTIONS["Language"]
        language_usage_data = TRAIT_QUESTIONS["Language Usage"]

        st.markdown(f"<div class='question-text'>{language_data['question']}</div>", unsafe_allow_html=True)
        selected_language = st.radio("", language_data["options"], key="language_preference")
        
        st.markdown(f"<div class='question-text'>{language_usage_data['question']}</div>", unsafe_allow_html=True)
        selected_language_usage = st.radio("", language_usage_data["options"], key="language_usage")

        # Store the selected responses in session state
        for option, value in language_data["responses"]:
            if option == selected_language:
                st.session_state['language'] = value
                break

        for option, value in language_usage_data["responses"]:
            if option == selected_language_usage:
                st.session_state['language_usage'] = value
                break

        # Add a button to submit background questions
        if st.button("إرسال الأسئلة الإضافية"):
            st.session_state['background_completed'] = True
            st.rerun()

    elif st.session_state.get('background_completed', False) and not st.session_state.get('level_determined', False):
        # Determine the fitting track
        ranked_skills = sorted(st.session_state['score'].items(), key=lambda item: item[1], reverse=True)
        if ranked_skills:
            top_skill, _ = ranked_skills[0]
            st.session_state['recommended_track'] = top_skill

        # Display level determination questions
        st.markdown("<h2 style='text-align: center;'>تحديد المستوى</h2>", unsafe_allow_html=True)
        st.markdown(f"<p class='subtitle-text'>من فضلك أجب على هذه الأسئلة لتحديد مستواك في مجال {st.session_state['recommended_track']}.</p>", unsafe_allow_html=True)

        # Ask level determination questions
        level_responses = []
        for q_key, q_data in LEVEL_QUESTIONS.items():
            question = q_data["question"].replace("[Track Name]", st.session_state['recommended_track'])
            options = q_data["options"]
            st.markdown(f"<div class='question-text'>{question}</div>", unsafe_allow_html=True)
            
            selected_option = st.radio("", options, key=f"level_{q_key}")
            
            # Store the selected response
            for option, value in q_data["responses"]:
                if option == selected_option:
                    level_responses.append(value)
                    break

        # Calculate the final level based on responses
        if level_responses:
            # Assign weights to responses (Beginner: 1, Intermediate: 2, Advanced: 3)
            level_scores = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
            total_score = sum(level_scores[response] for response in level_responses)
            average_score = total_score / len(level_responses)

            # Determine the final level
            if average_score < 1.5:
                st.session_state['level'] = "Beginner"
            elif average_score < 2.5:
                st.session_state['level'] = "Intermediate"
            else:
                st.session_state['level'] = "Advanced"

        # Add a button to submit level determination
        if st.button("إرسال تحديد المستوى"):
            st.session_state['level_determined'] = True
            st.rerun()

    elif st.session_state.get('level_determined', False):
        show_results()
        st.markdown("<div class='restart-button'></div>", unsafe_allow_html=True)
        if st.button("إعادة الاختبار"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()