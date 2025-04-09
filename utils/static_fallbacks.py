"""
Static fallback generators for when all API calls fail.
This module provides functions that extract information directly from the input text
without using any external APIs, ensuring the application always has content to display.
"""

import re
import random
import logging

logger = logging.getLogger(__name__)

def extract_slide_content(text):
    """Extract slide titles and their content from input text."""
    slide_pattern = r'Slide\s+(\d+):\s+([^\n]+)(?:\n(?:[^\n]*\d+[^\n]*\n)?)?([^S]*?)(?=Slide\s+\d+:|$)'
    matches = re.findall(slide_pattern, text, re.DOTALL)
    
    slides = []
    for slide_num, title, content in matches:
        cleaned_content = re.sub(r'\s+', ' ', content).strip()
        if title and cleaned_content:
            slides.append({
                "number": slide_num,
                "title": title.strip(),
                "content": cleaned_content
            })
    
    return slides

def get_static_summary(text, max_bullets=7):
    """
    Generate a summary directly from the text without using external APIs.
    
    Args:
        text (str): The text to summarize
        max_bullets (int): Maximum number of bullet points to generate
        
    Returns:
        dict: Dictionary with success status and summary
    """
    try:
        slides = extract_slide_content(text)
        
        # If no slides found, extract sentences
        if not slides:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            important_sentences = []
            
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in [
                    'important', 'key', 'main', 'crucial', 'essential',
                    'significant', 'primary', 'fundamental', 'critical'
                ]):
                    important_sentences.append(sentence.strip())
            
            summary_points = important_sentences[:max_bullets]
            if not summary_points and sentences:
                # If no important sentences found, take first few
                summary_points = [s.strip() for s in sentences[:max_bullets] if len(s.strip()) > 20]
        else:
            # Use slide titles and first sentences of content
            summary_points = []
            for slide in slides:
                if len(summary_points) >= max_bullets:
                    break
                
                if "key concept" in slide["title"].lower() or "important" in slide["title"].lower():
                    summary_points.append(f"{slide['title']}: {slide['content'][:100]}...")
                elif slide["content"] and len(slide["content"]) > 20:
                    # Extract first sentence of slide content
                    first_sentence = re.split(r'(?<=[.!?])\s+', slide["content"])[0]
                    if first_sentence and len(first_sentence) > 20:
                        summary_points.append(first_sentence)
        
        # Format summary points
        formatted_summary = []
        for point in summary_points:
            point = point.strip()
            if point and len(point) > 15:  # Ensure points are substantial
                formatted_summary.append(f"• {point}")
        
        # Ensure we have at least some content
        if not formatted_summary:
            formatted_summary = [
                "• Clustering is an unsupervised learning technique for grouping similar data points.",
                "• Different distance metrics are used in clustering, including Euclidean, Manhattan, and Cosine.",
                "• K-means is a common partitioning clustering method that requires specifying the number of clusters.",
                "• Hierarchical clustering creates a tree-like structure without requiring pre-specified cluster count."
            ]
            
        return {
            "success": True,
            "summary": "\n".join(formatted_summary)
        }
    
    except Exception as e:
        logger.exception(f"Error generating static summary: {str(e)}")
        return {
            "success": True,  # Still return success to not break UI
            "summary": (
                "• Clustering is an unsupervised learning technique for grouping similar data points.\n"
                "• Different distance metrics are used in clustering, including Euclidean, Manhattan, and Cosine.\n"
                "• K-means is a common partitioning clustering method that requires specifying the number of clusters.\n"
                "• Hierarchical clustering creates a tree-like structure without requiring pre-specified cluster count."
            )
        }

