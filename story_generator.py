from dotenv import load_dotenv
import os
from google import genai
from gtts import gTTS
# To convert the speech to audio stream
from io import BytesIO

from google.genai import types
from io import BytesIO
import wave
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")

# Client instance:
client = genai.Client(api_key=GOOGLE_API_KEY)

# Function to create advanced prompt based on style
def create_advanced_prompt(style):
    # --- Base prompt ---
    base_prompt = f"""
    **Your Persona:** You are a friendly and engaging storyteller. Your goal is to tell a story that is fun and easy to read.
    **Your Main Goal:** Write a story in simple, clear, and modern English.
    **Your Task:** Create one single story that connects all the provided images in order.
    **Style Requirement:** The story must fit the '{style}' genre.
    **Core Instructions:**
    1.  **Tell One Single Story:** Connect all images into a narrative with a beginning, middle, and end.
    2.  **Use Every Image:** Include a key detail from each image.
    3.  **Creative Interpretation:** Infer the relationships between the images.
    4.  **Nationality**: Use only Indian Names,Characters, Places , Persona Etc.
    **Output Format:**
    -   **Title:** Start with a simple and clear title.
    -   **Length:** The story must be between 4 and 5 paragraphs.
    """

    # --- Add Style-Specific Instructions (System Instruction)---
    style_instruction = ""
    if style == "Morale":
        style_instruction = "\n**Special Section:** After the story, you MUST add a section starting with the exact tag `[MORAL]:` followed by the single-sentence moral of the story."
    elif style == "Mystery":
        style_instruction = "\n**Special Section:** After the story, you MUST add a section starting with the exact tag `[SOLUTION]:` that reveals the culprit and the key clue."
    elif style == "Thriller":
        style_instruction = "\n**Special Section:** After the story, you MUST add a section starting with the exact tag `[TWIST]:` that reveals a final, shocking twist."

    return base_prompt + style_instruction

# Function taht takes images and style and generates story
def generate_story(images,style):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        # contents=[images, "Write a short on the given set of images"]
        contents=[images, create_advanced_prompt(style)]
        )
    return response.text

# Function: To narrate the story (takes text and returns audio stream)
# def narrate_story(story_text):
#     try:
#         tts = gTTS(text=story_text, lang='en', slow=False)
#         # BytesIO will create an temporary audio and then store the audio within the file (this wont be stored on device permanently i.e. it will exist until our app is running)
#         audio_stream = BytesIO()
#         # The following line will convert text into audio and write into the audio_stream
#         tts.write_to_fp(audio_stream)
#         # This will set the pointer to the start of the stream, we add this because always the pointer will start from the very beginning
#         audio_stream.seek(0)
#         return audio_stream
#     except Exception as e:
#         return f"Error in generating narration: {e}"

def narrate_story(story_text: str):
    """
    Generate narration audio for the story using Gemini TTS.
    Returns an in-memory WAV file (BytesIO) that Streamlit can play.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",  # TTS-capable model
            contents=story_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            # Pick any prebuilt TTS voice you like; 'Kore' is just an example
                            voice_name="Kore",
                        )
                    )
                ),
            ),
        )

        # PCM audio bytes from the response
        pcm_data = response.candidates[0].content.parts[0].inline_data.data

        # Wrap PCM in a proper WAV container so Streamlit can play it easily
        audio_stream = BytesIO()
        with wave.open(audio_stream, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)   # 16-bit audio
            wf.setframerate(24000)
            wf.writeframes(pcm_data)

        audio_stream.seek(0)
        return audio_stream

    except Exception as e:
        # Log if you want: print(e)
        return None