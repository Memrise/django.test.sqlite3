from django.db.backends.sqlite3.creation import OriginalDatabaseCreation


class DatabaseCreation(OriginalDatabaseCreation):

    def _create_test_db(self, verbosity, autoclobber):
        """
        Creates a test database, prompting the user for confirmation if the
        database already exists. Returns the name of the test database created.
        """
        test_database_name = super(DatabaseCreation, self)._create_test_db(verbosity, autoclobber)

        if verbosity >= 1:
            print "Creating test database for alias '%s'..." % (self.connection.alias)

        # Get a cursor (even though we don't need one yet). This has the side
        # effect of initializing the test database.
        self.connection.cursor()

        return test_database_name
