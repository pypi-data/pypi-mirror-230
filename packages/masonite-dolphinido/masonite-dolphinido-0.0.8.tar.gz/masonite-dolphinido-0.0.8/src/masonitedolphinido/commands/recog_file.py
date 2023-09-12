from masonite.commands import Command
from masonitedolphinido.dolphinido import Dolphinido
from masonitedolphinido.helpers import output

class RecogFile(Command):
    """
    The command recognizes audio from audio file.

    dolphinido:recog-file
        {audiofile : The absolute file path of the audio file to be recognized. }
    """

    def __init__(self):
        super().__init__()
        self.dolphinido = Dolphinido()

    def handle(self):
        audio_file = self.argument("audiofile")
        try:
            result = self.dolphinido.recognize_file(audio_file)
            output(result)		
        except Exception as err:
            self.error(str(err))
        