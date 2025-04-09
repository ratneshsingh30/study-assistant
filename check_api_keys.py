import os
import sys
import streamlit as st

def check_api_keys():
    """Check for required API keys and display appropriate messages"""
    
    openai_key = os.environ.get("OPENAI_API_KEY")
    huggingface_key = os.environ.get("HUGGINGFACE_API_KEY")
    
    if not openai_key:
        st.error(
            "⚠️ OpenAI API key not found! Please provide an API key to use AI-powered features. "
            "Set the OPENAI_API_KEY environment variable or add it as a secret in Streamlit Cloud."
        )
        st.info(
            "You can get an OpenAI API key at: https://platform.openai.com/api-keys"
        )
        return False
    
    if not huggingface_key:
        st.warning(
            "⚠️ Hugging Face API key not found. This is optional, but recommended for fallback functionality. "
            "Set the HUGGINGFACE_API_KEY environment variable or add it as a secret in Streamlit Cloud."
        )
        st.info(
            "You can get a Hugging Face API key at: https://huggingface.co/settings/tokens"
        )
    
    return True


if __name__ == "__main__":
    # This allows the script to be run standalone to check API keys
    check_api_keys()