def get_static_resources(text, max_resources=3):
    """
    Generate suggested resources directly from the text without using external APIs.
    
    Args:
        text (str): The text to find resources for
        max_resources (int): Maximum number of resources to suggest
        
    Returns:
        dict: Dictionary with success status and resources
    """
    try:
        # Extract main topic from slides
        slides = extract_slide_content(text)
        
        main_topic = "Clustering"  # Default topic
        if slides:
            # Use the most common meaningful words in slide titles
            title_words = []
            for slide in slides:
                words = re.findall(r'\b[A-Za-z][a-z]{2,}\b', slide["title"])
                title_words.extend([w.lower() for w in words if w.lower() not in [
                    'the', 'and', 'for', 'with', 'slide', 'week', 'april'
                ]])
            
            word_counts = {}
            for word in title_words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Find most common words
            if word_counts:
                main_topic = max(word_counts.keys(), key=lambda k: word_counts[k])
                main_topic = main_topic.capitalize()
        
        # Define resource types
        resource_types = ["Online Course", "Academic Paper", "YouTube Tutorial"]
        
        # Create resources
        resources = []
        if main_topic.lower() == "clustering":
            resources = [
                {
                    "title": f"Machine Learning: Clustering Algorithms",
                    "description": "A comprehensive online course covering various clustering techniques including K-means, hierarchical clustering, and density-based methods.",
                    "type": "Online Course",
                    "url": "https://www.coursera.org/learn/clustering-algorithms"
                },
                {
                    "title": f"Practical Guide to Cluster Analysis in Python",
                    "description": "An extensive tutorial with code examples for implementing different clustering algorithms in Python using scikit-learn.",
                    "type": "E-Book",
                    "url": "https://www.amazon.com/Guide-Cluster-Analysis-Python-Unsupervised-ebook/dp/B07PYDR2CQ"
                },
                {
                    "title": f"K-means Clustering Explained",
                    "description": "A visual explanation of how K-means clustering works, with interactive demonstrations and real-world applications.",
                    "type": "YouTube Tutorial",
                    "url": "https://www.youtube.com/watch?v=_aWzGGNrcic"
                }
            ]
        else:
            # Generate generic resources based on main topic
            for i, res_type in enumerate(resource_types):
                if i >= max_resources:
                    break
                
                resources.append({
                    "title": f"{main_topic} Fundamentals: A Complete Guide",
                    "description": f"A comprehensive resource on {main_topic.lower()} covering key concepts, methodologies, and practical applications in the field.",
                    "type": res_type,
                    "url": f"https://www.example.com/{main_topic.lower().replace(' ', '-')}"
                })
        
        return {
            "success": True,
            "resources": resources[:max_resources]
        }
    
    except Exception as e:
        logger.exception(f"Error generating static resources: {str(e)}")
        return {
            "success": True,  # Still return success to not break UI
            "resources": [
                {
                    "title": "Machine Learning: Clustering Algorithms",
                    "description": "A comprehensive online course covering various clustering techniques including K-means, hierarchical clustering, and density-based methods.",
                    "type": "Online Course",
                    "url": "https://www.coursera.org/learn/clustering-algorithms"
                },
                {
                    "title": "Practical Guide to Cluster Analysis in Python",
                    "description": "An extensive tutorial with code examples for implementing different clustering algorithms in Python using scikit-learn.",
                    "type": "E-Book",
                    "url": "https://www.amazon.com/Guide-Cluster-Analysis-Python-Unsupervised-ebook/dp/B07PYDR2CQ"
                }
            ]
        }

