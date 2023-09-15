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

class BuiltInDocumentPropertyCollection(DocumentPropertyCollection):
    '''A collection of built-in document properties.'''
    
    @overload
    def index_of(self, name : str) -> int:
        '''Gets the index of a property by name.
        
        :param name: The case-insensitive name of the property.
        :returns: The zero based index. Negative value if not found.'''
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.DocumentProperty, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.DocumentProperty, index : int, count : int) -> int:
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.properties.DocumentProperty]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.properties.DocumentProperty], array_index : int, count : int):
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.DocumentProperty) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.DocumentProperty, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.DocumentProperty, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.properties.DocumentProperty) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    @property
    def language(self) -> str:
        '''Gets the document's language.'''
        ...
    
    @language.setter
    def language(self, value : str):
        '''Sets the document's language.'''
        ...
    
    @property
    def author(self) -> str:
        '''Gets the name of the document's author.'''
        ...
    
    @author.setter
    def author(self, value : str):
        '''Sets the name of the document's author.'''
        ...
    
    @property
    def bytes(self) -> int:
        '''Represents an estimate of the number of bytes in the document.'''
        ...
    
    @bytes.setter
    def bytes(self, value : int):
        '''Represents an estimate of the number of bytes in the document.'''
        ...
    
    @property
    def characters(self) -> int:
        '''Represents an estimate of the number of characters in the document.'''
        ...
    
    @characters.setter
    def characters(self, value : int):
        '''Represents an estimate of the number of characters in the document.'''
        ...
    
    @property
    def characters_with_spaces(self) -> int:
        ...
    
    @characters_with_spaces.setter
    def characters_with_spaces(self, value : int):
        ...
    
    @property
    def comments(self) -> str:
        '''Gets the document comments.'''
        ...
    
    @comments.setter
    def comments(self, value : str):
        '''Sets the document comments.'''
        ...
    
    @property
    def category(self) -> str:
        '''Gets the category of the document.'''
        ...
    
    @category.setter
    def category(self, value : str):
        '''Sets the category of the document.'''
        ...
    
    @property
    def content_type(self) -> str:
        ...
    
    @content_type.setter
    def content_type(self, value : str):
        ...
    
    @property
    def content_status(self) -> str:
        ...
    
    @content_status.setter
    def content_status(self, value : str):
        ...
    
    @property
    def company(self) -> str:
        '''Gets the company property.'''
        ...
    
    @company.setter
    def company(self, value : str):
        '''Sets the company property.'''
        ...
    
    @property
    def hyperlink_base(self) -> str:
        ...
    
    @hyperlink_base.setter
    def hyperlink_base(self, value : str):
        ...
    
    @property
    def created_time(self) -> DateTime:
        ...
    
    @created_time.setter
    def created_time(self, value : DateTime):
        ...
    
    @property
    def created_universal_time(self) -> DateTime:
        ...
    
    @created_universal_time.setter
    def created_universal_time(self, value : DateTime):
        ...
    
    @property
    def keywords(self) -> str:
        '''Gets the document keywords.'''
        ...
    
    @keywords.setter
    def keywords(self, value : str):
        '''Sets the document keywords.'''
        ...
    
    @property
    def last_printed(self) -> DateTime:
        ...
    
    @last_printed.setter
    def last_printed(self, value : DateTime):
        ...
    
    @property
    def last_printed_universal_time(self) -> DateTime:
        ...
    
    @last_printed_universal_time.setter
    def last_printed_universal_time(self, value : DateTime):
        ...
    
    @property
    def last_saved_by(self) -> str:
        ...
    
    @last_saved_by.setter
    def last_saved_by(self, value : str):
        ...
    
    @property
    def last_saved_time(self) -> DateTime:
        ...
    
    @last_saved_time.setter
    def last_saved_time(self, value : DateTime):
        ...
    
    @property
    def last_saved_universal_time(self) -> DateTime:
        ...
    
    @last_saved_universal_time.setter
    def last_saved_universal_time(self, value : DateTime):
        ...
    
    @property
    def lines(self) -> int:
        '''Represents an estimate of the number of lines in the document.'''
        ...
    
    @lines.setter
    def lines(self, value : int):
        '''Represents an estimate of the number of lines in the document.'''
        ...
    
    @property
    def manager(self) -> str:
        '''Gets the manager property.'''
        ...
    
    @manager.setter
    def manager(self, value : str):
        '''Sets the manager property.'''
        ...
    
    @property
    def name_of_application(self) -> str:
        ...
    
    @name_of_application.setter
    def name_of_application(self, value : str):
        ...
    
    @property
    def pages(self) -> int:
        '''Represents an estimate of the number of pages in the document.'''
        ...
    
    @pages.setter
    def pages(self, value : int):
        '''Represents an estimate of the number of pages in the document.'''
        ...
    
    @property
    def paragraphs(self) -> int:
        '''Represents an estimate of the number of paragraphs in the document.'''
        ...
    
    @paragraphs.setter
    def paragraphs(self, value : int):
        '''Represents an estimate of the number of paragraphs in the document.'''
        ...
    
    @property
    def revision_number(self) -> str:
        ...
    
    @revision_number.setter
    def revision_number(self, value : str):
        ...
    
    @property
    def subject(self) -> str:
        '''Gets the subject of the document.'''
        ...
    
    @subject.setter
    def subject(self, value : str):
        '''Sets the subject of the document.'''
        ...
    
    @property
    def template(self) -> str:
        '''Gets the informational name of the document template.'''
        ...
    
    @template.setter
    def template(self, value : str):
        '''Sets the informational name of the document template.'''
        ...
    
    @property
    def title(self) -> str:
        '''Gets the title of the document.'''
        ...
    
    @title.setter
    def title(self, value : str):
        '''Sets the title of the document.'''
        ...
    
    @property
    def total_editing_time(self) -> float:
        ...
    
    @total_editing_time.setter
    def total_editing_time(self, value : float):
        ...
    
    @property
    def version(self) -> str:
        '''Represents the version number of the application that created the document.'''
        ...
    
    @version.setter
    def version(self, value : str):
        '''Represents the version number of the application that created the document.'''
        ...
    
    @property
    def document_version(self) -> str:
        ...
    
    @document_version.setter
    def document_version(self, value : str):
        ...
    
    @property
    def scale_crop(self) -> bool:
        ...
    
    @scale_crop.setter
    def scale_crop(self, value : bool):
        ...
    
    @property
    def links_up_to_date(self) -> bool:
        ...
    
    @links_up_to_date.setter
    def links_up_to_date(self, value : bool):
        ...
    
    @property
    def words(self) -> int:
        '''Represents an estimate of the number of words in the document.'''
        ...
    
    @words.setter
    def words(self, value : int):
        '''Represents an estimate of the number of words in the document.'''
        ...
    
    ...

