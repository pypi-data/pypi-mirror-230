from masoniteorm.models import Model
from masoniteorm.scopes import UUIDPrimaryKeyMixin
from masonitedolphinido.helpers import grouper


class Audio(Model, UUIDPrimaryKeyMixin):
    __fillable__ = ["id", "hash", "metadata", "hashcount"]

    def get_by_hash(self, hash: str):
        return self.query().where("hash", hash).first()
    
    def get_by_id(self, id):
        return self.query().find(id)
    
    def update_hash_count(self, hashcount):
        self.hashcount = hashcount
        self.save()
        return self


class AudioFingerprint(Model):
    __fillable__ = ['id', 'audio_id', 'fingerprint', 'offset']
    
    def match(self, fingerprints):
        return self.query().where_in('fingerprint', fingerprints).get()

    def insert(self, audio: Audio, fingerprints: set):
        values = []
        for fingerprint, offset in fingerprints:
            values.append({'audio_id': audio.id, 'fingerprint': fingerprint, 'offset': offset})
            
        for split_values in grouper(values, 1000):
            self.query().builder.new().bulk_create(split_values)