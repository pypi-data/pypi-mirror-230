from masonite.commands import Command
from masonitedolphinido.dolphinido import Dolphinido
from masonitedolphinido.helpers import output

class RecogMic(Command):
    """
    The command recognizes audio from microphone device.

    dolphinido:recog-mic
        {duration : The number of seconds to record audio using microphone device. }
    """

    def __init__(self):
        super().__init__()
        self.dolphinido = Dolphinido()

    def handle(self):
        duration = self.argument("duration")
        try:
            result = self.dolphinido.recognize_recording(duration)
            output(result)		
        except Exception as err:
            self.error(str(err))
        