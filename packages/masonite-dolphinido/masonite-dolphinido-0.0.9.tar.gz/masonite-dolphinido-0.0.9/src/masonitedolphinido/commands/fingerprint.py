from masonite.commands import Command
from masonitedolphinido.dolphinido import Dolphinido

class Fingerprint(Command):
    """
    Generates audio fingerprints of the given audio file. It accepts mp3 file only

    dolphinido:fingerprint
        {audiofile : The absolute file path of the audio file to be fingerprinted. }
    """

    def __init__(self):
        super().__init__()
        self.dolphinido = Dolphinido()

    def handle(self):
        audio_file = self.argument("audiofile")
        try:
            result = self.dolphinido.create_audio(audio_file)
            if result:
                self.info("Fingerprint operation successful")		
        except Exception as err:
            self.error(str(err))
        