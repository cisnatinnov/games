import google.genai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

def chat(text):
  response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=text
  )
  try:
    return response.text
  except:
    return 'An exception occurred'

def generate_image(prompt):
  response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=prompt
  )
  try:
    # Check for media attribute (list of dicts)
    if hasattr(response, "media") and response.media: # type: ignore
      for item in response.media: # type: ignore
        if "url" in item and item["url"]:
          return item["url"]
        if "base64" in item and item["base64"]:
          return "data:image/png;base64," + item["base64"]
    # Check for image_url attribute
    if hasattr(response, "image_url") and response.image_url: # type: ignore
      return response.image_url # type: ignore
    # Check for image_base64 attribute
    if hasattr(response, "image_base64") and response.image_base64: # type: ignore
      return "data:image/png;base64," + response.image_base64 # type: ignore
    # If the model returns a text saying it can't generate images, handle gracefully
    if hasattr(response, "text") and response.text:
      if "can't create images" in response.text.lower() or "text-based ai" in response.text.lower():
        return None
      return response.text
    return None
  except Exception:
    return None
