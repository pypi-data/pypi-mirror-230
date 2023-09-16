"""Helper tests."""
import pytest
import sqlalchemy as sa
from mock import ANY, call, patch

from pg2elastic import helper


@pytest.mark.usefixtures("table_creator")
class TestHelper(object):
    """Helper tests."""

    @patch("pg2elastic.helper.logger")
    @patch("pg2elastic.helper.get_config")
    @patch("pg2elastic.helper.Sync")
    def test_teardown_with_drop_db(self, mock_sync, mock_config, mock_logger):
        mock_config.return_value = "tests/fixtures/schema.json"
        mock_sync.truncate_schemas.return_value = None
        with patch("pg2elastic.helper.database_exists", return_value=True):
            with patch("pg2elastic.helper.drop_database") as mock_db:
                helper.teardown(drop_db=True, config="fixtures/schema.json")
                assert mock_db.call_args_list == [
                    call(ANY),
                    call(ANY),
                ]

        mock_logger.warning.assert_not_called()

    @patch("pg2elastic.helper.logger")
    @patch("pg2elastic.helper.get_config")
    def test_teardown_without_drop_db(self, mock_config, mock_logger):
        mock_config.return_value = "tests/fixtures/schema.json"

        with patch("pg2elastic.node.Tree.build", return_value=None):
            with patch("pg2elastic.sync.Sync") as mock_sync:
                mock_sync.tree.build.return_value = None
                mock_sync.truncate_schemas.side_effect = (
                    sa.exc.OperationalError
                )
                helper.teardown(drop_db=False, config="fixtures/schema.json")
                assert mock_logger.warning.call_args_list == [
                    call(ANY),
                    call(ANY),
                ]
