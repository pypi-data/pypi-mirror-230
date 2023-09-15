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

class PivotArea:
    '''Presents the selected area of the PivotTable.'''
    
    def select(self, axis_type : aspose.cells.pivot.PivotFieldType, field_position : int, selection_type : aspose.cells.pivot.PivotTableSelectionType):
        '''Select the area with filters.
        
        :param axis_type: The region of the PivotTable to which this rule applies.
        :param field_position: Position of the field within the axis to which this rule applies.
        :param selection_type: Specifies what can be selected in a PivotTable during a structured selection.'''
        ...
    
    @property
    def filters(self) -> aspose.cells.pivot.PivotAreaFilterCollection:
        '''Gets all filters for this PivotArea.'''
        ...
    
    @property
    def only_data(self) -> bool:
        ...
    
    @only_data.setter
    def only_data(self, value : bool):
        ...
    
    @property
    def only_label(self) -> bool:
        ...
    
    @only_label.setter
    def only_label(self, value : bool):
        ...
    
    @property
    def is_row_grand_included(self) -> bool:
        ...
    
    @is_row_grand_included.setter
    def is_row_grand_included(self, value : bool):
        ...
    
    @property
    def is_column_grand_included(self) -> bool:
        ...
    
    @is_column_grand_included.setter
    def is_column_grand_included(self, value : bool):
        ...
    
    @property
    def axis_type(self) -> aspose.cells.pivot.PivotFieldType:
        ...
    
    @axis_type.setter
    def axis_type(self, value : aspose.cells.pivot.PivotFieldType):
        ...
    
    @property
    def rule_type(self) -> aspose.cells.pivot.PivotAreaType:
        ...
    
    @rule_type.setter
    def rule_type(self, value : aspose.cells.pivot.PivotAreaType):
        ...
    
    @property
    def is_outline(self) -> bool:
        ...
    
    @is_outline.setter
    def is_outline(self, value : bool):
        ...
    
    ...

class PivotAreaFilter:
    '''Represents the filter of :py:class:`aspose.cells.pivot.PivotArea` for :py:class:`aspose.cells.pivot.PivotTable`.'''
    
    def is_subtotal_set(self, subtotal_type : aspose.cells.pivot.PivotFieldSubtotalType) -> bool:
        '''Gets which subtotal is set for this filter.
        
        :param subtotal_type: The subtotal function type.'''
        ...
    
    def set_subtotals(self, subtotal_type : aspose.cells.pivot.PivotFieldSubtotalType, shown : bool):
        '''Subtotal for the filter.
        
        :param subtotal_type: The subtotal function.
        :param shown: Indicates if showing this subtotal data.'''
        ...
    
    @property
    def selected(self) -> bool:
        '''Indicates whether this field has selection.
        Only works when the PivotTable is in Outline view.'''
        ...
    
    @selected.setter
    def selected(self, value : bool):
        '''Indicates whether this field has selection.
        Only works when the PivotTable is in Outline view.'''
        ...
    
    ...

class PivotAreaFilterCollection:
    '''Represents the list of filters for :py:class:`aspose.cells.pivot.PivotArea`'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.pivot.PivotAreaFilter]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.pivot.PivotAreaFilter], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotAreaFilter, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotAreaFilter, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotAreaFilter) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotAreaFilter, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotAreaFilter, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.pivot.PivotAreaFilter) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class PivotField:
    '''Represents a field in a PivotTable report.'''
    
    @overload
    def hide_item(self, index : int, is_hidden : bool):
        '''Sets whether the specific PivotItem in a data field is hidden.
        
        :param index: the index of the pivotItem in the pivotField.
        :param is_hidden: whether the specific PivotItem is hidden'''
        ...
    
    @overload
    def hide_item(self, item_value : str, is_hidden : bool):
        '''Sets whether the specific PivotItem in a data field is hidden.
        
        :param item_value: the value of the pivotItem in the pivotField.
        :param is_hidden: whether the specific PivotItem is hidden'''
        ...
    
    def get_pivot_filter_by_type(self, type : aspose.cells.pivot.PivotFilterType) -> aspose.cells.pivot.PivotFilter:
        '''Gets the pivot filter of the pivot field by type'''
        ...
    
    def get_pivot_filters(self) -> list:
        '''Gets the pivot filters of the pivot field'''
        ...
    
    def init_pivot_items(self):
        '''Init the pivot items of the pivot field'''
        ...
    
    def get_calculated_field_formula(self) -> str:
        '''Get the formula string of the specified calculated field .'''
        ...
    
    def set_subtotals(self, subtotal_type : aspose.cells.pivot.PivotFieldSubtotalType, shown : bool):
        '''Sets whether the specified field shows that subtotals.
        
        :param subtotal_type: subtotals type.
        :param shown: whether the specified field shows that subtotals.'''
        ...
    
    def get_subtotals(self, subtotal_type : aspose.cells.pivot.PivotFieldSubtotalType) -> bool:
        '''Gets whether the specified field shows that subtotals.
        
        :param subtotal_type: subtotals type.
        :returns: whether the specified field shows that subtotals.'''
        ...
    
    def is_hidden_item(self, index : int) -> bool:
        '''Indicates whether the specific PivotItem is hidden.
        
        :param index: the index of the pivotItem in the pivotField.
        :returns: whether the specific PivotItem is hidden'''
        ...
    
    def is_hidden_item_detail(self, index : int) -> bool:
        '''Indicates whether the specific PivotItem is hidden detail.
        
        :param index: the index of the pivotItem in the pivotField.
        :returns: whether the specific PivotItem is hidden detail'''
        ...
    
    def hide_item_detail(self, index : int, is_hidden_detail : bool):
        '''Sets whether the specific PivotItem in a pivot field is hidden detail.
        
        :param index: the index of the pivotItem in the pivotField.
        :param is_hidden_detail: whether the specific PivotItem is hidden'''
        ...
    
    def hide_detail(self, is_hidden_detail : bool):
        '''Sets whether the PivotItems in a pivot field is hidden detail.That is collapse/expand this field.
        
        :param is_hidden_detail: whether the PivotItems is hidden'''
        ...
    
    def add_calculated_item(self, name : str, formula : str):
        '''Add a calculated item to the pivot field.
        
        :param name: The item's name.
        :param formula: The item's formula'''
        ...
    
    @property
    def pivot_items(self) -> aspose.cells.pivot.PivotItemCollection:
        ...
    
    @property
    def range(self) -> aspose.cells.pivot.SxRng:
        '''Gets the group range of the pivot field'''
        ...
    
    @property
    def is_calculated_field(self) -> bool:
        ...
    
    @property
    def base_index(self) -> int:
        ...
    
    @base_index.setter
    def base_index(self, value : int):
        ...
    
    @property
    def position(self) -> int:
        '''Represents the PivotField index in the PivotFields.'''
        ...
    
    @property
    def name(self) -> str:
        '''Represents the PivotField name.'''
        ...
    
    @property
    def display_name(self) -> str:
        ...
    
    @display_name.setter
    def display_name(self, value : str):
        ...
    
    @property
    def is_auto_subtotals(self) -> bool:
        ...
    
    @is_auto_subtotals.setter
    def is_auto_subtotals(self, value : bool):
        ...
    
    @property
    def drag_to_column(self) -> bool:
        ...
    
    @drag_to_column.setter
    def drag_to_column(self, value : bool):
        ...
    
    @property
    def drag_to_hide(self) -> bool:
        ...
    
    @drag_to_hide.setter
    def drag_to_hide(self, value : bool):
        ...
    
    @property
    def drag_to_row(self) -> bool:
        ...
    
    @drag_to_row.setter
    def drag_to_row(self, value : bool):
        ...
    
    @property
    def drag_to_page(self) -> bool:
        ...
    
    @drag_to_page.setter
    def drag_to_page(self, value : bool):
        ...
    
    @property
    def drag_to_data(self) -> bool:
        ...
    
    @drag_to_data.setter
    def drag_to_data(self, value : bool):
        ...
    
    @property
    def is_multiple_item_selection_allowed(self) -> bool:
        ...
    
    @is_multiple_item_selection_allowed.setter
    def is_multiple_item_selection_allowed(self, value : bool):
        ...
    
    @property
    def is_repeat_item_labels(self) -> bool:
        ...
    
    @is_repeat_item_labels.setter
    def is_repeat_item_labels(self, value : bool):
        ...
    
    @property
    def is_include_new_items_in_filter(self) -> bool:
        ...
    
    @is_include_new_items_in_filter.setter
    def is_include_new_items_in_filter(self, value : bool):
        ...
    
    @property
    def is_insert_page_breaks_between_items(self) -> bool:
        ...
    
    @is_insert_page_breaks_between_items.setter
    def is_insert_page_breaks_between_items(self, value : bool):
        ...
    
    @property
    def show_all_items(self) -> bool:
        ...
    
    @show_all_items.setter
    def show_all_items(self, value : bool):
        ...
    
    @property
    def non_auto_sort_default(self) -> bool:
        ...
    
    @non_auto_sort_default.setter
    def non_auto_sort_default(self, value : bool):
        ...
    
    @property
    def is_auto_sort(self) -> bool:
        ...
    
    @is_auto_sort.setter
    def is_auto_sort(self, value : bool):
        ...
    
    @property
    def is_ascend_sort(self) -> bool:
        ...
    
    @is_ascend_sort.setter
    def is_ascend_sort(self, value : bool):
        ...
    
    @property
    def auto_sort_field(self) -> int:
        ...
    
    @auto_sort_field.setter
    def auto_sort_field(self, value : int):
        ...
    
    @property
    def is_auto_show(self) -> bool:
        ...
    
    @is_auto_show.setter
    def is_auto_show(self, value : bool):
        ...
    
    @property
    def is_ascend_show(self) -> bool:
        ...
    
    @is_ascend_show.setter
    def is_ascend_show(self, value : bool):
        ...
    
    @property
    def auto_show_count(self) -> int:
        ...
    
    @auto_show_count.setter
    def auto_show_count(self, value : int):
        ...
    
    @property
    def auto_show_field(self) -> int:
        ...
    
    @auto_show_field.setter
    def auto_show_field(self, value : int):
        ...
    
    @property
    def function(self) -> aspose.cells.ConsolidationFunction:
        '''Represents the function used to summarize the PivotTable data field.'''
        ...
    
    @function.setter
    def function(self, value : aspose.cells.ConsolidationFunction):
        '''Represents the function used to summarize the PivotTable data field.'''
        ...
    
    @property
    def data_display_format(self) -> aspose.cells.pivot.PivotFieldDataDisplayFormat:
        ...
    
    @data_display_format.setter
    def data_display_format(self, value : aspose.cells.pivot.PivotFieldDataDisplayFormat):
        ...
    
    @property
    def base_field_index(self) -> int:
        ...
    
    @base_field_index.setter
    def base_field_index(self, value : int):
        ...
    
    @property
    def base_item_position(self) -> aspose.cells.pivot.PivotItemPosition:
        ...
    
    @base_item_position.setter
    def base_item_position(self, value : aspose.cells.pivot.PivotItemPosition):
        ...
    
    @property
    def base_item_index(self) -> int:
        ...
    
    @base_item_index.setter
    def base_item_index(self, value : int):
        ...
    
    @property
    def current_page_item(self) -> int:
        ...
    
    @current_page_item.setter
    def current_page_item(self, value : int):
        ...
    
    @property
    def number(self) -> int:
        '''Represents the built-in display format of numbers and dates.'''
        ...
    
    @number.setter
    def number(self, value : int):
        '''Represents the built-in display format of numbers and dates.'''
        ...
    
    @property
    def insert_blank_row(self) -> bool:
        ...
    
    @insert_blank_row.setter
    def insert_blank_row(self, value : bool):
        ...
    
    @property
    def show_subtotal_at_top(self) -> bool:
        ...
    
    @show_subtotal_at_top.setter
    def show_subtotal_at_top(self, value : bool):
        ...
    
    @property
    def show_in_outline_form(self) -> bool:
        ...
    
    @show_in_outline_form.setter
    def show_in_outline_form(self, value : bool):
        ...
    
    @property
    def number_format(self) -> str:
        ...
    
    @number_format.setter
    def number_format(self, value : str):
        ...
    
    @property
    def items(self) -> List[str]:
        '''Get all base items;'''
        ...
    
    @property
    def original_items(self) -> List[str]:
        ...
    
    @property
    def item_count(self) -> int:
        ...
    
    @property
    def show_compact(self) -> bool:
        ...
    
    @show_compact.setter
    def show_compact(self, value : bool):
        ...
    
    ...

