from typing import List


class Model:
    def __init__(self, name: str, columns: List[str]):
        self.name = name
        self.columns = columns
