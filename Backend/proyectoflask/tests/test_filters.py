import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from PIL import Image
from app.filters import apply_anamorphic, apply_logo, apply_sepia

class TestImageFilters(unittest.TestCase):
    def setUp(self):
        # Crear una imagen de prueba
        self.test_image = Image.new('RGB', (100, 100), color = 'white')

    def test_apply_sepia(self):
        result_image = apply_sepia(self.test_image)
        self.assertIsInstance(result_image, Image.Image)

    def test_apply_anamorphic(self):
        result_image = apply_anamorphic(self.test_image)
        self.assertIsInstance(result_image, Image.Image)

    def test_apply_logo(self):
        result_image = apply_logo(self.test_image)
        self.assertIsInstance(result_image, Image.Image)

if __name__ == '__main__':
    unittest.main()
