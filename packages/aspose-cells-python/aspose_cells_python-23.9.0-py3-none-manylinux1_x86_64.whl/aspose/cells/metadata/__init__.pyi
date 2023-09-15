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

class MetadataOptions:
    '''Represents the options of loading metadata of the file.'''
    
    @property
    def metadata_type(self) -> aspose.cells.metadata.MetadataType:
        ...
    
    @property
    def password(self) -> str:
        '''Represents Workbook file encryption password.'''
        ...
    
    @password.setter
    def password(self, value : str):
        '''Represents Workbook file encryption password.'''
        ...
    
    @property
    def key_length(self) -> int:
        ...
    
    @key_length.setter
    def key_length(self, value : int):
        ...
    
    ...

class WorkbookMetadata:
    '''Represents the meta data.'''
    
    @overload
    def save(self, file_name : str):
        '''Save the modified metadata to the file.
        
        :param file_name: The file name.'''
        ...
    
    @overload
    def save(self, stream : io.RawIOBase):
        '''Save the modified metadata to the stream.
        
        :param stream: The stream.'''
        ...
    
    @property
    def options(self) -> aspose.cells.metadata.MetadataOptions:
        '''Gets the options of the metadata.'''
        ...
    
    @property
    def built_in_document_properties(self) -> aspose.cells.properties.BuiltInDocumentPropertyCollection:
        ...
    
    @property
    def custom_document_properties(self) -> aspose.cells.properties.CustomDocumentPropertyCollection:
        ...
    
    ...

class MetadataType:
    '''Represents the type of metadata.'''
    
    @classmethod
    @property
    def ENCRYPTION(cls) -> MetadataType:
        '''Encrypts the file.'''
        ...
    
    @classmethod
    @property
    def DECRYPTION(cls) -> MetadataType:
        '''Decrypts the file.'''
        ...
    
    @classmethod
    @property
    def DOCUMENT_PROPERTIES(cls) -> MetadataType:
        '''Load the properties of the file.'''
        ...
    
    ...

