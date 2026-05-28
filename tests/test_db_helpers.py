from unittest import TestCase, main

from app_core import db
from app_core.db import connection, safe_queries


class DbFacadeTests(TestCase):
    def test_db_facade_reexports_expected_helpers(self):
        self.assertIs(db.get_connection, connection.get_connection)
        self.assertIs(db.get_database_url, connection.get_database_url)
        self.assertIs(db.is_db_available, connection.is_db_available)
        self.assertIs(db.safe_fetch_one, safe_queries.safe_fetch_one)
        self.assertIs(db.safe_fetch_all, safe_queries.safe_fetch_all)
        self.assertIs(db.safe_execute, safe_queries.safe_execute)
        self.assertIs(db.fetch_one, safe_queries.fetch_one)
        self.assertIs(db.fetch_all, safe_queries.fetch_all)
        self.assertIs(db.execute_write, safe_queries.execute_write)


if __name__ == "__main__":
    main()
