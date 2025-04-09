"""
Export utilities for the AI Study Assistant.
Provides functionality to export study materials in various formats.
"""

import base64
import json
import io
import os
from datetime import datetime
import streamlit as st

def get_download_link(content, filename, text):
    """
    Generate a download link for a file.
    
    Args:
        content (str): Content to be downloaded
        filename (str): Name of the download file
        text (str): Text to display for the download link
        
    Returns:
        str: HTML string for the download link
    """
    # Encode the content to base64
    b64 = base64.b64encode(content.encode()).decode()
    
    # Generate the download link
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'
    return href

def format_markdown_content(title, results):
    """
    Format study materials as markdown content.
    
    Args:
        title (str): Title for the markdown content
        results (dict): Dictionary containing study materials
        
    Returns:
        str: Formatted markdown content
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    markdown_content = f"# {title}\nGenerated on: {now}\n\n"
    
    # Add Key Concepts Summary
    markdown_content += "## 🧠 Key Concepts Summary\n\n"
    if "summary" in results and results["summary"] and isinstance(results["summary"], dict):
        summary = results["summary"].get("summary", "")
        if summary:
            markdown_content += f"{summary}\n\n"
    
    # Add Suggested Resources
    markdown_content += "## 📚 Suggested Resources\n\n"
    if "resources" in results and results["resources"] and isinstance(results["resources"], dict):
        resources = results["resources"].get("resources", [])
        if resources and isinstance(resources, list):
            for resource in resources:
                if isinstance(resource, dict) and "title" in resource and "url" in resource:
                    markdown_content += f"- [{resource['title']}]({resource['url']})\n"
            markdown_content += "\n"
    
    # Add Study Guide
    markdown_content += "## 📝 Study Guide & Flashcards\n\n"
    if "study_guide" in results and results["study_guide"] and isinstance(results["study_guide"], dict):
        study_guide = results["study_guide"].get("study_guide", {})
        
        # Key Terms
        if study_guide and "key_terms" in study_guide and study_guide["key_terms"]:
            markdown_content += "### Key Terms\n\n"
            for term_entry in study_guide["key_terms"]:
                if isinstance(term_entry, dict) and "term" in term_entry and "definition" in term_entry:
                    markdown_content += f"**{term_entry['term']}**: {term_entry['definition']}\n\n"
        
        # Important Concepts
        if study_guide and "important_concepts" in study_guide and study_guide["important_concepts"]:
            markdown_content += "### Important Concepts\n\n"
            for i, concept in enumerate(study_guide["important_concepts"]):
                markdown_content += f"{i+1}. {concept}\n"
            markdown_content += "\n"
        
        # Flashcards
        if study_guide and "flashcards" in study_guide and study_guide["flashcards"]:
            markdown_content += "### Flashcards\n\n"
            for i, card in enumerate(study_guide["flashcards"]):
                if isinstance(card, dict) and "question" in card and "answer" in card:
                    markdown_content += f"**Q{i+1}:** {card['question']}\n\n"
                    markdown_content += f"**A{i+1}:** {card['answer']}\n\n"
    
    # Add Quiz
    markdown_content += "## ❓ Practice Quiz\n\n"
    if "quiz" in results and results["quiz"] and isinstance(results["quiz"], dict):
        quiz = results["quiz"].get("quiz", [])
        if quiz and isinstance(quiz, list):
            for i, question in enumerate(quiz):
                if isinstance(question, dict) and "question" in question and "options" in question:
                    markdown_content += f"**Question {i+1}:** {question['question']}\n\n"
                    
                    options = question.get("options", {})
                    for opt, text in options.items():
                        markdown_content += f"- {opt}: {text}\n"
                    
                    # Include correct answer
                    if "correct_answer" in question:
                        markdown_content += f"\n*Correct Answer: {question['correct_answer']}*\n\n"
    
    # Add Topic Notes if available
    if "topic_notes" in results and results["topic_notes"] and isinstance(results["topic_notes"], dict):
        topic_notes = results["topic_notes"].get("notes", [])
        if topic_notes and isinstance(topic_notes, list):
            markdown_content += "## 📘 Detailed Topic Notes\n\n"
            for section in topic_notes:
                if isinstance(section, dict) and "topic" in section:
                    markdown_content += f"### {section['topic']}\n\n"
                    
                    if "definition" in section:
                        markdown_content += f"**Definition:** {section['definition']}\n\n"
                    
                    if "key_points" in section and isinstance(section["key_points"], list):
                        markdown_content += "**Key Points:**\n\n"
                        for point in section["key_points"]:
                            markdown_content += f"- {point}\n"
                        markdown_content += "\n"
                    
                    if "examples" in section and isinstance(section["examples"], list):
                        markdown_content += "**Examples:**\n\n"
                        for example in section["examples"]:
                            markdown_content += f"- {example}\n"
                        markdown_content += "\n"
                    
                    if "diagrams" in section and isinstance(section["diagrams"], list):
                        markdown_content += "**Diagrams:**\n\n"
                        for diagram in section["diagrams"]:
                            markdown_content += f"- {diagram}\n"
                        markdown_content += "\n"
    
    return markdown_content

def export_to_json(results, title="AI Study Assistant Results"):
    """
    Export study materials to JSON format.
    
    Args:
        results (dict): Dictionary containing study materials
        title (str): Title for the JSON file
        
    Returns:
        dict: Dictionary with the JSON content, filename, and download link text
    """
    # Clean up the results dictionary to ensure it's serializable
    clean_results = {
        "title": title,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": results
    }
    
    # Convert to JSON string with indentation for readability
    json_str = json.dumps(clean_results, indent=2)
    
    # Generate filename
    filename = f"study_materials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return {
        "content": json_str,
        "filename": filename,
        "download_text": "Download as JSON"
    }

def export_to_markdown(results, title="AI Study Assistant Results"):
    """
    Export study materials to Markdown format.
    
    Args:
        results (dict): Dictionary containing study materials
        title (str): Title for the markdown file
        
    Returns:
        dict: Dictionary with the markdown content, filename, and download link text
    """
    # Format the content as markdown
    markdown_str = format_markdown_content(title, results)
    
    # Generate filename
    filename = f"study_materials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    return {
        "content": markdown_str,
        "filename": filename,
        "download_text": "Download as Markdown"
    }

def export_to_text(results, title="AI Study Assistant Results"):
    """
    Export study materials to plain text format.
    
    Args:
        results (dict): Dictionary containing study materials
        title (str): Title for the text file
        
    Returns:
        dict: Dictionary with the text content, filename, and download link text
    """
    # Use the markdown content but without formatting
    markdown_str = format_markdown_content(title, results)
    
    # Replace markdown formatting with plain text alternatives
    # This is a simple conversion - it won't handle all markdown syntax
    text_str = markdown_str
    text_str = text_str.replace("## ", "").replace("### ", "")
    text_str = text_str.replace("**", "").replace("*", "")
    text_str = text_str.replace("[", "").replace("](", " - ").replace(")", "")
    
    # Generate filename
    filename = f"study_materials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    return {
        "content": text_str,
        "filename": filename,
        "download_text": "Download as Text"
    }

def create_export_section(results):
    """
    Create a section in the app for exporting study materials.
    
    Args:
        results (dict): Dictionary containing study materials
        
    Returns:
        None: This function directly renders UI elements using Streamlit
    """
    st.markdown('<h2 class="section-header">📥 Export Study Materials</h2>', unsafe_allow_html=True)
    
    # Check if we have results to export
    if not results or not any(key in results for key in ["summary", "resources", "study_guide", "quiz", "topic_notes"]):
        st.info("No study materials available to export.")
        return
    
    # Ask the user for a title for their export
    title = st.text_input("Title for your study materials:", "AI Study Assistant Results")
    
    # Create columns for the different export formats
    col1, col2, col3 = st.columns(3)
    
    # Export as Markdown
    with col1:
        markdown_export = export_to_markdown(results, title)
        markdown_link = get_download_link(
            markdown_export["content"],
            markdown_export["filename"],
            markdown_export["download_text"]
        )
        st.markdown(markdown_link, unsafe_allow_html=True)
    
    # Export as JSON
    with col2:
        json_export = export_to_json(results, title)
        json_link = get_download_link(
            json_export["content"],
            json_export["filename"],
            json_export["download_text"]
        )
        st.markdown(json_link, unsafe_allow_html=True)
    
    # Export as Text
    with col3:
        text_export = export_to_text(results, title)
        text_link = get_download_link(
            text_export["content"],
            text_export["filename"],
            text_export["download_text"]
        )
        st.markdown(text_link, unsafe_allow_html=True)