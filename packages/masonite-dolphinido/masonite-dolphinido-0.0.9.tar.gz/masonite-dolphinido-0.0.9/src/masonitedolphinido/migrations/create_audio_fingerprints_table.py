"""CreateAudioFingerprintsTable Migration."""

from masoniteorm.migrations import Migration


class CreateAudioFingerprintsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("audio_fingerprints") as table:
            table.increments("id")
            table.uuid("audio_id")
            table.string("fingerprint")
            table.integer("offset")
            table.timestamps()
            
            table.foreign('audio_id').references('id').on('audios').on_delete('cascade')
            

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("audio_fingerprints")
