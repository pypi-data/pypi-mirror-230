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

class ConnectionParameter:
    '''Specifies properties about any parameters used with external data connections
    Parameters are valid for ODBC and web queries.'''
    
    @property
    def sql_type(self) -> aspose.cells.externalconnections.SqlDataType:
        ...
    
    @sql_type.setter
    def sql_type(self, value : aspose.cells.externalconnections.SqlDataType):
        ...
    
    @property
    def refresh_on_change(self) -> bool:
        ...
    
    @refresh_on_change.setter
    def refresh_on_change(self, value : bool):
        ...
    
    @property
    def prompt(self) -> str:
        '''Prompt string for the parameter. Presented to the spreadsheet user along with input UI
        to collect the parameter value before refreshing the external data. Used only when
        parameterType = prompt.'''
        ...
    
    @prompt.setter
    def prompt(self, value : str):
        '''Prompt string for the parameter. Presented to the spreadsheet user along with input UI
        to collect the parameter value before refreshing the external data. Used only when
        parameterType = prompt.'''
        ...
    
    @property
    def type(self) -> aspose.cells.externalconnections.ConnectionParameterType:
        '''Type of parameter used.
        If the parameterType=value, then the value from boolean, double, integer,
        or string will be used.  In this case, it is expected that only one of
        {boolean, double, integer, or string} will be specified.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.externalconnections.ConnectionParameterType):
        '''Type of parameter used.
        If the parameterType=value, then the value from boolean, double, integer,
        or string will be used.  In this case, it is expected that only one of
        {boolean, double, integer, or string} will be specified.'''
        ...
    
    @property
    def name(self) -> str:
        '''The name of the parameter.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''The name of the parameter.'''
        ...
    
    @property
    def cell_reference(self) -> str:
        ...
    
    @cell_reference.setter
    def cell_reference(self, value : str):
        ...
    
    @property
    def value(self) -> any:
        '''Non-integer numeric value,Integer value,String value or Boolean value
        to use as the query parameter. Used only when parameterType is value.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Non-integer numeric value,Integer value,String value or Boolean value
        to use as the query parameter. Used only when parameterType is value.'''
        ...
    
    ...

class ConnectionParameterCollection:
    '''Specifies the :py:class:`aspose.cells.externalconnections.ConnectionParameter` collection'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.externalconnections.ConnectionParameter]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.externalconnections.ConnectionParameter], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.externalconnections.ConnectionParameter, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.externalconnections.ConnectionParameter, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.externalconnections.ConnectionParameter) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.externalconnections.ConnectionParameter, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.externalconnections.ConnectionParameter, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.externalconnections.ConnectionParameter) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class DBConnection(ExternalConnection):
    '''Specifies all properties associated with an ODBC or OLE DB external data connection.'''
    
    @property
    def id(self) -> int:
        '''Gets the id of the connection.'''
        ...
    
    @property
    def power_query_formula(self) -> aspose.cells.querytables.PowerQueryFormula:
        ...
    
    @property
    def type(self) -> aspose.cells.externalconnections.ConnectionDataSourceType:
        '''Gets or Sets the external connection DataSource type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.externalconnections.ConnectionDataSourceType):
        '''Gets or Sets the external connection DataSource type.'''
        ...
    
    @property
    def source_file(self) -> str:
        ...
    
    @source_file.setter
    def source_file(self, value : str):
        ...
    
    @property
    def sso_id(self) -> str:
        ...
    
    @sso_id.setter
    def sso_id(self, value : str):
        ...
    
    @property
    def save_password(self) -> bool:
        ...
    
    @save_password.setter
    def save_password(self, value : bool):
        ...
    
    @property
    def save_data(self) -> bool:
        ...
    
    @save_data.setter
    def save_data(self, value : bool):
        ...
    
    @property
    def refresh_on_load(self) -> bool:
        ...
    
    @refresh_on_load.setter
    def refresh_on_load(self, value : bool):
        ...
    
    @property
    def reconnection_method_type(self) -> aspose.cells.externalconnections.ReConnectionMethodType:
        ...
    
    @reconnection_method_type.setter
    def reconnection_method_type(self, value : aspose.cells.externalconnections.ReConnectionMethodType):
        ...
    
    @property
    def reconnection_method(self) -> aspose.cells.externalconnections.ReConnectionMethodType:
        ...
    
    @reconnection_method.setter
    def reconnection_method(self, value : aspose.cells.externalconnections.ReConnectionMethodType):
        ...
    
    @property
    def only_use_connection_file(self) -> bool:
        ...
    
    @only_use_connection_file.setter
    def only_use_connection_file(self, value : bool):
        ...
    
    @property
    def odc_file(self) -> str:
        ...
    
    @odc_file.setter
    def odc_file(self, value : str):
        ...
    
    @property
    def is_new(self) -> bool:
        ...
    
    @is_new.setter
    def is_new(self, value : bool):
        ...
    
    @property
    def name(self) -> str:
        '''Specifies the name of the connection. Each connection must have a unique name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Specifies the name of the connection. Each connection must have a unique name.'''
        ...
    
    @property
    def keep_alive(self) -> bool:
        ...
    
    @keep_alive.setter
    def keep_alive(self, value : bool):
        ...
    
    @property
    def refresh_internal(self) -> int:
        ...
    
    @refresh_internal.setter
    def refresh_internal(self, value : int):
        ...
    
    @property
    def connection_id(self) -> int:
        ...
    
    @property
    def connection_description(self) -> str:
        ...
    
    @connection_description.setter
    def connection_description(self, value : str):
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def credentials_method_type(self) -> aspose.cells.externalconnections.CredentialsMethodType:
        ...
    
    @credentials_method_type.setter
    def credentials_method_type(self, value : aspose.cells.externalconnections.CredentialsMethodType):
        ...
    
    @property
    def credentials(self) -> aspose.cells.externalconnections.CredentialsMethodType:
        '''Specifies the authentication method to be used when establishing (or re-establishing) the connection.'''
        ...
    
    @credentials.setter
    def credentials(self, value : aspose.cells.externalconnections.CredentialsMethodType):
        '''Specifies the authentication method to be used when establishing (or re-establishing) the connection.'''
        ...
    
    @property
    def background_refresh(self) -> bool:
        ...
    
    @background_refresh.setter
    def background_refresh(self, value : bool):
        ...
    
    @property
    def parameters(self) -> aspose.cells.externalconnections.ConnectionParameterCollection:
        '''Gets :py:class:`aspose.cells.externalconnections.ConnectionParameterCollection` for an ODBC or web query.'''
        ...
    
    @property
    def connection_info(self) -> str:
        ...
    
    @connection_info.setter
    def connection_info(self, value : str):
        ...
    
    @property
    def command_type(self) -> aspose.cells.externalconnections.OLEDBCommandType:
        ...
    
    @command_type.setter
    def command_type(self, value : aspose.cells.externalconnections.OLEDBCommandType):
        ...
    
    @property
    def command(self) -> str:
        '''The string containing the database command to pass to the data provider API that will
        interact with the external source in order to retrieve data'''
        ...
    
    @command.setter
    def command(self, value : str):
        '''The string containing the database command to pass to the data provider API that will
        interact with the external source in order to retrieve data'''
        ...
    
    @property
    def sever_command(self) -> str:
        ...
    
    @sever_command.setter
    def sever_command(self, value : str):
        ...
    
    ...

class DataModelConnection(ExternalConnection):
    '''Specifies a data model connection'''
    
    @property
    def id(self) -> int:
        '''Gets the id of the connection.'''
        ...
    
    @property
    def power_query_formula(self) -> aspose.cells.querytables.PowerQueryFormula:
        ...
    
    @property
    def type(self) -> aspose.cells.externalconnections.ConnectionDataSourceType:
        '''Gets or Sets the external connection DataSource type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.externalconnections.ConnectionDataSourceType):
        '''Gets or Sets the external connection DataSource type.'''
        ...
    
    @property
    def source_file(self) -> str:
        ...
    
    @source_file.setter
    def source_file(self, value : str):
        ...
    
    @property
    def sso_id(self) -> str:
        ...
    
    @sso_id.setter
    def sso_id(self, value : str):
        ...
    
    @property
    def save_password(self) -> bool:
        ...
    
    @save_password.setter
    def save_password(self, value : bool):
        ...
    
    @property
    def save_data(self) -> bool:
        ...
    
    @save_data.setter
    def save_data(self, value : bool):
        ...
    
    @property
    def refresh_on_load(self) -> bool:
        ...
    
    @refresh_on_load.setter
    def refresh_on_load(self, value : bool):
        ...
    
    @property
    def reconnection_method_type(self) -> aspose.cells.externalconnections.ReConnectionMethodType:
        ...
    
    @reconnection_method_type.setter
    def reconnection_method_type(self, value : aspose.cells.externalconnections.ReConnectionMethodType):
        ...
    
    @property
    def reconnection_method(self) -> aspose.cells.externalconnections.ReConnectionMethodType:
        ...
    
    @reconnection_method.setter
    def reconnection_method(self, value : aspose.cells.externalconnections.ReConnectionMethodType):
        ...
    
    @property
    def only_use_connection_file(self) -> bool:
        ...
    
    @only_use_connection_file.setter
    def only_use_connection_file(self, value : bool):
        ...
    
    @property
    def odc_file(self) -> str:
        ...
    
    @odc_file.setter
    def odc_file(self, value : str):
        ...
    
    @property
    def is_new(self) -> bool:
        ...
    
    @is_new.setter
    def is_new(self, value : bool):
        ...
    
    @property
    def name(self) -> str:
        '''Specifies the name of the connection. Each connection must have a unique name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Specifies the name of the connection. Each connection must have a unique name.'''
        ...
    
    @property
    def keep_alive(self) -> bool:
        ...
    
    @keep_alive.setter
    def keep_alive(self, value : bool):
        ...
    
    @property
    def refresh_internal(self) -> int:
        ...
    
    @refresh_internal.setter
    def refresh_internal(self, value : int):
        ...
    
    @property
    def connection_id(self) -> int:
        ...
    
    @property
    def connection_description(self) -> str:
        ...
    
    @connection_description.setter
    def connection_description(self, value : str):
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def credentials_method_type(self) -> aspose.cells.externalconnections.CredentialsMethodType:
        ...
    
    @credentials_method_type.setter
    def credentials_method_type(self, value : aspose.cells.externalconnections.CredentialsMethodType):
        ...
    
    @property
    def credentials(self) -> aspose.cells.externalconnections.CredentialsMethodType:
        '''Specifies the authentication method to be used when establishing (or re-establishing) the connection.'''
        ...
    
    @credentials.setter
    def credentials(self, value : aspose.cells.externalconnections.CredentialsMethodType):
        '''Specifies the authentication method to be used when establishing (or re-establishing) the connection.'''
        ...
    
    @property
    def background_refresh(self) -> bool:
        ...
    
    @background_refresh.setter
    def background_refresh(self, value : bool):
        ...
    
    @property
    def parameters(self) -> aspose.cells.externalconnections.ConnectionParameterCollection:
        '''Gets :py:class:`aspose.cells.externalconnections.ConnectionParameterCollection` for an ODBC or web query.'''
        ...
    
    ...

