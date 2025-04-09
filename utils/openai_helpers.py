import os
from openai import OpenAI
import json

# Initialize OpenAI client
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = "gpt-4o"

# Create client only if API key is available
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")

def get_summary(text, max_bullets=7):
    """
    Generate a summary of the given text in bullet points.
    
    Args:
        text (str): The text to summarize
        max_bullets (int): Maximum number of bullet points to generate
        
    Returns:
        dict: Dictionary with success status and either summary or error message
    """
    if client is None:
        return {"success": False, "error": "OpenAI API key not configured"}
        
    try:
        prompt = f"""
        Create a comprehensive, structured summary of the key concepts from the following text:

        {text}
        
        Structure your response with:
        1. Major headings using markdown format (## Heading)
        2. Under each heading, provide:
           - A clear definition or explanation (1-2 sentences)
           - Key points organized as bullet points (• for main points, - for sub-points)
           - Important terms in **bold** 
           - At least one example for each concept when available
           - If diagrams were described in the text, note with [DIAGRAM: brief description]
        
        Include no more than {max_bullets} major headings to maintain focus on the most critical concepts.
        Use markdown formatting throughout for clear, structured presentation.
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        
        summary = response.choices[0].message.content
        return {"success": True, "summary": summary}
    
    except Exception as e:
        return {"success": False, "error": f"Error generating summary: {str(e)}"}

def get_resources(topic, max_resources=3):
    """
    Generate suggested resources for the given topic.
    
    Args:
        topic (str): The topic to find resources for
        max_resources (int): Maximum number of resources to suggest
        
    Returns:
        dict: Dictionary with success status and either resources or error message
    """
    if client is None:
        return {"success": False, "error": "OpenAI API key not configured"}
        
    try:
        prompt = f"""
        Create {max_resources} reliable educational resources on the topic: "{topic}"
        
        For each resource, create:
        1. A descriptive title that accurately reflects the content
        2. A detailed description (1-2 sentences) explaining what the learner will gain
        3. The source website (using only these domains: youtube.com, khanacademy.org, coursera.org, edx.org, mit.edu, stanford.edu, harvard.edu, ted.com)
        4. The type of resource (video, course, article, etc.)
        
        Format each resource as a search URL that would lead to relevant content.
        For example:
        - YouTube: https://www.youtube.com/results?search_query=machine+learning+for+beginners
        - Khan Academy: https://www.khanacademy.org/search?page_search_query=linear+algebra+basics
        - Coursera: https://www.coursera.org/search?query=data+science+certification
        
        Return the information in JSON format with this structure:
        {{
            "resources": [
                {{
                    "title": "Descriptive Resource Title",
                    "description": "Detailed description of what this resource covers",
                    "url": "https://search-url-for-this-topic",
                    "type": "Type of resource (video, course, article, etc.)"
                }}
            ]
        }}
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=1000,
        )
        
        try:
            content = response.choices[0].message.content
            resources = json.loads(content)
            # Make sure resources has the expected format
            if "resources" not in resources:
                resources = {"resources": resources}
            return {"success": True, "resources": resources}
        except json.JSONDecodeError as e:
            # Fallback for invalid JSON
            return {"success": False, "error": f"Error parsing JSON response: {str(e)}"}
    
    except Exception as e:
        return {"success": False, "error": f"Error finding resources: {str(e)}"}

def generate_study_guide(text):
    """
    Generate a study guide with definitions, key terms, and flashcards.
    
    Args:
        text (str): The text to generate a study guide from
        
    Returns:
        dict: Dictionary with success status and either study guide or error message
    """
    if client is None:
        return {"success": False, "error": "OpenAI API key not configured"}
        
    try:
        prompt = f"""
        Create a comprehensive study guide based on the following text:
        
        {text}
        
        Include the following sections in JSON format:
        1. Key terms and definitions
        2. Important concepts
        3. Flashcards (question on front, answer on back)
        
        Return the output in this JSON structure:
        {{
            "study_guide": {{
                "key_terms": [
                    {{"term": "Term 1", "definition": "Definition 1"}},
                    {{"term": "Term 2", "definition": "Definition 2"}}
                ],
                "important_concepts": [
                    "Concept 1 explanation",
                    "Concept 2 explanation"
                ],
                "flashcards": [
                    {{"question": "Question 1?", "answer": "Answer 1"}},
                    {{"question": "Question 2?", "answer": "Answer 2"}}
                ]
            }}
        }}
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=2000,
        )
        
        try:
            content = response.choices[0].message.content
            result = json.loads(content)
            # Make sure response has expected format
            if "study_guide" not in result:
                result = {"study_guide": result}
            return {"success": True, "study_guide": result}
        except json.JSONDecodeError as e:
            # Fallback for invalid JSON
            return {"success": False, "error": f"Error parsing JSON response: {str(e)}"}
    
    except Exception as e:
        return {"success": False, "error": f"Error generating study guide: {str(e)}"}

def generate_quiz(text, num_questions=5):
    """
    Generate multiple-choice quiz questions based on the text.
    
    Args:
        text (str): The text to generate questions from
        num_questions (int): Number of questions to generate
        
    Returns:
        dict: Dictionary with success status and either quiz or error message
    """
    if client is None:
        return {"success": False, "error": "OpenAI API key not configured"}
        
    try:
        prompt = f"""
        Create {num_questions} multiple-choice questions based on this text:
        
        {text}
        
        Each question should have:
        1. A question
        2. Four answer options (A, B, C, D)
        3. The correct answer letter
        4. An explanation of why the answer is correct
        
        Return the questions in this JSON format:
        {{
            "quiz": [
                {{
                    "question": "Question text?",
                    "options": {{
                        "A": "Option A",
                        "B": "Option B",
                        "C": "Option C",
                        "D": "Option D"
                    }},
                    "correct_answer": "A",
                    "explanation": "Explanation of why A is correct"
                }}
            ]
        }}
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=2000,
        )
        
        try:
            content = response.choices[0].message.content
            result = json.loads(content)
            # Make sure response has expected format
            if "quiz" not in result:
                # If the response is an array, wrap it in an object
                if isinstance(result, list):
                    result = {"quiz": result}
                # If it's an object but doesn't have quiz key, add it
                else:
                    result = {"quiz": result}
            return {"success": True, "quiz": result}
        except json.JSONDecodeError as e:
            # Fallback for invalid JSON
            return {"success": False, "error": f"Error parsing JSON response: {str(e)}"}
    
    except Exception as e:
        return {"success": False, "error": f"Error generating quiz: {str(e)}"}

def generate_personalized_insights(prompt_text):
    """
    Generate personalized insights based on a user's profile and study content.
    
    Args:
        prompt_text (str): The full prompt containing resume, LinkedIn, and study content
        
    Returns:
        dict: Dictionary with success status and either insights or error message
    """
    if client is None:
        return {"success": False, "error": "OpenAI API key not configured"}
        
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=2000,
        )
        
        insights_text = response.choices[0].message.content
        
        # Extract the various sections
        sections = {
            "relevance": extract_section(insights_text, "relates to the person's background"),
            "alignment": extract_section(insights_text, "align with their skills"),
            "growth_areas": extract_section(insights_text, "Areas for growth"),
            "applications": extract_section(insights_text, "apply this knowledge"),
            "learning_path": extract_section(insights_text, "learning path")
        }
        
        return {"success": True, "insights": sections}
    
    except Exception as e:
        return {"success": False, "error": f"Error generating personalized insights: {str(e)}"}

def extract_section(text, section_marker):
    """Extract a specific section from AI-generated text based on marker phrase"""
    import re
    
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