class PivotFieldCollection:
    '''Represents a collection of all the PivotField objects
    in the PivotTable's specific PivotFields type.'''
    
    def add_by_base_index(self, base_field_index : int) -> int:
        '''Adds a PivotField Object to the specific type PivotFields.
        
        :param base_field_index: field index in the base PivotFields.
        :returns: the index of  the PivotField Object in this PivotFields.'''
        ...
    
    def add(self, pivot_field : aspose.cells.pivot.PivotField) -> int:
        '''Adds a PivotField Object to the specific type PivotFields.
        
        :param pivot_field: a PivotField Object.
        :returns: the index of  the PivotField Object in this PivotFields.'''
        ...
    
    def clear(self):
        '''clear all fields of PivotFieldCollection'''
        ...
    
    @property
    def type(self) -> aspose.cells.pivot.PivotFieldType:
        '''Gets the PivotFields type.'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of the pivotFields.'''
        ...
    
    def __getitem__(self, key : int) -> aspose.cells.pivot.PivotField:
        '''Gets the PivotField Object at the specific index.'''
        ...
    
    ...

class PivotFilter:
    '''Represents a PivotFilter in PivotFilter Collection.'''
    
    @property
    def auto_filter(self) -> aspose.cells.AutoFilter:
        ...
    
    @property
    def filter_type(self) -> aspose.cells.pivot.PivotFilterType:
        ...
    
    @property
    def field_index(self) -> int:
        ...
    
    @property
    def value1(self) -> str:
        '''Gets the string value1 of the label pivot filter.'''
        ...
    
    @value1.setter
    def value1(self, value : str):
        '''Gets the string value1 of the label pivot filter.'''
        ...
    
    @property
    def value2(self) -> str:
        '''Gets the string value2 of the label pivot filter.'''
        ...
    
    @value2.setter
    def value2(self, value : str):
        '''Gets the string value2 of the label pivot filter.'''
        ...
    
    @property
    def measure_fld_index(self) -> int:
        ...
    
    @measure_fld_index.setter
    def measure_fld_index(self, value : int):
        ...
    
    @property
    def member_property_field_index(self) -> int:
        ...
    
    @member_property_field_index.setter
    def member_property_field_index(self, value : int):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of the pivot filter.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets the name of the pivot filter.'''
        ...
    
    @property
    def evaluation_order(self) -> int:
        ...
    
    @evaluation_order.setter
    def evaluation_order(self, value : int):
        ...
    
    ...

class PivotFilterCollection:
    '''Represents a collection of all the PivotFilter objects'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.pivot.PivotFilter]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.pivot.PivotFilter], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotFilter, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotFilter, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotFilter) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotFilter, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotFilter, index : int, count : int) -> int:
        ...
    
    def add(self, field_index : int, type : aspose.cells.pivot.PivotFilterType) -> int:
        '''Adds a PivotFilter Object to the specific type
        
        :param field_index: the PivotField index
        :param type: the PivotFilter type
        :returns: the index of  the PivotFilter Object in this PivotFilterCollection.'''
        ...
    
    def clear_filter(self, field_index : int):
        '''Clear PivotFilter from the specific PivotField
        
        :param field_index: the PivotField index'''
        ...
    
    def binary_search(self, item : aspose.cells.pivot.PivotFilter) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class PivotFormatCondition:
    '''Represents a PivotTable Format Condition in PivotFormatCondition Collection.'''
    
    @overload
    def add_data_area_condition(self, field_name : str):
        '''Adds PivotTable conditional format limit in the data fields.
        
        :param field_name: The name of PivotField.'''
        ...
    
    @overload
    def add_data_area_condition(self, data_field : aspose.cells.pivot.PivotField):
        '''Adds PivotTable conditional format limit in the data fields.
        
        :param data_field: The PivotField in the data fields.'''
        ...
    
    @overload
    def add_row_area_condition(self, field_name : str):
        '''Adds PivotTable conditional format limit in the row fields.
        
        :param field_name: The name of PivotField.'''
        ...
    
    @overload
    def add_row_area_condition(self, row_field : aspose.cells.pivot.PivotField):
        '''Adds PivotTable conditional format limit in the row fields.
        
        :param row_field: The PivotField in the row fields.'''
        ...
    
    @overload
    def add_column_area_condition(self, field_name : str):
        '''Adds PivotTable conditional format limit in the column fields.
        
        :param field_name: The name of PivotField.'''
        ...
    
    @overload
    def add_column_area_condition(self, column_field : aspose.cells.pivot.PivotField):
        '''Adds PivotTable conditional format limit in the column fields.
        
        :param column_field: The PivotField in the column fields.'''
        ...
    
    def set_conditional_areas(self):
        '''Sets conditional areas of PivotFormatCondition object.'''
        ...
    
    @property
    def scope_type(self) -> aspose.cells.pivot.PivotConditionFormatScopeType:
        ...
    
    @scope_type.setter
    def scope_type(self, value : aspose.cells.pivot.PivotConditionFormatScopeType):
        ...
    
    @property
    def rule_type(self) -> aspose.cells.pivot.PivotConditionFormatRuleType:
        ...
    
    @rule_type.setter
    def rule_type(self, value : aspose.cells.pivot.PivotConditionFormatRuleType):
        ...
    
    @property
    def format_conditions(self) -> aspose.cells.FormatConditionCollection:
        ...
    
    ...

