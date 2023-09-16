"""
Tests for "validate" logic of "PostgreSQL" DB Connector class.
"""

# System Imports.

# Internal Imports.
from .test_core import TestPostgresqlDatabaseParent
from tests.connectors.core.test_validate import CoreValidateTestMixin


class TestPostgresqlValidate(TestPostgresqlDatabaseParent, CoreValidateTestMixin):
    """
    Tests "PostgreSQL" DB Connector class validation logic.
    """
    @classmethod
    def setUpClass(cls):
        # Run parent setup logic.
        super().setUpClass()

        # Also call CoreTestMixin setup logic.
        cls.set_up_class()

        # Define database name to use in tests.
        cls.test_db_name = '{0}test_validate'.format(cls.test_db_name_start)

        # Ensure database does not currently exists.
        # Guarantees tests are done from a consistent state.
        try:
            cls.connector.database.drop(cls.test_db_name, display_query=False, display_results=False)
        except cls.connector.errors.database_does_not_exist:
            # Database already exists, as we want.
            pass

        # Create desired database.
        cls.connector.database.create(cls.test_db_name)

        # Select desired database.
        cls.connector.database.use(cls.test_db_name)

        # Check that database has no tables.
        results = cls.connector.tables.show()
        if len(results) > 0:
            for result in results:
                cls.connector.tables.drop(result)

        # Import here to prevent errors if database type is not installed on system.
        from py_dbcn.connectors.postgresql.validate import (
            QUOTE_COLUMN_FORMAT,
            QUOTE_IDENTIFIER_FORMAT,
            QUOTE_ORDER_BY_FORMAT,
            QUOTE_STR_LITERAL_FORMAT,
        )

        # Initialize variables.
        cls._quote_columns_format = '{0}{1}{0}'.format(QUOTE_COLUMN_FORMAT, '{0}')
        cls._quote_select_identifier_format = '{0}{1}{0}'.format(QUOTE_IDENTIFIER_FORMAT, '{0}')
        cls._quote_order_by_format = '{0}{1}{0}'.format(QUOTE_ORDER_BY_FORMAT, '{0}')
        cls._quote_str_literal_format = '{0}{1}{0}'.format(QUOTE_STR_LITERAL_FORMAT, '{0}')

    def test__column_quote_format(self):
        # Verify quote str is as we expect.
        self.assertText('"{0}"', self._quote_columns_format)

    def test__select_identifier_quote_format(self):
        # Verify quote str is as we expect.
        self.assertText('"{0}"', self._quote_select_identifier_format)

    def test__order_by_quote_format(self):
        # Verify quote str is as we expect.
        self.assertText('"{0}"', self._quote_order_by_format)

    def test__str_literal_quote_format(self):
        # Verify quote str is as we expect.
        self.assertText("'{0}'", self._quote_str_literal_format)
