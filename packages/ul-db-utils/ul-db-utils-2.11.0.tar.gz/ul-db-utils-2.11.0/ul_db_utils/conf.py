import os.path
from typing import Optional

THIS_LIBRARY_DIR = os.path.dirname(__file__)

APPLICATION__DB_URI: Optional[str] = os.environ.get('APPLICATION__DB_URI', None)  # none only for backward compatibility
