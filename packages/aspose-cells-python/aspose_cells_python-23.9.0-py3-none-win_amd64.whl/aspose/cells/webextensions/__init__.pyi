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

class WebExtension:
    '''Represents an Office Add-in instance.'''
    
    @property
    def id(self) -> str:
        '''Gets and sets the uniquely identifies the Office Add-in instance in the current document.'''
        ...
    
    @id.setter
    def id(self, value : str):
        '''Gets and sets the uniquely identifies the Office Add-in instance in the current document.'''
        ...
    
    @property
    def is_frozen(self) -> bool:
        ...
    
    @is_frozen.setter
    def is_frozen(self, value : bool):
        ...
    
    @property
    def reference(self) -> aspose.cells.webextensions.WebExtensionReference:
        '''Get the primary reference to an Office Add-in.'''
        ...
    
    @property
    def alter_references(self) -> aspose.cells.webextensions.WebExtensionReferenceCollection:
        ...
    
    @property
    def properties(self) -> aspose.cells.webextensions.WebExtensionPropertyCollection:
        '''Gets all properties of web extension.'''
        ...
    
    @property
    def bindings(self) -> aspose.cells.webextensions.WebExtensionBindingCollection:
        '''Gets all bindings relationship between an Office Add-in and the data in the document.'''
        ...
    
    ...

class WebExtensionBinding:
    '''Represents a binding relationship between an Office Add-in and the data in the document.'''
    
    @property
    def id(self) -> str:
        '''Gets and sets the binding identifier.'''
        ...
    
    @id.setter
    def id(self, value : str):
        '''Gets and sets the binding identifier.'''
        ...
    
    @property
    def type(self) -> str:
        '''Gets and sets the binding type.'''
        ...
    
    @type.setter
    def type(self, value : str):
        '''Gets and sets the binding type.'''
        ...
    
    @property
    def appref(self) -> str:
        '''Gets and sets the binding key used to map the binding entry in this list with the bound data in the document.'''
        ...
    
    @appref.setter
    def appref(self, value : str):
        '''Gets and sets the binding key used to map the binding entry in this list with the bound data in the document.'''
        ...
    
    ...

class WebExtensionBindingCollection:
    '''Represents the list of binding relationships between an Office Add-in and the data in the document.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.webextensions.WebExtensionBinding]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.webextensions.WebExtensionBinding], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtensionBinding, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtensionBinding, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionBinding) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionBinding, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionBinding, index : int, count : int) -> int:
        ...
    
    def add(self) -> int:
        '''Adds an a binding relationship between an Office Add-in and the data in the document.'''
        ...
    
    def binary_search(self, item : aspose.cells.webextensions.WebExtensionBinding) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class WebExtensionCollection:
    '''Represents the list of web extension.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.webextensions.WebExtension]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.webextensions.WebExtension], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtension, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtension, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtension) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtension, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtension, index : int, count : int) -> int:
        ...
    
    def add(self) -> int:
        '''Adds a web extension.
        
        :returns: The index.'''
        ...
    
    def add_web_video_player(self, url : str, auto_play : bool, start_time : int, end_time : int) -> int:
        '''Add a web video player into exel.
        
        :param auto_play: Indicates whether auto playing the video.
        :param start_time: The start time in unit of seconds.
        :param end_time: The end time in unit of seconds.'''
        ...
    
    def binary_search(self, item : aspose.cells.webextensions.WebExtension) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class WebExtensionProperty:
    '''Represents an Office Add-in custom property.'''
    
    @property
    def name(self) -> str:
        '''Gets and set a custom property name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and set a custom property name.'''
        ...
    
    @property
    def value(self) -> str:
        '''Gets and sets a custom property value.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Gets and sets a custom property value.'''
        ...
    
    ...

