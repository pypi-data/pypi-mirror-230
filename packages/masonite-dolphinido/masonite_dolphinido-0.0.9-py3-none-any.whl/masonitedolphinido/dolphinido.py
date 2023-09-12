import pickle
from pyaudioreader.audiofile import AudioFile
from pysdrradio.radio import Radio
from tinytag import TinyTag
from masonitedolphinido import settings as config
from masonitedolphinido.models import Audio, AudioFingerprint
from masonitedolphinido.fingerprint import Fingerprint
from masonitedolphinido.audiometa import Audiometa
from masonitedolphinido.exceptions import AudioDuplicate
from masonitedolphinido.recognition import AudioRecognizer, FileRecognizer, MicrophoneRecognizer

class Dolphinido:

    def __init__(self):
        self.audios = Audio()
        self.fingerprints = AudioFingerprint()

        self.fingerprint =  Fingerprint()

        self.limit = config.FINGERPRINT_LIMIT
        if self.limit == -1:
            self.limit = None

    def radio(self)-> Radio: 
        radio = Radio()
        return radio

    def create_audio(self, audio_file, audio_id=None):
        hash = AudioFile.get_hash(audio_file)
        audiotag = TinyTag.get(audio_file)
        metadata = self.__encode_audio_tag(audiotag)

        audio = self.audios.get_by_hash(hash)
        if audio:
            raise AudioDuplicate

        if audio_id:
            audio = self.audios.create({"id": audio_id, "hash": hash, "metadata": metadata})   
        else:
            audio = self.audios.create({"hash": hash, "metadata": metadata})

        hashcount = self.create_fingerprint(audio_file)
        audio.update_hash_count(hashcount)
        return audio

    def create_fingerprint(self, audio_file):
        hash = AudioFile.get_hash(audio_file)
        audio = self.audios.get_by_hash(hash)
        hashcount = 0

        if audio and audio.hashcount is None:
            fingerprints = self.fingerprint_file(audio_file) 
            hashcount = len(fingerprints)
            self.fingerprints.insert(audio, fingerprints)
        return hashcount
        
    def fingerprint_file(self, audio_file, limit=None):
        if limit is None:
            limit = self.limit

        channels, frame_rate = AudioFile.read(audio_file, limit)
        fingerprints = set()

        for _ , channel in enumerate(channels, start=1):
            hashes = self.fingerprint.fingerprint(channel, Fs=frame_rate)
            fingerprints |= set(hashes)

        return fingerprints

    def fingerprint_audio(self, samples):
        fingerprints = self.fingerprint.fingerprint(samples)
        return fingerprints
    
    def recognize_file(self, audio_file):
        recognizer = FileRecognizer(self)
        return recognizer.recognize(audio_file)

    def recognize_recording(self, seconds):
        recognizer = MicrophoneRecognizer(self)
        return recognizer.recognize(seconds)
    
    def recognize_audio(self, samples):
        recognizer = AudioRecognizer(self)
        return recognizer.recognize(samples)

    def find_matches(self, fingerprints):
        return self.fingerprints.match(fingerprints)

    def find_audio(self, audio_id):
        audio = self.audios.get_by_id(audio_id)
        payload = audio.metadata
        audiotag = self.__decode_audio_tag(payload)
        audio.metadata = audiotag
        return audio
    
    def audio_exists(self, audio_file):
        hash = AudioFile.get_hash(audio_file)
        audio = self.audios.get_by_hash(hash)
        if audio:
            return True
        else:
            return False
	
    def __encode_audio_tag(self, audiotag: TinyTag):
        audiometa = Audiometa(
            title=audiotag.title,
            artist=audiotag.artist,
            album=audiotag.album,
            genre=audiotag.genre,
            year=audiotag.year,
            filesize=audiotag.filesize,
            duration=audiotag.duration,
            bitrate=audiotag.bitrate,
        )
        payload = pickle.dumps({"audiometa": audiometa })
        return payload
    
    def __decode_audio_tag(self, payload):
        unserialized = pickle.loads(payload)
        audiotag = unserialized["audiometa"]
        return audiotag