class ExternalConnection:
    '''Specifies an external data connection'''
    
    @property
    def id(self) -> int:
        '''Gets the id of the connection.'''
        ...
    
    @property
    def power_query_formula(self) -> aspose.cells.querytables.PowerQueryFormula:
        ...
    
    @property
    def type(self) -> aspose.cells.externalconnections.ConnectionDataSourceType:
        '''Gets or Sets the external connection DataSource type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.externalconnections.ConnectionDataSourceType):
        '''Gets or Sets the external connection DataSource type.'''
        ...
    
    @property
    def source_file(self) -> str:
        ...
    
    @source_file.setter
    def source_file(self, value : str):
        ...
    
    @property
    def sso_id(self) -> str:
        ...
    
    @sso_id.setter
    def sso_id(self, value : str):
        ...
    
    @property
    def save_password(self) -> bool:
        ...
    
    @save_password.setter
    def save_password(self, value : bool):
        ...
    
    @property
    def save_data(self) -> bool:
        ...
    
    @save_data.setter
    def save_data(self, value : bool):
        ...
    
    @property
    def refresh_on_load(self) -> bool:
        ...
    
    @refresh_on_load.setter
    def refresh_on_load(self, value : bool):
        ...
    
    @property
    def reconnection_method_type(self) -> aspose.cells.externalconnections.ReConnectionMethodType:
        ...
    
    @reconnection_method_type.setter
    def reconnection_method_type(self, value : aspose.cells.externalconnections.ReConnectionMethodType):
        ...
    
    @property
    def reconnection_method(self) -> aspose.cells.externalconnections.ReConnectionMethodType:
        ...
    
    @reconnection_method.setter
    def reconnection_method(self, value : aspose.cells.externalconnections.ReConnectionMethodType):
        ...
    
    @property
    def only_use_connection_file(self) -> bool:
        ...
    
    @only_use_connection_file.setter
    def only_use_connection_file(self, value : bool):
        ...
    
    @property
    def odc_file(self) -> str:
        ...
    
    @odc_file.setter
    def odc_file(self, value : str):
        ...
    
    @property
    def is_new(self) -> bool:
        ...
    
    @is_new.setter
    def is_new(self, value : bool):
        ...
    
    @property
    def name(self) -> str:
        '''Specifies the name of the connection. Each connection must have a unique name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Specifies the name of the connection. Each connection must have a unique name.'''
        ...
    
    @property
    def keep_alive(self) -> bool:
        ...
    
    @keep_alive.setter
    def keep_alive(self, value : bool):
        ...
    
    @property
    def refresh_internal(self) -> int:
        ...
    
    @refresh_internal.setter
    def refresh_internal(self, value : int):
        ...
    
    @property
    def connection_id(self) -> int:
        ...
    
    @property
    def connection_description(self) -> str:
        ...
    
    @connection_description.setter
    def connection_description(self, value : str):
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def credentials_method_type(self) -> aspose.cells.externalconnections.CredentialsMethodType:
        ...
    
    @credentials_method_type.setter
    def credentials_method_type(self, value : aspose.cells.externalconnections.CredentialsMethodType):
        ...
    
    @property
    def credentials(self) -> aspose.cells.externalconnections.CredentialsMethodType:
        '''Specifies the authentication method to be used when establishing (or re-establishing) the connection.'''
        ...
    
    @credentials.setter
    def credentials(self, value : aspose.cells.externalconnections.CredentialsMethodType):
        '''Specifies the authentication method to be used when establishing (or re-establishing) the connection.'''
        ...
    
    @property
    def background_refresh(self) -> bool:
        ...
    
    @background_refresh.setter
    def background_refresh(self, value : bool):
        ...
    
    @property
    def parameters(self) -> aspose.cells.externalconnections.ConnectionParameterCollection:
        '''Gets :py:class:`aspose.cells.externalconnections.ConnectionParameterCollection` for an ODBC or web query.'''
        ...
    
    ...

class ExternalConnectionCollection:
    '''Specifies the :py:class:`aspose.cells.externalconnections.ExternalConnection` collection'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.externalconnections.ExternalConnection]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.externalconnections.ExternalConnection], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.externalconnections.ExternalConnection, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.externalconnections.ExternalConnection, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.externalconnections.ExternalConnection) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.externalconnections.ExternalConnection, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.externalconnections.ExternalConnection, index : int, count : int) -> int:
        ...
    
    def get_external_connection_by_id(self, conn_id : int) -> aspose.cells.externalconnections.ExternalConnection:
        '''Gets the :py:class:`aspose.cells.externalconnections.ExternalConnection` element with the specified id.
        
        :param conn_id: external connection id
        :returns: The element with the specified id.'''
        ...
    
    def binary_search(self, item : aspose.cells.externalconnections.ExternalConnection) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class WebQueryConnection(ExternalConnection):
    '''Specifies the properties for a web query source. A web query will retrieve data from HTML tables,
    and can also supply HTTP "Get" parameters to be processed by the web server in generating the HTML by
    including the parameters and parameter elements.'''
    
    @property
    def id(self) -> int:
        '''Gets the id of the connection.'''
        ...
    
    @property
    def power_query_formula(self) -> aspose.cells.querytables.PowerQueryFormula:
        ...
    
    @property
    def type(self) -> aspose.cells.externalconnections.ConnectionDataSourceType:
        '''Gets or Sets the external connection DataSource type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.externalconnections.ConnectionDataSourceType):
        '''Gets or Sets the external connection DataSource type.'''
        ...
    
    @property
    def source_file(self) -> str:
        ...
    
    @source_file.setter
    def source_file(self, value : str):
        ...
    
    @property
    def sso_id(self) -> str:
        ...
    
    @sso_id.setter
    def sso_id(self, value : str):
        ...
    
    @property
    def save_password(self) -> bool:
        ...
    
    @save_password.setter
    def save_password(self, value : bool):
        ...
    
    @property
    def save_data(self) -> bool:
        ...
    
    @save_data.setter
    def save_data(self, value : bool):
        ...
    
    @property
    def refresh_on_load(self) -> bool:
        ...
    
    @refresh_on_load.setter
    def refresh_on_load(self, value : bool):
        ...
    
    @property
    def reconnection_method_type(self) -> aspose.cells.externalconnections.ReConnectionMethodType:
        ...
    
    @reconnection_method_type.setter
    def reconnection_method_type(self, value : aspose.cells.externalconnections.ReConnectionMethodType):
        ...
    
    @property
    def reconnection_method(self) -> aspose.cells.externalconnections.ReConnectionMethodType:
        ...
    
    @reconnection_method.setter
    def reconnection_method(self, value : aspose.cells.externalconnections.ReConnectionMethodType):
        ...
    
    @property
    def only_use_connection_file(self) -> bool:
        ...
    
    @only_use_connection_file.setter
    def only_use_connection_file(self, value : bool):
        ...
    
    @property
    def odc_file(self) -> str:
        ...
    
    @odc_file.setter
    def odc_file(self, value : str):
        ...
    
    @property
    def is_new(self) -> bool:
        ...
    
    @is_new.setter
    def is_new(self, value : bool):
        ...
    
    @property
    def name(self) -> str:
        '''Specifies the name of the connection. Each connection must have a unique name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Specifies the name of the connection. Each connection must have a unique name.'''
        ...
    
    @property
    def keep_alive(self) -> bool:
        ...
    
    @keep_alive.setter
    def keep_alive(self, value : bool):
        ...
    
    @property
    def refresh_internal(self) -> int:
        ...
    
    @refresh_internal.setter
    def refresh_internal(self, value : int):
        ...
    
    @property
    def connection_id(self) -> int:
        ...
    
    @property
    def connection_description(self) -> str:
        ...
    
    @connection_description.setter
    def connection_description(self, value : str):
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def credentials_method_type(self) -> aspose.cells.externalconnections.CredentialsMethodType:
        ...
    
    @credentials_method_type.setter
    def credentials_method_type(self, value : aspose.cells.externalconnections.CredentialsMethodType):
        ...
    
    @property
    def credentials(self) -> aspose.cells.externalconnections.CredentialsMethodType:
        '''Specifies the authentication method to be used when establishing (or re-establishing) the connection.'''
        ...
    
    @credentials.setter
    def credentials(self, value : aspose.cells.externalconnections.CredentialsMethodType):
        '''Specifies the authentication method to be used when establishing (or re-establishing) the connection.'''
        ...
    
    @property
    def background_refresh(self) -> bool:
        ...
    
    @background_refresh.setter
    def background_refresh(self, value : bool):
        ...
    
    @property
    def parameters(self) -> aspose.cells.externalconnections.ConnectionParameterCollection:
        '''Gets :py:class:`aspose.cells.externalconnections.ConnectionParameterCollection` for an ODBC or web query.'''
        ...
    
    @property
    def is_xml(self) -> bool:
        ...
    
    @is_xml.setter
    def is_xml(self, value : bool):
        ...
    
    @property
    def is_xl97(self) -> bool:
        ...
    
    @is_xl97.setter
    def is_xl97(self, value : bool):
        ...
    
    @property
    def is_xl2000(self) -> bool:
        ...
    
    @is_xl2000.setter
    def is_xl2000(self, value : bool):
        ...
    
    @property
    def url(self) -> str:
        '''URL to use to refresh external data.'''
        ...
    
    @url.setter
    def url(self, value : str):
        '''URL to use to refresh external data.'''
        ...
    
    @property
    def is_text_dates(self) -> bool:
        ...
    
    @is_text_dates.setter
    def is_text_dates(self, value : bool):
        ...
    
    @property
    def is_xml_source_data(self) -> bool:
        ...
    
    @is_xml_source_data.setter
    def is_xml_source_data(self, value : bool):
        ...
    
    @property
    def post(self) -> str:
        '''Returns the string used with the post method of inputting data into a web server
        to return data from a web query.'''
        ...
    
    @post.setter
    def post(self, value : str):
        '''Returns or sets the string used with the post method of inputting data into a web server
        to return data from a web query.'''
        ...
    
    @property
    def is_parse_pre(self) -> bool:
        ...
    
    @is_parse_pre.setter
    def is_parse_pre(self, value : bool):
        ...
    
    @property
    def is_html_tables(self) -> bool:
        ...
    
    @is_html_tables.setter
    def is_html_tables(self, value : bool):
        ...
    
    @property
    def html_format(self) -> aspose.cells.externalconnections.HtmlFormatHandlingType:
        ...
    
    @html_format.setter
    def html_format(self, value : aspose.cells.externalconnections.HtmlFormatHandlingType):
        ...
    
    @property
    def is_same_settings(self) -> bool:
        ...
    
    @is_same_settings.setter
    def is_same_settings(self, value : bool):
        ...
    
    @property
    def edit_web_page(self) -> str:
        ...
    
    @edit_web_page.setter
    def edit_web_page(self, value : str):
        ...
    
    @property
    def edit_page(self) -> str:
        ...
    
    @edit_page.setter
    def edit_page(self, value : str):
        ...
    
    @property
    def is_consecutive(self) -> bool:
        ...
    
    @is_consecutive.setter
    def is_consecutive(self, value : bool):
        ...
    
    ...

class ConnectionDataSourceType:
    '''Specifies external database source type'''
    
    @classmethod
    @property
    def ODBC_BASED_SOURCE(cls) -> ConnectionDataSourceType:
        '''ODBC-based source'''
        ...
    
    @classmethod
    @property
    def DAO_BASED_SOURCE(cls) -> ConnectionDataSourceType:
        '''DAO-based source'''
        ...
    
    @classmethod
    @property
    def FILE_BASED_DATA_BASE_SOURCE(cls) -> ConnectionDataSourceType:
        '''File based database source'''
        ...
    
    @classmethod
    @property
    def WEB_QUERY(cls) -> ConnectionDataSourceType:
        '''Web query'''
        ...
    
    @classmethod
    @property
    def OLEDB_BASED_SOURCE(cls) -> ConnectionDataSourceType:
        '''OLE DB-based source'''
        ...
    
    @classmethod
    @property
    def TEXT_BASED_SOURCE(cls) -> ConnectionDataSourceType:
        '''Text-based source'''
        ...
    
    @classmethod
    @property
    def ADO_RECORD_SET(cls) -> ConnectionDataSourceType:
        '''ADO record set'''
        ...
    
    @classmethod
    @property
    def DSP(cls) -> ConnectionDataSourceType:
        '''DSP'''
        ...
    
    @classmethod
    @property
    def OLEDB_DATA_MODEL(cls) -> ConnectionDataSourceType:
        '''OLE DB data source created by the Spreadsheet Data Model.'''
        ...
    
    @classmethod
    @property
    def DATA_FEED_DATA_MODEL(cls) -> ConnectionDataSourceType:
        '''Data feed data source created by the Spreadsheet Data Model.'''
        ...
    
    @classmethod
    @property
    def WORKSHEET_DATA_MODEL(cls) -> ConnectionDataSourceType:
        '''Worksheet data source created by the Spreadsheet Data Model.'''
        ...
    
    @classmethod
    @property
    def TABLE(cls) -> ConnectionDataSourceType:
        '''Worksheet data source created by the Spreadsheet Data Model.'''
        ...
    
    @classmethod
    @property
    def TEXT_DATA_MODEL(cls) -> ConnectionDataSourceType:
        '''Text data source created by the Spreadsheet Data Model.'''
        ...
    
    @classmethod
    @property
    def UNKNOWN(cls) -> ConnectionDataSourceType:
        '''Text data source created by the Spreadsheet Data Model.'''
        ...
    
    ...

class ConnectionParameterType:
    '''Specifies the parameter type of external connection'''
    
    @classmethod
    @property
    def CELL(cls) -> ConnectionParameterType:
        '''Get the parameter value from a cell on each refresh.'''
        ...
    
    @classmethod
    @property
    def PROMPT(cls) -> ConnectionParameterType:
        '''Prompt the user on each refresh for a parameter value.'''
        ...
    
    @classmethod
    @property
    def VALUE(cls) -> ConnectionParameterType:
        '''Use a constant value on each refresh for the parameter value.'''
        ...
    
    ...

class CredentialsMethodType:
    '''Specifies Credentials method used for server access.'''
    
    @classmethod
    @property
    def INTEGRATED(cls) -> CredentialsMethodType:
        '''Integrated Authentication'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> CredentialsMethodType:
        '''No Credentials'''
        ...
    
    @classmethod
    @property
    def PROMPT(cls) -> CredentialsMethodType:
        '''Prompt Credentials'''
        ...
    
    @classmethod
    @property
    def STORED(cls) -> CredentialsMethodType:
        '''Stored Credentials'''
        ...
    
    ...

