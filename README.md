# AI Study Assistant

An AI-powered study assistant that transforms various inputs into comprehensive study materials using Streamlit.

## Features

- Process various input types:
  - Text input
  - Document uploads (PDF, DOCX, PPTX, TXT)
  - YouTube video transcripts
  - Audio file transcriptions
  
- Generate comprehensive study materials:
  - Key point summaries
  - Detailed study guides
  - Interactive quizzes
  - Topic-specific notes
  - Suggested resources
  - Personalized insights

## Deployment on Streamlit Cloud

### Prerequisites

1. GitHub account
2. Streamlit Cloud account (free tier available)
3. OpenAI API key (required)
4. Hugging Face API key (optional, but recommended for fallback functionality)

### Steps to Deploy

1. Fork this repository to your GitHub account
2. Sign in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and select this repository
4. Set the main file path to `app.py`
5. Under "Advanced settings", add your API keys as secrets:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `HUGGINGFACE_API_KEY`: Your Hugging Face API key (optional)
6. Deploy the app

The app will automatically install the required dependencies from `github_requirements.txt` and download the necessary NLTK data.

## Local Development

### Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r github_requirements.txt
   ```
3. Run the NLTK data setup script:
   ```
   python setup.py
   ```
4. Set your API keys as environment variables:
   ```
   export OPENAI_API_KEY="your-openai-api-key"
   export HUGGINGFACE_API_KEY="your-huggingface-api-key"  # Optional
   ```
5. Run the app:
   ```
   streamlit run app.py
   ```

## Architecture

The application is organized into modules:
- `app.py`: Main Streamlit application
- `utils/`: Utility functions organized by purpose
  - `content_processor.py`: Text processing and analysis
  - `file_processor.py`: File handling for various formats
  - `transcription.py`: Audio and video transcription
  - `openai_helpers.py`: OpenAI API integration
  - `free_ai_helpers.py`: Alternative AI APIs
  - `static_fallbacks.py`: Fallback functionality when APIs are unavailable
  - `personal_insight.py`: Personalized study recommendations
  - `export_utils.py`: Export functionality for study materials

## Important Note

Make sure to rename `github_requirements.txt` to `requirements.txt` before pushing to GitHub, as Streamlit Cloud will look for a file named `requirements.txt`.