import os
from typing import Optional


class TokenCache:
    def get(self) -> Optional[str]:
        raise NotImplementedError()

    def set(self, token):
        raise NotImplementedError()


class FileCache(TokenCache):
    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path

    def get(self) -> str:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                token = file.read()

            return token

    def set(self, token):
        with open(self.file_path, 'w') as file:
            file.write(token)