import unittest
import sys, os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

SCRIPT_DIR = str(Path(__file__).absolute().parent)
ZETANE_DIR = str(Path(__file__).absolute().parent.parent)
sys.path.append(ZETANE_DIR)

import zetane

class BaseTestCase(unittest.TestCase):
  def setUp(self):
    load_dotenv(SCRIPT_DIR + "/.env")
    api_key = os.getenv("ZETANE_API_KEY", None)
    address = os.getenv("ZETANE_ADDRESS", None)
    zetane.config(api_key=api_key, address=address)
