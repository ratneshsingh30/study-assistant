import streamlit as st
import os
import io
import tempfile
import json
import base64
import sys

# Try to download NLTK data on startup
try:
    import nltk_setup
    nltk_setup.download_nltk_data()
except Exception as e:
    st.warning(f"NLTK setup warning: {e}")

# Check for API keys
import check_api_keys
has_openai_key = check_api_keys.check_api_keys()

# Import application modules
from utils.transcription import get_youtube_transcript, transcribe_audio
from utils.file_processor import process_file
from utils.content_processor import (
    get_summary, 
    get_resources, 
    generate_study_guide, 
    generate_quiz,
    extract_main_topics
)
from utils.personal_insight import process_profile_data
from utils.export_utils import create_export_section

# Set page config
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'resources' not in st.session_state:
    st.session_state.resources = None
if 'study_guide' not in st.session_state:
    st.session_state.study_guide = None
if 'quiz' not in st.session_state:
    st.session_state.quiz = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'main_topic' not in st.session_state:
    st.session_state.main_topic = ""
if 'personalized_insights' not in st.session_state:
    st.session_state.personalized_insights = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'total_steps' not in st.session_state:
    st.session_state.total_steps = 5


def reset_session():
    """Reset session state variables to initial values"""
    st.session_state.input_text = ""
    st.session_state.summary = None
    st.session_state.resources = None
    st.session_state.study_guide = None
    st.session_state.quiz = None
    st.session_state.is_processing = False
    st.session_state.processing_complete = False
    st.session_state.main_topic = ""
    st.session_state.personalized_insights = None
    st.session_state.current_step = 0
    st.rerun()


def process_input():
    """Process user input and generate study materials"""
    st.session_state.is_processing = True
    st.session_state.processing_complete = False
    
    # Update the UI
    st.rerun()


def progress_step():
    """Increment the progress step"""
    st.session_state.current_step += 1
    if st.session_state.current_step > st.session_state.total_steps:
        st.session_state.current_step = st.session_state.total_steps
    

def display_header():
    """Display the app header"""
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("# 🎓")
    with col2:
        st.title("AI Study Assistant")
        st.write("Turn any lecture or topic into a complete learning kit.")


