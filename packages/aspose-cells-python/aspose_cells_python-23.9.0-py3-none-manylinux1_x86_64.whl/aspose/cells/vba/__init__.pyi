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

class VbaModule:
    '''Represents the module in VBA project.'''
    
    @property
    def name(self) -> str:
        '''Gets and sets the name of Module.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and sets the name of Module.'''
        ...
    
    @property
    def type(self) -> aspose.cells.vba.VbaModuleType:
        '''Gets the type of module.'''
        ...
    
    @property
    def codes(self) -> str:
        '''Gets and sets the codes of module.'''
        ...
    
    @codes.setter
    def codes(self, value : str):
        '''Gets and sets the codes of module.'''
        ...
    
    ...

class VbaModuleCollection:
    '''Represents the list of :py:class:`aspose.cells.vba.VbaModule`'''
    
    @overload
    def add(self, sheet : aspose.cells.Worksheet) -> int:
        '''Adds module for a worksheet.
        
        :param sheet: The worksheet'''
        ...
    
    @overload
    def add(self, type : aspose.cells.vba.VbaModuleType, name : str) -> int:
        '''Adds module.
        
        :param type: The type of module.
        :param name: The name of module.'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.vba.VbaModule]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.vba.VbaModule], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.vba.VbaModule, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.vba.VbaModule, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.vba.VbaModule) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.vba.VbaModule, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.vba.VbaModule, index : int, count : int) -> int:
        ...
    
    def add_designer_storage(self, name : str, data : bytes):
        ''''''
        ...
    
    def get_designer_storage(self, name : str) -> bytes:
        '''Represents the data of Designer.'''
        ...
    
    def binary_search(self, item : aspose.cells.vba.VbaModule) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class VbaProject:
    '''Represents the VBA project.'''
    
    def sign(self, digital_signature : aspose.cells.digitalsignatures.DigitalSignature):
        '''Sign this VBA project by a DigitalSignature
        
        :param digital_signature: DigitalSignature'''
        ...
    
    def protect(self, islocked_for_viewing : bool, password : str):
        '''Protects or unprotects this VBA project.
        
        :param islocked_for_viewing: indicates whether locks project for viewing.
        :param password: If the value is null, unprotects this VBA project, otherwise projects the this VBA project.'''
        ...
    
    def copy(self, source : aspose.cells.vba.VbaProject):
        '''Copy VBA project from other file.'''
        ...
    
    def validate_password(self, password : str) -> bool:
        '''Validates protection password.
        
        :param password: the password
        :returns: Whether password is the protection password of this VBA project'''
        ...
    
    @property
    def is_valid_signed(self) -> bool:
        ...
    
    @property
    def cert_raw_data(self) -> bytes:
        ...
    
    @property
    def encoding(self) -> System.Text.Encoding:
        '''Gets and sets the encoding of VBA project.'''
        ...
    
    @encoding.setter
    def encoding(self, value : System.Text.Encoding):
        '''Gets and sets the encoding of VBA project.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets and sets the name of the VBA project.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and sets the name of the VBA project.'''
        ...
    
    @property
    def is_signed(self) -> bool:
        ...
    
    @property
    def is_protected(self) -> bool:
        ...
    
    @property
    def islocked_for_viewing(self) -> bool:
        ...
    
    @property
    def modules(self) -> aspose.cells.vba.VbaModuleCollection:
        '''Gets all :py:class:`aspose.cells.vba.VbaModule` objects.'''
        ...
    
    @property
    def references(self) -> aspose.cells.vba.VbaProjectReferenceCollection:
        '''Gets all references of VBA project.'''
        ...
    
    ...

class VbaProjectReference:
    '''Represents the reference of VBA project.'''
    
    def copy(self, source : aspose.cells.vba.VbaProjectReference):
        ''''''
        ...
    
    @property
    def type(self) -> aspose.cells.vba.VbaProjectReferenceType:
        '''Gets the type of this reference.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets and sets the name of the reference.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and sets the name of the reference.'''
        ...
    
    @property
    def libid(self) -> str:
        '''Gets and sets the Libid of the reference.'''
        ...
    
    @libid.setter
    def libid(self, value : str):
        '''Gets and sets the Libid of the reference.'''
        ...
    
    @property
    def twiddledlibid(self) -> str:
        '''Gets and sets the twiddled Libid of the reference.'''
        ...
    
    @twiddledlibid.setter
    def twiddledlibid(self, value : str):
        '''Gets and sets the twiddled Libid of the reference.'''
        ...
    
    @property
    def extended_libid(self) -> str:
        ...
    
    @extended_libid.setter
    def extended_libid(self, value : str):
        ...
    
    @property
    def relative_libid(self) -> str:
        ...
    
    @relative_libid.setter
    def relative_libid(self, value : str):
        ...
    
    ...

class VbaProjectReferenceCollection:
    '''Represents all references of VBA project.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.vba.VbaProjectReference]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.vba.VbaProjectReference], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.vba.VbaProjectReference, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.vba.VbaProjectReference, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.vba.VbaProjectReference) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.vba.VbaProjectReference, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.vba.VbaProjectReference, index : int, count : int) -> int:
        ...
    
    def add_registered_reference(self, name : str, libid : str) -> int:
        '''Add a reference to an Automation type library.
        
        :param name: The name of reference.
        :param libid: The identifier of an Automation type library.'''
        ...
    
    def add_control_refrernce(self, name : str, libid : str, twiddledlibid : str, extended_libid : str) -> int:
        '''Add a reference to a twiddled type library and its extended type library.
        
        :param name: The name of reference.
        :param libid: The identifier of an Automation type library.
        :param twiddledlibid: The identifier of a twiddled type library
        :param extended_libid: The identifier of an extended type library'''
        ...
    
    def add_project_refrernce(self, name : str, absolute_libid : str, relative_libid : str) -> int:
        '''Adds a reference to an external VBA project.
        
        :param name: The name of reference.
        :param absolute_libid: The referenced VBA project's identifier with an absolute path.
        :param relative_libid: The referenced VBA project's identifier with an relative path.'''
        ...
    
    def binary_search(self, item : aspose.cells.vba.VbaProjectReference) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class VbaModuleType:
    '''Represents the type of VBA module.'''
    
    @classmethod
    @property
    def PROCEDURAL(cls) -> VbaModuleType:
        '''Represents a procedural module.'''
        ...
    
    @classmethod
    @property
    def DOCUMENT(cls) -> VbaModuleType:
        '''Represents a document module.'''
        ...
    
    @classmethod
    @property
    def CLASS(cls) -> VbaModuleType:
        '''Represents a class module.'''
        ...
    
    @classmethod
    @property
    def DESIGNER(cls) -> VbaModuleType:
        '''Represents a designer module.'''
        ...
    
    ...

class VbaProjectReferenceType:
    '''Represents the type of VBA project reference.'''
    
    @classmethod
    @property
    def REGISTERED(cls) -> VbaProjectReferenceType:
        '''Specifies a reference to an Automation type library.'''
        ...
    
    @classmethod
    @property
    def CONTROL(cls) -> VbaProjectReferenceType:
        '''Specifies a reference to a twiddled type library and its extended type library.'''
        ...
    
    @classmethod
    @property
    def PROJECT(cls) -> VbaProjectReferenceType:
        '''Specifies a reference to an external VBA project.'''
        ...
    
    ...

