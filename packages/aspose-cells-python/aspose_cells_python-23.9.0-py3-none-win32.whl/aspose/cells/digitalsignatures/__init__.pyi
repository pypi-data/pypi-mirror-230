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

class DigitalSignature:
    '''Signature in file.'''
    
    @property
    def certificate(self) -> System.Security.Cryptography.X509Certificates.X509Certificate2:
        '''Certificate object that was used to sign the document.'''
        ...
    
    @certificate.setter
    def certificate(self, value : System.Security.Cryptography.X509Certificates.X509Certificate2):
        '''Certificate object that was used to sign the document.'''
        ...
    
    @property
    def comments(self) -> str:
        '''The purpose to signature.'''
        ...
    
    @comments.setter
    def comments(self, value : str):
        '''The purpose to signature.'''
        ...
    
    @property
    def sign_time(self) -> DateTime:
        ...
    
    @sign_time.setter
    def sign_time(self, value : DateTime):
        ...
    
    @property
    def id(self) -> Guid:
        '''Specifies a GUID which can be cross-referenced with the GUID of the signature line stored in the document content.
        Default value is Empty (all zeroes) Guid.'''
        ...
    
    @id.setter
    def id(self, value : Guid):
        '''Specifies a GUID which can be cross-referenced with the GUID of the signature line stored in the document content.
        Default value is Empty (all zeroes) Guid.'''
        ...
    
    @property
    def text(self) -> str:
        '''Specifies the text of actual signature in the digital signature.
        Default value is Empty.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Specifies the text of actual signature in the digital signature.
        Default value is Empty.'''
        ...
    
    @property
    def image(self) -> bytes:
        '''Specifies an image for the digital signature.
        Default value is null.'''
        ...
    
    @image.setter
    def image(self, value : bytes):
        '''Specifies an image for the digital signature.
        Default value is null.'''
        ...
    
    @property
    def provider_id(self) -> Guid:
        ...
    
    @provider_id.setter
    def provider_id(self, value : Guid):
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def x_ad_es_type(self) -> aspose.cells.digitalsignatures.XAdESType:
        ...
    
    @x_ad_es_type.setter
    def x_ad_es_type(self, value : aspose.cells.digitalsignatures.XAdESType):
        ...
    
    ...

class DigitalSignatureCollection:
    '''Provides a collection of digital signatures attached to a document.'''
    
    def add(self, digital_signature : aspose.cells.digitalsignatures.DigitalSignature):
        '''Add one signature to DigitalSignatureCollection.
        
        :param digital_signature: Digital signature in collection.'''
        ...
    
    ...

class XAdESType:
    '''Type of XML Advanced Electronic Signature (XAdES).'''
    
    @classmethod
    @property
    def NONE(cls) -> XAdESType:
        '''XAdES is off.'''
        ...
    
    @classmethod
    @property
    def X_AD_ES(cls) -> XAdESType:
        '''Basic XAdES.'''
        ...
    
    ...

