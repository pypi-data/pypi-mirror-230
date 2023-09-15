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

class ListColumn:
    '''Represents a column in a Table.'''
    
    def get_custom_totals_row_formula(self, is_r1c1 : bool, is_local : bool) -> str:
        '''Gets the formula of totals row of this list column.
        
        :param is_r1c1: Whether the formula needs to be formatted as R1C1.
        :param is_local: Whether the formula needs to be formatted by locale.
        :returns: The formula of this list column.'''
        ...
    
    def set_custom_totals_row_formula(self, formula : str, is_r1c1 : bool, is_local : bool):
        '''Gets the formula of totals row of this list column.
        
        :param formula: the formula for this list column.
        :param is_r1c1: Whether the formula needs to be formatted as R1C1.
        :param is_local: Whether the formula needs to be formatted by locale.'''
        ...
    
    def get_custom_calculated_formula(self, is_r1c1 : bool, is_local : bool) -> str:
        '''Gets the formula of this list column.
        
        :param is_r1c1: Whether the formula needs to be formatted as R1C1.
        :param is_local: Whether the formula needs to be formatted by locale.
        :returns: The formula of this list column.'''
        ...
    
    def set_custom_calculated_formula(self, formula : str, is_r1c1 : bool, is_local : bool):
        '''Sets the formula for this list column.
        
        :param formula: the formula for this list column.
        :param is_r1c1: Whether the formula needs to be formatted as R1C1.
        :param is_local: Whether the formula needs to be formatted by locale.'''
        ...
    
    def get_data_style(self) -> aspose.cells.Style:
        '''Gets the style of the data in this column of the table.'''
        ...
    
    def set_data_style(self, style : aspose.cells.Style):
        '''Sets the style of the data in this column of the table.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets and sets the name of the column.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and sets the name of the column.'''
        ...
    
    @property
    def totals_calculation(self) -> aspose.cells.tables.TotalsCalculation:
        ...
    
    @totals_calculation.setter
    def totals_calculation(self, value : aspose.cells.tables.TotalsCalculation):
        ...
    
    @property
    def range(self) -> aspose.cells.Range:
        '''Gets the range of this list column.'''
        ...
    
    @property
    def formula(self) -> str:
        '''Gets and sets the formula of the list column.'''
        ...
    
    @formula.setter
    def formula(self, value : str):
        '''Gets and sets the formula of the list column.'''
        ...
    
    @property
    def totals_row_label(self) -> str:
        ...
    
    @totals_row_label.setter
    def totals_row_label(self, value : str):
        ...
    
    ...