class PivotFormatConditionCollection:
    '''Represents PivotTable Format Conditions.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.pivot.PivotFormatCondition]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.pivot.PivotFormatCondition], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotFormatCondition, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotFormatCondition, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotFormatCondition) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotFormatCondition, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotFormatCondition, index : int, count : int) -> int:
        ...
    
    def add(self) -> int:
        '''Adds a pivot FormatCondition to the collection.
        
        :returns: pivot FormatCondition object index.'''
        ...
    
    def binary_search(self, item : aspose.cells.pivot.PivotFormatCondition) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class PivotItem:
    '''Represents a item in a PivotField report.'''
    
    def move(self, count : int, is_same_parent : bool):
        '''Moves the item up or down
        
        :param count: The number of moving up or down.
        Move the item up if this is less than zero;
        Move the item down if this is greater than zero.
        :param is_same_parent: Specifying whether moving operation is in the same parent node or not'''
        ...
    
    def get_string_value(self) -> str:
        '''Gets the string value of the pivot item
        If the value is null, it will return ""'''
        ...
    
    def get_double_value(self) -> float:
        '''Gets the double value of the pivot item
        If the value is null or not number ,it will return 0'''
        ...
    
    def get_date_time_value(self) -> DateTime:
        '''Gets the date time value of the pivot item
        If the value is null ,it will return DateTime.MinValue'''
        ...
    
    @property
    def is_hidden(self) -> bool:
        ...
    
    @is_hidden.setter
    def is_hidden(self, value : bool):
        ...
    
    @property
    def is_hide_detail(self) -> bool:
        ...
    
    @is_hide_detail.setter
    def is_hide_detail(self, value : bool):
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value of the pivot item'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of the pivot item.'''
        ...
    
    @property
    def index(self) -> int:
        '''Gets the index of the pivot item in the pivot field'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Gets the index of the pivot item in the pivot field'''
        ...
    
    ...

class PivotItemCollection:
    '''Represents a collection of all the PivotItem objects in the PivotField's'''
    
    def changeitems_order(self, source_index : int, dest_index : int):
        '''Directly changes the orders of the two items.
        
        :param source_index: The current index
        :param dest_index: The dest index'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of the pivot items.'''
        ...
    
    def __getitem__(self, key : int) -> aspose.cells.pivot.PivotItem:
        '''Gets the PivotItem Object at the specific index.'''
        ...
    
    ...

class PivotPageFields:
    '''Represents the pivot page field items
    if the pivot table data source is consolidation ranges.
    It only can contain up to 4 fields.'''
    
    def add_page_field(self, page_items : List[str]):
        '''Adds a page field.
        
        :param page_items: Page field item label'''
        ...
    
    def add_identify(self, range_index : int, page_item_index : List[int]):
        '''Sets which item label in each page field to use to identify the data range.
        The pageItemIndex.Length must be equal to PageFieldCount, so please add the page field first.
        
        :param range_index: The consolidation data range index.
        :param page_item_index: The page item index in the each page field.
        pageItemIndex[2] = 1 means the second item in the third field to use to identify this range.
        pageItemIndex[1] = -1 means no item in the second field to use to identify this range
        and MS will auto create "blank" item in the second field  to identify this range.'''
        ...
    
    @property
    def page_field_count(self) -> int:
        ...
    
    ...

