import os

from dotenv import load_dotenv

load_dotenv()

DATA_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
