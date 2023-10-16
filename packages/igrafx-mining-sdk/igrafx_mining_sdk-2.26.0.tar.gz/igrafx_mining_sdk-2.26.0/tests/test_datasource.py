# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
from pathlib import Path
import pytest
from igrafx_mining_sdk.project import Project
from igrafx_mining_sdk.datasource import Datasource
from igrafx_mining_sdk.workgroup import Workgroup
from dotenv import load_dotenv
import os

# Load environment variables from .env file
dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path)

NAME = os.environ.get('NAME')
TYPE = os.environ.get('TYPE')
HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')

wg_id = os.environ.get('WG_ID')
wg_key = os.environ.get('WG_KEY')
wg_url = os.environ.get('WG_URL')
wg_auth = os.environ.get('WG_AUTH')
project_id = os.environ.get('PROJECT_ID')


class TestDatasource:
    """Class for testing Datasource class.
    Workgroup and project are pytest fixtures defined in conftest.py file.
    """

    def test_create_datasource(self, workgroup):
        """Test creating a Datasource"""
        ds = Datasource(NAME, TYPE, HOST, PORT, workgroup.api_connector)
        assert isinstance(ds, Datasource)

    def test_columns(self):
        """Test the columns of a Datasource"""

        w = Workgroup(wg_id, wg_key, wg_url, wg_auth)
        p = Project(project_id, w.api_connector)
        ds = p.edges_datasource
        assert ds.columns != []

    def test_non_empty_ds(self):
        """Test that the datasource is not empty"""
        w = Workgroup(wg_id, wg_key, wg_url, wg_auth)
        project = Project(project_id, w.api_connector)
        for pr in w.get_project_list():
            try:
                len(pr.process_keys)
                project = pr
                break
            except Exception:
                continue

        ds = project.nodes_datasource
        assert 0 < len(ds.load_dataframe(load_limit=10)) <= 10

    def test_read_only(self):
        """Test that the datasource is read only"""
        w = Workgroup(wg_id, wg_key, wg_url, wg_auth)
        project = Project(project_id, w.api_connector)
        for pr in w.get_project_list():
            try:
                len(pr.process_keys)
                project = pr
                break
            except Exception:
                continue

        ds = project.edges_datasource
        pk = project.process_keys[0]
        # Test that all of those requests will fail
        with pytest.raises(Exception):
            assert ds.request(f'DELETE FROM "{ds.name}" WHERE processkey = \'{pk}\'')
        with pytest.raises(Exception):
            assert ds.request(f'INSERT INTO "{ds.name}"(processkey) VALUES (\'{pk}\')')
        with pytest.raises(Exception):
            assert ds.request(f'DROP TABLE "{ds.name}"')
            ds.drop()
        with pytest.raises(Exception):
            assert ds.request(f'ALTER TABLE "{ds.name}" DROP COLUMN processkey')

    def test_close(self, workgroup, project):
        """Test that the Datasource can be closed"""
        ds = Datasource(NAME, TYPE, HOST, PORT, workgroup.api_connector)
        # ensure connection and cursor are none
        assert ds._cursor is None
        assert ds._connection is None

        # initialize both cursor and connection
        cursor = ds.cursor
        connection = ds.connection
        assert cursor is not None
        assert connection is not None

        # close cursor and connection then check that they are none again
        ds.close()
        assert ds._cursor is None
        assert ds._connection is None
