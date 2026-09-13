# -*- coding: utf-8 -*-
"""
PARVAT NETRA -- Discovery Bridge for E2E Playwright Tests
Enables automated execution under: python -m unittest discover -s tests -p "test_*.py"
"""

from tests.e2e_playwright_test import TestE2EPlaywright

if __name__ == "__main__":
    import unittest
    unittest.main()