class PivotTable:
    '''Summary description for PivotTable.'''
    
    @overload
    def remove_field(self, field_type : aspose.cells.pivot.PivotFieldType, field_name : str):
        '''Removes a field from specific field area
        
        :param field_type: The fields area type.
        :param field_name: The name in the base fields.'''
        ...
    
    @overload
    def remove_field(self, field_type : aspose.cells.pivot.PivotFieldType, base_field_index : int):
        '''Removes a field from specific field area
        
        :param field_type: The fields area type.
        :param base_field_index: The field index in the base fields.'''
        ...
    
    @overload
    def remove_field(self, field_type : aspose.cells.pivot.PivotFieldType, pivot_field : aspose.cells.pivot.PivotField):
        '''Remove field from specific field area
        
        :param field_type: the fields area type.
        :param pivot_field: the field in the base fields.'''
        ...
    
    @overload
    def add_field_to_area(self, field_type : aspose.cells.pivot.PivotFieldType, field_name : str) -> int:
        '''Adds the field to the specific area.
        
        :param field_type: The fields area type.
        :param field_name: The name in the base fields.
        :returns: The field position in the specific fields.If there is no field named as it, return -1.'''
        ...
    
    @overload
    def add_field_to_area(self, field_type : aspose.cells.pivot.PivotFieldType, base_field_index : int) -> int:
        '''Adds the field to the specific area.
        
        :param field_type: The fields area type.
        :param base_field_index: The field index in the base fields.
        :returns: The field position in the specific fields.'''
        ...
    
    @overload
    def add_field_to_area(self, field_type : aspose.cells.pivot.PivotFieldType, pivot_field : aspose.cells.pivot.PivotField) -> int:
        '''Adds the field to the specific area.
        
        :param field_type: the fields area type.
        :param pivot_field: the field in the base fields.
        :returns: the field position in the specific fields.'''
        ...
    
    @overload
    def add_calculated_field(self, name : str, formula : str, drag_to_data_area : bool):
        '''Adds a calculated field to pivot field.
        
        :param name: The name of the calculated field
        :param formula: The formula of the calculated field.
        :param drag_to_data_area: True,drag this field to data area immediately'''
        ...
    
    @overload
    def add_calculated_field(self, name : str, formula : str):
        '''Adds a calculated field to pivot field and drag it to data area.
        
        :param name: The name of the calculated field
        :param formula: The formula of the calculated field.'''
        ...
    
    @overload
    def move(self, row : int, column : int):
        '''Moves the PivotTable to a different location in the worksheet.
        
        :param row: row index.
        :param column: column index.'''
        ...
    
    @overload
    def move(self, dest_cell_name : str):
        '''Moves the PivotTable to a different location in the worksheet.
        
        :param dest_cell_name: the dest cell name.'''
        ...
    
    @overload
    def format(self, pivot_area : aspose.cells.pivot.PivotArea, style : aspose.cells.Style):
        '''Formats selected area of the PivotTable.'''
        ...
    
    @overload
    def format(self, row : int, column : int, style : aspose.cells.Style):
        '''Format the cell in the pivottable area
        
        :param row: Row Index of the cell
        :param column: Column index of the cell
        :param style: Style which is to format the cell'''
        ...
    
    @overload
    def set_auto_group_field(self, base_field_index : int):
        '''Sets auto field group by the PivotTable.
        
        :param base_field_index: The row or column field index in the base fields'''
        ...
    
    @overload
    def set_auto_group_field(self, pivot_field : aspose.cells.pivot.PivotField):
        '''Sets auto field group by the PivotTable.
        
        :param pivot_field: The row or column field in the specific fields'''
        ...
    
    @overload
    def set_manual_group_field(self, base_field_index : int, start_val : float, end_val : float, group_by_list : list, interval_num : float):
        '''Sets manual field group by the PivotTable.
        
        :param base_field_index: The row or column field index in the base fields
        :param start_val: Specifies the starting value for numeric grouping.
        :param end_val: Specifies the ending value for numeric grouping.
        :param group_by_list: Specifies the grouping type list. Specified by PivotTableGroupType
        :param interval_num: Specifies the interval number group by  numeric grouping.'''
        ...
    
    @overload
    def set_manual_group_field(self, pivot_field : aspose.cells.pivot.PivotField, start_val : float, end_val : float, group_by_list : list, interval_num : float):
        '''Sets manual field group by the PivotTable.
        
        :param pivot_field: The row or column field in the base fields
        :param start_val: Specifies the starting value for numeric grouping.
        :param end_val: Specifies the ending value for numeric grouping.
        :param group_by_list: Specifies the grouping type list. Specified by PivotTableGroupType
        :param interval_num: Specifies the interval number group by numeric grouping.'''
        ...
    
    @overload
    def set_manual_group_field(self, base_field_index : int, start_val : DateTime, end_val : DateTime, group_by_list : list, interval_num : int):
        '''Sets manual field group by the PivotTable.
        
        :param base_field_index: The row or column field index in the base fields
        :param start_val: Specifies the starting value for date grouping.
        :param end_val: Specifies the ending value for date grouping.
        :param group_by_list: Specifies the grouping type list. Specified by PivotTableGroupType
        :param interval_num: Specifies the interval number group by in days grouping.The number of days must be positive integer of nonzero'''
        ...
    
    @overload
    def set_manual_group_field(self, pivot_field : aspose.cells.pivot.PivotField, start_val : DateTime, end_val : DateTime, group_by_list : list, interval_num : int):
        '''Sets manual field group by the PivotTable.
        
        :param pivot_field: The row or column field in the base fields
        :param start_val: Specifies the starting value for date grouping.
        :param end_val: Specifies the ending value for date grouping.
        :param group_by_list: Specifies the grouping type list. Specified by PivotTableGroupType
        :param interval_num: Specifies the interval number group by in days grouping.The number of days must be positive integer of nonzero'''
        ...
    
    @overload
    def set_ungroup(self, base_field_index : int):
        '''Sets ungroup by the PivotTable
        
        :param base_field_index: The row or column field index in the base fields'''
        ...
    
    @overload
    def set_ungroup(self, pivot_field : aspose.cells.pivot.PivotField):
        '''Sets ungroup by the PivotTable
        
        :param pivot_field: The row or column field in the base fields'''
        ...
    
    def copy_style(self, pivot_table : aspose.cells.pivot.PivotTable):
        '''Copies named style from another pivot table.
        
        :param pivot_table: Source pivot table.'''
        ...
    
    def show_report_filter_page(self, page_field : aspose.cells.pivot.PivotField):
        '''Show all the report filter pages according to PivotField, the PivotField must be located in the PageFields.
        
        :param page_field: The PivotField object'''
        ...
    
    def show_report_filter_page_by_name(self, field_name : str):
        '''Show all the report filter pages according to PivotField's name, the PivotField must be located in the PageFields.
        
        :param field_name: The name of PivotField'''
        ...
    
    def show_report_filter_page_by_index(self, pos_index : int):
        '''Show all the report filter pages according to the position index in the PageFields
        
        :param pos_index: The position index in the PageFields'''
        ...
    
    def fields(self, field_type : aspose.cells.pivot.PivotFieldType) -> aspose.cells.pivot.PivotFieldCollection:
        '''Gets the specific fields by the field type.
        
        :param field_type: the field type.
        :returns: the specific fields'''
        ...
    
    def change_data_source(self, source : List[str]):
        '''Set pivottable's source data.
        Sheet1!$A$1:$C$3'''
        ...
    
    def get_source(self) -> List[str]:
        '''Get pivottable's source data.'''
        ...
    
    def refresh_data(self):
        '''Refreshes pivottable's data and setting from it's data source.'''
        ...
    
    def calculate_data(self):
        '''Calculates pivottable's data to cells.'''
        ...
    
    def clear_data(self):
        '''Clear PivotTable's data and formatting'''
        ...
    
    def calculate_range(self):
        '''Calculates pivottable's range.'''
        ...
    
    def format_all(self, style : aspose.cells.Style):
        '''Format all the cell in the pivottable area
        
        :param style: Style which is to format'''
        ...
    
    def format_row(self, row : int, style : aspose.cells.Style):
        '''Format the row data in the pivottable area
        
        :param row: Row Index of the Row object
        :param style: Style which is to format'''
        ...
    
    def get_horizontal_breaks(self) -> list:
        '''get pivot table row index list of horizontal pagebreaks'''
        ...
    
    def show_in_compact_form(self):
        '''Layouts the PivotTable in compact form.'''
        ...
    
    def show_in_outline_form(self):
        '''Layouts the PivotTable in outline form.'''
        ...
    
    def show_in_tabular_form(self):
        '''Layouts the PivotTable in tabular form.'''
        ...
    
    def get_cell_by_display_name(self, display_name : str) -> aspose.cells.Cell:
        '''Gets the Cell object by the DisplayName of PivotField
        
        :param display_name: the DisplayName of PivotField
        :returns: the Cell object'''
        ...
    
    def get_children(self) -> List[aspose.cells.pivot.PivotTable]:
        '''Gets the Children Pivot Tables which use this PivotTable data as data source.
        
        :returns: the PivotTable array object'''
        ...
    
    @property
    def is_excel_2003_compatible(self) -> bool:
        ...
    
    @is_excel_2003_compatible.setter
    def is_excel_2003_compatible(self, value : bool):
        ...
    
    @property
    def refreshed_by_who(self) -> str:
        ...
    
    @property
    def refresh_date(self) -> DateTime:
        ...
    
    @property
    def pivot_table_style_name(self) -> str:
        ...
    
    @pivot_table_style_name.setter
    def pivot_table_style_name(self, value : str):
        ...
    
    @property
    def pivot_table_style_type(self) -> aspose.cells.pivot.PivotTableStyleType:
        ...
    
    @pivot_table_style_type.setter
    def pivot_table_style_type(self, value : aspose.cells.pivot.PivotTableStyleType):
        ...
    
    @property
    def column_fields(self) -> aspose.cells.pivot.PivotFieldCollection:
        ...
    
    @property
    def row_fields(self) -> aspose.cells.pivot.PivotFieldCollection:
        ...
    
    @property
    def page_fields(self) -> aspose.cells.pivot.PivotFieldCollection:
        ...
    
    @property
    def data_fields(self) -> aspose.cells.pivot.PivotFieldCollection:
        ...
    
    @property
    def data_field(self) -> aspose.cells.pivot.PivotField:
        ...
    
    @property
    def base_fields(self) -> aspose.cells.pivot.PivotFieldCollection:
        ...
    
    @property
    def pivot_filters(self) -> aspose.cells.pivot.PivotFilterCollection:
        ...
    
    @property
    def column_range(self) -> aspose.cells.CellArea:
        ...
    
    @property
    def row_range(self) -> aspose.cells.CellArea:
        ...
    
    @property
    def data_body_range(self) -> aspose.cells.CellArea:
        ...
    
    @property
    def table_range1(self) -> aspose.cells.CellArea:
        ...
    
    @property
    def table_range2(self) -> aspose.cells.CellArea:
        ...
    
    @property
    def column_grand(self) -> bool:
        ...
    
    @column_grand.setter
    def column_grand(self, value : bool):
        ...
    
    @property
    def is_grid_drop_zones(self) -> bool:
        ...
    
    @is_grid_drop_zones.setter
    def is_grid_drop_zones(self, value : bool):
        ...
    
    @property
    def row_grand(self) -> bool:
        ...
    
    @row_grand.setter
    def row_grand(self, value : bool):
        ...
    
    @property
    def display_null_string(self) -> bool:
        ...
    
    @display_null_string.setter
    def display_null_string(self, value : bool):
        ...
    
    @property
    def null_string(self) -> str:
        ...
    
    @null_string.setter
    def null_string(self, value : str):
        ...
    
    @property
    def display_error_string(self) -> bool:
        ...
    
    @display_error_string.setter
    def display_error_string(self, value : bool):
        ...
    
    @property
    def data_field_header_name(self) -> str:
        ...
    
    @data_field_header_name.setter
    def data_field_header_name(self, value : str):
        ...
    
    @property
    def error_string(self) -> str:
        ...
    
    @error_string.setter
    def error_string(self, value : str):
        ...
    
    @property
    def is_auto_format(self) -> bool:
        ...
    
    @is_auto_format.setter
    def is_auto_format(self, value : bool):
        ...
    
    @property
    def autofit_column_width_on_update(self) -> bool:
        ...
    
    @autofit_column_width_on_update.setter
    def autofit_column_width_on_update(self, value : bool):
        ...
    
    @property
    def auto_format_type(self) -> aspose.cells.pivot.PivotTableAutoFormatType:
        ...
    
    @auto_format_type.setter
    def auto_format_type(self, value : aspose.cells.pivot.PivotTableAutoFormatType):
        ...
    
    @property
    def has_blank_rows(self) -> bool:
        ...
    
    @has_blank_rows.setter
    def has_blank_rows(self, value : bool):
        ...
    
    @property
    def merge_labels(self) -> bool:
        ...
    
    @merge_labels.setter
    def merge_labels(self, value : bool):
        ...
    
    @property
    def preserve_formatting(self) -> bool:
        ...
    
    @preserve_formatting.setter
    def preserve_formatting(self, value : bool):
        ...
    
    @property
    def show_drill(self) -> bool:
        ...
    
    @show_drill.setter
    def show_drill(self, value : bool):
        ...
    
    @property
    def enable_drilldown(self) -> bool:
        ...
    
    @enable_drilldown.setter
    def enable_drilldown(self, value : bool):
        ...
    
    @property
    def enable_field_dialog(self) -> bool:
        ...
    
    @enable_field_dialog.setter
    def enable_field_dialog(self, value : bool):
        ...
    
    @property
    def enable_field_list(self) -> bool:
        ...
    
    @enable_field_list.setter
    def enable_field_list(self, value : bool):
        ...
    
    @property
    def enable_wizard(self) -> bool:
        ...
    
    @enable_wizard.setter
    def enable_wizard(self, value : bool):
        ...
    
    @property
    def subtotal_hidden_page_items(self) -> bool:
        ...
    
    @subtotal_hidden_page_items.setter
    def subtotal_hidden_page_items(self, value : bool):
        ...
    
    @property
    def grand_total_name(self) -> str:
        ...
    
    @grand_total_name.setter
    def grand_total_name(self, value : str):
        ...
    
    @property
    def manual_update(self) -> bool:
        ...
    
    @manual_update.setter
    def manual_update(self, value : bool):
        ...
    
    @property
    def is_multiple_field_filters(self) -> bool:
        ...
    
    @is_multiple_field_filters.setter
    def is_multiple_field_filters(self, value : bool):
        ...
    
    @property
    def missing_items_limit(self) -> aspose.cells.pivot.PivotMissingItemLimitType:
        ...
    
    @missing_items_limit.setter
    def missing_items_limit(self, value : aspose.cells.pivot.PivotMissingItemLimitType):
        ...
    
    @property
    def enable_data_value_editing(self) -> bool:
        ...
    
    @enable_data_value_editing.setter
    def enable_data_value_editing(self, value : bool):
        ...
    
    @property
    def show_data_tips(self) -> bool:
        ...
    
    @show_data_tips.setter
    def show_data_tips(self, value : bool):
        ...
    
    @property
    def show_member_property_tips(self) -> bool:
        ...
    
    @show_member_property_tips.setter
    def show_member_property_tips(self, value : bool):
        ...
    
    @property
    def show_values_row(self) -> bool:
        ...
    
    @show_values_row.setter
    def show_values_row(self, value : bool):
        ...
    
    @property
    def show_empty_col(self) -> bool:
        ...
    
    @show_empty_col.setter
    def show_empty_col(self, value : bool):
        ...
    
    @property
    def show_empty_row(self) -> bool:
        ...
    
    @show_empty_row.setter
    def show_empty_row(self, value : bool):
        ...
    
    @property
    def field_list_sort_ascending(self) -> bool:
        ...
    
    @field_list_sort_ascending.setter
    def field_list_sort_ascending(self, value : bool):
        ...
    
    @property
    def print_drill(self) -> bool:
        ...
    
    @print_drill.setter
    def print_drill(self, value : bool):
        ...
    
    @property
    def alt_text_title(self) -> str:
        ...
    
    @alt_text_title.setter
    def alt_text_title(self, value : str):
        ...
    
    @property
    def alt_text_description(self) -> str:
        ...
    
    @alt_text_description.setter
    def alt_text_description(self, value : str):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of the PivotTable'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets the name of the PivotTable'''
        ...
    
    @property
    def column_header_caption(self) -> str:
        ...
    
    @column_header_caption.setter
    def column_header_caption(self, value : str):
        ...
    
    @property
    def indent(self) -> int:
        '''Specifies the indentation increment for compact axis and can be used to set the Report Layout to Compact Form.'''
        ...
    
    @indent.setter
    def indent(self, value : int):
        '''Specifies the indentation increment for compact axis and can be used to set the Report Layout to Compact Form.'''
        ...
    
    @property
    def row_header_caption(self) -> str:
        ...
    
    @row_header_caption.setter
    def row_header_caption(self, value : str):
        ...
    
    @property
    def show_row_header_caption(self) -> bool:
        ...
    
    @show_row_header_caption.setter
    def show_row_header_caption(self, value : bool):
        ...
    
    @property
    def custom_list_sort(self) -> bool:
        ...
    
    @custom_list_sort.setter
    def custom_list_sort(self, value : bool):
        ...
    
    @property
    def pivot_format_conditions(self) -> aspose.cells.pivot.PivotFormatConditionCollection:
        ...
    
    @property
    def page_field_order(self) -> aspose.cells.PrintOrderType:
        ...
    
    @page_field_order.setter
    def page_field_order(self, value : aspose.cells.PrintOrderType):
        ...
    
    @property
    def page_field_wrap_count(self) -> int:
        ...
    
    @page_field_wrap_count.setter
    def page_field_wrap_count(self, value : int):
        ...
    
    @property
    def tag(self) -> str:
        '''Gets a string saved with the PivotTable report.'''
        ...
    
    @tag.setter
    def tag(self, value : str):
        '''Gets a string saved with the PivotTable report.'''
        ...
    
    @property
    def save_data(self) -> bool:
        ...
    
    @save_data.setter
    def save_data(self, value : bool):
        ...
    
    @property
    def refresh_data_on_opening_file(self) -> bool:
        ...
    
    @refresh_data_on_opening_file.setter
    def refresh_data_on_opening_file(self, value : bool):
        ...
    
    @property
    def refresh_data_flag(self) -> bool:
        ...
    
    @refresh_data_flag.setter
    def refresh_data_flag(self, value : bool):
        ...
    
    @property
    def external_connection_data_source(self) -> aspose.cells.externalconnections.ExternalConnection:
        ...
    
    @property
    def data_source(self) -> List[str]:
        ...
    
    @data_source.setter
    def data_source(self, value : List[str]):
        ...
    
    @property
    def pivot_formats(self) -> aspose.cells.pivot.PivotTableFormatCollection:
        ...
    
    @property
    def item_print_titles(self) -> bool:
        ...
    
    @item_print_titles.setter
    def item_print_titles(self, value : bool):
        ...
    
    @property
    def print_titles(self) -> bool:
        ...
    
    @print_titles.setter
    def print_titles(self, value : bool):
        ...
    
    @property
    def display_immediate_items(self) -> bool:
        ...
    
    @display_immediate_items.setter
    def display_immediate_items(self, value : bool):
        ...
    
    @property
    def is_selected(self) -> bool:
        ...
    
    @is_selected.setter
    def is_selected(self, value : bool):
        ...
    
    @property
    def show_pivot_style_row_header(self) -> bool:
        ...
    
    @show_pivot_style_row_header.setter
    def show_pivot_style_row_header(self, value : bool):
        ...
    
    @property
    def show_pivot_style_column_header(self) -> bool:
        ...
    
    @show_pivot_style_column_header.setter
    def show_pivot_style_column_header(self, value : bool):
        ...
    
    @property
    def show_pivot_style_row_stripes(self) -> bool:
        ...
    
    @show_pivot_style_row_stripes.setter
    def show_pivot_style_row_stripes(self, value : bool):
        ...
    
    @property
    def show_pivot_style_column_stripes(self) -> bool:
        ...
    
    @show_pivot_style_column_stripes.setter
    def show_pivot_style_column_stripes(self, value : bool):
        ...
    
    @property
    def show_pivot_style_last_column(self) -> bool:
        ...
    
    @show_pivot_style_last_column.setter
    def show_pivot_style_last_column(self, value : bool):
        ...
    
    ...