class WebExtensionPropertyCollection:
    '''Represents the list of web extension properties.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.webextensions.WebExtensionProperty]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.webextensions.WebExtensionProperty], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtensionProperty, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtensionProperty, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionProperty) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionProperty, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionProperty, index : int, count : int) -> int:
        ...
    
    def add(self, name : str, value : str) -> int:
        '''Adds web extension property.
        
        :param name: The name of property.
        :param value: The value of property.
        :returns: The index of added property.'''
        ...
    
    def remove_at(self, name : str):
        '''Remove the property by the name.
        
        :param name: The name of the property.'''
        ...
    
    def binary_search(self, item : aspose.cells.webextensions.WebExtensionProperty) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class WebExtensionReference:
    '''Represents identify the provider location and version of the extension.'''
    
    @property
    def id(self) -> str:
        '''Gets and sets the identifier associated with the Office Add-in within a catalog provider.
        The identifier MUST be unique within a catalog provider.'''
        ...
    
    @id.setter
    def id(self, value : str):
        '''Gets and sets the identifier associated with the Office Add-in within a catalog provider.
        The identifier MUST be unique within a catalog provider.'''
        ...
    
    @property
    def version(self) -> str:
        '''Gets and sets the version.'''
        ...
    
    @version.setter
    def version(self, value : str):
        '''Gets and sets the version.'''
        ...
    
    @property
    def store_name(self) -> str:
        ...
    
    @store_name.setter
    def store_name(self, value : str):
        ...
    
    @property
    def store_type(self) -> aspose.cells.webextensions.WebExtensionStoreType:
        ...
    
    @store_type.setter
    def store_type(self, value : aspose.cells.webextensions.WebExtensionStoreType):
        ...
    
    ...

class WebExtensionReferenceCollection:
    '''Represents the list of web extension reference.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.webextensions.WebExtensionReference]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.webextensions.WebExtensionReference], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtensionReference, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtensionReference, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionReference) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionReference, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionReference, index : int, count : int) -> int:
        ...
    
    def add(self) -> int:
        '''Adds an empty reference of web extension.'''
        ...
    
    def binary_search(self, item : aspose.cells.webextensions.WebExtensionReference) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class WebExtensionTaskPane:
    '''Represents a persisted taskpane object.'''
    
    @property
    def web_extension(self) -> aspose.cells.webextensions.WebExtension:
        ...
    
    @web_extension.setter
    def web_extension(self, value : aspose.cells.webextensions.WebExtension):
        ...
    
    @property
    def dock_state(self) -> str:
        ...
    
    @dock_state.setter
    def dock_state(self, value : str):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the default width value for this taskpane instance.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the default width value for this taskpane instance.'''
        ...
    
    @property
    def row(self) -> int:
        '''Gets and sets the index, enumerating from the outside to the inside, of this taskpane among other persisted taskpanes docked in the same default location.'''
        ...
    
    @row.setter
    def row(self, value : int):
        '''Gets and sets the index, enumerating from the outside to the inside, of this taskpane among other persisted taskpanes docked in the same default location.'''
        ...
    
    ...

class WebExtensionTaskPaneCollection:
    '''Represents the list of task pane.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.webextensions.WebExtensionTaskPane]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.webextensions.WebExtensionTaskPane], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtensionTaskPane, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.webextensions.WebExtensionTaskPane, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionTaskPane) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionTaskPane, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.webextensions.WebExtensionTaskPane, index : int, count : int) -> int:
        ...
    
    def add(self) -> int:
        '''Adds task pane.
        
        :returns: The index.'''
        ...
    
    def binary_search(self, item : aspose.cells.webextensions.WebExtensionTaskPane) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class WebExtensionStoreType:
    '''Represents the store type of web extension.'''
    
    @classmethod
    @property
    def OMEX(cls) -> WebExtensionStoreType:
        '''Specifies that the store type is Office.com.'''
        ...
    
    @classmethod
    @property
    def SP_CATALOG(cls) -> WebExtensionStoreType:
        '''Specifies that the store type is SharePoint corporate catalog.'''
        ...
    
    @classmethod
    @property
    def SP_APP(cls) -> WebExtensionStoreType:
        '''Specifies that the store type is a SharePoint web application.'''
        ...
    
    @classmethod
    @property
    def EXCHANGE(cls) -> WebExtensionStoreType:
        '''Specifies that the store type is an Exchange server.'''
        ...
    
    @classmethod
    @property
    def FILE_SYSTEM(cls) -> WebExtensionStoreType:
        '''Specifies that the store type is a file system share.'''
        ...
    
    @classmethod
    @property
    def REGISTRY(cls) -> WebExtensionStoreType:
        '''Specifies that the store type is the system registry.'''
        ...
    
    @classmethod
    @property
    def EX_CATALOG(cls) -> WebExtensionStoreType:
        '''Specifies that the store type is Centralized Deployment via Exchange.'''
        ...
    
    ...

