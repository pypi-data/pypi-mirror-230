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

class Slicer:
    '''summary description of Slicer View'''
    
    def add_pivot_connection(self, pivot : aspose.cells.pivot.PivotTable):
        '''Adds PivotTable connection.
        
        :param pivot: The PivotTable object'''
        ...
    
    def remove_pivot_connection(self, pivot : aspose.cells.pivot.PivotTable):
        '''Removes PivotTable connection.
        
        :param pivot: The PivotTable object'''
        ...
    
    def refresh(self):
        '''Refreshing the slicer.Meanwhile, Refreshing and Calculating  relative PivotTables.'''
        ...
    
    @property
    def title(self) -> str:
        '''Specifies the title of the current Slicer object.'''
        ...
    
    @title.setter
    def title(self, value : str):
        '''Specifies the title of the current Slicer object.'''
        ...
    
    @property
    def alternative_text(self) -> str:
        ...
    
    @alternative_text.setter
    def alternative_text(self, value : str):
        ...
    
    @property
    def is_printable(self) -> bool:
        ...
    
    @is_printable.setter
    def is_printable(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def placement(self) -> aspose.cells.drawing.PlacementType:
        '''Represents the way the drawing object is attached to the cells below it.
        The property controls the placement of an object on a worksheet.'''
        ...
    
    @placement.setter
    def placement(self, value : aspose.cells.drawing.PlacementType):
        '''Represents the way the drawing object is attached to the cells below it.
        The property controls the placement of an object on a worksheet.'''
        ...
    
    @property
    def locked_aspect_ratio(self) -> bool:
        ...
    
    @locked_aspect_ratio.setter
    def locked_aspect_ratio(self, value : bool):
        ...
    
    @property
    def locked_position(self) -> bool:
        ...
    
    @locked_position.setter
    def locked_position(self, value : bool):
        ...
    
    @property
    def slicer_cache(self) -> aspose.cells.slicers.SlicerCache:
        ...
    
    @property
    def parent(self) -> aspose.cells.Worksheet:
        '''Returns the Worksheet object that represents the sheet that contains the slicer. Read-only.'''
        ...
    
    @property
    def style_type(self) -> aspose.cells.slicers.SlicerStyleType:
        ...
    
    @style_type.setter
    def style_type(self, value : aspose.cells.slicers.SlicerStyleType):
        ...
    
    @property
    def name(self) -> str:
        '''Returns the name of the specified slicer'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Returns or sets the name of the specified slicer'''
        ...
    
    @property
    def caption(self) -> str:
        '''Returns the caption of the specified slicer.'''
        ...
    
    @caption.setter
    def caption(self, value : str):
        '''Returns or sets the caption of the specified slicer.'''
        ...
    
    @property
    def caption_visible(self) -> bool:
        ...
    
    @caption_visible.setter
    def caption_visible(self, value : bool):
        ...
    
    @property
    def number_of_columns(self) -> int:
        ...
    
    @number_of_columns.setter
    def number_of_columns(self, value : int):
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
    def width(self) -> float:
        '''Returns the width of the specified slicer, in points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Returns or sets the width of the specified slicer, in points.'''
        ...
    
    @property
    def width_pixel(self) -> int:
        ...
    
    @width_pixel.setter
    def width_pixel(self, value : int):
        ...
    
    @property
    def height(self) -> float:
        '''Returns the height of the specified slicer, in points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Returns or sets the height of the specified slicer, in points.'''
        ...
    
    @property
    def height_pixel(self) -> int:
        ...
    
    @height_pixel.setter
    def height_pixel(self, value : int):
        ...
    
    @property
    def column_width_pixel(self) -> int:
        ...
    
    @column_width_pixel.setter
    def column_width_pixel(self, value : int):
        ...
    
    @property
    def column_width(self) -> float:
        ...
    
    @column_width.setter
    def column_width(self, value : float):
        ...
    
    @property
    def row_height_pixel(self) -> int:
        ...
    
    @row_height_pixel.setter
    def row_height_pixel(self, value : int):
        ...
    
    @property
    def row_height(self) -> float:
        ...
    
    @row_height.setter
    def row_height(self, value : float):
        ...
    
    ...

class SlicerCache:
    '''summary description of slicer cache'''
    
    @property
    def cross_filter_type(self) -> aspose.cells.slicers.SlicerCacheCrossFilterType:
        ...
    
    @cross_filter_type.setter
    def cross_filter_type(self, value : aspose.cells.slicers.SlicerCacheCrossFilterType):
        ...
    
    @property
    def list(self) -> bool:
        '''Returns whether the slicer associated with the specified slicer cache is based on an Non-OLAP data source. Read-only'''
        ...
    
    @property
    def slicer_cache_items(self) -> aspose.cells.slicers.SlicerCacheItemCollection:
        ...
    
    @property
    def name(self) -> str:
        '''Returns the name of the slicer cache.'''
        ...
    
    @property
    def source_name(self) -> str:
        ...
    
    ...

class SlicerCacheItem:
    '''Represent slicer data source item'''
    
    @property
    def selected(self) -> bool:
        '''Specifies whether the SlicerItem is selected or not.'''
        ...
    
    @selected.setter
    def selected(self, value : bool):
        '''Specifies whether the SlicerItem is selected or not.'''
        ...
    
    @property
    def value(self) -> str:
        '''Returns the label text for the slicer item. Read-only.'''
        ...
    
    ...

class SlicerCacheItemCollection:
    '''Represent the collection of SlicerCacheItem'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.slicers.SlicerCacheItem]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.slicers.SlicerCacheItem], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.slicers.SlicerCacheItem, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.slicers.SlicerCacheItem, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.slicers.SlicerCacheItem) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.slicers.SlicerCacheItem, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.slicers.SlicerCacheItem, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.slicers.SlicerCacheItem) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class SlicerCollection:
    '''Specifies the collection of all the Slicer objects on the specified worksheet.'''
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, dest_cell_name : str, base_field_name : str) -> int:
        '''Add a new Slicer using PivotTable as data source
        
        :param pivot: PivotTable object
        :param dest_cell_name: The cell in the upper-left corner of the Slicer range.
        :param base_field_name: The name of PivotField in PivotTable.BaseFields
        :returns: The new add Slicer index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, row : int, column : int, base_field_name : str) -> int:
        '''Add a new Slicer using PivotTable as data source
        
        :param pivot: PivotTable object
        :param row: Row index of the cell in the upper-left corner of the Slicer range.
        :param column: Column index of the cell in the upper-left corner of the Slicer range.
        :param base_field_name: The name of PivotField in PivotTable.BaseFields
        :returns: The new add Slicer index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, row : int, column : int, base_field_index : int) -> int:
        '''Add a new Slicer using PivotTable as data source
        
        :param pivot: PivotTable object
        :param row: Row index of the cell in the upper-left corner of the Slicer range.
        :param column: Column index of the cell in the upper-left corner of the Slicer range.
        :param base_field_index: The index of PivotField in PivotTable.BaseFields
        :returns: The new add Slicer index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, dest_cell_name : str, base_field_index : int) -> int:
        '''Add a new Slicer using PivotTable as data source
        
        :param pivot: PivotTable object
        :param dest_cell_name: The cell in the upper-left corner of the Slicer range.
        :param base_field_index: The index of PivotField in PivotTable.BaseFields
        :returns: The new add Slicer index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, row : int, column : int, base_field : aspose.cells.pivot.PivotField) -> int:
        '''Add a new Slicer using PivotTable as data source
        
        :param pivot: PivotTable object
        :param row: Row index of the cell in the upper-left corner of the Slicer range.
        :param column: Column index of the cell in the upper-left corner of the Slicer range.
        :param base_field: The PivotField in PivotTable.BaseFields
        :returns: The new add Slicer index'''
        ...
    
    @overload
    def add(self, pivot : aspose.cells.pivot.PivotTable, dest_cell_name : str, base_field : aspose.cells.pivot.PivotField) -> int:
        '''Add a new Slicer using PivotTable as data source
        
        :param pivot: PivotTable object
        :param dest_cell_name: The cell in the upper-left corner of the Slicer range.
        :param base_field: The PivotField in PivotTable.BaseFields
        :returns: The new add Slicer index'''
        ...
    
    @overload
    def add(self, table : aspose.cells.tables.ListObject, index : int, dest_cell_name : str) -> int:
        '''Add a new Slicer using ListObjet as data source
        
        :param table: ListObject object
        :param index: The index of ListColumn in ListObject.ListColumns
        :param dest_cell_name: The cell in the upper-left corner of the Slicer range.
        :returns: The new add Slicer index'''
        ...
    
    @overload
    def add(self, table : aspose.cells.tables.ListObject, list_column : aspose.cells.tables.ListColumn, dest_cell_name : str) -> int:
        '''Add a new Slicer using ListObjet as data source
        
        :param table: ListObject object
        :param list_column: The ListColumn in ListObject.ListColumns
        :param dest_cell_name: The cell in the upper-left corner of the Slicer range.
        :returns: The new add Slicer index'''
        ...
    
    @overload
    def add(self, table : aspose.cells.tables.ListObject, list_column : aspose.cells.tables.ListColumn, row : int, column : int) -> int:
        '''Add a new Slicer using ListObjet as data source
        
        :param table: ListObject object
        :param list_column: The ListColumn in ListObject.ListColumns
        :param row: Row index of the cell in the upper-left corner of the Slicer range.
        :param column: Column index of the cell in the upper-left corner of the Slicer range.
        :returns: The new add Slicer index'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.slicers.Slicer]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.slicers.Slicer], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.slicers.Slicer, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.slicers.Slicer, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.slicers.Slicer) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.slicers.Slicer, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.slicers.Slicer, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.slicers.Slicer) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class SlicerCacheCrossFilterType:
    '''Represent the type of SlicerCacheCrossFilterType'''
    
    @classmethod
    @property
    def NONE(cls) -> SlicerCacheCrossFilterType:
        '''The table style element of the slicer style for slicer items
        with no data is not applied to slicer items with no data, and slicer items
        with no data are not sorted separately in the list of slicer items in the slicer view'''
        ...
    
    @classmethod
    @property
    def SHOW_ITEMS_WITH_DATA_AT_TOP(cls) -> SlicerCacheCrossFilterType:
        '''The table style element of the slicer style for slicer items with
        no data is applied to slicer items with no data, and slicer items
        with no data are sorted at the bottom in the list of slicer items in the slicer view'''
        ...
    
    @classmethod
    @property
    def SHOW_ITEMS_WITH_NO_DATA(cls) -> SlicerCacheCrossFilterType:
        '''The table style element of the slicer style for slicer items with no data
        is applied to slicer items with no data, and slicer items with no data
        are not sorted separately in the list of slicer items in the slicer view.'''
        ...
    
    ...