class PivotTableCollection:
    '''Represents the collection of all the PivotTable objects on the specified worksheet.'''
    
    @overload
    def add(self, source_data : str, dest_cell_name : str, table_name : str) -> int:
        '''Adds a new PivotTable cache to a PivotCaches collection.
        
        :param source_data: The data for the new PivotTable cache.
        :param dest_cell_name: The cell in the upper-left corner of the PivotTable report's destination range.
        :param table_name: The name of the new PivotTable report.
        :returns: The new added cache index.'''
        ...
    
    @overload
    def add(self, source_data : str, dest_cell_name : str, table_name : str, use_same_source : bool) -> int:
        '''Adds a new PivotTable cache to a PivotCaches collection.
        
        :param source_data: The data for the new PivotTable cache.
        :param dest_cell_name: The cell in the upper-left corner of the PivotTable report's destination range.
        :param table_name: The name of the new PivotTable report.
        :param use_same_source: Indicates whether using same data source when another existing pivot table has used this data source.
        If the property is true, it will save memory.
        :returns: The new added cache index.'''
        ...
    
    @overload
    def add(self, source_data : str, row : int, column : int, table_name : str) -> int:
        '''Adds a new PivotTable cache to a PivotCaches collection.
        
        :param source_data: The data cell range for the new PivotTable.Example : Sheet1!A1:C8
        :param row: Row index of the cell in the upper-left corner of the PivotTable report's destination range.
        :param column: Column index of the cell in the upper-left corner of the PivotTable report's destination range.
        :param table_name: The name of the new PivotTable report.
        :returns: The new added cache index.'''
        ...
    
    @overload
    def add(self, source_data : str, row : int, column : int, table_name : str, use_same_source : bool) -> int:
        '''Adds a new PivotTable cache to a PivotCaches collection.
        
        :param source_data: The data cell range for the new PivotTable.Example : Sheet1!A1:C8
        :param row: Row index of the cell in the upper-left corner of the PivotTable report's destination range.
        :param column: Column index of the cell in the upper-left corner of the PivotTable report's destination range.
        :param table_name: The name of the new PivotTable report.
        :param use_same_source: Indicates whether using same data source when another existing pivot table has used this data source.
        If the property is true, it will save memory.
        :returns: The new added cache index.'''
        ...
    
    @overload
    def add(self, pivot_table : aspose.cells.pivot.PivotTable, dest_cell_name : str, table_name : str) -> int:
        '''Adds a new PivotTable Object to the collection from another PivotTable.
        
        :param pivot_table: The source pivotTable.
        :param dest_cell_name: The cell in the upper-left corner of the PivotTable report's destination range.
        :param table_name: The name of the new PivotTable report.
        :returns: The new added PivotTable index.'''
        ...
    
    @overload
    def add(self, pivot_table : aspose.cells.pivot.PivotTable, row : int, column : int, table_name : str) -> int:
        '''Adds a new PivotTable Object to the collection from another PivotTable.
        
        :param pivot_table: The source pivotTable.
        :param row: Row index of the cell in the upper-left corner of the PivotTable report's destination range.
        :param column: Column index of the cell in the upper-left corner of the PivotTable report's destination range.
        :param table_name: The name of the new PivotTable report.
        :returns: The new added PivotTable index.'''
        ...
    
    @overload
    def add(self, source_data : List[str], is_auto_page : bool, page_fields : aspose.cells.pivot.PivotPageFields, dest_cell_name : str, table_name : str) -> int:
        '''Adds a new PivotTable Object to the collection with multiple consolidation ranges as data source.
        
        :param source_data: The multiple consolidation ranges,such as {"Sheet1!A1:C8","Sheet2!A1:B8"}
        :param is_auto_page: Whether auto create a single page field.
        If true,the following param pageFields will be ignored.
        :param page_fields: The pivot page field items.
        :param dest_cell_name: destCellName The name of the new PivotTable report.
        :param table_name: the name of the new PivotTable report.
        :returns: The new added PivotTable index.'''
        ...
    
    @overload
    def add(self, source_data : List[str], is_auto_page : bool, page_fields : aspose.cells.pivot.PivotPageFields, row : int, column : int, table_name : str) -> int:
        '''Adds a new PivotTable Object to the collection with multiple consolidation ranges as data source.
        
        :param source_data: The multiple consolidation ranges,such as {"Sheet1!A1:C8","Sheet2!A1:B8"}
        :param is_auto_page: Whether auto create a single page field.
        If true,the following param pageFields will be ignored
        :param page_fields: The pivot page field items.
        :param row: Row index of the cell in the upper-left corner of the PivotTable report's destination range.
        :param column: Column index of the cell in the upper-left corner of the PivotTable report's destination range.
        :param table_name: The name of the new PivotTable report.
        :returns: The new added PivotTable index.'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.pivot.PivotTable]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.pivot.PivotTable], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotTable, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotTable, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotTable) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotTable, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotTable, index : int, count : int) -> int:
        ...
    
    def remove_at(self, index : int, keep_data : bool):
        '''Deletes the PivotTable at the specified index
        
        :param index: the position index in PivotTable collection
        :param keep_data: Whether to keep the PivotTable data'''
        ...
    
    def binary_search(self, item : aspose.cells.pivot.PivotTable) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class PivotTableFormat:
    '''Represents the format defined in the PivotTable.'''
    
    def get_style(self) -> aspose.cells.Style:
        '''Gets the formatted style.'''
        ...
    
    def set_style(self, style : aspose.cells.Style):
        '''Sets the style of the pivot area.'''
        ...
    
    @property
    def pivot_area(self) -> aspose.cells.pivot.PivotArea:
        ...
    
    ...

class PivotTableFormatCollection:
    '''Represents the collection of formats applied to PivotTable.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.pivot.PivotTableFormat]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.pivot.PivotTableFormat], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotTableFormat, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.pivot.PivotTableFormat, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotTableFormat) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotTableFormat, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.pivot.PivotTableFormat, index : int, count : int) -> int:
        ...
    
    def add(self) -> int:
        '''Add a :py:class:`aspose.cells.pivot.PivotTableFormat`.
        
        :returns: The index of new format.'''
        ...
    
    def format_area(self, axis_type : aspose.cells.pivot.PivotFieldType, field_position : int, subtotal_type : aspose.cells.pivot.PivotFieldSubtotalType, selection_type : aspose.cells.pivot.PivotTableSelectionType, is_grand_row : bool, is_grand_column : bool, style : aspose.cells.Style) -> aspose.cells.pivot.PivotTableFormat:
        '''Formats selected area.
        
        :param axis_type: The region of the PivotTable to which this rule applies.
        :param field_position: Position of the field within the axis to which this rule applies.
        :param subtotal_type: The subtotal filter type of the pivot field
        :param selection_type: Indicates how to select data.
        :param is_grand_row: Indicates whether selecting grand total rows.
        :param is_grand_column: Indicates whether selecting grand total columns.
        :param style: The style which appies to the area of the pivot table.'''
        ...
    
    def binary_search(self, item : aspose.cells.pivot.PivotTableFormat) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class SxRng:
    '''Represents Group Range in a PivotField.'''
    
    @property
    def is_auto_start(self) -> any:
        ...
    
    @property
    def is_auto_end(self) -> any:
        ...
    
    @property
    def start(self) -> any:
        '''Represents the start object for the group range.'''
        ...
    
    @property
    def end(self) -> any:
        '''Represents the end object for the group range.'''
        ...
    
    @property
    def by(self) -> any:
        '''Represents the interval object for the group range.'''
        ...
    
    @property
    def group_by_types(self) -> List[bool]:
        ...
    
    ...