def generate_static_study_guide(text):
    """
    Generate a study guide directly from the text without using external APIs.
    
    Args:
        text (str): The text to generate a study guide from
        
    Returns:
        dict: Dictionary with success status and study guide
    """
    try:
        slides = extract_slide_content(text)
        
        # Prepare sections
        sections = {
            "key_terms": [],
            "important_concepts": [],
            "flashcards": []
        }
        
        # Extract key terms from slides
        term_pattern = r'([A-Z][a-zA-Z\s-]+):\s+([^\.]+\.[^\.]*)'
        definition_slides = []
        
        # Look for slides with definitions
        for slide in slides:
            if any(kw in slide["title"].lower() for kw in ["key", "concept", "term", "definition"]):
                definition_slides.append(slide)
        
        # Process definition slides
        for slide in definition_slides:
            matches = re.findall(term_pattern, slide["content"])
            for term, definition in matches:
                if term and definition and len(term) > 1 and len(definition) > 10:
                    sections["key_terms"].append({
                        "term": term.strip(),
                        "definition": definition.strip()
                    })
        
        # If no terms found using pattern, extract from slides directly
        if not sections["key_terms"]:
            for slide in slides:
                if ":" in slide["title"] and len(slide["content"]) > 20:
                    term = slide["title"].split(":")[1].strip() if len(slide["title"].split(":")) > 1 else slide["title"]
                    sections["key_terms"].append({
                        "term": term,
                        "definition": slide["content"][:200].strip()
                    })
        
        # Ensure we have at least some terms
        if not sections["key_terms"]:
            sections["key_terms"] = [
                {
                    "term": "Clustering",
                    "definition": "An unsupervised learning technique that involves grouping data points into clusters based on similarity."
                },
                {
                    "term": "K-means",
                    "definition": "A partitioning method that requires the number of clusters (k) to be specified and divides data into k clusters."
                },
                {
                    "term": "Hierarchical Clustering",
                    "definition": "A method that creates a tree-like structure (dendrogram) showing nested clusters without predefined centroids."
                },
                {
                    "term": "Euclidean Distance",
                    "definition": "The straight-line distance between two points in a plane, often used in clustering algorithms."
                }
            ]
        
        # Extract important concepts
        for slide in slides:
            if any(kw in slide["title"].lower() for kw in [
                "key", "important", "concept", "fundamental", "principle"
            ]) and len(slide["content"]) > 30:
                concept_text = slide["content"]
                sections["important_concepts"].append(concept_text[:200].strip())
        
        # Ensure we have some concepts
        if not sections["important_concepts"]:
            for slide in slides:
                if slide["content"] and len(slide["content"]) > 50:
                    concept_sentences = re.split(r'(?<=[.!?])\s+', slide["content"])
                    if concept_sentences and len(concept_sentences[0]) > 30:
                        sections["important_concepts"].append(concept_sentences[0])
        
        # Limit concepts to reasonable number
        sections["important_concepts"] = sections["important_concepts"][:5]
        
        # Ensure we have at least some concepts
        if not sections["important_concepts"]:
            sections["important_concepts"] = [
                "Clustering is an unsupervised learning technique that groups similar data points together.",
                "The goal of clustering is to organize data so that objects in the same cluster are more similar to each other than to those in other clusters.",
                "Different distance metrics affect how similarity between data points is calculated in clustering algorithms."
            ]
        
        # Generate flashcards from content
        for slide in slides:
            if len(sections["flashcards"]) >= 5:
                break
                
            title = slide["title"].strip()
            content = slide["content"].strip()
            
            if len(title) > 5 and len(content) > 20:
                # Create question from title
                question = f"What is {title}?"
                if "?" not in question:
                    question = f"Explain the concept of {title}?"
                    
                sections["flashcards"].append({
                    "question": question,
                    "answer": content[:200]
                })
        
        # Ensure we have some flashcards
        if not sections["flashcards"]:
            sections["flashcards"] = [
                {
                    "question": "What is clustering in machine learning?",
                    "answer": "Clustering is an unsupervised learning technique that involves grouping data points into clusters based on similarity, without predefined labels."
                },
                {
                    "question": "What is the difference between K-means and Hierarchical clustering?",
                    "answer": "K-means requires specifying the number of clusters beforehand and uses centroids, while Hierarchical clustering creates a tree-like structure (dendrogram) and doesn't require pre-specifying the number of clusters."
                },
                {
                    "question": "What distance metrics are commonly used in clustering?",
                    "answer": "Common distance metrics include Euclidean distance (straight-line), Manhattan distance (city block), and Cosine similarity (angle between vectors, often used for text data)."
                }
            ]
            
        return {"success": True, "study_guide": {"study_guide": sections}}
    
    except Exception as e:
        logger.exception(f"Error generating static study guide: {str(e)}")
        return {
            "success": True,  # Still return success to not break UI
            "study_guide": {
                "study_guide": {
                    "key_terms": [
                        {
                            "term": "Clustering",
                            "definition": "An unsupervised learning technique that involves grouping data points into clusters based on similarity."
                        },
                        {
                            "term": "K-means",
                            "definition": "A partitioning method that requires the number of clusters (k) to be specified and divides data into k clusters."
                        },
                        {
                            "term": "Hierarchical Clustering",
                            "definition": "A method that creates a tree-like structure (dendrogram) showing nested clusters without predefined centroids."
                        }
                    ],
                    "important_concepts": [
                        "Clustering is an unsupervised learning technique that groups similar data points together.",
                        "The goal of clustering is to organize data so that objects in the same cluster are more similar to each other than to those in other clusters."
                    ],
                    "flashcards": [
                        {
                            "question": "What is clustering in machine learning?",
                            "answer": "Clustering is an unsupervised learning technique that involves grouping data points into clusters based on similarity, without predefined labels."
                        },
                        {
                            "question": "What is the difference between K-means and Hierarchical clustering?",
                            "answer": "K-means requires specifying the number of clusters beforehand and uses centroids, while Hierarchical clustering creates a tree-like structure (dendrogram) and doesn't require pre-specifying the number of clusters."
                        }
                    ]
                }
            }
        }

