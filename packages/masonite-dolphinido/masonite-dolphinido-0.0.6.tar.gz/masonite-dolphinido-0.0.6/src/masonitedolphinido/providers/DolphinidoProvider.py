from masonite.packages import PackageProvider
from masonitedolphinido.commands import *

class DolphinidoProvider(PackageProvider):

    def configure(self):
        self.root("masonitedolphinido")\
        .name("masonitedolphinido")\
        .config("config/fingerprint.py", publish=True)\
        .migrations(
            "migrations/create_audios_table.py", 
            "migrations/create_audio_fingerprints_table.py"
        )
    
    def register(self):
        self.application.make('commands')\
        .add(FingerprintCommand())\
        .add(RadioCommand())\
        .add(RecogFileCommand())\
        .add(RecogMicCommand())\
        .add(RecogRadioCommand())
    
    def boot(self):
        pass
