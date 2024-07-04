import unittest
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches
from app.features.dynamo.tools import PptxSubLoader
from app.services.logger import setup_logger

class TestPptxSubLoader(unittest.TestCase):
    def setUp(self):
        self.logger = setup_logger(__name__)
        self.sample_pptx_content = BytesIO()
        prs = Presentation()
        slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)
        title = slide.shapes.title
        title.text = "Hello, World!"
        prs.save(self.sample_pptx_content)
        self.sample_pptx_content.seek(0)

    def test_load(self):
        loader = PptxSubLoader(self.sample_pptx_content, 'pptx')
        documents = loader.load()
        self.assertTrue(len(documents) > 0)
        self.assertIn('Hello, World!', documents[0].page_content)

if __name__ == '__main__':
    unittest.main()
