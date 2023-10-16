# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE

from pathlib import Path
import pytest
from igrafx_mining_sdk.project import Project
from igrafx_mining_sdk.workgroup import Workgroup
from igrafx_mining_sdk.graph import Graph
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


class TestGraph:
    """Tests for the Graph class.
    Workgroup and project are pytest fixtures defined in conftest.py file.
    """
    def test_graph_creation(self, workgroup, project):
        """Test the creation of a Graph object."""
        w = Workgroup(wg_id, wg_key, wg_url, wg_auth)
        project = Project(project_id, w.api_connector)
        g = project.graph()
        assert isinstance(g, Graph)

    def test_graph_instance(self):
        """Test the creation of a Graph object."""
        # Test with another project because indexation time returns error
        w = Workgroup(wg_id, wg_key, wg_url, wg_auth)
        project = Project(project_id, w.api_connector)
        g = project.get_graph_instances(limit=1)[0]
        assert g.rework_total is not None
        assert g.concurrency_rate is not None

    def test_graph_with_bad_edges(self):
        """Test a graph that has bad edges."""
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / 'data' / 'graphs' / 'graph_with_invalid_edges.json'
        with pytest.raises(Exception):
            assert Graph.from_json(14, str(file_path))

    def test_from_json(self):
        """Test the creation of a Graph object from a json string and display."""
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / 'data' / 'graphs' / 'graph.json'
        g = Graph.from_json(0, str(file_path))
        assert len(g) > 0
