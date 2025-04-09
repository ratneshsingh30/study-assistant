# Preparing for GitHub Deployment

Follow these steps to make your app ready for GitHub deployment to Streamlit Cloud:

## 1. Create a proper directory structure

Ensure your repository has the following structure:
```
AI-Study-Assistant/
├── .streamlit/
│   └── config.toml
├── utils/
│   ├── __init__.py
│   ├── content_processor.py
│   ├── export_utils.py
│   ├── file_processor.py
│   ├── free_ai_helpers.py
│   ├── openai_helpers.py
│   ├── personal_insight.py
│   ├── static_fallbacks.py
│   └── transcription.py
├── .gitignore
├── app.py             (renamed from app_streamlit.py)
├── check_api_keys.py
├── nltk_setup.py
├── README.md
└── requirements.txt   (renamed from github_requirements.txt)
```

## 2. Prepare the files for GitHub

1. Rename the files:
   - Rename `app_streamlit.py` to `app.py`
   - Rename `github_requirements.txt` to `requirements.txt`
   
   ```bash
   mv app_streamlit.py app.py
   mv github_requirements.txt requirements.txt
   ```

2. Make sure you don't include sensitive information in your repository.

## 3. Set up GitHub repository and push your code

1. Create a new repository on GitHub.

2. Initialize Git (if not already done):
   ```bash
   git init
   ```

3. Add your files:
   ```bash
   git add .
   ```

4. Commit your changes:
   ```bash
   git commit -m "Initial commit"
   ```

5. Connect to your GitHub repository:
   ```bash
   git remote add origin https://github.com/your-username/AI-Study-Assistant.git
   ```

6. Push your code:
   ```bash
   git push -u origin main
   ```

## 4. Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Create a new app
4. Select your repository
5. Set the following:
   - Main file path: `app.py`
   - Python version: 3.11
   - Add the following secrets:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `HUGGINGFACE_API_KEY`: Your Hugging Face API key (optional)
6. Click "Deploy"

Your app should now be running on Streamlit Cloud with proper API keys configuration!

## Notes
- The app will automatically check for API keys on startup
- NLTK data will be downloaded automatically when the app runs for the first time
- Make sure all paths in your code are relative to the project root directory