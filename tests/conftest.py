from pathlib import Path

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env():
    # Load environment variables from .env file
    dotenv_path = Path(__file__).parent / "../.env"
    load_dotenv(dotenv_path=dotenv_path)
