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

class CustomXmlPart:
    '''Represents a Custom XML Data Storage Part (custom XML data within a package).'''
    
    @property
    def data(self) -> bytes:
        '''Gets the XML content of this Custom XML Data Storage Part.'''
        ...
    
    @data.setter
    def data(self, value : bytes):
        '''Sets the XML content of this Custom XML Data Storage Part.'''
        ...
    
    @property
    def schema_data(self) -> bytes:
        ...
    
    @schema_data.setter
    def schema_data(self, value : bytes):
        ...
    
    @property
    def id(self) -> str:
        '''Gets and sets the id of the custom xml part.'''
        ...
    
    @id.setter
    def id(self, value : str):
        '''Gets and sets the id of the custom xml part.'''
        ...
    
    ...

class CustomXmlPartCollection:
    '''Represents a Custom XML Data Storage Part (custom XML data within a package).'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.markup.CustomXmlPart]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.markup.CustomXmlPart], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.markup.CustomXmlPart, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.markup.CustomXmlPart, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.markup.CustomXmlPart) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.markup.CustomXmlPart, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.markup.CustomXmlPart, index : int, count : int) -> int:
        ...
    
    def add(self, data : bytes, shema_data : bytes) -> int:
        '''Adds an item to the collection.
        
        :param data: The XML content of this Custom XML Data Storage Part.
        :param shema_data: The set of XML schemas that are associated with this custom XML part.'''
        ...
    
    def select_by_id(self, id : str) -> aspose.cells.markup.CustomXmlPart:
        '''Gets an item by id.
        
        :param id: Contains the GUID for the custom XML part.'''
        ...
    
    def binary_search(self, item : aspose.cells.markup.CustomXmlPart) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class SmartTag:
    '''Represents a smart tag.'''
    
    def set_link(self, uri : str, name : str):
        '''Change the name and  the namespace URI of the smart tag.
        
        :param uri: The namespace URI of the smart tag.
        :param name: The name of the smart tag.'''
        ...
    
    @property
    def deleted(self) -> bool:
        '''Indicates whether the smart tag is deleted.'''
        ...
    
    @deleted.setter
    def deleted(self, value : bool):
        '''Indicates whether the smart tag is deleted.'''
        ...
    
    @property
    def properties(self) -> aspose.cells.markup.SmartTagPropertyCollection:
        '''Gets and set the properties of the smart tag.'''
        ...
    
    @properties.setter
    def properties(self, value : aspose.cells.markup.SmartTagPropertyCollection):
        '''Gets and set the properties of the smart tag.'''
        ...
    
    @property
    def uri(self) -> str:
        '''Gets the namespace URI of the smart tag.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of the smart tag.'''
        ...
    
    ...

class SmartTagCollection:
    '''Represents all smart tags in the cell.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.markup.SmartTag]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.markup.SmartTag], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.markup.SmartTag, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.markup.SmartTag, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.markup.SmartTag) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.markup.SmartTag, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.markup.SmartTag, index : int, count : int) -> int:
        ...
    
    def add(self, uri : str, name : str) -> int:
        '''Adds a smart tag.
        
        :param uri: Specifies the namespace URI of the smart tag
        :param name: Specifies the name of the smart tag.
        :returns: The index of smart tag in the list.'''
        ...
    
    def binary_search(self, item : aspose.cells.markup.SmartTag) -> int:
        ...
    
    @property
    def row(self) -> int:
        '''Gets the row of the cell smart tags.'''
        ...
    
    @property
    def column(self) -> int:
        '''Gets the column of the cell smart tags.'''
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class SmartTagOptions:
    '''Represents the options of the smart tag.'''
    
    @property
    def embed_smart_tags(self) -> bool:
        ...
    
    @embed_smart_tags.setter
    def embed_smart_tags(self, value : bool):
        ...
    
    @property
    def show_type(self) -> aspose.cells.markup.SmartTagShowType:
        ...
    
    @show_type.setter
    def show_type(self, value : aspose.cells.markup.SmartTagShowType):
        ...
    
    ...

class SmartTagProperty:
    '''Represents the property of the cell smart tag.'''
    
    @property
    def name(self) -> str:
        '''Gets and sets the name of the property.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and sets the name of the property.'''
        ...
    
    @property
    def value(self) -> str:
        '''Gets and sets the value of the property.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Gets and sets the value of the property.'''
        ...
    
    ...

class SmartTagPropertyCollection:
    '''Represents all properties of cell smart tag.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.markup.SmartTagProperty]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.markup.SmartTagProperty], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.markup.SmartTagProperty, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.markup.SmartTagProperty, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.markup.SmartTagProperty) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.markup.SmartTagProperty, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.markup.SmartTagProperty, index : int, count : int) -> int:
        ...
    
    def add(self, name : str, value : str) -> int:
        '''Adds a property of cell's smart tag.
        
        :param name: The name of the property
        :param value: The value of the property.
        :returns: return :py:class:`aspose.cells.markup.SmartTagProperty`'''
        ...
    
    def binary_search(self, item : aspose.cells.markup.SmartTagProperty) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class SmartTagSetting:
    '''Represents all :py:class:`aspose.cells.markup.SmartTagCollection` object in the worksheet.'''
    
    @overload
    def add(self, row : int, column : int) -> int:
        '''Adds a :py:class:`aspose.cells.markup.SmartTagCollection` object to a cell.
        
        :param row: The row of the cell.
        :param column: The column of the cell.
        :returns: Returns index of a :py:class:`aspose.cells.markup.SmartTagCollection` object in the worksheet.'''
        ...
    
    @overload
    def add(self, cell_name : str) -> int:
        '''Add a cell smart tags.
        
        :param cell_name: The name of the cell.'''
        ...
    
    ...

class SmartTagShowType:
    '''Represents the show type of the smart tag.'''
    
    @classmethod
    @property
    def ALL(cls) -> SmartTagShowType:
        '''Indicates that smart tags are enabled and shown'''
        ...
    
    @classmethod
    @property
    def NO_SMART_TAG_INDICATOR(cls) -> SmartTagShowType:
        '''Indicates that the smart tags are enabled but the indicator not be shown.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> SmartTagShowType:
        '''Indicates that smart tags are disabled and not displayed.'''
        ...
    
    ...

