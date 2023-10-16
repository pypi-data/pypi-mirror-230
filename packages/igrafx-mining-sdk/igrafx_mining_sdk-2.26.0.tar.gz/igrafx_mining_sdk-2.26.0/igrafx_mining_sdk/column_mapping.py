# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE

from enum import Enum
from typing import List, Union


class FileType(str, Enum):
    """Type of the file that can be added."""
    csv = "csv"
    xls = "xls"
    xlsx = "xlsx"


class FileStructure:
    """ A FileStructure used to create a column mapping"""
    def __init__(self, file_type: FileType, charset: str = "UTF-8", delimiter: str = ",", quote_char: str = '"',
                 escape_char: str = '\\',
                 eol_char: str = "\\r\\n", comment_char: str = "#", sheet_name: str = None,
                 header: bool = True):
        """ Creates a FileStructure used to create a column mapping

        :param file_type: the type of the file (CSV, XLS, XLSX)
        :param charset: the charset of the file (UTF-8, ...)
        :param delimiter: the delimiter of the file (';', ',', ...)
        :param quote_char: the character to quote field in the file ('\',...)
        :param escape_char: the character to escape('\\', ...)
        :param eol_char: the character for the end of line ('\\n')
        :param header: the character to comment ('#')
        :param comment_char: boolean to say if the file contains a header
        :param sheet_name: the name of the sheet in Excel file
        """

        self.file_type = file_type
        self.charset = charset
        self.delimiter = delimiter
        self.quote_char = quote_char
        self.escape_char = escape_char
        self.eol_char = eol_char
        self.header = header
        self.comment_char = comment_char
        self.sheet_name = sheet_name

    def to_dict(self):
        """Returns the JSON dictionnary format of the FileStructure"""

        res = {
            'fileType': self.file_type.value,
            'charset': self.charset,
            'delimiter': self.delimiter,
            'quoteChar': self.quote_char,
            'escapeChar': self.escape_char,
            'eolChar': self.eol_char,
            'header': self.header,
            'commentChar': self.comment_char,
        }
        if self.sheet_name is not None:
            res['sheetName'] = self.sheet_name
        return res


class DimensionAggregation(Enum):
    """Class DimensionAggregation for the aggregation types used in column mapping"""
    FIRST = "FIRST"
    LAST = "LAST"
    DISTINCT = "DISTINCT"


class GroupedTasksDimensionAggregation(Enum):
    """Class GroupedTasksDimensionAggregation for the aggregation types used in column mapping"""
    FIRST = "FIRST"
    LAST = "LAST"


class MetricAggregation(Enum):
    """Class MetricAggregation for the aggregation types used in column mapping"""
    FIRST = "FIRST"
    LAST = "LAST"
    MIN = "MIN"
    MAX = "MAX"
    SUM = "SUM"
    AVG = "AVG"
    MEDIAN = "MEDIAN"


class ColumnType(Enum):
    """Class ColumnType for the column types used in column mapping"""
    CASE_ID = "case_id"
    TASK_NAME = "task_name"
    TIME = "time"
    METRIC = "metric"
    DIMENSION = "dimension"


class Column:
    """A Column used in the column mapping"""
    def __init__(self, name: str, index: int, column_type: ColumnType, *, is_case_scope: bool = False,
                 aggregation: Union[MetricAggregation, DimensionAggregation] = None, grouped_tasks_columns: [] = None,
                 grouped_tasks_aggregation: Union[GroupedTasksDimensionAggregation, MetricAggregation] = None,
                 unit: str = None, time_format: str = None):
        """
        :param name: the name of the column
        :param index: the index of the column
        :param column_type: the type of the column, based on ColumnType
        :param is_case_scope: boolean to say if the column is a case scope column
        :param aggregation: the aggregation of the column
        :param grouped_tasks_columns: list of columns indices that are grouped
        :param grouped_tasks_aggregation: the aggregation of the grouped tasks
        :param unit: the unit of the column
        :param time_format: the time format of the column
        """

        self.name = name
        self.index = index
        self.column_type = column_type
        self.is_case_scope = is_case_scope
        self.aggregation = aggregation
        self.grouped_tasks_columns = grouped_tasks_columns
        self.grouped_tasks_aggregation = grouped_tasks_aggregation
        self.unit = unit
        self.time_format = time_format

        if self.column_type == ColumnType.TIME:
            if time_format is None:
                raise ValueError("time_format is required for time column")
        else:
            if self.time_format is not None:
                raise ValueError("time_format can only be used with 'time' column type")

        if any(p is not None for p in [self.aggregation, self.unit]) and self.column_type not in [
            ColumnType.METRIC, ColumnType.DIMENSION]:
            raise ValueError(f"Aggregation and unit parameters are not allowed for {self.column_type.value} columns")

        if self.column_type == ColumnType.METRIC and self.aggregation is not None and self.aggregation not in MetricAggregation:
            raise ValueError("Aggregation of a 'metric' column type must be a MetricAggregation")

        if self.column_type == ColumnType.DIMENSION and self.aggregation is not None and self.aggregation not in DimensionAggregation:
            raise ValueError("Aggregation of a 'dimension' column type must be a DimensionAggregation")

        if self.column_type == ColumnType.METRIC and self.grouped_tasks_aggregation is not None and self.grouped_tasks_aggregation not in MetricAggregation:
            raise ValueError("Grouped task aggregation of a 'METRIC' column type must be a MetricAggregation")

        if self.column_type == ColumnType.DIMENSION and self.grouped_tasks_aggregation is not None and self.grouped_tasks_aggregation not in GroupedTasksDimensionAggregation:
            raise ValueError(
                "Grouped task aggregation of a 'DIMENSION' column type must be a GroupedTasksDimensionAggregation")

        if self.grouped_tasks_columns is not None and self.column_type != ColumnType.TASK_NAME:
            raise ValueError("Attribute 'grouped_tasks_columns' can only be used with 'TASK_NAME' column type")

    def to_dict(self):
        """Returns the JSON dictionary format of the Column"""

        res = {'columnIndex': self.index}
        if self.aggregation is not None:
            res['aggregation'] = self.aggregation.value
        if self.unit is not None:
            res['unit'] = self.unit
        if self.column_type == ColumnType.TIME:
            res['format'] = self.time_format
        elif self.column_type in [ColumnType.METRIC, ColumnType.DIMENSION]:
            res['name'] = self.name
            res['isCaseScope'] = self.is_case_scope
        if self.grouped_tasks_columns is not None:
            res['groupedTasksColumns'] = self.grouped_tasks_columns
        if self.grouped_tasks_aggregation is not None:
            res['groupedTasksAggregation'] = self.grouped_tasks_aggregation
        return res


