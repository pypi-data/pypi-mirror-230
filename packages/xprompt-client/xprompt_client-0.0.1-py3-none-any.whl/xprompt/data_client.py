import os.path
import time

import requests

import xprompt
from xprompt.constants import BACKEND_ENDPOINT
from xprompt_common.errors import TryAgain


class OutputConvertorClient:
    @staticmethod
    def file_ext_to_output_format(file_path: str):
        _, ext = os.path.splitext(file_path)
        if ext in [".wav", ".mp3"]:
            return "audio/mpeg"

        raise ValueError(f"Unsupported file type: {file_path}")

    @classmethod
    def convert(cls, text, output_type, **kwargs):
        start = time.time()
        timeout = kwargs.pop("timeout", None)
        payload = {"text": text, "output_format": output_type, **kwargs}

        while True:
            try:
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "Authorization": f"Bearer {xprompt.api_key}",
                }

                response = requests.post(
                    f"{BACKEND_ENDPOINT}/convert_output", headers=headers, json=payload
                )
                if response.status_code == 409:
                    raise TryAgain("failed with conflict")

                return response.content
            except TryAgain:
                if timeout is not None and time.time() > start + timeout:
                    raise
                time.sleep(1)


if __name__ == "__main__":
    res = OutputConvertorClient()
    xprompt.api_key = ""
    content = res.convert("sure, this is something", "audio")
    with open("./test.mp3", "wb") as f:
        f.write(content)

    print("done")
