import os
import tempfile
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import re
from faster_whisper import WhisperModel

# Initialize Whisper model
# Options for model size: "tiny", "base", "small", "medium", "large-v2"
model_size = "base"
whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")

def extract_youtube_id(url):
    """Extract YouTube video ID from a URL."""
    # Common YouTube URL patterns
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\?\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\?\s]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_youtube_transcript(youtube_url):
    """Get transcript from a YouTube video URL."""
    try:
        # Extract video ID from the URL
        video_id = extract_youtube_id(youtube_url)
        
        if not video_id:
            return {"success": False, "error": "Could not extract YouTube video ID from the URL."}
        
        try:
            # First try to get the transcript directly without listing all available ones
            transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = ' '.join([entry['text'] for entry in transcript_data])
            return {"success": True, "transcript": full_transcript}
        except Exception as inner_e:
            # If direct method fails, try the more complex approach with language detection
            try:
                # Get available transcripts
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Try to get English transcript first
                try:
                    transcript = transcript_list.find_transcript(['en'])
                except:
                    # If no English transcript, try to get any transcript and translate it
                    available_transcripts = list(transcript_list)
                    if not available_transcripts:
                        return {"success": False, "error": "No transcripts available for this video."}
                    
                    # Get the first available transcript
                    transcript = available_transcripts[0]
                    
                    # Try to translate it if it's not in English
                    if transcript.language_code != 'en':
                        try:
                            transcript = transcript.translate('en')
                        except:
                            # Continue with original language if translation fails
                            pass
                
                # Get the transcript text
                transcript_data = transcript.fetch()
                
                # Combine all text pieces
                full_transcript = ' '.join([entry['text'] for entry in transcript_data])
                
                return {"success": True, "transcript": full_transcript}
            except Exception as nested_e:
                return {"success": False, "error": f"Failed to get transcript: {str(nested_e)}"}
    
    except Exception as e:
        return {"success": False, "error": f"Error getting YouTube transcript: {str(e)}"}

def transcribe_audio(audio_file):
    """Transcribe audio file using Hugging Face's faster-whisper implementation."""
    temp_path = None
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            # Write uploaded file to the temp file
            temp_file.write(audio_file.getvalue())
            temp_path = temp_file.name
        
        # Transcribe the audio file with faster-whisper
        segments, info = whisper_model.transcribe(temp_path, beam_size=5)
        
        # Check if transcription was successful
        if not segments:
            return {"success": False, "error": "No speech detected in the audio file."}
        
        # Combine all segments into a full transcript
        transcription_text = ""
        for segment in segments:
            transcription_text += segment.text + " "
        
        # Clean up the temporary file
        if temp_path:
            os.unlink(temp_path)
            temp_path = None
        
        if not transcription_text.strip():
            return {"success": False, "error": "Transcription result is empty."}
        
        return {"success": True, "transcript": transcription_text.strip()}
    
    except Exception as e:
        # Clean up the temporary file if it exists
        if temp_path:
            try:
                os.unlink(temp_path)
            except:
                pass
        
        return {"success": False, "error": f"Error transcribing audio: {str(e)}"}