class ListColumnCollection:
    '''Represents A collection of all the :py:class:`aspose.cells.tables.ListColumn` objects in the specified ListObject object.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.tables.ListColumn]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.tables.ListColumn], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.tables.ListColumn, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.tables.ListColumn, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.ListColumn) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.ListColumn, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.ListColumn, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.tables.ListColumn) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class ListObject:
    '''Represents a list object on a worksheet.
    The ListObject object is a member of the ListObjects collection.
    The ListObjects collection contains all the list objects on a worksheet.'''
    
    @overload
    def put_cell_value(self, row_offset : int, column_offset : int, value : any):
        '''Put the value to the cell.
        
        :param row_offset: The row offset in the table.
        :param column_offset: The column offset in the table.
        :param value: The cell value.'''
        ...
    
    @overload
    def put_cell_value(self, row_offset : int, column_offset : int, value : any, is_totals_row_label : bool):
        '''Put the value to the cell.
        
        :param row_offset: The row offset in the table.
        :param column_offset: The column offset in the table.
        :param value: The cell value.
        :param is_totals_row_label: Indicates whether it is a label for total row,only works for total row.
        If False and this row is total row, a new row will be inserted.'''
        ...
    
    @overload
    def put_cell_formula(self, row_offset : int, column_offset : int, formula : str):
        '''Put the formula to the cell in the table.
        
        :param row_offset: The row offset in the table.
        :param column_offset: The column offset in the table.
        :param formula: The formula of the cell.'''
        ...
    
    @overload
    def put_cell_formula(self, row_offset : int, column_offset : int, formula : str, is_totals_row_formula : bool):
        '''Put the formula to the cell in the table.
        
        :param row_offset: The row offset in the table.
        :param column_offset: The column offset in the table.
        :param formula: The formula of the cell.'''
        ...
    
    @overload
    def convert_to_range(self):
        '''Convert the table to range.'''
        ...
    
    @overload
    def convert_to_range(self, options : aspose.cells.tables.TableToRangeOptions):
        '''Convert the table to range.
        
        :param options: the options when converting table to range.'''
        ...
    
    def resize(self, start_row : int, start_column : int, end_row : int, end_column : int, has_headers : bool):
        '''Resize the range of the list object.
        
        :param start_row: The start row index of the new range.
        :param start_column: The start column index of the new range.
        :param end_row: The end row index of the new range.
        :param end_column: The end column index of the new range.
        :param has_headers: Whether this table has headers.'''
        ...
    
    def update_column_name(self):
        '''Updates all list columns' name from the worksheet.'''
        ...
    
    def filter(self) -> aspose.cells.AutoFilter:
        '''Filter the table.'''
        ...
    
    def apply_style_to_range(self):
        '''Apply the table style to the range.'''
        ...
    
    @property
    def start_row(self) -> int:
        ...
    
    @property
    def start_column(self) -> int:
        ...
    
    @property
    def end_row(self) -> int:
        ...
    
    @property
    def end_column(self) -> int:
        ...
    
    @property
    def list_columns(self) -> aspose.cells.tables.ListColumnCollection:
        ...
    
    @property
    def show_header_row(self) -> bool:
        ...
    
    @show_header_row.setter
    def show_header_row(self, value : bool):
        ...
    
    @property
    def show_totals(self) -> bool:
        ...
    
    @show_totals.setter
    def show_totals(self, value : bool):
        ...
    
    @property
    def data_range(self) -> aspose.cells.Range:
        ...
    
    @property
    def query_table(self) -> aspose.cells.QueryTable:
        ...
    
    @property
    def data_source_type(self) -> aspose.cells.tables.TableDataSourceType:
        ...
    
    @property
    def auto_filter(self) -> aspose.cells.AutoFilter:
        ...
    
    @property
    def display_name(self) -> str:
        ...
    
    @display_name.setter
    def display_name(self, value : str):
        ...
    
    @property
    def comment(self) -> str:
        '''Gets and sets the comment of the table.'''
        ...
    
    @comment.setter
    def comment(self, value : str):
        '''Gets and sets the comment of the table.'''
        ...
    
    @property
    def show_table_style_first_column(self) -> bool:
        ...
    
    @show_table_style_first_column.setter
    def show_table_style_first_column(self, value : bool):
        ...
    
    @property
    def show_table_style_last_column(self) -> bool:
        ...
    
    @show_table_style_last_column.setter
    def show_table_style_last_column(self, value : bool):
        ...
    
    @property
    def show_table_style_row_stripes(self) -> bool:
        ...
    
    @show_table_style_row_stripes.setter
    def show_table_style_row_stripes(self, value : bool):
        ...
    
    @property
    def show_table_style_column_stripes(self) -> bool:
        ...
    
    @show_table_style_column_stripes.setter
    def show_table_style_column_stripes(self, value : bool):
        ...
    
    @property
    def table_style_type(self) -> aspose.cells.tables.TableStyleType:
        ...
    
    @table_style_type.setter
    def table_style_type(self, value : aspose.cells.tables.TableStyleType):
        ...
    
    @property
    def table_style_name(self) -> str:
        ...
    
    @table_style_name.setter
    def table_style_name(self, value : str):
        ...
    
    @property
    def xml_map(self) -> aspose.cells.XmlMap:
        ...
    
    @property
    def alternative_text(self) -> str:
        ...
    
    @alternative_text.setter
    def alternative_text(self, value : str):
        ...
    
    @property
    def alternative_description(self) -> str:
        ...
    
    @alternative_description.setter
    def alternative_description(self, value : str):
        ...
    
    ...

