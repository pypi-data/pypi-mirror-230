__app_name__ = "xprompt"
__version__ = "0.0.1"

import os
from typing import Optional

from xprompt.admin_client import login
from xprompt.openai_client import (
    OpenAIChatCompletion,
    OpenAICompletion,
    OpenAIEmbedding,
)

api_key = os.environ.get("API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")

# Path of a file with an API key, whose contents can change. Supercedes
# `api_key` if set.  The main use case is volume-mounted Kubernetes secrets,
# which are updated automatically.
api_key_path: Optional[str] = os.environ.get("API_KEY_PATH")

debug = False
log = None  # Set to either 'debug' or 'info', controls console logging


__all__ = [
    "OpenAIChatCompletion",
    "OpenAICompletion",
    "OpenAIEmbedding",
    "login",
    "api_key",
    "openai_api_key",
    "api_key_path",
    "debug",
    "log",
]
