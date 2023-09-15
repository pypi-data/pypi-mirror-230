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

class PivotGlobalizationSettings:
    '''Represents the globalization settings for pivot tables.'''
    
    def get_text_of_total(self) -> str:
        '''Gets the text of "Total" label in the PivotTable.
        You need to override this method when the PivotTable contains two or more PivotFields in the data area.
        
        :returns: The text of "Total" label'''
        ...
    
    def get_text_of_grand_total(self) -> str:
        '''Gets the text of "Grand Total" label in the PivotTable.
        
        :returns: The text of "Grand Total" label'''
        ...
    
    def get_text_of_multiple_items(self) -> str:
        '''Gets the text of "(Multiple Items)" label in the PivotTable.
        
        :returns: The text of "(Multiple Items)" label'''
        ...
    
    def get_text_of_all(self) -> str:
        '''Gets the text of "(All)" label in the PivotTable.
        
        :returns: The text of "(All)" label'''
        ...
    
    def get_text_of_protection(self) -> str:
        '''Gets the protection name in the PivotTable.
        
        :returns: The protection name of PivotTable'''
        ...
    
    def get_text_of_protected_name(self, protected_name : str) -> str:
        '''Gets the text for specified protected name.
        
        :param protected_name: The protected name in PivotTable.
        :returns: The local prorected names of PivotTable.'''
        ...
    
    def get_text_of_column_labels(self) -> str:
        '''Gets the text of "Column Labels" label in the PivotTable.
        
        :returns: The text of column labels'''
        ...
    
    def get_text_of_row_labels(self) -> str:
        '''Gets the text of "Row Labels" label in the PivotTable.
        
        :returns: The text of row labels'''
        ...
    
    def get_text_of_empty_data(self) -> str:
        '''Gets the text of "(blank)" label in the PivotTable.
        
        :returns: The text of empty data'''
        ...
    
    def get_text_of_data_field_header(self) -> str:
        '''Gets the the text of the value area field header in the PivotTable.
        
        :returns: The text of data field header name'''
        ...
    
    def get_text_of_sub_total(self, sub_total_type : aspose.cells.pivot.PivotFieldSubtotalType) -> str:
        '''Gets the text of :py:class:`aspose.cells.pivot.PivotFieldSubtotalType` type in the PivotTable.
        
        :param sub_total_type: The :py:class:`aspose.cells.pivot.PivotFieldSubtotalType`
        :returns: The text of given type'''
        ...
    
    ...

