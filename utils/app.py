import streamlit as st
import re
import os
from utils.content_processor import process_input
from utils.export_utils import create_export_section
import json

# Set custom theme and styling
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 2.5rem !important;
        font-weight: 700;
        color: #4f8bf9;
        margin-bottom: 1rem;
        text-align: center;
        padding: 0.5rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    .section-header {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 1.5rem !important;
        font-weight: 600;
        color: #1f77b4;
        margin-top: 1.5rem;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid #e6e9ef;
    }
    
    .resource-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        border-left: 4px solid #4CAF50;
    }
    
    .key-point {
        font-weight: bold;
        color: #2c3e50;
        background-color: #f8f9fa;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #3498db;
    }
    
    .example-text {
        background-color: #eaf2fd;
        padding: 0.8rem;
        border-radius: 6px;
        margin-top: 0.5rem;
        font-style: italic;
        border-left: 3px solid #9b59b6;
    }
    
    .term-definition {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 5px;
        line-height: 1.6;
        border-left: 3px solid #f39c12;
    }
    
    .concept-item {
        background-color: #f8f9fa;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
        border-left: 3px solid #27ae60;
    }
    
    .concept-number {
        font-weight: bold;
        color: #27ae60;
        margin-right: 0.5rem;
    }
    
    .flashcard-q {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 8px 8px 0 0;
        border-top: 3px solid #3498db;
    }
    
    .flashcard-a {
        background-color: #eafaf1;
        padding: 1rem;
        border-radius: 0 0 8px 8px;
        border-bottom: 3px solid #2ecc71;
    }
    
    .stButton>button {
        background-color: #4f8bf9;
        color: white;
    }
    
    .tab-content {
        padding: 1.5rem;
        border: 1px solid #e6e9ef;
        border-radius: 0 0 5px 5px;
    }
    
    .insight-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .insight-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .insight-section h4 {
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-weight: 600;
        border-bottom: 1px solid #e6e9ef;
        padding-bottom: 0.3rem;
    }
    
    .insight-section p {
        margin-top: 0.5rem;
        line-height: 1.6;
    }
    
    .definition-box {
        background-color: #f5f8fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2980b9;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .diagram-ref {
        background-color: #f0f7fb;
        padding: 0.8rem;
        border-radius: 6px;
        margin-top: 0.5rem;
        border-left: 3px solid #3498db;
        color: #2c3e50;
        font-size: 0.9rem;
    }
    
    .diagram-ref i {
        margin-right: 0.5rem;
        color: #3498db;
    }
