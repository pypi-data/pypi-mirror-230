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

class NumbersLoadOptions(aspose.cells.LoadOptions):
    '''Represents the options of loading Apple Numbers files.'''
    
    def set_paper_size(self, type : aspose.cells.PaperSizeType):
        '''Sets the default print paper size from default printer's setting.
        
        :param type: The default paper size.'''
        ...
    
    @property
    def load_format(self) -> aspose.cells.LoadFormat:
        ...
    
    @property
    def password(self) -> str:
        '''Gets and set the password of the workbook.'''
        ...
    
    @password.setter
    def password(self, value : str):
        '''Gets and set the password of the workbook.'''
        ...
    
    @property
    def parsing_formula_on_open(self) -> bool:
        ...
    
    @parsing_formula_on_open.setter
    def parsing_formula_on_open(self, value : bool):
        ...
    
    @property
    def parsing_pivot_cached_records(self) -> bool:
        ...
    
    @parsing_pivot_cached_records.setter
    def parsing_pivot_cached_records(self, value : bool):
        ...
    
    @property
    def language_code(self) -> aspose.cells.CountryCode:
        ...
    
    @language_code.setter
    def language_code(self, value : aspose.cells.CountryCode):
        ...
    
    @property
    def region(self) -> aspose.cells.CountryCode:
        '''Gets the system regional settings based on CountryCode at the time the file was loaded.'''
        ...
    
    @region.setter
    def region(self, value : aspose.cells.CountryCode):
        '''Sets the system regional settings based on CountryCode at the time the file was loaded.'''
        ...
    
    @property
    def default_style_settings(self) -> aspose.cells.DefaultStyleSettings:
        ...
    
    @property
    def standard_font(self) -> str:
        ...
    
    @standard_font.setter
    def standard_font(self, value : str):
        ...
    
    @property
    def standard_font_size(self) -> float:
        ...
    
    @standard_font_size.setter
    def standard_font_size(self, value : float):
        ...
    
    @property
    def interrupt_monitor(self) -> aspose.cells.AbstractInterruptMonitor:
        ...
    
    @interrupt_monitor.setter
    def interrupt_monitor(self, value : aspose.cells.AbstractInterruptMonitor):
        ...
    
    @property
    def ignore_not_printed(self) -> bool:
        ...
    
    @ignore_not_printed.setter
    def ignore_not_printed(self, value : bool):
        ...
    
    @property
    def check_data_valid(self) -> bool:
        ...
    
    @check_data_valid.setter
    def check_data_valid(self, value : bool):
        ...
    
    @property
    def check_excel_restriction(self) -> bool:
        ...
    
    @check_excel_restriction.setter
    def check_excel_restriction(self, value : bool):
        ...
    
    @property
    def keep_unparsed_data(self) -> bool:
        ...
    
    @keep_unparsed_data.setter
    def keep_unparsed_data(self, value : bool):
        ...
    
    @property
    def load_filter(self) -> aspose.cells.LoadFilter:
        ...
    
    @load_filter.setter
    def load_filter(self, value : aspose.cells.LoadFilter):
        ...
    
    @property
    def light_cells_data_handler(self) -> aspose.cells.LightCellsDataHandler:
        ...
    
    @light_cells_data_handler.setter
    def light_cells_data_handler(self, value : aspose.cells.LightCellsDataHandler):
        ...
    
    @property
    def memory_setting(self) -> aspose.cells.MemorySetting:
        ...
    
    @memory_setting.setter
    def memory_setting(self, value : aspose.cells.MemorySetting):
        ...
    
    @property
    def warning_callback(self) -> aspose.cells.IWarningCallback:
        ...
    
    @warning_callback.setter
    def warning_callback(self, value : aspose.cells.IWarningCallback):
        ...
    
    @property
    def auto_fitter_options(self) -> aspose.cells.AutoFitterOptions:
        ...
    
    @auto_fitter_options.setter
    def auto_fitter_options(self, value : aspose.cells.AutoFitterOptions):
        ...
    
    @property
    def auto_filter(self) -> bool:
        ...
    
    @auto_filter.setter
    def auto_filter(self, value : bool):
        ...
    
    @property
    def font_configs(self) -> aspose.cells.IndividualFontConfigs:
        ...
    
    @font_configs.setter
    def font_configs(self, value : aspose.cells.IndividualFontConfigs):
        ...
    
    @property
    def ignore_useless_shapes(self) -> bool:
        ...
    
    @ignore_useless_shapes.setter
    def ignore_useless_shapes(self, value : bool):
        ...
    
    @property
    def preserve_padding_spaces_in_formula(self) -> bool:
        ...
    
    @preserve_padding_spaces_in_formula.setter
    def preserve_padding_spaces_in_formula(self, value : bool):
        ...
    
    @property
    def load_table_type(self) -> aspose.cells.numbers.LoadNumbersTableType:
        ...
    
    @load_table_type.setter
    def load_table_type(self, value : aspose.cells.numbers.LoadNumbersTableType):
        ...
    
    ...

class LoadNumbersTableType:
    '''Indicates type of loading tables when some tables are in a sheet.'''
    
    @classmethod
    @property
    def ONE_TABLE_PER_SHEET(cls) -> LoadNumbersTableType:
        ...
    
    @classmethod
    @property
    def OVERRIDE_OTHER_TABLES(cls) -> LoadNumbersTableType:
        ...
    
    @classmethod
    @property
    def TILE_TABLES(cls) -> LoadNumbersTableType:
        ...
    
    ...

