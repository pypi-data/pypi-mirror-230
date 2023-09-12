from masonite.packages import PackageProvider
from masonitedolphinido.commands.fingerprint import Fingerprint
from masonitedolphinido.commands.radio import Radio
from masonitedolphinido.commands.recog_file import RecogFile
from masonitedolphinido.commands.recog_mic import RecogMic
from masonitedolphinido.commands.recog_radio import RecogRadio

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
        .add(Fingerprint())\
        .add(Radio())\
        .add(RecogFile())\
        .add(RecogMic())\
        .add(RecogRadio())
    
    def boot(self):
        pass