</style>
""", unsafe_allow_html=True)

# Set up logging for debugging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import personalized insights module
from utils.personal_insight import process_profile_data

# Check if OpenAI API key is available and provide info about alternatives
openai_api_key = os.environ.get("OPENAI_API_KEY")

if not openai_api_key:
    st.warning("⚠️ OpenAI API key not found. Using free AI APIs as fallback for generating study materials.")
    logger.warning("OpenAI API key not found. Will use free AI APIs.")
else:
    logger.info("OpenAI API key found. Will try OpenAI first, with free AI APIs as fallback.")

# Function to check if URL is a valid YouTube URL
def is_youtube_url(url):
    youtube_regex = r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'
    return bool(re.match(youtube_regex, url))

# Initialize session state
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'error' not in st.session_state:
    st.session_state.error = None
if 'show_answers' not in st.session_state:
    st.session_state.show_answers = {}
if 'personal_insights' not in st.session_state:
    st.session_state.personal_insights = None

def reset_app():
    """Reset the app to its initial state"""
    st.session_state.processing_complete = False
    st.session_state.results = None
    st.session_state.processing = False
    st.session_state.error = None
    st.session_state.show_answers = {}
    st.session_state.personal_insights = None
    st.rerun()

# Header section
st.markdown('<h1 class="main-header">🎓 AI Study Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; margin-bottom: 2rem;">Turn any lecture or topic into a complete learning kit in minutes.</p>', unsafe_allow_html=True)

# Main content
if not st.session_state.processing_complete:
    # Input options
    st.subheader("Choose Your Input Method")
    
    tab1, tab2, tab3, tab4 = st.tabs(["✏️ Enter Topic", "🔗 YouTube URL", "🔊 Upload Audio", "📄 Upload Files"])
    
    with tab1:
        text_input = st.text_area("Enter a topic or paste lecture text:", height=150, 
                                  placeholder="E.g., Photosynthesis process in plants...")
        text_submit = st.button("Generate Study Kit", key="text_submit")
        
        if text_submit and text_input.strip():
            st.session_state.processing = True
            with st.spinner("Processing your text..."):
                results = process_input("text", text_input)
                if results["success"]:
                    st.session_state.results = results
                    st.session_state.processing_complete = True
                    st.rerun()
                else:
                    st.session_state.error = results["error"]
                    st.error(f"Error: {results['error']}")
        elif text_submit:
            st.warning("Please enter some text first.")
    
    with tab2:
        youtube_url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")
        youtube_submit = st.button("Generate Study Kit", key="youtube_submit")
        
        if youtube_submit and youtube_url.strip():
            if is_youtube_url(youtube_url):
                st.session_state.processing = True
                with st.spinner("Processing YouTube video..."):
                    results = process_input("youtube", youtube_url)
                    if results["success"]:
                        st.session_state.results = results
                        st.session_state.processing_complete = True
                        st.rerun()
                    else:
                        st.session_state.error = results["error"]
                        st.error(f"Error: {results['error']}")
            else:
                st.warning("Please enter a valid YouTube URL.")
        elif youtube_submit:
            st.warning("Please enter a YouTube URL first.")
    
    with tab3:
        uploaded_file = st.file_uploader("Upload audio file (MP3):", type=["mp3"])
        audio_submit = st.button("Generate Study Kit", key="audio_submit")
        
        if audio_submit and uploaded_file is not None:
            st.session_state.processing = True
            with st.spinner("Transcribing and processing audio..."):
                results = process_input("audio", uploaded_file)
                if results["success"]:
                    st.session_state.results = results
                    st.session_state.processing_complete = True
                    st.rerun()
                else:
                    st.session_state.error = results["error"]
                    st.error(f"Error: {results['error']}")
        elif audio_submit:
            st.warning("Please upload an audio file first.")
            
    with tab4:
        st.write("Upload lecture notes, course materials, or multiple files for processing:")
        
        file_type_options = [
            "Document (.pdf, .docx, .pptx)",
            "Video (.mp4, .mov)",
            "Code (.py, .ipynb)",
            "Multiple Files (.zip)"
        ]
        
        file_type_choice = st.radio("Select file type:", file_type_options)
        
        # Set the file types based on the user's selection
        if "Document" in file_type_choice:
            allowed_types = ["pdf", "docx", "pptx"]
            upload_label = "Upload document files:"
        elif "Video" in file_type_choice:
            allowed_types = ["mp4", "mov", "avi", "mkv"]
            upload_label = "Upload video file (will extract audio):"
        elif "Code" in file_type_choice:
            allowed_types = ["py", "ipynb", "txt"]
            upload_label = "Upload code or text files:"
        elif "Multiple" in file_type_choice:
            allowed_types = ["zip"]
            upload_label = "Upload ZIP archive (containing multiple files):"
        
        uploaded_file = st.file_uploader(upload_label, type=allowed_types)
        
        file_submit = st.button("Generate Study Kit", key="file_submit")
        
        if file_submit and uploaded_file is not None:
            st.session_state.processing = True
            
            # Determine file extension
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            with st.spinner(f"Processing {file_extension.upper()} file..."):
                # Process file with appropriate message
                if file_extension == "zip":
                    status_message = "Extracting and processing files from ZIP archive..."
                elif file_extension in ["mp4", "mov", "avi", "mkv"]:
                    status_message = "Extracting audio from video and transcribing..."
                elif file_extension in ["docx", "pptx", "pdf"]:
                    status_message = f"Extracting text from {file_extension.upper()} document..."
                else:
                    status_message = f"Processing {file_extension.upper()} file..."
                
                st.info(status_message)
                results = process_input("file", uploaded_file)
                
                if results["success"]:
                    st.session_state.results = results
                    st.session_state.processing_complete = True
                    st.rerun()
                else:
                    st.session_state.error = results["error"]
                    st.error(f"Error: {results['error']}")
        elif file_submit:
            st.warning("Please upload a file first.")

else:
    # Display results
    results = st.session_state.results
    
    # Add a reset button at the top
    if st.button("Start Over", key="reset_top"):
        reset_app()
    
    # Section 1: Key Concepts Summary
    st.markdown('<h2 class="section-header">🧠 Key Concepts Summary</h2>', unsafe_allow_html=True)
    try:
        if results and "summary" in results and results["summary"]:
            st.markdown(results["summary"])
        else:
            st.info("No summary available.")
    except Exception as e:
        st.error(f"Error displaying summary: {str(e)}")
        st.info("No summary available.")
    
    # Section 2: Suggested Resources
    st.markdown('<h2 class="section-header">📚 Suggested Resources</h2>', unsafe_allow_html=True)
    try:
        if results and "resources" in results and results["resources"]:
            resources = results["resources"].get("resources", []) if isinstance(results["resources"], dict) else []
            
            if resources and isinstance(resources, list) and len(resources) > 0:
                for resource in resources:
                    if isinstance(resource, dict) and "title" in resource and "type" in resource:
                        st.markdown(f'<div class="resource-card">' +
                                  f'<h4>{resource["title"]} <small>({resource["type"]})</small></h4>' +
                                  f'<p>{resource.get("description", "")}</p>' +
                                  (f'<a href="{resource["url"]}" target="_blank">🔗 Access Resource</a>' if "url" in resource else "") +
                                  f'</div>', unsafe_allow_html=True)
            else:
                st.info("No resources details available.")
        else:
            st.info("No resources available.")
    except Exception as e:
        st.error(f"Error displaying resources: {str(e)}")
        st.info("No resources available.")
    
    # Section 3: Study Guide & Flashcards
    st.markdown('<h2 class="section-header">📝 Study Guide & Flashcards</h2>', unsafe_allow_html=True)
    
    # Handle the case where results["study_guide"] might be None or not a dictionary
    try:
        if results and "study_guide" in results and results["study_guide"]:
            # Try to get the study guide data safely
            study_guide = results["study_guide"].get("study_guide", {}) if isinstance(results["study_guide"], dict) else {}
            
            # Key Terms
            if study_guide and "key_terms" in study_guide and study_guide["key_terms"]:
                st.subheader("Key Terms")
                for term_entry in study_guide["key_terms"]:
                    if isinstance(term_entry, dict) and "term" in term_entry and "definition" in term_entry:
                        with st.expander(f"📌 {term_entry['term']}"):
                            st.markdown(f'<div class="term-definition">{term_entry["definition"]}</div>', unsafe_allow_html=True)
            
            # Important Concepts
            if study_guide and "important_concepts" in study_guide and study_guide["important_concepts"]:
                st.subheader("Important Concepts")
                for i, concept in enumerate(study_guide["important_concepts"]):
                    st.markdown(f'<div class="concept-item"><span class="concept-number">{i+1}.</span> {concept}</div>', unsafe_allow_html=True)
            
            # Flashcards
            if study_guide and "flashcards" in study_guide and study_guide["flashcards"]:
                st.subheader("Flashcards")
                for i, card in enumerate(study_guide["flashcards"]):
                    # Initialize show_answers state for this card if not present
                    if i not in st.session_state.show_answers:
                        st.session_state.show_answers[i] = False
                    
                    if isinstance(card, dict) and "question" in card and "answer" in card:
                        question = card["question"]
                        answer = card["answer"]
                        
                        col1, col2 = st.columns([5, 1])
                        with col1:
                            st.markdown(f'<div class="flashcard-q"><strong>Q:</strong> {question}</div>', unsafe_allow_html=True)
                            
                            if st.session_state.show_answers[i]:
                                st.markdown(f'<div class="flashcard-a"><strong>A:</strong> {answer}</div>', unsafe_allow_html=True)
                        
                        with col2:
                            if st.button("Reveal" if not st.session_state.show_answers[i] else "Hide", key=f"fc_{i}"):
                                st.session_state.show_answers[i] = not st.session_state.show_answers[i]
                                st.rerun()
            
            if (not study_guide or 
                "key_terms" not in study_guide or 
                "important_concepts" not in study_guide or 
                "flashcards" not in study_guide):
                st.info("Some study guide components could not be generated.")
        else:
            st.info("No study guide available.")
    except Exception as e:
        st.error(f"Error displaying study guide: {str(e)}")
        st.info("No study guide available.")
    
    # Section 4: Practice Quiz
    st.markdown('<h2 class="section-header">❓ Practice Quiz</h2>', unsafe_allow_html=True)
    
    # Handle the case where results["quiz"] might be None or not a dictionary
    try:
        if results and "quiz" in results and results["quiz"]:
            # Try to get the quiz data safely
            quiz = results["quiz"].get("quiz", []) if isinstance(results["quiz"], dict) else []
            
            # Verify we have quiz questions
            if quiz and isinstance(quiz, list) and len(quiz) > 0:
                # Initialize session state for quiz scores if not present
                if 'quiz_submitted' not in st.session_state:
                    st.session_state.quiz_submitted = False
                if 'quiz_answers' not in st.session_state:
                    st.session_state.quiz_answers = {}
                if 'quiz_score' not in st.session_state:
                    st.session_state.quiz_score = 0
                
                # Show quiz questions
                if not st.session_state.quiz_submitted:
                    with st.form(key="quiz_form"):
                        valid_questions = 0
                        
                        for i, question in enumerate(quiz):
                            # Verify question has required fields
                            if not isinstance(question, dict) or "question" not in question or "options" not in question:
                                continue
                                
                            # Verify options is a dictionary
                            options = question.get("options", {})
                            if not isinstance(options, dict) or len(options) < 2:
                                continue
                                
                            valid_questions += 1
                            st.markdown(f"**Question {valid_questions}:** {question['question']}")
                            
                            st.session_state.quiz_answers[i] = st.radio(
                                f"Select your answer for question {valid_questions}:",
                                options.keys(),
                                format_func=lambda x: f"{x}: {options[x]}",
                                key=f"q_{i}",
                                index=None  # No default selection
                            )
                            st.write("---")
                        
                        # Only show submit if we have valid questions
                        if valid_questions > 0:
                            submit_quiz = st.form_submit_button("Submit Quiz")
                            
                            if submit_quiz:
                                # Calculate score
                                correct_count = 0
                                for i, question in enumerate(quiz):
                                    if (isinstance(question, dict) and 
                                        "correct_answer" in question and 
                                        st.session_state.quiz_answers.get(i) == question["correct_answer"]):
                                        correct_count += 1
                                
                                st.session_state.quiz_score = correct_count
                                st.session_state.quiz_submitted = True
                                st.rerun()
                        else:
                            st.info("No valid quiz questions available.")
                
                # Show quiz results
                else:
                    valid_questions = sum(1 for q in quiz if isinstance(q, dict) and "question" in q and "options" in q)
                    st.subheader(f"Your Score: {st.session_state.quiz_score}/{valid_questions}")
                    
                    for i, question in enumerate(quiz):
                        # Skip invalid questions
                        if not isinstance(question, dict) or "question" not in question or "options" not in question:
                            continue
                            
                        user_answer = st.session_state.quiz_answers.get(i)
                        correct_answer = question.get("correct_answer", "")
                        
                        st.markdown(f"**Question {i+1}:** {question['question']}")
                        options = question.get("options", {})
                        
                        for opt, text in options.items():
                            if opt == correct_answer:
                                st.success(f"✓ {opt}: {text} (Correct Answer)")
                            elif opt == user_answer:
                                st.error(f"✗ {opt}: {text} (Your Answer)")
                            else:
                                st.write(f"{opt}: {text}")
                        
                        st.info(f"**Explanation:** {question.get('explanation', 'No explanation provided.')}")
                        st.write("---")
                    
                    if st.button("Retake Quiz"):
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_score = 0
                        st.rerun()
            else:
                st.info("No quiz questions available.")
        else:
            st.info("No quiz available.")
    except Exception as e:
        st.error(f"Error displaying quiz: {str(e)}")
        st.info("No quiz available.")
    
    # Section 5: Detailed Notes with Examples
    st.markdown('<h2 class="section-header">📔 Detailed Topic Notes</h2>', unsafe_allow_html=True)
    
    try:
        if results and "detailed_notes" in results and results["detailed_notes"]:
            # Try to get the detailed notes data safely
            notes_data = results["detailed_notes"].get("notes", []) if isinstance(results["detailed_notes"], dict) else []
            
            # Verify we have notes sections
            if notes_data and isinstance(notes_data, list) and len(notes_data) > 0:
                for section in notes_data:
                    # Support both the old "title" and new "topic" field names
                    section_title = section.get("topic", section.get("title", "Untitled Section"))
                    section_key = "title" if "title" in section else "topic"
                    
                    if isinstance(section, dict) and section_key in section:
                        with st.expander(f"📌 {section_title}", expanded=True):
                            # Display definition (if available)
                            if "definition" in section and section["definition"]:
                                st.markdown(f'<div class="definition-box"><strong>Definition:</strong> {section["definition"]}</div>', unsafe_allow_html=True)
                                st.write("---")
                            
                            # Display key points in bold
                            if "key_points" in section and section["key_points"]:
                                st.subheader("Key Points:")
                                for point in section["key_points"]:
                                    # For key points that are already in bold format, extract and display the text
                                    if isinstance(point, str) and point.startswith("**") and point.endswith("**"):
                                        point_text = point[2:-2]  # Remove the ** markers
                                    else:
                                        point_text = point
                                    st.markdown(f'<div class="key-point">{point_text}</div>', unsafe_allow_html=True)
                                st.write("---")
                            
                            # Display content
                            if "content" in section and section["content"]:
                                st.markdown(section["content"])
                            
                            # Display examples (multiple if available)
                            if "examples" in section and section["examples"] and isinstance(section["examples"], list):
                                st.subheader("Examples:")
                                for example in section["examples"]:
                                    st.markdown(f'<div class="example-text">{example}</div>', unsafe_allow_html=True)
                            # Fallback for old format with single example
                            elif "example" in section and section["example"]:
                                st.subheader("Example:")
                                st.markdown(f'<div class="example-text">{section["example"]}</div>', unsafe_allow_html=True)
                            
                            # Display diagram references (if available)
                            if "diagrams" in section and section["diagrams"] and isinstance(section["diagrams"], list) and len(section["diagrams"]) > 0:
                                st.subheader("Diagram References:")
                                for diagram in section["diagrams"]:
                                    st.markdown(f'<div class="diagram-ref"><i>📊</i> {diagram}</div>', unsafe_allow_html=True)
            else:
                st.info("No detailed notes available.")
        else:
            st.info("No detailed notes available.")
    except Exception as e:
        st.error(f"Error displaying detailed notes: {str(e)}")
        st.info("No detailed notes available.")
    
    # Section 6: Personalized Insights
    st.markdown('<h2 class="section-header">👤 Personalized Insights (Optional)</h2>', unsafe_allow_html=True)
    
    # Check if we already have generated insights
    if st.session_state.personal_insights:
        try:
            if isinstance(st.session_state.personal_insights, dict):
                # Try to safely access the insights
                if "insights" in st.session_state.personal_insights and st.session_state.personal_insights["insights"]:
                    insights = st.session_state.personal_insights["insights"]
                    
                    st.write("Here are personalized insights based on your professional profile:")
                    
                    # Check that all sections exist
                    if isinstance(insights, dict):
                        st.markdown('<div class="insight-container">', unsafe_allow_html=True)
                        
                        st.markdown('<div class="insight-section">' +
                                     '<h4>🔄 Relevance to Your Background</h4>' +
                                     f'<p>{insights.get("relevance", "No relevance information available.")}</p>' +
                                     '</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="insight-section">' +
                                     '<h4>🎯 Alignment with Your Skills</h4>' +
                                     f'<p>{insights.get("alignment", "No alignment information available.")}</p>' +
                                     '</div>', unsafe_allow_html=True)
                            
                        st.markdown('<div class="insight-section">' +
                                     '<h4>📈 Areas for Growth</h4>' +
                                     f'<p>{insights.get("growth_areas", "No growth areas information available.")}</p>' +
                                     '</div>', unsafe_allow_html=True)
                            
                        st.markdown('<div class="insight-section">' +
                                     '<h4>💡 Practical Applications</h4>' +
                                     f'<p>{insights.get("applications", "No applications information available.")}</p>' +
                                     '</div>', unsafe_allow_html=True)
                            
                        st.markdown('<div class="insight-section">' +
                                     '<h4>🛤️ Personalized Learning Path</h4>' +
                                     f'<p>{insights.get("learning_path", "No learning path information available.")}</p>' +
                                     '</div>', unsafe_allow_html=True)
                                     
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("Invalid format for insights data.")
                else:
                    st.error("No insights data found in the generated results.")
                    
            if st.button("Reset Personalized Insights", key="reset_insights"):
                st.session_state.personal_insights = None
                st.rerun()
                
        except Exception as e:
            st.error(f"Error displaying personal insights: {str(e)}")
            if st.button("Reset Personalized Insights", key="reset_error"):
                st.session_state.personal_insights = None
                st.rerun()
    else:
        # Show form to upload profile data
        st.write("Upload your resume and/or LinkedIn profile to receive personalized insights about how this topic relates to your background and career path.")
        
        resume_col, linkedin_file_col, linkedin_url_col = st.columns([1, 1, 1])
        
        with resume_col:
            resume_file = st.file_uploader("Upload your resume (PDF/DOCX):", type=["pdf", "docx"], key="resume_upload")
        
        with linkedin_file_col:
            linkedin_file = st.file_uploader("Upload LinkedIn profile (PDF/DOCX/TXT):", type=["pdf", "docx", "txt"], key="linkedin_upload")
        
        with linkedin_url_col:
            linkedin_url = st.text_input("Or paste LinkedIn profile URL:", placeholder="https://www.linkedin.com/in/yourusername", key="linkedin_url")
            if linkedin_url and not linkedin_file:
                linkedin_file = linkedin_url  # Pass the URL as a string instead of a file object
        
        if st.button("Generate Personalized Insights", key="generate_insights"):
            if resume_file is None and linkedin_file is None and linkedin_url == "":
                st.warning("Please upload at least one file (resume or LinkedIn profile) or provide a LinkedIn URL.")
            else:
                with st.spinner("Analyzing your profile and generating personalized insights..."):
                    # Get the study content from the results, with safe access
                    study_content = ""
                    if results and "transcript" in results and results["transcript"]:
                        study_content = results["transcript"]
                    
                    # Generate personalized insights
                    insights_result = process_profile_data(resume_file, linkedin_file, study_content)
                    
                    if insights_result["success"]:
                        st.session_state.personal_insights = insights_result
                        st.success("Personalized insights generated!")
                        st.rerun()
                    else:
                        st.error(f"Error generating personalized insights: {insights_result['error']}")
    
    # Add export functionality
    if results:
        create_export_section(results)
    
    # Add another reset button at the bottom
    if st.button("Start Over", key="reset_bottom"):
        reset_app()

# Footer
st.markdown("---")
st.markdown("🎓 **AI Study Assistant** | Made with ❤️ using Streamlit and AI APIs")
