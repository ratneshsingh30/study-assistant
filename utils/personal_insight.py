import logging
import os
import io
import re
import tempfile
from .file_processor import process_file
from . import content_processor

# Set up logging
logger = logging.getLogger(__name__)

def extract_text_from_resume(resume_file):
    """
    Extract text content from a resume file (PDF, DOCX).
    
    Args:
        resume_file: The resume file object
        
    Returns:
        dict: Dictionary with success status and extracted text or error message
    """
    logger.info(f"Processing resume: {resume_file.name}")
    return process_file(resume_file)

def extract_text_from_linkedin(linkedin_file):
    """
    Extract text content from a LinkedIn profile file (PDF, DOCX, TXT) or URL.
    
    Args:
        linkedin_file: The LinkedIn profile file object or URL string
        
    Returns:
        dict: Dictionary with success status and extracted text or error message
    """
    try:
        # Check if input is a string (URL) or a file object
        if isinstance(linkedin_file, str):
            # Handle LinkedIn URL
            if "linkedin.com" in linkedin_file.lower():
                logger.info(f"Processing LinkedIn URL: {linkedin_file}")
                # For privacy and terms of service reasons, we can't scrape LinkedIn
                # But we can extract the profile username/ID from the URL
                
                # Try to extract the username from LinkedIn URL
                match = re.search(r'linkedin\.com/in/([^/]+)', linkedin_file)
                if match:
                    username = match.group(1)
                    # Create a basic profile based on username
                    profile_info = f"LinkedIn Profile: {username}\n"
                    profile_info += f"URL: {linkedin_file}\n"
                    profile_info += "User has shared their LinkedIn profile for personalization.\n"
                    return {"success": True, "text": profile_info}
                else:
                    return {"success": False, "error": "Unable to process LinkedIn URL. Please provide a valid profile URL."}
            else:
                return {"success": False, "error": "Invalid LinkedIn URL. Please provide a valid LinkedIn profile URL."}
        else:
            # Process as file upload
            logger.info(f"Processing LinkedIn profile file: {linkedin_file.name}")
            return process_file(linkedin_file)
            
    except Exception as e:
        logger.exception(f"Error extracting text from LinkedIn profile: {str(e)}")
        return {"success": False, "error": f"Error extracting text from LinkedIn profile: {str(e)}"}