class ListObjectCollection:
    '''Represents a collection of :py:class:`aspose.cells.tables.ListObject` objects in the worksheet.'''
    
    @overload
    def add(self, start_row : int, start_column : int, end_row : int, end_column : int, has_headers : bool) -> int:
        '''Adds a ListObject to the worksheet.
        
        :param start_row: The start row of the list range.
        :param start_column: The start row of the list range.
        :param end_row: The start row of the list range.
        :param end_column: The start row of the list range.
        :param has_headers: Whether the range has headers.
        :returns: The index of the new ListObject'''
        ...
    
    @overload
    def add(self, start_cell : str, end_cell : str, has_headers : bool) -> int:
        '''Adds a ListObject to the worksheet.
        
        :param start_cell: The start cell of the list range.
        :param end_cell: The end cell of the list range.
        :param has_headers: Whether the range has headers.
        :returns: The index of the new ListObject'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.tables.ListObject]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.tables.ListObject], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.tables.ListObject, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.tables.ListObject, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.ListObject) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.ListObject, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.ListObject, index : int, count : int) -> int:
        ...
    
    def update_column_name(self):
        '''Update all column name of the tables.'''
        ...
    
    def binary_search(self, item : aspose.cells.tables.ListObject) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class TableStyle:
    '''Represents the table style.'''
    
    @property
    def name(self) -> str:
        '''Gets the name of table style.'''
        ...
    
    @property
    def table_style_elements(self) -> aspose.cells.tables.TableStyleElementCollection:
        ...
    
    ...

class TableStyleCollection:
    '''Represents all custom table styles.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.tables.TableStyle]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.tables.TableStyle], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.tables.TableStyle, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.tables.TableStyle, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.TableStyle) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.TableStyle, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.TableStyle, index : int, count : int) -> int:
        ...
    
    def add_table_style(self, name : str) -> int:
        '''Adds a custom table style.
        
        :param name: The table style name.
        :returns: The index of the table style.'''
        ...
    
    def add_pivot_table_style(self, name : str) -> int:
        '''Adds a custom pivot table style.
        
        :param name: The pivot table style name.
        :returns: The index of the pivot table style.'''
        ...
    
    def get_builtin_table_style(self, type : aspose.cells.tables.TableStyleType) -> aspose.cells.tables.TableStyle:
        '''Gets the builtin table style
        
        :param type: The builtin table style type.'''
        ...
    
    def binary_search(self, item : aspose.cells.tables.TableStyle) -> int:
        ...
    
    @property
    def default_table_style_name(self) -> str:
        ...
    
    @default_table_style_name.setter
    def default_table_style_name(self, value : str):
        ...
    
    @property
    def default_pivot_style_name(self) -> str:
        ...
    
    @default_pivot_style_name.setter
    def default_pivot_style_name(self, value : str):
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class TableStyleElement:
    '''Represents the element of the table style.'''
    
    def get_element_style(self) -> aspose.cells.Style:
        '''Gets the element style.
        
        :returns: Returns the :py:class:`aspose.cells.Style` object.'''
        ...
    
    def set_element_style(self, style : aspose.cells.Style):
        '''Sets the element style.
        
        :param style: The element style.'''
        ...
    
    @property
    def size(self) -> int:
        '''Number of rows or columns in a single band of striping.
        Applies only when type is firstRowStripe, secondRowStripe, firstColumnStripe, or secondColumnStripe.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Number of rows or columns in a single band of striping.
        Applies only when type is firstRowStripe, secondRowStripe, firstColumnStripe, or secondColumnStripe.'''
        ...
    
    @property
    def type(self) -> aspose.cells.tables.TableStyleElementType:
        '''Gets the element type.'''
        ...
    
    ...

class TableStyleElementCollection:
    '''Represents all elements of the table style.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.tables.TableStyleElement]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.tables.TableStyleElement], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.tables.TableStyleElement, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.tables.TableStyleElement, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.TableStyleElement) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.TableStyleElement, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.tables.TableStyleElement, index : int, count : int) -> int:
        ...
    
    def add(self, type : aspose.cells.tables.TableStyleElementType) -> int:
        '''Adds an element.
        
        :param type: The type of the element
        :returns: Returns the index of the element in the list.'''
        ...
    
    def binary_search(self, item : aspose.cells.tables.TableStyleElement) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class TableToRangeOptions:
    '''Represents the options when converting table to range.'''
    
    @property
    def last_row(self) -> int:
        ...
    
    @last_row.setter
    def last_row(self, value : int):
        ...
    
    ...

class TableDataSourceType:
    '''Represents the table's data source type.'''
    
    @classmethod
    @property
    def WORKSHEET(cls) -> TableDataSourceType:
        '''Excel Worksheet Table'''
        ...
    
    @classmethod
    @property
    def SHARE_POINT(cls) -> TableDataSourceType:
        '''Read-write SharePoint linked List'''
        ...
    
    @classmethod
    @property
    def XML(cls) -> TableDataSourceType:
        '''XML mapper Table'''
        ...
    
    @classmethod
    @property
    def QUERY_TABLE(cls) -> TableDataSourceType:
        '''Query Table'''
        ...
    
    ...

