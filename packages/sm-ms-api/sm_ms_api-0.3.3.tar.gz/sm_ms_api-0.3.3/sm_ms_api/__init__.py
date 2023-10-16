from io import BytesIO
from pathlib import Path

import requests


class SMMS(object):
    root: str = "https://sm.ms/api/v2/"

    def __init__(self, token: str):
        self.header = {"Authorization": token}

    def upload_image(self, file: Path | str | BytesIO, name=None) -> str:
        if isinstance(file, str) or isinstance(file, Path):
            with open(file, "rb") as file:
                files = {"smfile": file}
        else:
            files = {"smfile": (name, file.getvalue())}
        res = requests.post(self.root + "upload", files=files, headers=self.header)
        res = res.json()
        if res["success"]:
            return res["data"]["url"]
        elif res["code"] == "image_repeated":
            return res["images"]
        else:
            raise ImageUploadError(res["message"])


class ImageUploadError(Exception):
    pass
