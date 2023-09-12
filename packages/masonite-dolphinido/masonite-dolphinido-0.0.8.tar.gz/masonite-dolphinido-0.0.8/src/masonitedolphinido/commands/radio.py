from masonite.commands import Command
from masonitedolphinido.dolphinido import Dolphinido

class Radio(Command):
    """
    The command plays an fm radio station using RTL-SDR dongle.

    dolphinido:radio
        {station : The radio station frequency. }
    """

    def __init__(self):
        super().__init__()
        self.dolphinido = Dolphinido()

    def handle(self):
        station = self.argument("station")
        try:
            radio = self.dolphinido.radio()
            radio.tune(float(station))
            radio.play()		
        except Exception as err:
            self.error(str(err))
        