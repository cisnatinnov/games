import os
import unittest
from PIL import Image

from ai import create_app
from config.settings import Config


class ClassifyImageTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.client = self.app.test_client()
        # ensure upload folder exists
        Config.create_upload_folder()

    def tearDown(self):
        # clean uploads
        try:
            for f in os.listdir(Config.UPLOAD_FOLDER):
                if f.startswith('test_img'):
                    os.remove(os.path.join(Config.UPLOAD_FOLDER, f))
        except Exception:
            pass

    def test_classify_image_local_fallback(self):
        # create small test image in upload folder
        img_path = os.path.join(Config.UPLOAD_FOLDER, 'test_img.png')
        Image.new('RGB', (10, 10), 'red').save(img_path)

        with open(img_path, 'rb') as imgf:
            data = {
                'file': (imgf, 'test_img.png'),
                'prompt': 'Describe this image'
            }
            resp = self.client.post('/classify_image', data=data, content_type='multipart/form-data')

        self.assertEqual(resp.status_code, 200)
        j = resp.get_json()
        self.assertIsInstance(j, dict)
        self.assertIn('description', j)
        self.assertTrue(j.get('processed', False))


if __name__ == '__main__':
    unittest.main()
