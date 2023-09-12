"""CreateAudiosTable Migration."""

from masoniteorm.migrations import Migration


class CreateAudiosTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("audios") as table:
            table.uuid('id').primary()
            table.string('hash_id').unique().nullable()
            table.integer('hash_count').nullable()
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("audios")
