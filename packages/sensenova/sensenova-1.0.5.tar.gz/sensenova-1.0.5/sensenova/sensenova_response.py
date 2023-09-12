from typing import Optional


class SensenovaResponse:
    def __init__(self, data, headers):
        self._headers = headers
        self.data = data