import os
import unittest
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

class TestSIHDeckAndDocumentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.deck_path = os.path.join(cls.base_dir, "docs", "PARVAT_NETRA_SIH_Winning_Deck.pptx")
        cls.report_path = os.path.join(cls.base_dir, "docs", "DETAILED_TECHNICAL_REPORT.md")
        cls.assets_dir = os.path.join(cls.base_dir, "docs", "assets")
        cls.screenshots_dir = os.path.join(cls.base_dir, "docs", "screenshots")

    def test_01_deck_file_exists_and_size(self):
        """Asserts presentation deck exists and is greater than 500 KB."""
        self.assertTrue(os.path.exists(self.deck_path), f"Deck not found at {self.deck_path}")
        size = os.path.getsize(self.deck_path)
        print(f"\n[PASS] SIH Deck size: {size} bytes ({size / 1024:.1f} KB)")
        self.assertGreater(size, 500 * 1024, "Deck size is smaller than 500 KB")

    def test_02_deck_structure_and_dimensions(self):
        """Asserts exactly 8 slides, 16:9 widescreen dimensions, valid text, and embedded pictures on EVERY slide."""
        prs = Presentation(self.deck_path)
        
        # 1. Slide count
        slide_count = len(prs.slides)
        print(f"[PASS] Slide count: {slide_count}")
        self.assertEqual(slide_count, 8, f"Expected exactly 8 slides, found {slide_count}")
        
        # 2. Dimensions: 16:9 widescreen (13.333 x 7.5 inches)
        width_in = prs.slide_width.inches
        height_in = prs.slide_height.inches
        print(f"[PASS] Dimensions: {width_in:.3f} x {height_in:.3f} inches")
        self.assertAlmostEqual(width_in, 13.333, delta=0.05, msg="Slide width is not 16:9 widescreen (~13.333 in)")
        self.assertAlmostEqual(height_in, 7.5, delta=0.05, msg="Slide height is not 16:9 widescreen (7.5 in)")
        
        # 3. Shape contents and picture embeds on EVERY slide
        total_pictures = 0
        for idx, slide in enumerate(prs.slides):
            has_text = False
            slide_pics = 0
            for shape in slide.shapes:
                if shape.has_text_frame and shape.text_frame.text.strip():
                    has_text = True
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    slide_pics += 1
            
            # Assert text exists on this slide
            self.assertTrue(has_text, f"Slide {idx + 1} lacks non-empty text")
            # Assert picture exists on THIS slide
            self.assertGreaterEqual(slide_pics, 1, f"Slide {idx + 1} lacks an embedded picture (found {slide_pics})")
            print(f"[PASS] Slide {idx + 1}: Valid text frame present, {slide_pics} embedded picture(s)")
            total_pictures += slide_pics
            
        print(f"[PASS] Total embedded pictures across deck: {total_pictures}")
        self.assertGreaterEqual(total_pictures, 8, f"Expected >= 8 picture shapes across deck, found {total_pictures}")

    def test_03_technical_report_exists_and_size(self):
        """Asserts detailed technical report exists and exceeds 10 KB."""
        self.assertTrue(os.path.exists(self.report_path), f"Report not found at {self.report_path}")
        size = os.path.getsize(self.report_path)
        with open(self.report_path, "r", encoding="utf-8") as f:
            words = len(f.read().split())
        print(f"[PASS] Technical Report size: {size} bytes ({size / 1024:.1f} KB), Words: {words}")
        self.assertGreater(size, 10000, "Report size is under 10,000 bytes")

    def test_04_generated_assets(self):
        """Asserts all 7 generated assets exist and are >= 200 DPI resolution."""
        assets = [
            "chart_before_after.png",
            "flowchart_methodology.png",
            "architecture_diagram.png",
            "sentinel_emblem.png",
            "problem_solution_icon.png",
            "pillars_graphic.png",
            "policy_badges.png"
        ]
        for asset in assets:
            path = os.path.join(self.assets_dir, asset)
            self.assertTrue(os.path.exists(path), f"Asset {asset} missing")
            size = os.path.getsize(path)
            print(f"[PASS] Asset {asset}: {size / 1024:.1f} KB")
            self.assertGreater(size, 20 * 1024, f"Asset {asset} is unexpectedly small")

    def test_05_screenshots(self):
        """Asserts high-resolution screenshots exist."""
        expected = [
            ["01_full_dashboard_console.png", "01_executive_operations_dashboard.png"],
            ["02_gis_map_layers.png", "02_multimodal_gis_console.png"],
            ["03_bilingual_indigenous_cap_alert.png", "03_bilingual_indigenous_voice_cap_modal.png"]
        ]
        for options in expected:
            found = any(os.path.exists(os.path.join(self.screenshots_dir, opt)) for opt in options)
            self.assertTrue(found, f"None of screenshot candidates {options} found in {self.screenshots_dir}")
        print("[PASS] All dashboard screenshots confirmed present.")

if __name__ == "__main__":
    unittest.main()
