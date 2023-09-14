import os.path
from typing import Optional

THIS_LIBRARY_DIR = os.path.dirname(__file__)

APPLICATION__DB_ADDRESS: Optional[str] = os.environ['APPLICATION__DB_ADDRESS']  # Required to be
APPLICATION__DB_PORT: Optional[str] = os.environ['APPLICATION__DB_PORT']  # Required to be
APPLICATION__DB_SCHEMA: Optional[str] = os.environ['APPLICATION__DB_SCHEMA']  # Required to be
APPLICATION__DB_USER: Optional[str] = os.environ['APPLICATION__DB_USER']  # Required to be
APPLICATION__DB_PASSWORD: Optional[str] = os.environ['APPLICATION__DB_PASSWORD']  # Required to be
APPLICATION__DB_DATABASE: Optional[str] = os.environ['APPLICATION__DB_DATABASE']  # Required to be