class TableStyleElementType:
    '''Represents the Table or PivotTable style element type.'''
    
    @classmethod
    @property
    def BLANK_ROW(cls) -> TableStyleElementType:
        '''Table style element that applies to PivotTable's blank rows.'''
        ...
    
    @classmethod
    @property
    def FIRST_COLUMN(cls) -> TableStyleElementType:
        '''Table style element that applies to table's first column.'''
        ...
    
    @classmethod
    @property
    def FIRST_COLUMN_STRIPE(cls) -> TableStyleElementType:
        '''Table style element that applies to table's first column stripes.'''
        ...
    
    @classmethod
    @property
    def FIRST_COLUMN_SUBHEADING(cls) -> TableStyleElementType:
        '''Table style element that applies to PivotTable's first column subheading.'''
        ...
    
    @classmethod
    @property
    def FIRST_HEADER_CELL(cls) -> TableStyleElementType:
        '''Table style element that applies to table's first header row cell.'''
        ...
    
    @classmethod
    @property
    def FIRST_ROW_STRIPE(cls) -> TableStyleElementType:
        '''Table style element that applies to table's first row stripes.'''
        ...
    
    @classmethod
    @property
    def FIRST_ROW_SUBHEADING(cls) -> TableStyleElementType:
        '''Table style element that applies to PivotTable's first row subheading.'''
        ...
    
    @classmethod
    @property
    def FIRST_SUBTOTAL_COLUMN(cls) -> TableStyleElementType:
        '''Table style element that applies to PivotTable's first subtotal column.'''
        ...
    
    @classmethod
    @property
    def FIRST_SUBTOTAL_ROW(cls) -> TableStyleElementType:
        '''Table style element that applies to pivot table's first subtotal row.'''
        ...
    
    @classmethod
    @property
    def GRAND_TOTAL_COLUMN(cls) -> TableStyleElementType:
        '''Table style element that applies to pivot table's grand total column.'''
        ...
    
    @classmethod
    @property
    def GRAND_TOTAL_ROW(cls) -> TableStyleElementType:
        '''Table style element that applies to pivot table's grand total row.'''
        ...
    
    @classmethod
    @property
    def FIRST_TOTAL_CELL(cls) -> TableStyleElementType:
        '''Table style element that applies to table's first total row cell.'''
        ...
    
    @classmethod
    @property
    def HEADER_ROW(cls) -> TableStyleElementType:
        '''Table style element that applies to table's header row.'''
        ...
    
    @classmethod
    @property
    def LAST_COLUMN(cls) -> TableStyleElementType:
        '''Table style element that applies to table's last column.'''
        ...
    
    @classmethod
    @property
    def LAST_HEADER_CELL(cls) -> TableStyleElementType:
        '''Table style element that applies to table's last header row cell.'''
        ...
    
    @classmethod
    @property
    def LAST_TOTAL_CELL(cls) -> TableStyleElementType:
        '''Table style element that applies to table's last total row cell.'''
        ...
    
    @classmethod
    @property
    def PAGE_FIELD_LABELS(cls) -> TableStyleElementType:
        '''Table style element that applies to pivot table's page field labels.'''
        ...
    
    @classmethod
    @property
    def PAGE_FIELD_VALUES(cls) -> TableStyleElementType:
        '''Table style element that applies to pivot table's page field values.'''
        ...
    
    @classmethod
    @property
    def SECOND_COLUMN_STRIPE(cls) -> TableStyleElementType:
        '''Table style element that applies to table's second column stripes.'''
        ...
    
    @classmethod
    @property
    def SECOND_COLUMN_SUBHEADING(cls) -> TableStyleElementType:
        '''Table style element that applies to pivot table's second column subheading.'''
        ...
    
    @classmethod
    @property
    def SECOND_ROW_STRIPE(cls) -> TableStyleElementType:
        '''Table style element that applies to table's second row stripes.'''
        ...
    
    @classmethod
    @property
    def SECOND_ROW_SUBHEADING(cls) -> TableStyleElementType:
        '''Table style element that applies to pivot table's second row subheading.'''
        ...
    
    @classmethod
    @property
    def SECOND_SUBTOTAL_COLUMN(cls) -> TableStyleElementType:
        '''Table style element that applies to PivotTable's second subtotal column.'''
        ...
    
    @classmethod
    @property
    def SECOND_SUBTOTAL_ROW(cls) -> TableStyleElementType:
        '''Table style element that applies to PivotTable's second subtotal row.'''
        ...
    
    @classmethod
    @property
    def THIRD_COLUMN_SUBHEADING(cls) -> TableStyleElementType:
        '''Table style element that applies to PivotTable's third column subheading.'''
        ...
    
    @classmethod
    @property
    def THIRD_ROW_SUBHEADING(cls) -> TableStyleElementType:
        '''Table style element that applies to PivotTable's third row subheading.'''
        ...
    
    @classmethod
    @property
    def THIRD_SUBTOTAL_COLUMN(cls) -> TableStyleElementType:
        '''Table style element that applies to pivot table's third subtotal column.'''
        ...
    
    @classmethod
    @property
    def THIRD_SUBTOTAL_ROW(cls) -> TableStyleElementType:
        '''Table style element that applies to PivotTable's third subtotal row.'''
        ...
    
    @classmethod
    @property
    def TOTAL_ROW(cls) -> TableStyleElementType:
        '''Table style element that applies to table's total row.'''
        ...
    
    @classmethod
    @property
    def WHOLE_TABLE(cls) -> TableStyleElementType:
        '''Table style element that applies to table's entire content.'''
        ...
    
    ...