class ContentTypeProperty:
    '''Represents identifier information.'''
    
    @property
    def name(self) -> str:
        '''Returns the name of the object.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Returns or sets the name of the object.'''
        ...
    
    @property
    def value(self) -> str:
        '''Returns the value of the content type property.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Returns or sets the value of the content type property.'''
        ...
    
    @property
    def type(self) -> str:
        '''Gets and sets the type of the property.'''
        ...
    
    @type.setter
    def type(self, value : str):
        '''Gets and sets the type of the property.'''
        ...
    
    @property
    def is_nillable(self) -> bool:
        ...
    
    @is_nillable.setter
    def is_nillable(self, value : bool):
        ...
    
    ...

class ContentTypePropertyCollection:
    '''A collection of :py:class:`aspose.cells.properties.ContentTypeProperty` objects that represent additional information.'''
    
    @overload
    def add(self, name : str, value : str) -> int:
        '''Adds content type property information.
        
        :param name: The name of the content type property.
        :param value: The value of the content type property.'''
        ...
    
    @overload
    def add(self, name : str, value : str, type : str) -> int:
        '''Adds content type property information.
        
        :param name: The name of the content type property.
        :param value: The value of the content type property.
        :param type: The type of the content type property.'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.properties.ContentTypeProperty]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.properties.ContentTypeProperty], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.ContentTypeProperty, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.ContentTypeProperty, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.ContentTypeProperty) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.ContentTypeProperty, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.ContentTypeProperty, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.properties.ContentTypeProperty) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class CustomDocumentPropertyCollection(DocumentPropertyCollection):
    '''A collection of custom document properties.'''
    
    @overload
    def index_of(self, name : str) -> int:
        '''Gets the index of a property by name.
        
        :param name: The case-insensitive name of the property.
        :returns: The zero based index. Negative value if not found.'''
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.DocumentProperty, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.DocumentProperty, index : int, count : int) -> int:
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.properties.DocumentProperty]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.properties.DocumentProperty], array_index : int, count : int):
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.DocumentProperty) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.DocumentProperty, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.DocumentProperty, index : int, count : int) -> int:
        ...
    
    @overload
    def add(self, name : str, value : str) -> aspose.cells.properties.DocumentProperty:
        '''Creates a new custom document property of the **PropertyType.String** data type.
        
        :param name: The name of the property.
        :param value: The value of the property.
        :returns: The newly created property object.'''
        ...
    
    @overload
    def add(self, name : str, value : int) -> aspose.cells.properties.DocumentProperty:
        '''Creates a new custom document property of the **PropertyType.Number** data type.
        
        :param name: The name of the property.
        :param value: The value of the property.
        :returns: The newly created property object.'''
        ...
    
    @overload
    def add(self, name : str, value : DateTime) -> aspose.cells.properties.DocumentProperty:
        '''Creates a new custom document property of the **PropertyType.DateTime** data type.
        
        :param name: The name of the property.
        :param value: The value of the property.
        :returns: The newly created property object.'''
        ...
    
    @overload
    def add(self, name : str, value : bool) -> aspose.cells.properties.DocumentProperty:
        '''Creates a new custom document property of the **PropertyType.Boolean** data type.
        
        :param name: The name of the property.
        :param value: The value of the property.
        :returns: The newly created property object.'''
        ...
    
    @overload
    def add(self, name : str, value : float) -> aspose.cells.properties.DocumentProperty:
        '''Creates a new custom document property of the **PropertyType.Float** data type.
        
        :param name: The name of the property.
        :param value: The value of the property.
        :returns: The newly created property object.'''
        ...
    
    def binary_search(self, item : aspose.cells.properties.DocumentProperty) -> int:
        ...
    
    def add_link_to_content(self, name : str, source : str) -> aspose.cells.properties.DocumentProperty:
        '''Creates a new custom document property which links to content.
        
        :param name: The name of the property.
        :param source: The source of the property
        :returns: The newly created property object.'''
        ...
    
    def update_linked_property_value(self):
        '''Update custom document property value which links to content.'''
        ...
    
    def update_linked_range(self):
        '''Update custom document property value to linked range.'''
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class CustomProperty:
    '''Represents identifier information.'''
    
    @property
    def name(self) -> str:
        '''Returns the name of the object.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Returns or sets the name of the object.'''
        ...
    
    @property
    def string_value(self) -> str:
        ...
    
    @string_value.setter
    def string_value(self, value : str):
        ...
    
    @property
    def value(self) -> str:
        '''Returns the value of the custom property.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Returns or sets the value of the custom property.'''
        ...
    
    ...

class CustomPropertyCollection:
    '''A collection of :py:class:`aspose.cells.properties.CustomProperty` objects that represent additional information.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.properties.CustomProperty]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.properties.CustomProperty], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.CustomProperty, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.CustomProperty, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.CustomProperty) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.CustomProperty, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.CustomProperty, index : int, count : int) -> int:
        ...
    
    def add(self, name : str, value : str) -> int:
        '''Adds custom property information.
        
        :param name: The name of the custom property.
        :param value: The value of the custom property.'''
        ...
    
    def binary_search(self, item : aspose.cells.properties.CustomProperty) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class DocumentProperty:
    '''Represents a custom or built-in document property.'''
    
    def to_int(self) -> int:
        '''Returns the property value as integer.'''
        ...
    
    def to_double(self) -> float:
        '''Returns the property value as double.'''
        ...
    
    def to_date_time(self) -> DateTime:
        '''Returns the property value as DateTime in local timezone.'''
        ...
    
    def to_bool(self) -> bool:
        '''Returns the property value as bool.'''
        ...
    
    @property
    def name(self) -> str:
        '''Returns the name of the property.'''
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value of the property.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value of the property.'''
        ...
    
    @property
    def is_linked_to_content(self) -> bool:
        ...
    
    @property
    def source(self) -> str:
        '''The linked content source.'''
        ...
    
    @property
    def type(self) -> aspose.cells.properties.PropertyType:
        '''Gets the data type of the property.'''
        ...
    
    @property
    def is_generated_name(self) -> bool:
        ...
    
    ...

class DocumentPropertyCollection:
    '''Base class for :py:class:`aspose.cells.properties.BuiltInDocumentPropertyCollection` and :py:class:`aspose.cells.properties.CustomDocumentPropertyCollection` collections.'''
    
    @overload
    def index_of(self, name : str) -> int:
        '''Gets the index of a property by name.
        
        :param name: The case-insensitive name of the property.
        :returns: The zero based index. Negative value if not found.'''
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.DocumentProperty, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.properties.DocumentProperty, index : int, count : int) -> int:
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.properties.DocumentProperty]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.properties.DocumentProperty], array_index : int, count : int):
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.DocumentProperty) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.DocumentProperty, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.properties.DocumentProperty, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.properties.DocumentProperty) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class PropertyType:
    '''Specifies data type of a document property.'''
    
    @classmethod
    @property
    def BOOLEAN(cls) -> PropertyType:
        '''The property is a boolean value.'''
        ...
    
    @classmethod
    @property
    def DATE_TIME(cls) -> PropertyType:
        '''The property is a date time value.'''
        ...
    
    @classmethod
    @property
    def DOUBLE(cls) -> PropertyType:
        '''The property is a floating number.'''
        ...
    
    @classmethod
    @property
    def NUMBER(cls) -> PropertyType:
        '''The property is an integer number.'''
        ...
    
    @classmethod
    @property
    def STRING(cls) -> PropertyType:
        '''The property is a string value.'''
        ...
    
    @classmethod
    @property
    def BLOB(cls) -> PropertyType:
        '''The property is a byte array.'''
        ...
    
    ...

