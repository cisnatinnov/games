import google.generativeai as genai
import os
from dotenv import load_dotenv
import PIL.Image
import io

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

def chat(text, character=None, custom_prompt=None):
  try:
    # Character system instructions mapping
    system_instructions = {
        'gandalf': "You are Gandalf the Grey, a wise wizard from Middle-earth. Respond to the user with profound wisdom, mystical magic reference, poetic fantasy tones, and occasional friendly warnings. Keep your sentences atmospheric and magical. Always speak in character.",
        'jarvis': "You are JARVIS, a highly sophisticated AI butler. Respond with absolute politeness, clean cyber and technology terminology, address the user as 'Sir' or 'Ma'am', and maintain a helpful, futuristic, and sleek intelligence-system persona. Always stay in character.",
        'sherlock': "You are Sherlock Holmes, the brilliant Victorian consulting detective. Respond with razor-sharp analytical deduction, keen observation of minute details, classy British politeness, and intellectual eccentricity. Always stay in character.",
        'ramsay': "You are Gordon Ramsay, the energetic, high-octane celebrity chef. Respond with intense passion, dramatic kitchen/cooking metaphors, clean but dramatic exclamation marks, and hilarious but constructive critiques of user statements. Always stay in character."
    }
    
    instruction = None
    if character == 'custom' and custom_prompt:
        instruction = custom_prompt
    elif character in system_instructions:
        instruction = system_instructions[character]
        
    if instruction:
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=instruction)
    else:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
    response = model.generate_content(text)
    return response.text
  except Exception as e:
    print(f"An error occurred during chat: {e}")
    # --- MODIFIED: Return the specific error message ---
    return f"An error occurred: {str(e)}"

def classify_image(prompt, image_path):
  """Classify an image using the configured generative model.

  This attempts multiple safe ways to send the image to the API (bytes, stream,
  and base64 embedded) and falls back to a minimal local description if the
  API calls fail.
  """
  vision_model = genai.GenerativeModel('gemini-2.5-flash')
  try:
    # Read image bytes once
    with open(image_path, 'rb') as f:
      img_bytes = f.read()

    # Try: pass a file-like object (io.BytesIO)
    try:
      response = vision_model.generate_content([prompt, io.BytesIO(img_bytes)])
      if hasattr(response, 'text') and response.text:
        return response.text
    except Exception:
      pass

    # Try: pass raw bytes in a dict (some SDK versions accept this)
    try:
      response = vision_model.generate_content([prompt, {"image": img_bytes}])
      if hasattr(response, 'text') and response.text:
        return response.text
    except Exception:
      pass

    # Try: embed base64 image data in the prompt as a fallback
    try:
      import base64
      b64 = base64.b64encode(img_bytes).decode('utf-8')
      prompt_with_b64 = f"{prompt}\n\nImage (base64): data:image/png;base64,{b64}"
      response = vision_model.generate_content(prompt_with_b64)
      if hasattr(response, 'text') and response.text:
        return response.text
    except Exception:
      pass

    # If all remote attempts failed, provide a small local description
    try:
      with PIL.Image.open(image_path) as im:
        return f"Local fallback: format={im.format}, mode={im.mode}, size={im.size}"
    except Exception as e:
      return f"Image classification failed and fallback also failed: {str(e)}"

  except Exception as e:
    print(f"An error occurred during image classification: {e}")
    return f"An error occurred: {str(e)}"

def generate_image(prompt):
  try:
    model = genai.GenerativeModel('gemini-2.5-pro')
    
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