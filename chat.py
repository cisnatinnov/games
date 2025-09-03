from google.generativeai import GenerativeModel, configure
import os
from dotenv import load_dotenv
import PIL.Image
import io

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

configure(api_key=api_key)

def chat(text):
  try:
    model = GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(text)
    return response.text
  except Exception as e:
    print(f"An error occurred during chat: {e}")
    # --- MODIFIED: Return the specific error message ---
    return f"An error occurred: {str(e)}"

def classify_image(prompt, image_path):
  try:
    vision_model = GenerativeModel('gemini-2.5-flash')
    img = PIL.Image.open(image_path)
    response = vision_model.generate_content([prompt, img])
    return response.text
  except Exception as e:
    print(f"An error occurred during image classification: {e}")
    # --- MODIFIED: Return the specific error message ---
    return f"An error occurred: {str(e)}"

def generate_image(prompt):
  try:
    model = GenerativeModel('gemini-2.5-pro')
    
    response = model.generate_content(
      f"Generate an image of: {prompt}",
      generation_config={"response_mime_type": "image/png"}
    )

    image_data = response.parts[0].file_data

    # Save the image data to a file using PIL
    image_bytes = image_data.data
    image = PIL.Image.open(io.BytesIO(image_bytes))
    output_path = "generated_image.png"
    image.save(output_path)

    return output_path

  except Exception as e:
    print(f"An exception occurred during image generation: {e}")
    # --- MODIFIED: Return the specific error from the API ---
    # This will give you a much clearer idea of what's wrong (e.g., billing required, API not enabled, etc.)
    return f"Sorry, an error occurred while generating the image. Google API Error: {str(e)}"