class PivotAreaType:
    '''Indicates the type of rule being used to describe an area or aspect of the PivotTable.'''
    
    @classmethod
    @property
    def NONE(cls) -> PivotAreaType:
        '''No Pivot area.'''
        ...
    
    @classmethod
    @property
    def NORMAL(cls) -> PivotAreaType:
        '''Represents a header or item.'''
        ...
    
    @classmethod
    @property
    def DATA(cls) -> PivotAreaType:
        '''Represents something in the data area.'''
        ...
    
    @classmethod
    @property
    def ALL(cls) -> PivotAreaType:
        '''Represents the whole PivotTable.'''
        ...
    
    @classmethod
    @property
    def ORIGIN(cls) -> PivotAreaType:
        '''Represents the blank cells at the top-left of the PivotTable (top-right for RTL sheets).'''
        ...
    
    @classmethod
    @property
    def BUTTON(cls) -> PivotAreaType:
        '''Represents a field button.'''
        ...
    
    @classmethod
    @property
    def TOP_RIGHT(cls) -> PivotAreaType:
        '''Represents the blank cells at the top-right of the PivotTable (top-left for RTL sheets).'''
        ...
    
    ...

class PivotConditionFormatRuleType:
    '''Represents PivotTable condition formatting rule type.'''
    
    @classmethod
    @property
    def NONE(cls) -> PivotConditionFormatRuleType:
        '''Indicates that Top N conditional formatting is not evaluated'''
        ...
    
    @classmethod
    @property
    def ALL(cls) -> PivotConditionFormatRuleType:
        '''Indicates that Top N conditional formatting is
        evaluated across the entire scope range.'''
        ...
    
    @classmethod
    @property
    def ROW(cls) -> PivotConditionFormatRuleType:
        '''Indicates that Top N conditional formatting is evaluated for each row.'''
        ...
    
    @classmethod
    @property
    def COLUMN(cls) -> PivotConditionFormatRuleType:
        '''Indicates that Top N conditional formatting is
        evaluated for each column.'''
        ...
    
    ...

class PivotConditionFormatScopeType:
    '''Represents PivotTable condition formatting scope type.'''
    
    @classmethod
    @property
    def DATA(cls) -> PivotConditionFormatScopeType:
        '''Indicates that conditional formatting is applied to the selected data fields.'''
        ...
    
    @classmethod
    @property
    def FIELD(cls) -> PivotConditionFormatScopeType:
        '''Indicates that conditional formatting is applied to the selected PivotTable field intersections.'''
        ...
    
    @classmethod
    @property
    def SELECTION(cls) -> PivotConditionFormatScopeType:
        '''Indicates that conditional formatting is applied to the selected cells.'''
        ...
    
    ...

