##Motivation:
This is a dropin replacement for the django.db.backends.sqlite3 for use with **TESTING**. 

It solves the problem of testing code where models could be queried from multiple slaves or databases. Django provides a TEST_MIRROR setting, but it does not work correctly with in memory sqlite databases.

This is not intended to be used in production (although it might be able to)


##Usage:

Place db inside your project folder or where you keep your database backends

inside `settings.py`

<pre>
if 'test' in sys.argv:
	from Queue import Queue
	TEST_CONNECTION_QUEUE = Queue()

	TEST_ENGINE = 'project.db.sqlite3'
	DATABASES = {
		'default': {
			'ENGINE' : TEST_ENGINE,
		},
		'slave1': {
			'ENGINE' : TEST_ENGINE,
		}
	} 
</pre>

## Problem:
When we run our testsuite there are databases created for each of our database slaves, and the data does not exist equally on each of the slaves. This causes tests to fail or the developer to create 3-4 nested mock statements to ignore the Model.objects.using call. The purpose of the fix is to create a drop in solution that all developers can benefit from that does not increase the run time of the tests but allows us to not have to work around our .using statements.

### Fixing Test Mirroring:
Test Mirroring when specified increases the runtime of the tests by 10x and it's broken (does not do what you expect) for using Sqlite in memory databases.


### Using Sqlite Shared Cache:

Sqlite Shared Cache is similiar to a database named ":memory:" because the database is created in memory but by specifying a specific file URI "file::memory:?cache=shared" you are able to allow multiple connections to use the same data.

By default Sqlite databases created with the ":memory:" name are private and do not share data among connections.

Why we can't use the sqlite Shared Cache:

1. [File URI's](http://www.sqlite.org/uri.html) are not enabled by default in Sqlite3, you either need to compile it with a certain option or you specify it in configuration at runtime after a database is initialized

2. There is a [patch](http://bugs.python.org/file24420/sqlite-uri.v3.patch) for Python 3.4(?!) to turn this option on, with the native sqlite3 library

3. There are other sqlite libraries that do support using a File URI for sqlite, but the support for Shared Cache is extremely difficult to use.
#####Taken from [Another Python Sqlite Wrapper Documentation](http://apidoc.apsw.googlecode.com/hg/tips.html#shared-cache-mode)

>SQLite supports a shared cache mode where multiple connections to the same database can share a cache instead of having their own. It is not recommended that you use this mode.

>A big issue is that busy handling is not done the same way. The timeouts and handlers are ignored and instead SQLITE_LOCKED_SHAREDCACHE extended error is returned. Consequently you will have to do your own busy handling. (SQLite ticket, APSW ticket 59)

>The amount of memory and I/O saved is trivial compared to Python’s overal memory and I/O consumption. You may also need to tune the shared cache’s memory back up to what it would have been with seperate connections to get the same performance.

>The shared cache mode is targetted at embedded systems where every byte of memory and I/O matters. For example an MP3 player may only have kilobytes of memory available for SQLite.

None of us want to configure our own busy waiting for tests.

##Solution
#####Sharing the initial 'default' connection with all Database threads:

I created my own instance of the django.db.backends.sqlite3 database backend inside of db/sqlite3

Initially my poor understanding of the Django infrastructure led to a number of failed attempts.

1. Tried to create a global instance of DatabaseWrapper and return the same object upon it's initialization
    Problem: This doesn't properly register the different alias' objects and django will only see 'default'
2. Tried to create a global instance of the connection inside of create_test_db inside DatabaseCreation
    Problem: The connection and cursor created in this method actually aren't used - django only creates it to initialize the connection ahead of time.

Django database creation for tests happens in the following order:

0. django.db.\_\_init__.py is called and the settings are parsed for db backends and which code to use
0.1. DatabaseWrapper is created - which initializes classes for DatabaseFeatures, DatabaseOperations, DatabaseClient, DatabaseCreation, DatabaseIntrospection, and DatabaseValidation
    note: BaseDatabaseWrapper/DatabaseWrapper inherits from local which is a python thread
1. TestRunner is created
2. TestRunner inspects settings
3. TestRunner does a 1st pass to figure out the order of creation and which ones should or shouldnt be created (test mirroring)
4. Test Mirroring doesn't work for in memory sqlite databases because django always creates a test database for them regardless of your TEST_MIRROR settings. Test names for sqlite3 always return ":memory:", this is set in the database backend code.
5. TestRunner makes a call to create\_test\_db inside of [DatabaseCreation class](https://github.com/django/django/blob/stable/1.3.x/django/test/simple.py#L307)
6. The create\_test\_db method doesn't exist in the django.db.backends.sqlite3, I had to overload the method from it's parent BaseDatabaseCreation in order to modify it
7. create_test_db makes a call to 'syncdb', it makes a call to 'flush', it also initializes the cache tables, and then it creates a cursor... but that cursor isn't used for anything other than initializing the database.
8. Whenever a query gets executed - the DatabaseWrapper returns a cursor and calls cursor.execute

#####My solution:

1. I created a setting called TEST\_CONNECTION\_QUEUE initialized with a python Queue()
2. TEST\_CONNECTION\_QUEUE is a threadsafe queue which holds a single cursor object
3. I modified create\_test\_db to only run syncdb/flush/cache initialization for the 'default' database
4. Each time a cursor is asked for in cursor.execute, the DatabaseWrapper will pull the cursor from TEST\_CONNECTION\_QUEUE and put it back.
5. Removing the mock .using calls from a couple tests verifies that the solution works and the tests all pass so nothing was broken in the process.

Note: This technique *might* be able to be used on MySQL as an early form of connection pooling.