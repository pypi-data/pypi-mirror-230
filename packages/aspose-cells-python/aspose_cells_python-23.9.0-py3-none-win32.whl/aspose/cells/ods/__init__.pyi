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

class OdsCellField:
    '''Represents the cell field of ods.'''
    
    @property
    def custom_format(self) -> str:
        ...
    
    @custom_format.setter
    def custom_format(self, value : str):
        ...
    
    @property
    def field_type(self) -> aspose.cells.ods.OdsCellFieldType:
        ...
    
    @field_type.setter
    def field_type(self, value : aspose.cells.ods.OdsCellFieldType):
        ...
    
    @property
    def row(self) -> int:
        '''Get and sets the row index of the cell.'''
        ...
    
    @row.setter
    def row(self, value : int):
        '''Get and sets the row index of the cell.'''
        ...
    
    @property
    def column(self) -> int:
        '''Get and sets the column index of the cell.'''
        ...
    
    @column.setter
    def column(self, value : int):
        '''Get and sets the column index of the cell.'''
        ...
    
    ...

class OdsCellFieldCollection:
    '''Represents the fields of ODS.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.ods.OdsCellField]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.ods.OdsCellField], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.ods.OdsCellField, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.ods.OdsCellField, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.ods.OdsCellField) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.ods.OdsCellField, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.ods.OdsCellField, index : int, count : int) -> int:
        ...
    
    def add(self, row : int, column : int, field_type : aspose.cells.ods.OdsCellFieldType, format : str) -> int:
        '''Adds a field.
        
        :param row: The row index.
        :param column: The column index.
        :param field_type: The type of the field.
        :param format: The number format of the field.'''
        ...
    
    def update_fields_value(self):
        '''Update fields value to the cells.'''
        ...
    
    def binary_search(self, item : aspose.cells.ods.OdsCellField) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class OdsPageBackground:
    '''Represents the page background of ods.'''
    
    @property
    def type(self) -> aspose.cells.ods.OdsPageBackgroundType:
        '''Gets and sets the page background type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.ods.OdsPageBackgroundType):
        '''Gets and sets the page background type.'''
        ...
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Gets and sets the color of background.'''
        ...
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color):
        '''Gets and sets the color of background.'''
        ...
    
    @property
    def graphic_type(self) -> aspose.cells.ods.OdsPageBackgroundGraphicType:
        ...
    
    @graphic_type.setter
    def graphic_type(self, value : aspose.cells.ods.OdsPageBackgroundGraphicType):
        ...
    
    @property
    def graphic_position_type(self) -> aspose.cells.ods.OdsPageBackgroundGraphicPositionType:
        ...
    
    @graphic_position_type.setter
    def graphic_position_type(self, value : aspose.cells.ods.OdsPageBackgroundGraphicPositionType):
        ...
    
    @property
    def is_link(self) -> bool:
        ...
    
    @property
    def linked_graphic(self) -> str:
        ...
    
    @linked_graphic.setter
    def linked_graphic(self, value : str):
        ...
    
    @property
    def graphic_data(self) -> bytes:
        ...
    
    @graphic_data.setter
    def graphic_data(self, value : bytes):
        ...
    
    ...

class OdsCellFieldType:
    '''Represents the cell field type of ods.'''
    
    @classmethod
    @property
    def DATE(cls) -> OdsCellFieldType:
        '''Current date.'''
        ...
    
    @classmethod
    @property
    def SHEET_NAME(cls) -> OdsCellFieldType:
        '''The name of the sheet.'''
        ...
    
    @classmethod
    @property
    def TITLE(cls) -> OdsCellFieldType:
        '''The name of the file.'''
        ...
    
    ...

class OdsGeneratorType:
    '''Represents the type of ODS generator.'''
    
    @classmethod
    @property
    def LIBRE_OFFICE(cls) -> OdsGeneratorType:
        '''Libre Office'''
        ...
    
    @classmethod
    @property
    def OPEN_OFFICE(cls) -> OdsGeneratorType:
        '''Open Office'''
        ...
    
    ...

class OdsPageBackgroundGraphicPositionType:
    '''Represents the position.'''
    
    @classmethod
    @property
    def TOP_LEFT(cls) -> OdsPageBackgroundGraphicPositionType:
        '''Top left.'''
        ...
    
    @classmethod
    @property
    def TOP_CENTER(cls) -> OdsPageBackgroundGraphicPositionType:
        '''Top center.'''
        ...
    
    @classmethod
    @property
    def TOP_RIGHT(cls) -> OdsPageBackgroundGraphicPositionType:
        '''Top right.'''
        ...
    
    @classmethod
    @property
    def CENTER_LEFT(cls) -> OdsPageBackgroundGraphicPositionType:
        '''Center left.'''
        ...
    
    @classmethod
    @property
    def CENTER_CENTER(cls) -> OdsPageBackgroundGraphicPositionType:
        '''Center.'''
        ...
    
    @classmethod
    @property
    def CENTER_RIGHT(cls) -> OdsPageBackgroundGraphicPositionType:
        '''Center right.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_LEFT(cls) -> OdsPageBackgroundGraphicPositionType:
        '''Bottom left.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_CENTER(cls) -> OdsPageBackgroundGraphicPositionType:
        '''Bottom center.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_RIGHT(cls) -> OdsPageBackgroundGraphicPositionType:
        '''Bottom right.'''
        ...
    
    ...

class OdsPageBackgroundGraphicType:
    '''Represents the type of formatting page background with image.'''
    
    @classmethod
    @property
    def POSITION(cls) -> OdsPageBackgroundGraphicType:
        '''Set the image at specific position.'''
        ...
    
    @classmethod
    @property
    def AREA(cls) -> OdsPageBackgroundGraphicType:
        '''Stretch the image.'''
        ...
    
    @classmethod
    @property
    def TILE(cls) -> OdsPageBackgroundGraphicType:
        '''Repeat and repeat the image.'''
        ...
    
    ...

class OdsPageBackgroundType:
    '''Represents the page background type of ods.'''
    
    @classmethod
    @property
    def NONE(cls) -> OdsPageBackgroundType:
        '''No background.'''
        ...
    
    @classmethod
    @property
    def COLOR(cls) -> OdsPageBackgroundType:
        '''Formats the background with color.'''
        ...
    
    @classmethod
    @property
    def GRAPHIC(cls) -> OdsPageBackgroundType:
        '''Formats the background with image.'''
        ...
    
    ...

