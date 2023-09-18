from typing import Optional


class TextDeserialisationFailureException(Exception):
    def __init__(
            self,
            text: str,
            format: str,
            file_path: Optional[str] = None,
    ):
        self.text = text
        self.format = format
        self.file_path = file_path

    def __str__(self):
        return f'Failed to Deserialise the below text. \n' \
               f'Format: {self.format} \n' \
               f"File Path: {self.file_path} \n" \
               f"Text: \n" \
               f" {self.text}"