class TableStyleType:
    '''Represents the built-in table style type.'''
    
    @classmethod
    @property
    def NONE(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT1(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT2(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT3(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT4(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT5(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT6(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT7(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT8(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT9(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT10(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT11(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT12(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT13(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT14(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT15(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT16(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT17(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT18(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT19(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT20(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_LIGHT21(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM1(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM2(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM3(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM4(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM5(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM6(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM7(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM8(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM9(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM10(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM11(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM12(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM13(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM14(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM15(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM16(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM17(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM18(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM19(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM20(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM21(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM22(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM23(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM24(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM25(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM26(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM27(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_MEDIUM28(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK1(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK2(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK3(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK4(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK5(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK6(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK7(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK8(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK9(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK10(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def TABLE_STYLE_DARK11(cls) -> TableStyleType:
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> TableStyleType:
        ...
    
    ...

class TotalsCalculation:
    '''Determines the type of calculation in the Totals row of the list column.'''
    
    @classmethod
    @property
    def SUM(cls) -> TotalsCalculation:
        '''Represents Sum totals calculation.'''
        ...
    
    @classmethod
    @property
    def COUNT(cls) -> TotalsCalculation:
        '''Represents Count totals calculation.'''
        ...
    
    @classmethod
    @property
    def AVERAGE(cls) -> TotalsCalculation:
        '''Represents Average totals calculation.'''
        ...
    
    @classmethod
    @property
    def MAX(cls) -> TotalsCalculation:
        '''Represents Max totals calculation.'''
        ...
    
    @classmethod
    @property
    def MIN(cls) -> TotalsCalculation:
        '''Represents Min totals calculation.'''
        ...
    
    @classmethod
    @property
    def VAR(cls) -> TotalsCalculation:
        '''Represents Var totals calculation.'''
        ...
    
    @classmethod
    @property
    def COUNT_NUMS(cls) -> TotalsCalculation:
        '''Represents Count Nums totals calculation.'''
        ...
    
    @classmethod
    @property
    def STD_DEV(cls) -> TotalsCalculation:
        '''Represents StdDev totals calculation.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> TotalsCalculation:
        '''Represents No totals calculation.'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> TotalsCalculation:
        '''Represents custom calculation.'''
        ...
    
    ...

