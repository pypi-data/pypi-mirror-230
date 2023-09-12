from masonite.commands import Command
from masonitedolphinido.dolphinido import Dolphinido
from masonitedolphinido.helpers import output
import time

class RecogRadio(Command):
    """
    Recognizes audio from radio station.

    dolphinido:recog-radio
        {station : The radio station frequency to track and monitor. }
        {--loop : Loop the radio in order to listen to the radio in realtime. }
    """

    def __init__(self):
        super().__init__()
        self.dolphinido = Dolphinido()

    def handle(self):
        station = self.argument("station")
        option = self.option("loop")

        radio = self.dolphinido.radio()
        radio.tune(float(station))
        try:
            if option:
                while True: 
                    samples = radio.capture()
                    match = self.dolphinido.recognize_audio(samples)	
                    output(match)
                    time.sleep(10)
            else:
                samples = radio.capture()
                match = self.dolphinido.recognize_audio(samples)
                output(match)	
        except Exception as err:
            self.error(str(err))
        