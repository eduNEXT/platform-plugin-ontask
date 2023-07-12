"""
Open edX Django plugin for OnTask Learning.
"""
import os
from pathlib import Path
from .extensions.filters import AddInstructorLimesurveyTab

__version__ = '0.1.0'

ROOT_DIRECTORY = Path(os.path.dirname(os.path.abspath(__file__)))