def display_input_section():
    """Display the input options section"""
    st.subheader("📥 Input")
    
    # Create tabs for different input types
    input_tab, youtube_tab, upload_tab = st.tabs(["Type Topic", "YouTube URL", "Upload File/Audio"])
    
    with input_tab:
        manual_input = st.text_area(
            "Enter a topic or paste text content:",
            height=150,
            key="manual_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            generate_button = st.button("Generate Study Kit", type="primary", key="generate_text")
        
        if generate_button and manual_input:
            st.session_state.input_text = manual_input
            st.session_state.main_topic = extract_main_topics(manual_input)
            process_input()
    
    with youtube_tab:
        youtube_url = st.text_input(
            "Enter a YouTube video URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            key="youtube_url"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            process_youtube_button = st.button("Process YouTube", type="primary", key="process_youtube")
        
        if process_youtube_button and youtube_url:
            with st.spinner("Extracting transcript from YouTube..."):
                transcript_result = get_youtube_transcript(youtube_url)
                
                if transcript_result["success"]:
                    st.session_state.input_text = transcript_result["transcript"]
                    st.session_state.main_topic = extract_main_topics(st.session_state.input_text)
                    process_input()
                else:
                    st.error(f"Error: {transcript_result['error']}")
    
    with upload_tab:
        upload_col1, upload_col2 = st.columns(2)
        
        with upload_col1:
            upload_label = "Upload a document (PDF, DOCX, PPTX, TXT):"
            allowed_types = ["pdf", "docx", "pptx", "txt"]
            uploaded_file = st.file_uploader(
                upload_label,
                type=allowed_types,
                key="file_upload"
            )
            
            if uploaded_file is not None:
                file_process_button = st.button("Process Document", type="primary", key="process_file")
                
                if file_process_button:
                    with st.spinner("Processing document..."):
                        result = process_file(uploaded_file)
                        
                        if result["success"]:
                            st.session_state.input_text = result["text"]
                            st.session_state.main_topic = extract_main_topics(st.session_state.input_text)
                            process_input()
                        else:
                            st.error(f"Error: {result['error']}")
        
        with upload_col2:
            audio_file = st.file_uploader(
                "Upload an audio lecture (MP3, WAV, M4A):",
                type=["mp3", "wav", "m4a"],
                key="audio_upload"
            )
            
            if audio_file is not None:
                audio_process_button = st.button("Transcribe Audio", type="primary", key="process_audio")
                
                if audio_process_button:
                    with st.spinner("Transcribing audio... This may take a while."):
                        # Convert to BytesIO
                        audio_bytes = io.BytesIO(audio_file.getvalue())
                        result = transcribe_audio(audio_bytes)
                        
                        if result["success"]:
                            st.session_state.input_text = result["transcript"]
                            st.session_state.main_topic = extract_main_topics(st.session_state.input_text)
                            process_input()
                        else:
                            st.error(f"Error: {result['error']}")


def display_personalization_section():
    """Display personalization options"""
    # Only show this section if we have generated content
    if not st.session_state.processing_complete:
        return
    
    with st.expander("🧠 Personalize Learning (Optional)"):
        st.write("Upload your resume or LinkedIn profile for personalized learning insights.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            resume_file = st.file_uploader(
                "Upload your resume (PDF, DOCX):",
                type=["pdf", "docx"],
                key="resume_upload"
            )
        
        with col2:
            linkedin_file = st.file_uploader(
                "Upload LinkedIn profile (PDF, DOCX, TXT):",
                type=["pdf", "docx", "txt"],
                key="linkedin_upload"
            )
            
            # or enter LinkedIn URL
            linkedin_url = st.text_input(
                "Or enter your LinkedIn profile URL:",
                placeholder="https://www.linkedin.com/in/...",
                key="linkedin_url"
            )
        
        personalize_button = st.button("Generate Personalized Insights", key="personalize")
        
        if personalize_button:
            if resume_file or linkedin_file or linkedin_url:
                with st.spinner("Generating personalized learning insights..."):
                    linkedin_data = linkedin_file if linkedin_file else linkedin_url
                    
                    insights_result = process_profile_data(
                        resume_file, 
                        linkedin_data, 
                        st.session_state.input_text
                    )
                    
                    if insights_result["success"]:
                        st.session_state.personalized_insights = insights_result["insights"]
                        st.success("Personalized insights generated!")
                        st.rerun()
                    else:
                        st.error(f"Error: {insights_result['error']}")
            else:
                st.warning("Please provide either a resume, LinkedIn profile, or LinkedIn URL.")


def display_processing_screen():
    """Display processing screen with progress indicators"""
    if not st.session_state.is_processing:
        return
    
    st.subheader("⚙️ Generating Your Study Kit...")
    
    progress_bar = st.progress(0)
    
    # Update progress based on current step
    progress_value = st.session_state.current_step / st.session_state.total_steps
    progress_bar.progress(progress_value)
    
    # Show step indicators
    if st.session_state.current_step == 0:
        # Step 1: Extracting Key Concepts
        with st.spinner("Extracting Key Concepts..."):
            st.session_state.summary = get_summary(st.session_state.input_text)
            progress_step()
            st.rerun()
    
    elif st.session_state.current_step == 1:
        # Step 2: Finding Study Resources
        st.info("Key concepts extracted!")
        with st.spinner("Finding Study Resources..."):
            st.session_state.resources = get_resources(st.session_state.main_topic)
            progress_step()
            st.rerun()
    
    elif st.session_state.current_step == 2:
        # Step 3: Generating Study Guide
        st.info("Study resources found!")
        with st.spinner("Generating Study Guide..."):
            st.session_state.study_guide = generate_study_guide(st.session_state.input_text)
            progress_step()
            st.rerun()
    
    elif st.session_state.current_step == 3:
        # Step 4: Preparing Quiz
        st.info("Study guide generated!")
        with st.spinner("Preparing Quiz Questions..."):
            st.session_state.quiz = generate_quiz(st.session_state.input_text)
            progress_step()
            st.rerun()
    
    elif st.session_state.current_step == 4:
        # Step 5: Finalizing
        st.info("Quiz prepared!")
        with st.spinner("Finalizing your study kit..."):
            # Final step
            progress_step()
            st.session_state.is_processing = False
            st.session_state.processing_complete = True
            st.rerun()


def display_results():
    """Display the generated study materials"""
    if not st.session_state.processing_complete:
        return
    
    st.subheader(f"📚 Study Kit: {st.session_state.main_topic}")
    
    # Create tabs for different sections of the study kit
    summary_tab, resources_tab, study_guide_tab, quiz_tab, insights_tab, export_tab = st.tabs([
        "Key Concepts", "Resources", "Study Guide", "Quiz", "Personal Insights", "Export"
    ])
    
    with summary_tab:
        st.subheader("🧠 Key Concepts Summary")
        if st.session_state.summary and st.session_state.summary["success"]:
            st.markdown(st.session_state.summary["summary"])
        else:
            st.error("Failed to generate summary.")
    
    with resources_tab:
        st.subheader("📚 Recommended Resources")
        if st.session_state.resources and st.session_state.resources["success"]:
            resources = st.session_state.resources.get("resources", {}).get("resources", [])
            
            for i, resource in enumerate(resources):
                with st.expander(f"{resource['title']}"):
                    st.write(f"**Description:** {resource['description']}")
                    st.write(f"**Type:** {resource.get('type', 'Resource')}")
                    st.markdown(f"[Open Resource]({resource['url']})")
        else:
            st.error("Failed to find resources.")
    
    with study_guide_tab:
        st.subheader("📝 Study Guide & Flashcards")
        if st.session_state.study_guide and st.session_state.study_guide["success"]:
            study_guide = st.session_state.study_guide.get("study_guide", {}).get("study_guide", {})
            
            # Display key terms
            with st.expander("Key Terms and Definitions", expanded=True):
                terms = study_guide.get("key_terms", [])
                for term in terms:
                    st.markdown(f"**{term['term']}**: {term['definition']}")
            
            # Display important concepts
            with st.expander("Important Concepts", expanded=True):
                concepts = study_guide.get("important_concepts", [])
                for i, concept in enumerate(concepts):
                    st.markdown(f"**Concept {i+1}:** {concept}")
            
            # Display flashcards
            with st.expander("Flashcards", expanded=True):
                flashcards = study_guide.get("flashcards", [])
                
                for i, card in enumerate(flashcards):
                    # Create a unique key for each flashcard
                    card_key = f"flashcard_{i}"
                    
                    # Create a container for the flashcard
                    card_container = st.container()
                    
                    # Create columns for the flashcard
                    question_col, answer_col = st.columns(2)
                    
                    with question_col:
                        st.info(f"**Question {i+1}:** {card['question']}")
                    
                    with answer_col:
                        # Create a checkbox to toggle the answer visibility
                        show_answer = st.checkbox(f"Show Answer {i+1}", key=card_key)
                        
                        if show_answer:
                            st.success(f"**Answer:** {card['answer']}")
        else:
            st.error("Failed to generate study guide.")
    
    with quiz_tab:
        st.subheader("❓ Practice Quiz")
        if st.session_state.quiz and st.session_state.quiz["success"]:
            # Handle different quiz format structures
            quiz_data = st.session_state.quiz.get("quiz", None)
            if isinstance(quiz_data, dict) and "quiz" in quiz_data:
                quiz = quiz_data["quiz"]
            elif isinstance(quiz_data, list):
                quiz = quiz_data
            else:
                quiz = []
            
            # Create a form for the quiz
            with st.form(key="quiz_form"):
                correct_answers = 0
                total_questions = len(quiz)
                
                for i, question in enumerate(quiz):
                    st.markdown(f"**Question {i+1}:** {question['question']}")
                    
                    # Radio buttons for answer options
                    options = question.get("options", {})
                    answer_key = f"q{i}_answer"
                    user_answer = st.radio(
                        "Select your answer:",
                        options.keys(),
                        key=answer_key,
                        index=None
                    )
                    
                    # Show options
                    for opt_key, opt_value in options.items():
                        st.markdown(f"**{opt_key}:** {opt_value}")
                    
                    st.markdown("---")
                
                submit_button = st.form_submit_button("Check Answers")
                
                if submit_button:
                    for i, question in enumerate(quiz):
                        user_answer = st.session_state.get(f"q{i}_answer")
                        correct_answer = question.get("correct_answer")
                        
                        if user_answer == correct_answer:
                            correct_answers += 1
                    
                    # Display results
                    score_percentage = (correct_answers / total_questions) * 100
                    st.success(f"You got {correct_answers} out of {total_questions} correct ({score_percentage:.1f}%)!")
                    
                    # Display correct answers
                    st.subheader("Correct Answers:")
                    for i, question in enumerate(quiz):
                        user_answer = st.session_state.get(f"q{i}_answer")
                        correct_answer = question.get("correct_answer")
                        
                        if user_answer != correct_answer:
                            st.warning(
                                f"Question {i+1}: You selected {user_answer if user_answer else 'nothing'}, " 
                                f"correct answer is {correct_answer}."
                            )
        else:
            st.error("Failed to generate quiz questions.")
    
    with insights_tab:
        st.subheader("🔍 Personalized Learning Insights")
        if st.session_state.personalized_insights:
            insights = st.session_state.personalized_insights
            
            # Display career relevance
            with st.expander("Career Relevance", expanded=True):
                st.markdown(insights.get("career_relevance", "No career relevance information available."))
            
            # Display skill gaps
            with st.expander("Skill Development Recommendations", expanded=True):
                st.markdown(insights.get("skill_gaps", "No skill development recommendations available."))
            
            # Display learning path
            with st.expander("Suggested Learning Path", expanded=True):
                st.markdown(insights.get("learning_path", "No learning path recommendations available."))
            
            # Display project ideas
            with st.expander("Practical Project Ideas", expanded=True):
                st.markdown(insights.get("project_ideas", "No project ideas available."))
        else:
            st.info(
                "No personalized insights available. "
                "Upload your resume or LinkedIn profile in the 'Personalize Learning' section above."
            )
    
    with export_tab:
        st.subheader("💾 Export Study Materials")
        # Prepare results for export
        results = {
            "topic": st.session_state.main_topic,
            "summary": st.session_state.summary.get("summary") if st.session_state.summary else "",
            "resources": st.session_state.resources.get("resources", {}).get("resources", []) if st.session_state.resources else []
        }
        
        # Handle study guide format
        if st.session_state.study_guide and st.session_state.study_guide["success"]:
            study_guide_data = st.session_state.study_guide.get("study_guide", {})
            if isinstance(study_guide_data, dict) and "study_guide" in study_guide_data:
                results["study_guide"] = study_guide_data["study_guide"]
            else:
                results["study_guide"] = study_guide_data
        else:
            results["study_guide"] = {}
        
        # Handle quiz format
        if st.session_state.quiz and st.session_state.quiz["success"]:
            quiz_data = st.session_state.quiz.get("quiz", None)
            if isinstance(quiz_data, dict) and "quiz" in quiz_data:
                results["quiz"] = quiz_data["quiz"]
            elif isinstance(quiz_data, list):
                results["quiz"] = quiz_data
            else:
                results["quiz"] = []
        else:
            results["quiz"] = []
        
        # Add personalized insights if available
        if st.session_state.personalized_insights:
            results["personalized_insights"] = st.session_state.personalized_insights
        
        # Create export section
        create_export_section(results)


def display_sidebar():
    """Display the sidebar with options and information"""
    with st.sidebar:
        st.header("📋 Options")
        
        # Reset button
        if st.button("Start New Study Kit", key="reset"):
            reset_session()
        
        st.divider()
        
        # App info
        st.header("ℹ️ About")
        st.write(
            "AI Study Assistant helps you transform lectures, textbooks, and other learning "
            "materials into comprehensive study kits."
        )
        
        st.divider()
        
        # Credits
        st.write("**AI Study Assistant** © 2025")
        st.markdown(
            "Powered by OpenAI + Hugging Face"
        )


def main():
    """Main function to run the Streamlit app"""
    display_header()
    display_sidebar()
    
    if not st.session_state.is_processing and not st.session_state.processing_complete:
        display_input_section()
    
    if st.session_state.is_processing:
        display_processing_screen()
    
    if st.session_state.processing_complete:
        display_results()
        display_personalization_section()


if __name__ == "__main__":
    main()