from genai_compat import genai

import os
from dotenv import load_dotenv
import PIL.Image
import io

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

try:
  genai.configure(api_key=api_key)
except Exception:
  # ignore configure errors to preserve compatibility
  pass

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
    # Try primary image generation call (some SDK versions accept generation_config)
    try:
      response = model.generate_content(
        f"Generate an image of: {prompt}",
        generation_config={"response_mime_type": "image/png"}
      )
    except TypeError:
      # Older/other SDK variants may not accept generation_config
      response = model.generate_content(f"Generate an image of: {prompt}")

    # Helper: extract raw bytes from many possible response shapes
    def _extract_bytes(resp):
      import base64

      # If response is None
      if resp is None:
        return None

      # If response has parts (common pattern)
      parts = getattr(resp, 'parts', None)
      if parts:
        for p in parts:
          fd = getattr(p, 'file_data', None)
          if fd is None:
            # Some SDKs use 'binary' or 'data' directly on the part
            for attr in ('binary', 'data', 'image_bytes'):
              val = getattr(p, attr, None)
              if val:
                return bytes(val) if isinstance(val, (bytes, bytearray)) else base64.b64decode(val)
            continue

          # file_data may expose several shapes
          #  - .data as bytes or base64 string
          #  - .binary or .b64 fields
          data = getattr(fd, 'data', None)
          if data:
            if isinstance(data, (bytes, bytearray)):
              return bytes(data)
            if isinstance(data, str):
              try:
                return base64.b64decode(data)
              except Exception:
                pass

          for attr in ('binary', 'b64', 'base64'):
            val = getattr(fd, attr, None)
            if val:
              return base64.b64decode(val)

      # Some responses include base64 embedded in text
      text = getattr(resp, 'text', None) or getattr(resp, 'output', None)
      if isinstance(text, str) and 'data:image' in text:
        try:
          # find base64 part after comma
          idx = text.find('base64,')
          if idx != -1:
            b64 = text[idx + len('base64,'):].strip()
            return base64.b64decode(b64)
        except Exception:
          pass

      # If resp is a plain dict-like object
      if isinstance(resp, dict):
        # search common keys
        for key in ('image', 'image_bytes', 'data', 'binary', 'file'):
          val = resp.get(key)
          if val:
            if isinstance(val, (bytes, bytearray)):
              return bytes(val)
            if isinstance(val, str):
              try:
                return base64.b64decode(val)
              except Exception:
                pass

      return None

    image_bytes = _extract_bytes(response)

    # Last-resort: if the SDK returned a string with an embedded base64
    if not image_bytes and hasattr(response, 'text') and isinstance(response.text, str):
      import re, base64
      m = re.search(r'data:image\/(?:png|jpeg);base64,([A-Za-z0-9+/=\n\r]+)', response.text)
      if m:
        try:
          image_bytes = base64.b64decode(m.group(1))
        except Exception:
          image_bytes = None

    if not image_bytes:
      return 'Image generation did not return image bytes.'

    # Save the image data to a file using PIL
    try:
      image = PIL.Image.open(io.BytesIO(image_bytes))
      output_path = "generated_image.png"
      image.save(output_path)
      return output_path
    except Exception as e:
      return f"Failed to save generated image: {str(e)}"

  except Exception as e:
    print(f"An exception occurred during image generation: {e}")
    # --- MODIFIED: Return the specific error from the API ---
    # This will give you a much clearer idea of what's wrong (e.g., billing required, API not enabled, etc.)
    return f"Sorry, an error occurred while generating the image. Google API Error: {str(e)}"