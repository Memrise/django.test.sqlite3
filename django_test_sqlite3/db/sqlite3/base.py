from Queue import Queue

from django.db.backends.sqlite3.base import (DatabaseError,
                                             IntegrityError,
                                             DatabaseFeatures,
                                             DatabaseOperations,
                                             DatabaseWrapper as OriginalDatabaseWrapper)


CONNECTION_QUEUE = Queue()


class DatabaseWrapper(OriginalDatabaseWrapper):
    def get_new_connection(self, conn_params):
        if CONNECTION_QUEUE.empty():
            conn = super(DatabaseWrapper, self).get_new_connection(conn_params)
            CONNECTION_QUEUE.put(conn)
        else:
            conn = CONNECTION_QUEUE.get()
            CONNECTION_QUEUE.put(conn)

        return conn
