# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
from pathlib import Path

import pytest
from igrafx_mining_sdk.workgroup import Workgroup
from dotenv import load_dotenv
import os

# Load environment variables from .env file
dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path)

wg_id = os.environ.get('WG_ID')
wg_key = os.environ.get('WG_KEY')
wg_url = os.environ.get('WG_URL')
wg_auth = os.environ.get('WG_AUTH')
project_id = os.environ.get('PROJECT_ID')


class TestWorkgroup:
    """Tests for Workgroup class.
    Workgroup and project are pytest fixtures defined in conftest.py file.
    """

    def test_create_workgroup(self, workgroup):
        """Test to create a workgroup."""
        assert isinstance(workgroup, Workgroup)

    def test_wrong_login(self):
        """Test the login with wrong credentials."""
        with pytest.raises(Exception):
            assert Workgroup("a", "b")

    def test_projects(self, workgroup):
        """Test that there are projects in the workgroup."""
        assert len(workgroup.get_project_list()) > 0  # Since there should be projects in the workgroup

    def test_project_list(self, workgroup):
        """Test that the list of projects in a workgroup can be retrieved."""''
        assert workgroup.get_project_list()

    def test_project_from_id(self, workgroup):
        """Test that the project ID can be retrieved."""
        assert workgroup.project_from_id(project_id)