class SlicerCacheItemSortType:
    '''Specify the sort type of SlicerCacheItem'''
    
    @classmethod
    @property
    def ASCENDING(cls) -> SlicerCacheItemSortType:
        '''Ascending sort type'''
        ...
    
    @classmethod
    @property
    def DESCENDING(cls) -> SlicerCacheItemSortType:
        '''Descending sort type'''
        ...
    
    ...

class SlicerStyleType:
    '''Specify the style of slicer view'''
    
    @classmethod
    @property
    def SLICER_STYLE_LIGHT1(cls) -> SlicerStyleType:
        '''built-in light style one'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_LIGHT2(cls) -> SlicerStyleType:
        '''built-in light style two'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_LIGHT3(cls) -> SlicerStyleType:
        '''built-in light style three'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_LIGHT4(cls) -> SlicerStyleType:
        '''built-in light style four'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_LIGHT5(cls) -> SlicerStyleType:
        '''built-in light style five'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_LIGHT6(cls) -> SlicerStyleType:
        '''built-in light style six'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_OTHER1(cls) -> SlicerStyleType:
        '''built-in style other one'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_OTHER2(cls) -> SlicerStyleType:
        '''built-in style other two'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_DARK1(cls) -> SlicerStyleType:
        '''built-in dark style one'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_DARK2(cls) -> SlicerStyleType:
        '''built-in dark style tow'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_DARK3(cls) -> SlicerStyleType:
        '''built-in dark style three'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_DARK4(cls) -> SlicerStyleType:
        '''built-in dark style four'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_DARK5(cls) -> SlicerStyleType:
        '''built-in dark style five'''
        ...
    
    @classmethod
    @property
    def SLICER_STYLE_DARK6(cls) -> SlicerStyleType:
        '''built-in dark style six'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> SlicerStyleType:
        '''user-defined style, unsupported for now'''
        ...
    
    ...