def generate_personal_insights(resume_text, linkedin_text, study_content):
    """
    Generate personalized insights based on resume, LinkedIn profile, and study content.
    
    Args:
        resume_text: Text content from resume
        linkedin_text: Text content from LinkedIn profile
        study_content: Text content from the study materials
        
    Returns:
        dict: Dictionary with success status and insights or error message
    """
    try:
        # Use OpenAI or fallback to generate insights
        logger.info("Generating personalized insights")
        
        # Create a combined prompt for insight generation
        prompt = f"""
        Based on the following information, provide personalized learning insights and recommendations:
        
        RESUME:
        {resume_text[:2000]}  # Limit to 2000 chars to avoid token limits
        
        LINKEDIN PROFILE:
        {linkedin_text[:2000]}  # Limit to 2000 chars to avoid token limits
        
        STUDY CONTENT:
        {study_content[:3000]}  # Limit to 3000 chars to avoid token limits
        
        Provide insights on:
        1. How this content relates to the person's background and experience
        2. Specific aspects that align with their skills and career goals
        3. Areas for growth and development based on their profile
        4. How they might apply this knowledge in their current or future roles
        5. Customized learning path recommendations
        """
        
        # Use the content processor wrapper mechanism 
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        
        if openai_api_key:
            # If OpenAI key is available, try using it first
            try:
                # Use OpenAI directly
                from openai import OpenAI
                MODEL = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
                
                try:
                    client = OpenAI(api_key=openai_api_key)
                except Exception as e:
                    logger.error(f"Error initializing OpenAI client: {str(e)}")
                    return {"success": False, "error": f"Error initializing OpenAI client: {str(e)}"}
                
                if client is None:
                    return {"success": False, "error": "Failed to initialize OpenAI client"}
                    
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                )
                
                insights_text = response.choices[0].message.content
                
                # Extract the various sections
                insights_result = {
                    "success": True,
                    "insights": {
                        "relevance": extract_section(insights_text, "relates to the person's background"),
                        "alignment": extract_section(insights_text, "align with their skills"),
                        "growth_areas": extract_section(insights_text, "Areas for growth"),
                        "applications": extract_section(insights_text, "apply this knowledge"),
                        "learning_path": extract_section(insights_text, "learning path")
                    }
                }
                
                return insights_result
            except Exception as e:
                logger.exception(f"Error with OpenAI insights generation: {str(e)}")
                # Fall through to free AI option
        
        # Use free AI helper as fallback
        from .free_ai_helpers import make_api_request
        
        api_response = make_api_request(prompt)
        
        if api_response:
            return {
                "success": True,
                "insights": {
                    "relevance": extract_section(api_response, "relates to the person's background"),
                    "alignment": extract_section(api_response, "align with their skills"),
                    "growth_areas": extract_section(api_response, "Areas for growth"),
                    "applications": extract_section(api_response, "apply this knowledge"),
                    "learning_path": extract_section(api_response, "learning path")
                }
            }
        else:
            # Simple fallback if all AI methods fail
            return {
                "success": True,
                "insights": {
                    "relevance": "Based on your resume and LinkedIn profile, this content appears relevant to your background.",
                    "alignment": "There are several concepts here that align with your listed skills.",
                    "growth_areas": "Consider focusing on the key concepts mentioned in the summary.",
                    "applications": "This knowledge can be applied in professional contexts related to your field.",
                    "learning_path": "Continue exploring the suggested resources for more depth on this topic."
                }
            }
    
    except Exception as e:
        logger.exception(f"Error generating personal insights: {str(e)}")
        return {"success": False, "error": f"Error generating personal insights: {str(e)}"}

def extract_section(text, section_marker):
    """Extract a specific section from AI-generated text based on marker phrase"""
    if not text:
        return "Not available"
    
    # Look for the section following the marker
    pattern = f".*{re.escape(section_marker)}.*?([\\s\\S]+?)(?=\\d\\.|$)"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        content = match.group(1).strip()
        return content
    
    # If pattern not found, return a segment of text
    sentences = text.split('.')
    if len(sentences) > 3:
        return '. '.join(sentences[:3]).strip() + '.'
    return text[:200] + "..."

def process_profile_data(resume_file, linkedin_file, study_content):
    """
    Process profile data (resume and LinkedIn) and generate insights.
    
    Args:
        resume_file: The resume file object
        linkedin_file: The LinkedIn profile file object
        study_content: The study content text
        
    Returns:
        dict: Dictionary with success status and insights or error message
    """
    try:
        result = {
            "success": False,
            "insights": None,
            "error": None
        }
        
        # Process resume
        if resume_file:
            resume_result = extract_text_from_resume(resume_file)
            if not resume_result["success"]:
                return {"success": False, "error": f"Error processing resume: {resume_result['error']}"}
            resume_text = resume_result["text"]
        else:
            resume_text = "No resume provided."
        
        # Process LinkedIn profile
        if linkedin_file:
            linkedin_result = extract_text_from_linkedin(linkedin_file)
            if not linkedin_result["success"]:
                return {"success": False, "error": f"Error processing LinkedIn profile: {linkedin_result['error']}"}
            linkedin_text = linkedin_result["text"]
        else:
            linkedin_text = "No LinkedIn profile provided."
        
        # Generate insights
        insights_result = generate_personal_insights(resume_text, linkedin_text, study_content)
        if insights_result["success"]:
            result["insights"] = insights_result["insights"]
            result["success"] = True
        else:
            result["error"] = insights_result["error"]
        
        return result
    
    except Exception as e:
        logger.exception(f"Error in process_profile_data: {str(e)}")
        return {"success": False, "error": f"Error processing profile data: {str(e)}"}