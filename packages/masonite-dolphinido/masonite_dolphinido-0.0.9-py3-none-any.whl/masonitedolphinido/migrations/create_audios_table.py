"""CreateAudiosTable Migration."""

from masoniteorm.migrations import Migration


class CreateAudiosTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("audios") as table:
            table.uuid('id').primary()
            table.string('hash').unique()
            table.binary('metadata').nullable()
            table.integer('hashcount').nullable()
            
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("audios")