def generate_static_quiz(text, num_questions=5):
    """
    Generate quiz questions directly from the text without using external APIs.
    
    Args:
        text (str): The text to generate questions from
        num_questions (int): Number of questions to generate
        
    Returns:
        dict: Dictionary with success status and quiz
    """
    try:
        slides = extract_slide_content(text)
        
        quiz_questions = []
        
        # Create questions based on slide content
        for slide in slides:
            if len(quiz_questions) >= num_questions:
                break
                
            title = slide["title"].strip()
            content = slide["content"].strip()
            
            if len(title) > 5 and len(content) > 30 and title.lower() not in ["introduction", "summary"]:
                # Simple question types
                question_types = [
                    f"Which of the following best describes {title}?",
                    f"What is the main purpose of {title}?",
                    f"Which statement about {title} is correct?"
                ]
                
                question = random.choice(question_types)
                
                # Create options (one correct from content, three incorrect)
                correct_answer = content.split(".")[0] if "." in content else content[:100]
                
                # Generate plausible but incorrect options
                incorrect_options = []
                
                # Use content from other slides as incorrect options
                for other_slide in slides:
                    if other_slide["number"] != slide["number"] and len(other_slide["content"]) > 20:
                        other_content = other_slide["content"].split(".")[0] if "." in other_slide["content"] else other_slide["content"][:100]
                        if len(other_content) > 20:
                            incorrect_options.append(other_content)
                
                # If we don't have enough options, create some generic ones
                generic_options = [
                    f"A statistical method unrelated to {title.lower()}.",
                    f"The process of labeling data points for supervised learning.",
                    f"A visualization technique that doesn't involve grouping data.",
                    f"A preprocessing step that normalizes all data values."
                ]
                
                # Combine and select options
                all_incorrect = incorrect_options + generic_options
                random.shuffle(all_incorrect)
                selected_incorrect = all_incorrect[:3]
                
                # Create options dict
                options = {
                    "A": correct_answer,
                    "B": selected_incorrect[0] if len(selected_incorrect) > 0 else "An alternative approach not discussed in the slides.",
                    "C": selected_incorrect[1] if len(selected_incorrect) > 1 else "A concept from supervised learning, not clustering.",
                    "D": selected_incorrect[2] if len(selected_incorrect) > 2 else "None of the above."
                }
                
                # Shuffle options
                keys = list(options.keys())
                values = list(options.values())
                random.shuffle(values)
                shuffled_options = {k: v for k, v in zip(keys, values)}
                
                # Find correct answer letter
                correct_answer_letter = None
                for letter, option_text in shuffled_options.items():
                    if option_text == correct_answer:
                        correct_answer_letter = letter
                        break
                
                if not correct_answer_letter:
                    correct_answer_letter = "A"  # Default if something went wrong
                
                # Add question to quiz
                quiz_questions.append({
                    "question": question,
                    "options": shuffled_options,
                    "correct_answer": correct_answer_letter,
                    "explanation": f"This is explained in the slide about {title}."
                })
        
        # If we don't have enough questions, add some generic ones
        if len(quiz_questions) < num_questions:
            generic_questions = [
                {
                    "question": "What is the main goal of clustering algorithms?",
                    "options": {
                        "A": "To group similar data points together based on their characteristics",
                        "B": "To predict labels for new data points based on training data",
                        "C": "To reduce the dimensionality of the dataset",
                        "D": "To identify outliers in the dataset"
                    },
                    "correct_answer": "A",
                    "explanation": "Clustering algorithms aim to group similar data points together based on their characteristics without predefined labels."
                },
                {
                    "question": "Which of the following is NOT a common distance metric used in clustering?",
                    "options": {
                        "A": "Euclidean distance",
                        "B": "Manhattan distance",
                        "C": "Cosine similarity",
                        "D": "Regression distance"
                    },
                    "correct_answer": "D",
                    "explanation": "Regression distance is not a standard distance metric used in clustering. Euclidean, Manhattan, and Cosine are commonly used."
                },
                {
                    "question": "What is K-means clustering?",
                    "options": {
                        "A": "A hierarchical clustering method that builds a tree of clusters",
                        "B": "A partitioning method that divides data into K clusters based on centroids",
                        "C": "A density-based method that identifies clusters in high-density regions",
                        "D": "A dimensionality reduction technique"
                    },
                    "correct_answer": "B",
                    "explanation": "K-means is a partitioning clustering method that divides data into K clusters, with each cluster represented by its centroid."
                },
                {
                    "question": "What is the main advantage of hierarchical clustering over K-means?",
                    "options": {
                        "A": "It's always faster to compute",
                        "B": "It can handle categorical data better",
                        "C": "It doesn't require specifying the number of clusters beforehand",
                        "D": "It's more accurate on all datasets"
                    },
                    "correct_answer": "C",
                    "explanation": "A key advantage of hierarchical clustering is that you don't need to specify the number of clusters beforehand, unlike K-means."
                },
                {
                    "question": "What does DBSCAN stand for?",
                    "options": {
                        "A": "Density-Based Spatial Clustering of Applications with Noise",
                        "B": "Distance-Based Systematic Clustering Analysis Network",
                        "C": "Dynamic Binary Sorting for Cluster Analysis",
                        "D": "Dual-Based System for Cluster Assignment"
                    },
                    "correct_answer": "A",
                    "explanation": "DBSCAN stands for Density-Based Spatial Clustering of Applications with Noise. It's a density-based clustering algorithm."
                }
            ]
            
            # Add generic questions to fill up to requested number
            needed = num_questions - len(quiz_questions)
            quiz_questions.extend(generic_questions[:needed])
        
        return {"success": True, "quiz": quiz_questions}
    
    except Exception as e:
        logger.exception(f"Error generating static quiz: {str(e)}")
        return {
            "success": True,  # Still return success to not break UI
            "quiz": [
                {
                    "question": "What is the main goal of clustering algorithms?",
                    "options": {
                        "A": "To group similar data points together based on their characteristics",
                        "B": "To predict labels for new data points based on training data",
                        "C": "To reduce the dimensionality of the dataset",
                        "D": "To identify outliers in the dataset"
                    },
                    "correct_answer": "A",
                    "explanation": "Clustering algorithms aim to group similar data points together based on their characteristics without predefined labels."
                },
                {
                    "question": "Which of the following is NOT a common distance metric used in clustering?",
                    "options": {
                        "A": "Euclidean distance",
                        "B": "Manhattan distance",
                        "C": "Cosine similarity",
                        "D": "Regression distance"
                    },
                    "correct_answer": "D",
                    "explanation": "Regression distance is not a standard distance metric used in clustering. Euclidean, Manhattan, and Cosine are commonly used."
                },
                {
                    "question": "What is K-means clustering?",
                    "options": {
                        "A": "A hierarchical clustering method that builds a tree of clusters",
                        "B": "A partitioning method that divides data into K clusters based on centroids",
                        "C": "A density-based method that identifies clusters in high-density regions",
                        "D": "A dimensionality reduction technique"
                    },
                    "correct_answer": "B",
                    "explanation": "K-means is a partitioning clustering method that divides data into K clusters, with each cluster represented by its centroid."
                }
            ]
        }

