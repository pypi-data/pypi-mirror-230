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

class Timeline:
    '''Summary description of Timeline View
    Due to MS Excel, Excel 2003 does not support Timeline'''
    
    @property
    def caption(self) -> str:
        '''Returns the caption of the specified Timeline.'''
        ...
    
    @caption.setter
    def caption(self, value : str):
        '''Returns or sets the caption of the specified Timeline.'''
        ...
    
    @property
    def name(self) -> str:
        '''Returns the name of the specified Timeline'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Returns or sets the name of the specified Timeline'''
        ...
    
    @property
    def left_pixel(self) -> int:
        ...
    
    @left_pixel.setter
    def left_pixel(self, value : int):
        ...
    
    @property
    def top_pixel(self) -> int:
        ...
    
    @top_pixel.setter
    def top_pixel(self, value : int):
        ...
    
    @property
    def width_pixel(self) -> int:
        ...
    
    @width_pixel.setter
    def width_pixel(self, value : int):
        ...
    
    @property
    def height_pixel(self) -> int:
        ...
    
    @height_pixel.setter
    def height_pixel(self, value : int):
        ...
    
    ...

class TimelineCollection:
    '''Specifies the collection of all the Timeline objects on the specified worksheet.
    Due to MS Excel, Excel 2003 does not support Timeline.'''
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, row : int, column : int, base_field_name : str) -> int:
        '''Add a new Timeline using PivotTable as data source
        
        :param pivot: PivotTable object
        :param row: Row index of the cell in the upper-left corner of the Timeline range.
        :param column: Column index of the cell in the upper-left corner of the Timeline range.
        :param base_field_name: The name of PivotField in PivotTable.BaseFields
        :returns: The new add Timeline index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, dest_cell_name : str, base_field_name : str) -> int:
        '''Add a new Timeline using PivotTable as data source
        
        :param pivot: PivotTable object
        :param dest_cell_name: The cell name in the upper-left corner of the Timeline range.
        :param base_field_name: The name of PivotField in PivotTable.BaseFields
        :returns: The new add Timeline index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, row : int, column : int, base_field_index : int) -> int:
        '''Add a new Timeline using PivotTable as data source
        
        :param pivot: PivotTable object
        :param row: Row index of the cell in the upper-left corner of the Timeline range.
        :param column: Column index of the cell in the upper-left corner of the Timeline range.
        :param base_field_index: The index of PivotField in PivotTable.BaseFields
        :returns: The new add Timeline index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, dest_cell_name : str, base_field_index : int) -> int:
        '''Add a new Timeline using PivotTable as data source
        
        :param pivot: PivotTable object
        :param dest_cell_name: The cell name in the upper-left corner of the Timeline range.
        :param base_field_index: The index of PivotField in PivotTable.BaseFields
        :returns: The new add Timeline index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, row : int, column : int, base_field : aspose.cells.pivot.PivotField) -> int:
        '''Add a new Timeline using PivotTable as data source
        
        :param pivot: PivotTable object
        :param row: Row index of the cell in the upper-left corner of the Timeline range.
        :param column: Column index of the cell in the upper-left corner of the Timeline range.
        :param base_field: The PivotField in PivotTable.BaseFields
        :returns: The new add Timeline index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, dest_cell_name : str, base_field : aspose.cells.pivot.PivotField) -> int:
        '''Add a new Timeline using PivotTable as data source
        
        :param pivot: PivotTable object
        :param dest_cell_name: The cell name in the upper-left corner of the Timeline range.
        :param base_field: The PivotField in PivotTable.BaseFields
        :returns: The new add Timeline index'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.timelines.Timeline]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.timelines.Timeline], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.timelines.Timeline, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.timelines.Timeline, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.timelines.Timeline) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.timelines.Timeline, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.timelines.Timeline, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.timelines.Timeline) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

