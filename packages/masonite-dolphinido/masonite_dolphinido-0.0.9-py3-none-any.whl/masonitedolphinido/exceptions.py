
class AudioDuplicate(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("Audio already exists")