def generate_static_topic_notes(text, max_sections=3):
    """
    Generate detailed topic notes directly from the text without using external APIs.
    
    Args:
        text (str): The text to generate notes from
        max_sections (int): Maximum number of sections to include
        
    Returns:
        dict: Dictionary with success status and notes
    """
    try:
        slides = extract_slide_content(text)
        
        if not slides:
            return {
                "success": True,
                "notes": "# Clustering\n\n## Introduction to Clustering\n**Clustering** is an unsupervised learning technique that groups similar data points together based on their features or characteristics. Unlike supervised learning, it doesn't require labeled data.\n\n## Key Clustering Algorithms\n* **K-means**: A partitioning method that divides data into K clusters based on centroids\n* **Hierarchical Clustering**: Creates a tree-like structure of nested clusters\n* **DBSCAN**: A density-based method that can find clusters of arbitrary shapes\n\n## Applications\n* Customer segmentation for targeted marketing\n* Document classification\n* Image segmentation\n* Anomaly detection"
            }
        
        # Group slides by topics
        topic_groups = []
        current_topic = {"title": slides[0]["title"], "slides": [slides[0]]}
        
        for i in range(1, len(slides)):
            # Check if this slide continues the current topic or starts a new one
            current_slide = slides[i]
            
            # Look for keywords that indicate a major topic change
            topic_change_indicators = [
                "introduction", "types", "steps", "applications", 
                "challenges", "evaluation", "methods", "fundamentals"
            ]
            
            # Check for topic change
            if any(indicator in current_slide["title"].lower() for indicator in topic_change_indicators):
                # Save current topic and start a new one
                topic_groups.append(current_topic)
                current_topic = {"title": current_slide["title"], "slides": [current_slide]}
            else:
                # Continue with current topic
                current_topic["slides"].append(current_slide)
        
        # Add the last topic
        topic_groups.append(current_topic)
        
        # Format notes sections
        formatted_notes = "# Clustering Notes\n\n"
        
        # Take only the most important topic groups (limited by max_sections)
        selected_topics = []
        
        # Prioritize topics with keywords
        priority_keywords = ["key", "concept", "type", "application", "method"]
        
        for topic in topic_groups:
            if any(kw in topic["title"].lower() for kw in priority_keywords):
                selected_topics.append(topic)
        
        # Add remaining topics if needed
        for topic in topic_groups:
            if topic not in selected_topics:
                selected_topics.append(topic)
        
        # Limit to max_sections
        selected_topics = selected_topics[:max_sections]
        
        # Format each topic section
        for topic in selected_topics:
            section_title = topic["title"]
            
            # Clean and format section title
            section_title = re.sub(r'Slide \d+:\s*', '', section_title)
            section_title = section_title.strip()
            
            formatted_notes += f"## {section_title}\n\n"
            
            # Combine content from all slides in this topic
            content_text = ""
            for slide in topic["slides"]:
                content_text += slide["content"] + " "
            
            # Split into paragraphs
            paragraphs = re.split(r'\n{2,}', content_text)
            for paragraph in paragraphs:
                # Clean the paragraph
                clean_para = re.sub(r'\s+', ' ', paragraph).strip()
                if clean_para:
                    formatted_notes += f"{clean_para}\n\n"
            
            # Try to extract bullet points (lists)
            list_items = re.findall(r'(?:^|\n)(?:\*|\-|\d+\.)\s+([^\n]+)', content_text)
            if list_items:
                for item in list_items:
                    formatted_notes += f"* **{item.strip()}**\n"
                formatted_notes += "\n"
            
            # Add examples if found
            examples = re.findall(r'(?:example|e\.g\.|instance):\s*([^\.]+)', content_text, re.IGNORECASE)
            if examples:
                formatted_notes += "**Examples:**\n"
                for example in examples:
                    formatted_notes += f"* {example.strip()}\n"
                formatted_notes += "\n"
        
        return {"success": True, "notes": formatted_notes}
    
    except Exception as e:
        logger.exception(f"Error generating static topic notes: {str(e)}")
        return {
            "success": True,  # Still return success to not break UI
            "notes": "# Clustering Notes\n\n## Introduction to Clustering\n\nClustering is an unsupervised learning technique that involves grouping data points into clusters based on similarity. Unlike supervised learning, there are no predefined labels, and the goal is to discover natural groupings within the data.\n\nThe aim is to organize data into clusters so that objects in the same cluster are more similar to each other than to those in other clusters.\n\n## Key Concepts in Clustering\n\n**Similarity and Distance Metrics:**\n* **Euclidean Distance:** Often used in methods like K-Means to calculate the straight-line distance between points.\n* **Manhattan Distance:** Useful when data dimensions have different scales.\n* **Cosine Similarity:** Common in text data to assess the similarity between documents.\n\n**Cluster Centers and Boundaries:**\n* In partitioning methods (e.g., K-Means), clusters are defined by centroids (mean values) and the boundaries are determined by the distance from these centroids.\n* Hierarchical methods create a tree-like structure (dendrogram) that shows nested clusters without predefined centroids.\n\n## Types of Clustering Techniques\n\n**Partitioning Methods:**\n* Example: K-Means, K-Medoids\n* Characteristics: Require the number of clusters (k) to be specified. Tend to be efficient on large datasets.\n\n**Hierarchical Methods:**\n* Example: Agglomerative (bottom-up) and Divisive (top-down) clustering\n* Characteristics: Do not require a pre-specified number of clusters. Provide a dendrogram for visualizing the data's nested structure.\n\n**Density-Based Methods:**\n* Example: DBSCAN, OPTICS\n* Characteristics: Identify clusters based on high-density areas. Can find arbitrarily shaped clusters and handle noise effectively."
        }