class PivotFieldDataDisplayFormat:
    '''Represents data display format in the PivotTable data field.'''
    
    @classmethod
    @property
    def NORMAL(cls) -> PivotFieldDataDisplayFormat:
        '''Represents normal display format.'''
        ...
    
    @classmethod
    @property
    def DIFFERENCE_FROM(cls) -> PivotFieldDataDisplayFormat:
        '''Represents difference from display format.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE_OF(cls) -> PivotFieldDataDisplayFormat:
        '''Represents percentage of display format.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE_DIFFERENCE_FROM(cls) -> PivotFieldDataDisplayFormat:
        '''Represents percentage difference from  display format.'''
        ...
    
    @classmethod
    @property
    def RUNNING_TOTAL_IN(cls) -> PivotFieldDataDisplayFormat:
        '''Represents running total in display format.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE_OF_ROW(cls) -> PivotFieldDataDisplayFormat:
        '''Represents percentage of row display format.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE_OF_COLUMN(cls) -> PivotFieldDataDisplayFormat:
        '''Represents percentage of column display format.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE_OF_TOTAL(cls) -> PivotFieldDataDisplayFormat:
        '''Represents percentage of total display format.'''
        ...
    
    @classmethod
    @property
    def INDEX(cls) -> PivotFieldDataDisplayFormat:
        '''Represents index display format.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE_OF_PARENT_ROW_TOTAL(cls) -> PivotFieldDataDisplayFormat:
        '''Represents percentage of parent row total display format.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE_OF_PARENT_COLUMN_TOTAL(cls) -> PivotFieldDataDisplayFormat:
        '''Represents percentage of parent column total display format.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE_OF_PARENT_TOTAL(cls) -> PivotFieldDataDisplayFormat:
        '''Represents percentage of parent total display format.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE_OF_RUNNING_TOTAL_IN(cls) -> PivotFieldDataDisplayFormat:
        '''Represents percentage of running total in display format.'''
        ...
    
    @classmethod
    @property
    def RANK_SMALLEST_TO_LARGEST(cls) -> PivotFieldDataDisplayFormat:
        '''Represents smallest to largest display format.'''
        ...
    
    @classmethod
    @property
    def RANK_LARGEST_TO_SMALLEST(cls) -> PivotFieldDataDisplayFormat:
        '''Represents largest to smallest display format.'''
        ...
    
    ...

class PivotFieldSubtotalType:
    '''Summary description for PivotFieldSubtotalType.'''
    
    @classmethod
    @property
    def NONE(cls) -> PivotFieldSubtotalType:
        '''Represents None subtotal type.'''
        ...
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> PivotFieldSubtotalType:
        '''Represents Automatic subtotal type.'''
        ...
    
    @classmethod
    @property
    def SUM(cls) -> PivotFieldSubtotalType:
        '''Represents Sum subtotal type.'''
        ...
    
    @classmethod
    @property
    def COUNT(cls) -> PivotFieldSubtotalType:
        '''Represents Count subtotal type.'''
        ...
    
    @classmethod
    @property
    def AVERAGE(cls) -> PivotFieldSubtotalType:
        '''Represents Average subtotal type.'''
        ...
    
    @classmethod
    @property
    def MAX(cls) -> PivotFieldSubtotalType:
        '''Represents Max subtotal type.'''
        ...
    
    @classmethod
    @property
    def MIN(cls) -> PivotFieldSubtotalType:
        '''Represents Min subtotal type.'''
        ...
    
    @classmethod
    @property
    def PRODUCT(cls) -> PivotFieldSubtotalType:
        '''Represents Product subtotal type.'''
        ...
    
    @classmethod
    @property
    def COUNT_NUMS(cls) -> PivotFieldSubtotalType:
        '''Represents Count Nums subtotal type.'''
        ...
    
    @classmethod
    @property
    def STDEV(cls) -> PivotFieldSubtotalType:
        '''Represents Stdev subtotal type.'''
        ...
    
    @classmethod
    @property
    def STDEVP(cls) -> PivotFieldSubtotalType:
        '''Represents Stdevp subtotal type.'''
        ...
    
    @classmethod
    @property
    def VAR(cls) -> PivotFieldSubtotalType:
        '''Represents Var subtotal type.'''
        ...
    
    @classmethod
    @property
    def VARP(cls) -> PivotFieldSubtotalType:
        '''Represents Varp subtotal type.'''
        ...
    
    ...

class PivotFieldType:
    '''Represents PivotTable field type.'''
    
    @classmethod
    @property
    def UNDEFINED(cls) -> PivotFieldType:
        '''Presents base pivot field type.'''
        ...
    
    @classmethod
    @property
    def ROW(cls) -> PivotFieldType:
        '''Presents row pivot field type.'''
        ...
    
    @classmethod
    @property
    def COLUMN(cls) -> PivotFieldType:
        '''Presents column pivot field type.'''
        ...
    
    @classmethod
    @property
    def PAGE(cls) -> PivotFieldType:
        '''Presents page pivot field type.'''
        ...
    
    @classmethod
    @property
    def DATA(cls) -> PivotFieldType:
        '''Presents data pivot field type.'''
        ...
    
    ...

class PivotFilterType:
    '''Represents PivotTable Filter type.'''
    
    @classmethod
    @property
    def CAPTION_BEGINS_WITH(cls) -> PivotFilterType:
        '''Indicates the "begins with" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_BETWEEN(cls) -> PivotFilterType:
        '''Indicates the "is between" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_CONTAINS(cls) -> PivotFilterType:
        '''Indicates the "contains" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_ENDS_WITH(cls) -> PivotFilterType:
        '''Indicates the "ends with" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "equal" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_GREATER_THAN(cls) -> PivotFilterType:
        '''Indicates the "is greater than" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_GREATER_THAN_OR_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "is greater than or equal to" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_LESS_THAN(cls) -> PivotFilterType:
        '''Indicates the "is less than" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_LESS_THAN_OR_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "is less than or equal to" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_NOT_BEGINS_WITH(cls) -> PivotFilterType:
        '''Indicates the "does not begin with" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_NOT_BETWEEN(cls) -> PivotFilterType:
        '''Indicates the "is not between" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_NOT_CONTAINS(cls) -> PivotFilterType:
        '''Indicates the "does not contain" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_NOT_ENDS_WITH(cls) -> PivotFilterType:
        '''Indicates the "does not end with" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def CAPTION_NOT_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "not equal" filter for field captions.'''
        ...
    
    @classmethod
    @property
    def COUNT(cls) -> PivotFilterType:
        '''Indicates the "count" filter.'''
        ...
    
    @classmethod
    @property
    def DATE_BETWEEN(cls) -> PivotFilterType:
        '''Indicates the "between" filter for date values.'''
        ...
    
    @classmethod
    @property
    def DATE_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "equals" filter for date values.'''
        ...
    
    @classmethod
    @property
    def DATE_NEWER_THAN(cls) -> PivotFilterType:
        '''Indicates the "newer than" filter for date values.'''
        ...
    
    @classmethod
    @property
    def DATE_NEWER_THAN_OR_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "newer than or equal to" filter for date values.'''
        ...
    
    @classmethod
    @property
    def DATE_NOT_BETWEEN(cls) -> PivotFilterType:
        '''Indicates the "not between" filter for date values.'''
        ...
    
    @classmethod
    @property
    def DATE_NOT_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "does not equal" filter for date values.'''
        ...
    
    @classmethod
    @property
    def DATE_OLDER_THAN(cls) -> PivotFilterType:
        '''Indicates the "older than" filter for date values.'''
        ...
    
    @classmethod
    @property
    def DATE_OLDER_THAN_OR_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "older than or equal to" filter for date values.'''
        ...
    
    @classmethod
    @property
    def LAST_MONTH(cls) -> PivotFilterType:
        '''Indicates the "last month" filter for date values.'''
        ...
    
    @classmethod
    @property
    def LAST_QUARTER(cls) -> PivotFilterType:
        '''Indicates the "last quarter" filter for date values.'''
        ...
    
    @classmethod
    @property
    def LAST_WEEK(cls) -> PivotFilterType:
        '''Indicates the "last week" filter for date values.'''
        ...
    
    @classmethod
    @property
    def LAST_YEAR(cls) -> PivotFilterType:
        '''Indicates the "last year" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M1(cls) -> PivotFilterType:
        '''Indicates the "January" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M2(cls) -> PivotFilterType:
        '''Indicates the "February" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M3(cls) -> PivotFilterType:
        '''Indicates the "March" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M4(cls) -> PivotFilterType:
        '''Indicates the "April" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M5(cls) -> PivotFilterType:
        '''Indicates the "May" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M6(cls) -> PivotFilterType:
        '''Indicates the "June" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M7(cls) -> PivotFilterType:
        '''Indicates the "July" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M8(cls) -> PivotFilterType:
        '''Indicates the "August" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M9(cls) -> PivotFilterType:
        '''Indicates the "September" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M10(cls) -> PivotFilterType:
        '''Indicates the "October" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M11(cls) -> PivotFilterType:
        '''Indicates the "November" filter for date values.'''
        ...
    
    @classmethod
    @property
    def M12(cls) -> PivotFilterType:
        '''Indicates the "December" filter for date values.'''
        ...
    
    @classmethod
    @property
    def NEXT_MONTH(cls) -> PivotFilterType:
        '''Indicates the "next month" filter for date values.'''
        ...
    
    @classmethod
    @property
    def NEXT_QUARTER(cls) -> PivotFilterType:
        '''Indicates the "next quarter" for date values.'''
        ...
    
    @classmethod
    @property
    def NEXT_WEEK(cls) -> PivotFilterType:
        '''Indicates the "next week" for date values.'''
        ...
    
    @classmethod
    @property
    def NEXT_YEAR(cls) -> PivotFilterType:
        '''Indicates the "next year" filter for date values.'''
        ...
    
    @classmethod
    @property
    def PERCENT(cls) -> PivotFilterType:
        '''Indicates the "percent" filter for numeric values.'''
        ...
    
    @classmethod
    @property
    def Q1(cls) -> PivotFilterType:
        '''Indicates the "first quarter" filter for date values.'''
        ...
    
    @classmethod
    @property
    def Q2(cls) -> PivotFilterType:
        '''Indicates the "second quarter" filter for date values.'''
        ...
    
    @classmethod
    @property
    def Q3(cls) -> PivotFilterType:
        '''Indicates the "third quarter" filter for date values.'''
        ...
    
    @classmethod
    @property
    def Q4(cls) -> PivotFilterType:
        '''Indicates the "fourth quarter" filter for date values.'''
        ...
    
    @classmethod
    @property
    def SUM(cls) -> PivotFilterType:
        '''Indicates the "sum" filter for numeric values.'''
        ...
    
    @classmethod
    @property
    def THIS_MONTH(cls) -> PivotFilterType:
        '''Indicates the "this month" filter for date values.'''
        ...
    
    @classmethod
    @property
    def THIS_QUARTER(cls) -> PivotFilterType:
        '''Indicates the "this quarter" filter for date values.'''
        ...
    
    @classmethod
    @property
    def THIS_WEEK(cls) -> PivotFilterType:
        '''Indicates the "this week" filter for date values.'''
        ...
    
    @classmethod
    @property
    def THIS_YEAR(cls) -> PivotFilterType:
        '''Indicate the "this year" filter for date values.'''
        ...
    
    @classmethod
    @property
    def TODAY(cls) -> PivotFilterType:
        '''Indicates the "today" filter for date values.'''
        ...
    
    @classmethod
    @property
    def TOMORROW(cls) -> PivotFilterType:
        '''Indicates the "tomorrow" filter for date values.'''
        ...
    
    @classmethod
    @property
    def UNKNOWN(cls) -> PivotFilterType:
        '''Indicates the PivotTable filter is unknown to the application.'''
        ...
    
    @classmethod
    @property
    def VALUE_BETWEEN(cls) -> PivotFilterType:
        '''Indicates the "Value between" filter for text and numeric values.'''
        ...
    
    @classmethod
    @property
    def VALUE_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "value equal" filter for text and numeric values.'''
        ...
    
    @classmethod
    @property
    def VALUE_GREATER_THAN(cls) -> PivotFilterType:
        '''Indicates the "value greater than" filter for text and numeric values.'''
        ...
    
    @classmethod
    @property
    def VALUE_GREATER_THAN_OR_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "value greater than or equal to" filter for text and numeric values.'''
        ...
    
    @classmethod
    @property
    def VALUE_LESS_THAN(cls) -> PivotFilterType:
        '''Indicates the "value less than" filter for text and numeric values.'''
        ...
    
    @classmethod
    @property
    def VALUE_LESS_THAN_OR_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "value less than or equal to" filter for text and numeric values.'''
        ...
    
    @classmethod
    @property
    def VALUE_NOT_BETWEEN(cls) -> PivotFilterType:
        '''Indicates the "value not between" filter for text and numeric values.'''
        ...
    
    @classmethod
    @property
    def VALUE_NOT_EQUAL(cls) -> PivotFilterType:
        '''Indicates the "value not equal" filter for text and numeric values.'''
        ...
    
    @classmethod
    @property
    def YEAR_TO_DATE(cls) -> PivotFilterType:
        '''Indicates the "year-to-date" filter for date values.'''
        ...
    
    @classmethod
    @property
    def YESTERDAY(cls) -> PivotFilterType:
        '''Indicates the "yesterday" filter for date values.'''
        ...
    
    ...