class HtmlFormatHandlingType:
    '''Specifies how to handle formatting from the HTML source'''
    
    @classmethod
    @property
    def ALL(cls) -> HtmlFormatHandlingType:
        '''Transfer all HTML formatting into the worksheet along with data.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> HtmlFormatHandlingType:
        '''Bring data in as unformatted text (setting data types still occurs).'''
        ...
    
    @classmethod
    @property
    def RTF(cls) -> HtmlFormatHandlingType:
        '''Translate HTML formatting to rich text formatting on the data brought into the worksheet.'''
        ...
    
    ...

class OLEDBCommandType:
    '''Specifies the OLE DB command type.'''
    
    @classmethod
    @property
    def NONE(cls) -> OLEDBCommandType:
        '''The command type is not specified.'''
        ...
    
    @classmethod
    @property
    def CUBE_NAME(cls) -> OLEDBCommandType:
        '''Specifies a cube name'''
        ...
    
    @classmethod
    @property
    def SQL_STATEMENT(cls) -> OLEDBCommandType:
        '''Specifies a SQL statement'''
        ...
    
    @classmethod
    @property
    def TABLE_NAME(cls) -> OLEDBCommandType:
        '''Specifies a table name'''
        ...
    
    @classmethod
    @property
    def DEFAULT_INFORMATION(cls) -> OLEDBCommandType:
        '''Specifies that default information has been given, and it is up to the provider how to interpret.'''
        ...
    
    @classmethod
    @property
    def WEB_BASED_LIST(cls) -> OLEDBCommandType:
        '''Specifies a query which is against a web based List Data Provider.'''
        ...
    
    ...

class ReConnectionMethodType:
    '''Specifies what the spreadsheet application should do when a connection fails.'''
    
    @classmethod
    @property
    def REQUIRED(cls) -> ReConnectionMethodType:
        '''On refresh use the existing connection information and if it ends up being invalid
        then get updated connection information, if available from the external connection file.'''
        ...
    
    @classmethod
    @property
    def ALWAYS(cls) -> ReConnectionMethodType:
        '''On every refresh get updated connection information from the external connection file,
        if available, and use that instead of the existing connection information.
        In this case the data refresh will fail if the external connection file is unavailable.'''
        ...
    
    @classmethod
    @property
    def NEVER(cls) -> ReConnectionMethodType:
        '''Never get updated connection information from the external connection file
        even if it is available and even if the existing connection information is invalid'''
        ...
    
    ...

class SqlDataType:
    '''Specifies SQL data type of the parameter. Only valid for ODBC sources.'''
    
    @classmethod
    @property
    def SQL_UNSIGNED_OFFSET(cls) -> SqlDataType:
        '''sql unsigned offset'''
        ...
    
    @classmethod
    @property
    def SQL_SIGNED_OFFSET(cls) -> SqlDataType:
        '''sql signed offset'''
        ...
    
    @classmethod
    @property
    def SQL_GUID(cls) -> SqlDataType:
        '''sql guid'''
        ...
    
    @classmethod
    @property
    def SQL_W_LONG_VARCHAR(cls) -> SqlDataType:
        '''sql wide long variable char'''
        ...
    
    @classmethod
    @property
    def SQL_W_VARCHAR(cls) -> SqlDataType:
        '''sql wide variable char'''
        ...
    
    @classmethod
    @property
    def SQL_W_CHAR(cls) -> SqlDataType:
        '''sql wide char'''
        ...
    
    @classmethod
    @property
    def SQL_BIT(cls) -> SqlDataType:
        '''sql bit'''
        ...
    
    @classmethod
    @property
    def SQL_TINY_INT(cls) -> SqlDataType:
        '''sql tiny int'''
        ...
    
    @classmethod
    @property
    def SQL_BIG_INT(cls) -> SqlDataType:
        '''sql big int'''
        ...
    
    @classmethod
    @property
    def SQL_LONG_VAR_BINARY(cls) -> SqlDataType:
        '''sql long variable binary'''
        ...
    
    @classmethod
    @property
    def SQL_VAR_BINARY(cls) -> SqlDataType:
        '''sql variable binary'''
        ...
    
    @classmethod
    @property
    def SQL_BINARY(cls) -> SqlDataType:
        '''sql binary'''
        ...
    
    @classmethod
    @property
    def SQL_LONG_VAR_CHAR(cls) -> SqlDataType:
        '''sql long variable char'''
        ...
    
    @classmethod
    @property
    def SQL_UNKNOWN_TYPE(cls) -> SqlDataType:
        '''sql unknown type'''
        ...
    
    @classmethod
    @property
    def SQL_CHAR(cls) -> SqlDataType:
        '''sql char'''
        ...
    
    @classmethod
    @property
    def SQL_NUMERIC(cls) -> SqlDataType:
        '''sql numeric'''
        ...
    
    @classmethod
    @property
    def SQL_DECIMAL(cls) -> SqlDataType:
        '''sql decimal'''
        ...
    
    @classmethod
    @property
    def SQL_INTEGER(cls) -> SqlDataType:
        '''sql integer'''
        ...
    
    @classmethod
    @property
    def SQL_SMALL_INT(cls) -> SqlDataType:
        '''sql small int'''
        ...
    
    @classmethod
    @property
    def SQL_FLOAT(cls) -> SqlDataType:
        '''sql float'''
        ...
    
    @classmethod
    @property
    def SQL_REAL(cls) -> SqlDataType:
        '''sql real'''
        ...
    
    @classmethod
    @property
    def SQL_DOUBLE(cls) -> SqlDataType:
        '''sql double'''
        ...
    
    @classmethod
    @property
    def SQL_TYPE_DATE(cls) -> SqlDataType:
        '''sql date type'''
        ...
    
    @classmethod
    @property
    def SQL_TYPE_TIME(cls) -> SqlDataType:
        '''sql time type'''
        ...
    
    @classmethod
    @property
    def SQL_TYPE_TIMESTAMP(cls) -> SqlDataType:
        '''sql timestamp type'''
        ...
    
    @classmethod
    @property
    def SQL_VAR_CHAR(cls) -> SqlDataType:
        '''sql variable char'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_YEAR(cls) -> SqlDataType:
        '''sql interval year'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_MONTH(cls) -> SqlDataType:
        '''sql interval month'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_DAY(cls) -> SqlDataType:
        '''sql interval day'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_HOUR(cls) -> SqlDataType:
        '''sql interval hour'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_MINUTE(cls) -> SqlDataType:
        '''sql interval minute'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_SECOND(cls) -> SqlDataType:
        '''sql interval second'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_YEAR_TO_MONTH(cls) -> SqlDataType:
        '''sql interval year to month'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_DAY_TO_HOUR(cls) -> SqlDataType:
        '''sql interval day to hour'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_DAY_TO_MINUTE(cls) -> SqlDataType:
        '''sql interval day to minute'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_DAY_TO_SECOND(cls) -> SqlDataType:
        '''sql interval day to second'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_HOUR_TO_MINUTE(cls) -> SqlDataType:
        '''sql interval hour to minute'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_HOUR_TO_SECOND(cls) -> SqlDataType:
        '''sql interval hour to second'''
        ...
    
    @classmethod
    @property
    def SQL_INTERVAL_MINUTE_TO_SECOND(cls) -> SqlDataType:
        '''sql interval minute to second'''
        ...
    
    ...