class ColumnMapping:
    """Description of the columnMapping before sending a file"""
    def __init__(self, column_list: List[Column]):
        """ Creates a ColumnMapping

        :param column_list: the list of columns to use
        """
        column_indices = [c.index for c in column_list]
        if len(set(column_indices)) != len(column_indices):
            raise ValueError("Duplicate column indices")

        self.case_id_column = self.__get_columns_from_type(column_list, ColumnType.CASE_ID, expected_num=1)[0]
        self.task_name_column = self.__get_columns_from_type(column_list, ColumnType.TASK_NAME, expected_num=1)[0]
        self.time_columns = self.__get_columns_from_type(column_list, ColumnType.TIME, expected_num=[1, 2])
        self.metric_columns = self.__get_columns_from_type(column_list, ColumnType.METRIC)
        self.dimension_columns = self.__get_columns_from_type(column_list, ColumnType.DIMENSION)

        if self.task_name_column.grouped_tasks_columns is not None:
            if any(c.grouped_tasks_aggregation is None for c in self.metric_columns + self.dimension_columns):
                raise ValueError('If using "grouped_tasks_columns" for "task_name_column", please provide "grouped_task_aggregations" for other columns')

            if self.task_name_column.index not in self.task_name_column.grouped_tasks_columns:
                raise ValueError(
                    'The "grouped_tasks_columns" list must include at least an index of a column of type "TASK_NAME"')

            if self.case_id_column.index in self.task_name_column.grouped_tasks_columns:
                raise ValueError(
                    'The "grouped_tasks_columns" list cannot contain the index of a column of type "CASE_ID"')

            required_types = {ColumnType.METRIC, ColumnType.DIMENSION, ColumnType.TIME}
            other_types = set(c.column_type for c in self.metric_columns + self.dimension_columns + self.time_columns)
            # Check for the intersection of required_types and types of other columns.
            # If there is no intersection (none of the required types are present), raise an error
            if not required_types.intersection(other_types):
                raise ValueError(
                    'The "grouped_tasks_columns" list must contain the index of a column of type "METRIC", "DIMENSION", or "TIME"')

        if self.task_name_column.grouped_tasks_columns is None:
            if any(c.grouped_tasks_aggregation is not None for c in self.metric_columns + self.dimension_columns):
                raise ValueError('If not using "grouped_tasks_columns" for "task_name_column", please do not provide "grouped_task_aggregations" for other columns')

    def __get_columns_from_type(self, column_list: List[Column], filter: ColumnType, *,
                                expected_num: Union[int, List[int]] = None) -> List[Column]:
        """Returns a list of columns based on their type

        :param column_list: the list of columns to use
        :param filter: the type of the column
        :param expected_num: the expected number of columns
        :return: the list of columns
        """
        filtered_list = [c for c in column_list if c.column_type == filter]
        if expected_num is not None:
            if isinstance(expected_num, int):
                if len(filtered_list) != expected_num:
                    raise ValueError(f"Number of {filter} columns should be {expected_num}")
            else:
                if len(filtered_list) not in expected_num:
                    raise ValueError(f"Number of {filter} columns should be one of following values: {expected_num}")
        return filtered_list

    def to_dict(self):
        """Returns the JSON dictionary format of the ColumnMapping"""
        return {
            'caseIdMapping': self.case_id_column.to_dict(),
            'activityMapping': self.task_name_column.to_dict(),  # activity = task_name
            'timeMappings': [c.to_dict() for c in self.time_columns],
            'dimensionsMappings': [c.to_dict() for c in self.dimension_columns],
            'metricsMappings': [c.to_dict() for c in self.metric_columns],
        }