class PivotGroupByType:
    '''Represents PivotTable groupby type.'''
    
    @classmethod
    @property
    def RANGE_OF_VALUES(cls) -> PivotGroupByType:
        '''Presents range of values groupby type.'''
        ...
    
    @classmethod
    @property
    def SECONDS(cls) -> PivotGroupByType:
        '''Presents Seconds groupby type.'''
        ...
    
    @classmethod
    @property
    def MINUTES(cls) -> PivotGroupByType:
        '''Presents Minutes groupby type.'''
        ...
    
    @classmethod
    @property
    def HOURS(cls) -> PivotGroupByType:
        '''Presents Hours groupby type.'''
        ...
    
    @classmethod
    @property
    def DAYS(cls) -> PivotGroupByType:
        '''Presents Days groupby type.'''
        ...
    
    @classmethod
    @property
    def MONTHS(cls) -> PivotGroupByType:
        '''Presents Months groupby type.'''
        ...
    
    @classmethod
    @property
    def QUARTERS(cls) -> PivotGroupByType:
        '''Presents Quarters groupby type.'''
        ...
    
    @classmethod
    @property
    def YEARS(cls) -> PivotGroupByType:
        '''Presents Years groupby type.'''
        ...
    
    ...

class PivotItemPosition:
    '''Represents PivotTable base item Next/Previous/All position in the base field .'''
    
    @classmethod
    @property
    def PREVIOUS(cls) -> PivotItemPosition:
        '''Represents the previous pivot item in the PivotField.'''
        ...
    
    @classmethod
    @property
    def NEXT(cls) -> PivotItemPosition:
        '''Represents the next pivot item in the PivotField.'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> PivotItemPosition:
        '''Represents a pivot item index, as specified by Pivot Items, that specifies a pivot item in the PivotField.'''
        ...
    
    ...

class PivotMissingItemLimitType:
    '''Represents number of items to retain per field.'''
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> PivotMissingItemLimitType:
        '''The default number of unique items per PivotField allowed.'''
        ...
    
    @classmethod
    @property
    def MAX(cls) -> PivotMissingItemLimitType:
        '''The maximum number of unique items per PivotField allowed (>32,500).'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> PivotMissingItemLimitType:
        '''No unique items per PivotField allowed.'''
        ...
    
    ...

class PivotTableAutoFormatType:
    '''Represents PivotTable auto format type.'''
    
    @classmethod
    @property
    def NONE(cls) -> PivotTableAutoFormatType:
        '''Represents None format type.'''
        ...
    
    @classmethod
    @property
    def CLASSIC(cls) -> PivotTableAutoFormatType:
        '''Represents Classic auto format type.'''
        ...
    
    @classmethod
    @property
    def REPORT1(cls) -> PivotTableAutoFormatType:
        '''Represents Report1 format type.'''
        ...
    
    @classmethod
    @property
    def REPORT2(cls) -> PivotTableAutoFormatType:
        '''Represents Report2 format type.'''
        ...
    
    @classmethod
    @property
    def REPORT3(cls) -> PivotTableAutoFormatType:
        '''Represents Report3 format type.'''
        ...
    
    @classmethod
    @property
    def REPORT4(cls) -> PivotTableAutoFormatType:
        '''Represents Report4 format type.'''
        ...
    
    @classmethod
    @property
    def REPORT5(cls) -> PivotTableAutoFormatType:
        '''Represents Report5 format type.'''
        ...
    
    @classmethod
    @property
    def REPORT6(cls) -> PivotTableAutoFormatType:
        '''Represents Report6 format type.'''
        ...
    
    @classmethod
    @property
    def REPORT7(cls) -> PivotTableAutoFormatType:
        '''Represents Report7 format type.'''
        ...
    
    @classmethod
    @property
    def REPORT8(cls) -> PivotTableAutoFormatType:
        '''Represents Report8 format type.'''
        ...
    
    @classmethod
    @property
    def REPORT9(cls) -> PivotTableAutoFormatType:
        '''Represents Report9 format type.'''
        ...
    
    @classmethod
    @property
    def REPORT10(cls) -> PivotTableAutoFormatType:
        '''Represents Report10 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE1(cls) -> PivotTableAutoFormatType:
        '''Represents Table1 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE2(cls) -> PivotTableAutoFormatType:
        '''Represents Table2 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE3(cls) -> PivotTableAutoFormatType:
        '''Represents Table3 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE4(cls) -> PivotTableAutoFormatType:
        '''Represents Table4 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE5(cls) -> PivotTableAutoFormatType:
        '''Represents Table5 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE6(cls) -> PivotTableAutoFormatType:
        '''Represents Table6 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE7(cls) -> PivotTableAutoFormatType:
        '''Represents Table7 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE8(cls) -> PivotTableAutoFormatType:
        '''Represents Table8 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE9(cls) -> PivotTableAutoFormatType:
        '''Represents Table9 format type.'''
        ...
    
    @classmethod
    @property
    def TABLE10(cls) -> PivotTableAutoFormatType:
        '''Represents Table10 format type.'''
        ...
    
    ...

class PivotTableSelectionType:
    '''Specifies what can be selected in a PivotTable during a structured selection.
    These constants can be combined to select multiple types.'''
    
    @classmethod
    @property
    def DATA_AND_LABEL(cls) -> PivotTableSelectionType:
        '''Data and labels'''
        ...
    
    @classmethod
    @property
    def DATA_ONLY(cls) -> PivotTableSelectionType:
        '''Only selects data'''
        ...
    
    @classmethod
    @property
    def LABEL_ONLY(cls) -> PivotTableSelectionType:
        '''Only selects labels'''
        ...
    
    ...

class PivotTableStyleType:
    '''Represents the pivot table style type.'''
    
    @classmethod
    @property
    def NONE(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT1(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT2(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT3(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT4(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT5(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT6(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT7(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT8(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT9(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT10(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT11(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT12(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT13(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT14(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT15(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT16(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT17(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT18(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT19(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT20(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT21(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT22(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT23(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT24(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT25(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT26(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT27(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_LIGHT28(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM1(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM2(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM3(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM4(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM5(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM6(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM7(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM8(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM9(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM10(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM11(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM12(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM13(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM14(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM15(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM16(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM17(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM18(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM19(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM20(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM21(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM22(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM23(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM24(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM25(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM26(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM27(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_MEDIUM28(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK1(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK2(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK3(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK4(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK5(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK6(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK7(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK8(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK9(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK10(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK11(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK12(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK13(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK14(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK15(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK16(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK17(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK18(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK19(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK20(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK21(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK22(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK23(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK24(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK25(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK26(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK27(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def PIVOT_TABLE_STYLE_DARK28(cls) -> PivotTableStyleType:
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> PivotTableStyleType:
        ...
    
    ...

