import json
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

def generate_export_file(topic, summary, resources, study_guide, quiz, insights, export_format="md"):
    """
    Generate an export file with all study materials.
    
    Args:
        topic (str): The main topic of the study materials
        summary (dict): The summary data
        resources (dict): The resources data
        study_guide (dict): The study guide data
        quiz (dict): The quiz data
        insights (dict): The personalized insights data
        export_format (str): The format to export (md, txt, html, json)
        
    Returns:
        str: The content of the export file
    """
    try:
        if export_format == "json":
            return generate_json_export(topic, summary, resources, study_guide, quiz, insights)
        elif export_format == "html":
            return generate_html_export(topic, summary, resources, study_guide, quiz, insights)
        elif export_format == "txt":
            return generate_text_export(topic, summary, resources, study_guide, quiz, insights)
        else:  # Default to markdown
            return generate_markdown_export(topic, summary, resources, study_guide, quiz, insights)
    
    except Exception as e:
        logger.exception(f"Error generating export file: {str(e)}")
        # Return a simple error message in the requested format
        if export_format == "json":
            return json.dumps({"error": f"Failed to generate export: {str(e)}"})
        elif export_format == "html":
            return f"<html><body><h1>Error</h1><p>Failed to generate export: {str(e)}</p></body></html>"
        elif export_format == "txt":
            return f"ERROR: Failed to generate export: {str(e)}"
        else:
            return f"# Error\n\nFailed to generate export: {str(e)}"

def generate_markdown_export(topic, summary, resources, study_guide, quiz, insights):
    """Generate a Markdown export file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = f"""# Study Kit: {topic}
Generated on: {now}

## 1. Key Concepts Summary

