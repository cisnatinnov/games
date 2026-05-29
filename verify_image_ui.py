import os
import io
import base64
from PIL import Image

from ai import create_app
from config.settings import Config
import chat as chat_module
import blueprints.ai_routes as ai_routes

# Prepare environment
Config.create_upload_folder()
app = create_app(Config)
client = app.test_client()

print('Running verification tests for /image endpoint and UI logic...')

# Test 1: generate_image returns a data URL
data_url = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII='
# Patch the function used by the route (ai_routes holds the reference)
ai_routes.generate_image = lambda prompt: data_url
resp = client.post('/image', json={'text': 'test prompt'})
print('\nTest 1: data URL response')
print('Status:', resp.status_code)
print('JSON:', resp.get_json())

# Test 2: generate_image returns a filename located in the uploads folder
img_path = os.path.join(Config.UPLOAD_FOLDER, 'generated_image.png')
# create 1x1 red PNG
Image.new('RGB', (1, 1), (255, 0, 0)).save(img_path)
ai_routes.generate_image = lambda prompt: 'generated_image.png'
resp2 = client.post('/image', json={'text': 'test prompt file'})
print('\nTest 2: filename response')
print('Status:', resp2.status_code)
print('JSON:', resp2.get_json())

# Try to fetch the uploaded file via the app route
fetch = client.get('/uploads/generated_image.png')
print('\nFetch uploaded file:')
print('Status:', fetch.status_code)
print('Content-Type:', fetch.headers.get('Content-Type'))
print('Content-Length:', len(fetch.data) if fetch.status_code == 200 else 'N/A')

# Cleanup
try:
    os.remove(img_path)
except Exception:
    pass

print('\nVerification complete.')
