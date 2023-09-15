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

class PdfSecurityOptions:
    '''Options for encrypting and access permissions for a PDF document.
    PDF/A does not allow security setting.'''
    
    @property
    def user_password(self) -> str:
        ...
    
    @user_password.setter
    def user_password(self, value : str):
        ...
    
    @property
    def owner_password(self) -> str:
        ...
    
    @owner_password.setter
    def owner_password(self, value : str):
        ...
    
    @property
    def print_permission(self) -> bool:
        ...
    
    @print_permission.setter
    def print_permission(self, value : bool):
        ...
    
    @property
    def modify_document_permission(self) -> bool:
        ...
    
    @modify_document_permission.setter
    def modify_document_permission(self, value : bool):
        ...
    
    @property
    def extract_content_permission_obsolete(self) -> bool:
        ...
    
    @extract_content_permission_obsolete.setter
    def extract_content_permission_obsolete(self, value : bool):
        ...
    
    @property
    def annotations_permission(self) -> bool:
        ...
    
    @annotations_permission.setter
    def annotations_permission(self, value : bool):
        ...
    
    @property
    def fill_forms_permission(self) -> bool:
        ...
    
    @fill_forms_permission.setter
    def fill_forms_permission(self, value : bool):
        ...
    
    @property
    def extract_content_permission(self) -> bool:
        ...
    
    @extract_content_permission.setter
    def extract_content_permission(self, value : bool):
        ...
    
    @property
    def accessibility_extract_content(self) -> bool:
        ...
    
    @accessibility_extract_content.setter
    def accessibility_extract_content(self, value : bool):
        ...
    
    @property
    def assemble_document_permission(self) -> bool:
        ...
    
    @assemble_document_permission.setter
    def assemble_document_permission(self, value : bool):
        ...
    
    @property
    def full_quality_print_permission(self) -> bool:
        ...
    
    @full_quality_print_permission.setter
    def full_quality_print_permission(self, value : bool):
        ...
    
    ...

