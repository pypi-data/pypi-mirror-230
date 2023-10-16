# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE

from pathlib import Path
from igrafx_mining_sdk.project import Project, FileStructure
from igrafx_mining_sdk.column_mapping import Column, ColumnType, ColumnMapping, FileType
from igrafx_mining_sdk.datasource import Datasource
from igrafx_mining_sdk.workgroup import Workgroup
import pytest
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


class TestProject:
    """Tests for Project class.
    Workgroup and project are pytest fixtures defined in conftest.py file.
    """

    def test_project_exists(self, workgroup, project):
        """Test that a project exists."""
        project_exists = project.exists
        assert project_exists is True

    def test_init_project(self, workgroup, project):
        """Test initialization of a project."""
        assert isinstance(project, Project)

    def test_get_project_name(self, workgroup, project):
        """ Test that the project name is returned and correct."""
        project_name = project.get_project_name()
        assert project_name == "Test Project"

    @pytest.mark.dependency()
    def test_reset(self, workgroup, project):
        """Test that a project can be reset."""
        assert project.reset()

    @pytest.mark.dependency(depends=["TestProject::test_reset"])  # Will skip test if test_reset fails
    def test_add_column_mapping(self, workgroup, project):
        """Test that a column mapping can be created."""
        filestructure = FileStructure(
            file_type=FileType.xlsx,
            sheet_name="Sheet1"
        )
        column_list = [
            Column('case_id', 0, ColumnType.CASE_ID),
            Column('task_name', 1, ColumnType.TASK_NAME),
            Column('time', 2, ColumnType.TIME, time_format="yyyy-MM-dd'T'HH:mm")
        ]
        column_mapping = ColumnMapping(column_list)
        assert project.add_column_mapping(filestructure, column_mapping)

    def test_column_mapping_exists(self, workgroup, project):
        """Test that a column mapping can be created."""
        assert project.column_mapping_exists

    def test_get_mapping_infos(self, workgroup, project):
        """Test that the correct mapping infos can be returned"""
        assert project.get_mapping_infos()

    def test_add_csv_file(self, workgroup, project):
        """Test that a csv file can be added to a project."""
        project.reset()
        filestructure = FileStructure(
            file_type=FileType.csv,
        )
        column_list = [
            Column('Case ID', 0, ColumnType.CASE_ID),
            Column('Activity', 1, ColumnType.TASK_NAME),
            Column('Start Date', 2, ColumnType.TIME, time_format='dd/MM/yyyy HH:mm'),
            Column('End Date', 3, ColumnType.TIME, time_format='dd/MM/yyyy HH:mm'),
        ]
        column_mapping = ColumnMapping(column_list)
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / 'data' / 'tables' / 'testdata.csv'
        assert project.add_column_mapping(filestructure, column_mapping)
        assert project.add_file(str(file_path))

    def test_add_xlsx_file(self, workgroup, project):
        """Test that an xlsx file can be added to a project."""
        project.reset()
        filestructure = FileStructure(
            file_type=FileType.xlsx,
            sheet_name="Sheet1"
        )
        column_list = [
            Column('Case ID', 0, ColumnType.CASE_ID),
            Column('Start Timestamp', 1, ColumnType.TIME, time_format='yyyy/MM/dd HH:mm:ss.SSS'),
            Column('Complete Timestamp', 2, ColumnType.TIME, time_format='yyyy/MM/dd HH:mm:ss.SSS'),
            Column('Activity', 3, ColumnType.TASK_NAME),
            Column('Ressource', 4, ColumnType.DIMENSION),
        ]
        column_mapping = ColumnMapping(column_list)
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / 'data' / 'tables' / 'p2pShortExcel.xlsx'
        assert project.add_column_mapping(filestructure, column_mapping)
        assert project.add_file(str(file_path))

    def test_add_xls_file(self, workgroup, project):
        """Test that an xls file can be added to a project."""
        project.reset()
        filestructure = FileStructure(
            file_type=FileType.xls,
            sheet_name="Sheet1"
        )
        column_list = [
            Column('Case ID', 0, ColumnType.CASE_ID),
            Column('Start Timestamp', 1, ColumnType.TIME, time_format='yyyy/MM/dd HH:mm:ss.SSS'),
            Column('Complete Timestamp', 2, ColumnType.TIME, time_format='yyyy/MM/dd HH:mm:ss.SSS'),
            Column('Activity', 3, ColumnType.TASK_NAME),
            Column('Ressource', 4, ColumnType.DIMENSION),
        ]
        column_mapping = ColumnMapping(column_list)
        base_dir = Path(__file__).resolve().parent
        file_path = base_dir / 'data' / 'tables' / 'p2pShortExcel.xls'
        assert project.add_column_mapping(filestructure, column_mapping)
        assert project.add_file(str(file_path))

    def test_graph(self, workgroup, project):
        """Test the creation of a graph."""
        assert project.graph is not None

    def test_graph_instances(self):
        """Test the graph instances."""
        w = Workgroup(wg_id, wg_key, wg_url, wg_auth)
        project = Project(project_id, w.api_connector)
        print(project_id)
        assert len(project.get_graph_instances(limit=3, shuffle=False)) == 3
        assert len(project.get_graph_instances(limit=3, shuffle=True)) == 3

    def test_datasources_types(self):
        """Test the types of the datasources"""
        w = Workgroup(wg_id, wg_key, wg_url, wg_auth)
        project = Project(project_id, w.api_connector)
        assert project.nodes_datasource.__class__ == Datasource
        assert project.edges_datasource.__class__ == Datasource
        assert project.cases_datasource.__class__ == Datasource

    def test_get_project_variants(self, workgroup, project):
        """Test that the project correct variants are returned."""
        assert project.get_project_variants(1, 3)

    def test_get_project_completed_cases(self, project):
        """Test that the projects correct completed cases are returned."""
        # No Search Case ID
        assert project.get_project_completed_cases(1, 3)
        # With Search Case ID
        assert project.get_project_completed_cases(1, 3, "IF-1609205")



