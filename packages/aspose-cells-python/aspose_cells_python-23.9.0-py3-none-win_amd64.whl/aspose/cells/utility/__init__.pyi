from typing import List, Optional, Dict, Iterable
import aspose.pycore
import aspose.pydrawing
import aspose.cells
import aspose.cells.charts
import aspose.cells.digitalsignatures
import aspose.cells.drawing
import aspose.cells.drawing.activexcontrols
import aspose.cells.drawing.equations
import aspose.cells.drawing.texts
import aspose.cells.externalconnections
import aspose.cells.json
import aspose.cells.markup
import aspose.cells.metadata
import aspose.cells.numbers
import aspose.cells.ods
import aspose.cells.pivot
import aspose.cells.properties
import aspose.cells.querytables
import aspose.cells.rendering
import aspose.cells.rendering.pdfsecurity
import aspose.cells.revisions
import aspose.cells.saving
import aspose.cells.settings
import aspose.cells.slicers
import aspose.cells.tables
import aspose.cells.timelines
import aspose.cells.utility
import aspose.cells.vba
import aspose.cells.webextensions

class ExportRangeToJsonOptions:
    '''Indicates the options that exporting range to json.'''
    
    @property
    def has_header_row(self) -> bool:
        ...
    
    @has_header_row.setter
    def has_header_row(self, value : bool):
        ...
    
    @property
    def export_as_string(self) -> bool:
        ...
    
    @export_as_string.setter
    def export_as_string(self, value : bool):
        ...
    
    @property
    def export_empty_cells(self) -> bool:
        ...
    
    @export_empty_cells.setter
    def export_empty_cells(self, value : bool):
        ...
    
    @property
    def indent(self) -> str:
        '''Indicates the indent.'''
        ...
    
    @indent.setter
    def indent(self, value : str):
        '''Indicates the indent.'''
        ...
    
    ...

class JsonLayoutOptions:
    '''Represents the options of json layout type.'''
    
    @property
    def array_as_table(self) -> bool:
        ...
    
    @array_as_table.setter
    def array_as_table(self, value : bool):
        ...
    
    @property
    def ignore_null(self) -> bool:
        ...
    
    @ignore_null.setter
    def ignore_null(self, value : bool):
        ...
    
    @property
    def ignore_array_title(self) -> bool:
        ...
    
    @ignore_array_title.setter
    def ignore_array_title(self, value : bool):
        ...
    
    @property
    def ignore_object_title(self) -> bool:
        ...
    
    @ignore_object_title.setter
    def ignore_object_title(self, value : bool):
        ...
    
    @property
    def ignore_title(self) -> bool:
        ...
    
    @ignore_title.setter
    def ignore_title(self, value : bool):
        ...
    
    @property
    def convert_numeric_or_date(self) -> bool:
        ...
    
    @convert_numeric_or_date.setter
    def convert_numeric_or_date(self, value : bool):
        ...
    
    @property
    def number_format(self) -> str:
        ...
    
    @number_format.setter
    def number_format(self, value : str):
        ...
    
    @property
    def date_format(self) -> str:
        ...
    
    @date_format.setter
    def date_format(self, value : str):
        ...
    
    @property
    def title_style(self) -> aspose.cells.Style:
        ...
    
    @title_style.setter
    def title_style(self, value : aspose.cells.Style):
        ...
    
    ...

class JsonUtility:
    '''Represents the utility class of processing json.'''
    
    @overload
    @staticmethod
    def export_range_to_json(range : aspose.cells.Rangeoptions : aspose.cells.utility.ExportRangeToJsonOptions) -> str:
        '''Exporting the range to json file.
        
        :param range: The range.
        :param options: The options of exporting.
        :returns: The json string value.'''
        ...
    
    @overload
    @staticmethod
    def export_range_to_json(range : aspose.cells.Rangeoptions : aspose.cells.JsonSaveOptions) -> str:
        '''Exporting the range to json file.
        
        :param range: The range.
        :param options: The options of exporting.
        :returns: The json string value.'''
        ...
    
    @staticmethod
    def import_data(json : strcells : aspose.cells.Cells, row : int, column : int, option : aspose.cells.utility.JsonLayoutOptions) -> List[int]:
        '''Import the json string.
        
        :param json: The json string.
        :param cells: The Cells.
        :param row: The row index.
        :param column: The column index.
        :param option: The options of import json string.'''
        ...
    
    ...