"""
    
    # Add summary
    if summary and summary.get("success", False):
        content += summary.get("summary", "No summary available.")
    else:
        content += "No summary available."
    
    content += "\n\n## 2. Recommended Resources\n\n"
    
    # Add resources
    if resources and resources.get("success", False):
        res_list = resources.get("resources", {}).get("resources", [])
        if res_list:
            for res in res_list:
                content += f"### {res.get('title', 'Resource')}\n"
                content += f"**Type:** {res.get('type', 'Resource')}\n"
                content += f"**Description:** {res.get('description', 'No description available.')}\n"
                content += f"**URL:** [{res.get('url', '#')}]({res.get('url', '#')})\n\n"
        else:
            content += "No resources available.\n"
    else:
        content += "No resources available.\n"
    
    content += "\n## 3. Study Guide\n\n"
    
    # Add study guide
    if study_guide and study_guide.get("success", False):
        guide = study_guide.get("study_guide", {}).get("study_guide", {})
        
        # Key terms
        content += "### Key Terms and Definitions\n\n"
        terms = guide.get("key_terms", [])
        if terms:
            for term in terms:
                content += f"**{term.get('term', 'Term')}**: {term.get('definition', 'No definition available.')}\n\n"
        else:
            content += "No key terms available.\n"
        
        # Important concepts
        content += "\n### Important Concepts\n\n"
        concepts = guide.get("important_concepts", [])
        if concepts:
            for i, concept in enumerate(concepts):
                content += f"{i+1}. {concept}\n"
        else:
            content += "No important concepts available.\n"
        
        # Flashcards
        content += "\n### Flashcards\n\n"
        cards = guide.get("flashcards", [])
        if cards:
            for i, card in enumerate(cards):
                content += f"**Q{i+1}:** {card.get('question', 'Question')}\n"
                content += f"**A{i+1}:** {card.get('answer', 'Answer')}\n\n"
        else:
            content += "No flashcards available.\n"
    else:
        content += "No study guide available.\n"
    
    content += "\n## 4. Practice Quiz\n\n"
    
    # Add quiz
    if quiz and quiz.get("success", False):
        questions = quiz.get("quiz", {}).get("quiz", [])
        if questions:
            for i, q in enumerate(questions):
                content += f"### Question {i+1}: {q.get('question', 'Question')}\n\n"
                
                options = q.get("options", {})
                for key, value in options.items():
                    if key == q.get("correct_answer"):
                        content += f"- **{key}:** {value} ✓\n"
                    else:
                        content += f"- {key}: {value}\n"
                
                content += f"\n**Explanation:** {q.get('explanation', 'No explanation available.')}\n\n"
        else:
            content += "No quiz questions available.\n"
    else:
        content += "No quiz available.\n"
    
    # Add personalized insights if available
    if insights:
        content += "\n## 5. Personalized Insights\n\n"
        
        content += "### How This Content Relates to Your Background\n"
        content += insights.get("relevance", "No insights available.") + "\n\n"
        
        content += "### Alignment with Your Skills\n"
        content += insights.get("alignment", "No insights available.") + "\n\n"
        
        content += "### Areas for Growth\n"
        content += insights.get("growth_areas", "No insights available.") + "\n\n"
        
        content += "### Applying This Knowledge\n"
        content += insights.get("applications", "No insights available.") + "\n\n"
        
        content += "### Customized Learning Path\n"
        content += insights.get("learning_path", "No insights available.") + "\n\n"
    
    return content

def generate_text_export(topic, summary, resources, study_guide, quiz, insights):
    """Generate a plain text export file."""
    # Convert markdown to plain text
    md_content = generate_markdown_export(topic, summary, resources, study_guide, quiz, insights)
    
    # Replace markdown formatting with plain text equivalents
    text_content = md_content
    text_content = re.sub(r'#{1,6}\s+(.+)', r'\1\n' + '=' * 30, text_content)  # Replace headers
    text_content = re.sub(r'\*\*(.+?)\*\*', r'\1', text_content)  # Remove bold
    text_content = re.sub(r'\*(.+?)\*', r'\1', text_content)  # Remove italic
    text_content = re.sub(r'\[(.+?)\]\((.+?)\)', r'\1 (\2)', text_content)  # Convert links
    
    return text_content

def generate_html_export(topic, summary, resources, study_guide, quiz, insights):
    """Generate an HTML export file."""
    # Convert markdown to HTML
    md_content = generate_markdown_export(topic, summary, resources, study_guide, quiz, insights)
    
    # Simple markdown to HTML conversion (for a proper implementation, use a markdown library)
    html_content = md_content
    
    # Replace headers
    html_content = re.sub(r'# (.+)', r'<h1>\1</h1>', html_content)
    html_content = re.sub(r'## (.+)', r'<h2>\1</h2>', html_content)
    html_content = re.sub(r'### (.+)', r'<h3>\1</h3>', html_content)
    
    # Replace bold and italic
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
    
    # Replace links
    html_content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html_content)
    
    # Replace line breaks
    html_content = html_content.replace('\n\n', '</p><p>')
    
    # Wrap in HTML structure
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Study Kit: {topic}</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        a {{ color: #3498db; }}
        .resource {{ margin-bottom: 20px; padding: 10px; border: 1px solid #eee; }}
        .flashcard {{ margin-bottom: 15px; padding: 10px; background-color: #f9f9f9; }}
        .question {{ font-weight: bold; }}
        .quiz-question {{ margin-bottom: 30px; }}
        .option {{ margin-left: 20px; }}
        .correct {{ color: #27ae60; font-weight: bold; }}
    </style>
</head>
<body>
    <p>{html_content}</p>
</body>
</html>
"""
    
    return html

def generate_json_export(topic, summary, resources, study_guide, quiz, insights):
    """Generate a JSON export file."""
    export_data = {
        "topic": topic,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": summary.get("summary", "") if summary and summary.get("success", False) else None,
        "resources": resources.get("resources", {}).get("resources", []) if resources and resources.get("success", False) else [],
        "study_guide": study_guide.get("study_guide", {}).get("study_guide", {}) if study_guide and study_guide.get("success", False) else {},
        "quiz": quiz.get("quiz", {}).get("quiz", []) if quiz and quiz.get("success", False) else [],
        "insights": insights if insights else {}
    }
    
    return json.dumps(export_data, indent=2)

# Add utility function to help with text replacements in export formats
import re
