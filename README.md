# Forked

This repo has been forked from:

https://github.com/disdanes/django.test.sqlite3

And updated to work with Django 1.6.

# What this does

If you want to use a replication setup with in-memory sqlite3 for testing in django, it is impossible, as sqlite does not provide replication in-memory. Using this library gets around the issue by 'faking' multiple databases by creating a single connection to a single database and accessing it in a thread-safe manner via a queue.

# Usage

In your testing settings, use the `django_test_sqlite3.db.sqlite3` backend instead of Django's provided sqlite3 one.
