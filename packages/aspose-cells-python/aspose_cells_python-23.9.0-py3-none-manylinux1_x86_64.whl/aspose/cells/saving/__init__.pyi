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

class EbookSaveOptions(aspose.cells.HtmlSaveOptions):
    '''Represents the options for saving ebook file.'''
    
    @property
    def save_format(self) -> aspose.cells.SaveFormat:
        ...
    
    @property
    def clear_data(self) -> bool:
        ...
    
    @clear_data.setter
    def clear_data(self, value : bool):
        ...
    
    @property
    def cached_file_folder(self) -> str:
        ...
    
    @cached_file_folder.setter
    def cached_file_folder(self, value : str):
        ...
    
    @property
    def validate_merged_areas(self) -> bool:
        ...
    
    @validate_merged_areas.setter
    def validate_merged_areas(self, value : bool):
        ...
    
    @property
    def merge_areas(self) -> bool:
        ...
    
    @merge_areas.setter
    def merge_areas(self, value : bool):
        ...
    
    @property
    def create_directory(self) -> bool:
        ...
    
    @create_directory.setter
    def create_directory(self, value : bool):
        ...
    
    @property
    def sort_names(self) -> bool:
        ...
    
    @sort_names.setter
    def sort_names(self, value : bool):
        ...
    
    @property
    def sort_external_names(self) -> bool:
        ...
    
    @sort_external_names.setter
    def sort_external_names(self, value : bool):
        ...
    
    @property
    def refresh_chart_cache(self) -> bool:
        ...
    
    @refresh_chart_cache.setter
    def refresh_chart_cache(self, value : bool):
        ...
    
    @property
    def warning_callback(self) -> aspose.cells.IWarningCallback:
        ...
    
    @warning_callback.setter
    def warning_callback(self, value : aspose.cells.IWarningCallback):
        ...
    
    @property
    def update_smart_art(self) -> bool:
        ...
    
    @update_smart_art.setter
    def update_smart_art(self, value : bool):
        ...
    
    @property
    def ignore_invisible_shapes(self) -> bool:
        ...
    
    @ignore_invisible_shapes.setter
    def ignore_invisible_shapes(self, value : bool):
        ...
    
    @property
    def page_title(self) -> str:
        ...
    
    @page_title.setter
    def page_title(self, value : str):
        ...
    
    @property
    def attached_files_directory(self) -> str:
        ...
    
    @attached_files_directory.setter
    def attached_files_directory(self, value : str):
        ...
    
    @property
    def attached_files_url_prefix(self) -> str:
        ...
    
    @attached_files_url_prefix.setter
    def attached_files_url_prefix(self, value : str):
        ...
    
    @property
    def default_font_name(self) -> str:
        ...
    
    @default_font_name.setter
    def default_font_name(self, value : str):
        ...
    
    @property
    def worksheet_scalable(self) -> bool:
        ...
    
    @worksheet_scalable.setter
    def worksheet_scalable(self, value : bool):
        ...
    
    @property
    def is_export_comments(self) -> bool:
        ...
    
    @is_export_comments.setter
    def is_export_comments(self, value : bool):
        ...
    
    @property
    def export_comments_type(self) -> aspose.cells.PrintCommentsType:
        ...
    
    @export_comments_type.setter
    def export_comments_type(self, value : aspose.cells.PrintCommentsType):
        ...
    
    @property
    def disable_downlevel_revealed_comments(self) -> bool:
        ...
    
    @disable_downlevel_revealed_comments.setter
    def disable_downlevel_revealed_comments(self, value : bool):
        ...
    
    @property
    def is_exp_image_to_temp_dir(self) -> bool:
        ...
    
    @is_exp_image_to_temp_dir.setter
    def is_exp_image_to_temp_dir(self, value : bool):
        ...
    
    @property
    def image_scalable(self) -> bool:
        ...
    
    @image_scalable.setter
    def image_scalable(self, value : bool):
        ...
    
    @property
    def width_scalable(self) -> bool:
        ...
    
    @width_scalable.setter
    def width_scalable(self, value : bool):
        ...
    
    @property
    def export_single_tab(self) -> bool:
        ...
    
    @export_single_tab.setter
    def export_single_tab(self, value : bool):
        ...
    
    @property
    def export_images_as_base64(self) -> bool:
        ...
    
    @export_images_as_base64.setter
    def export_images_as_base64(self, value : bool):
        ...
    
    @property
    def export_active_worksheet_only(self) -> bool:
        ...
    
    @export_active_worksheet_only.setter
    def export_active_worksheet_only(self, value : bool):
        ...
    
    @property
    def export_print_area_only(self) -> bool:
        ...
    
    @export_print_area_only.setter
    def export_print_area_only(self, value : bool):
        ...
    
    @property
    def export_area(self) -> aspose.cells.CellArea:
        ...
    
    @export_area.setter
    def export_area(self, value : aspose.cells.CellArea):
        ...
    
    @property
    def parse_html_tag_in_cell(self) -> bool:
        ...
    
    @parse_html_tag_in_cell.setter
    def parse_html_tag_in_cell(self, value : bool):
        ...
    
    @property
    def html_cross_string_type(self) -> aspose.cells.HtmlCrossType:
        ...
    
    @html_cross_string_type.setter
    def html_cross_string_type(self, value : aspose.cells.HtmlCrossType):
        ...
    
    @property
    def hidden_col_display_type(self) -> aspose.cells.HtmlHiddenColDisplayType:
        ...
    
    @hidden_col_display_type.setter
    def hidden_col_display_type(self, value : aspose.cells.HtmlHiddenColDisplayType):
        ...
    
    @property
    def hidden_row_display_type(self) -> aspose.cells.HtmlHiddenRowDisplayType:
        ...
    
    @hidden_row_display_type.setter
    def hidden_row_display_type(self, value : aspose.cells.HtmlHiddenRowDisplayType):
        ...
    
    @property
    def encoding(self) -> System.Text.Encoding:
        '''If not set,use Encoding.UTF8 as default enconding type.'''
        ...
    
    @encoding.setter
    def encoding(self, value : System.Text.Encoding):
        '''If not set,use Encoding.UTF8 as default enconding type.'''
        ...
    
    @property
    def export_object_listener(self) -> aspose.cells.IExportObjectListener:
        ...
    
    @export_object_listener.setter
    def export_object_listener(self, value : aspose.cells.IExportObjectListener):
        ...
    
    @property
    def file_path_provider(self) -> aspose.cells.IFilePathProvider:
        ...
    
    @file_path_provider.setter
    def file_path_provider(self, value : aspose.cells.IFilePathProvider):
        ...
    
    @property
    def stream_provider(self) -> aspose.cells.IStreamProvider:
        ...
    
    @stream_provider.setter
    def stream_provider(self, value : aspose.cells.IStreamProvider):
        ...
    
    @property
    def image_options(self) -> aspose.cells.rendering.ImageOrPrintOptions:
        ...
    
    @property
    def save_as_single_file(self) -> bool:
        ...
    
    @save_as_single_file.setter
    def save_as_single_file(self, value : bool):
        ...
    
    @property
    def show_all_sheets(self) -> bool:
        ...
    
    @show_all_sheets.setter
    def show_all_sheets(self, value : bool):
        ...
    
    @property
    def export_page_headers(self) -> bool:
        ...
    
    @export_page_headers.setter
    def export_page_headers(self, value : bool):
        ...
    
    @property
    def export_page_footers(self) -> bool:
        ...
    
    @export_page_footers.setter
    def export_page_footers(self, value : bool):
        ...
    
    @property
    def export_hidden_worksheet(self) -> bool:
        ...
    
    @export_hidden_worksheet.setter
    def export_hidden_worksheet(self, value : bool):
        ...
    
    @property
    def presentation_preference(self) -> bool:
        ...
    
    @presentation_preference.setter
    def presentation_preference(self, value : bool):
        ...
    
    @property
    def cell_css_prefix(self) -> str:
        ...
    
    @cell_css_prefix.setter
    def cell_css_prefix(self, value : str):
        ...
    
    @property
    def table_css_id(self) -> str:
        ...
    
    @table_css_id.setter
    def table_css_id(self, value : str):
        ...
    
    @property
    def is_full_path_link(self) -> bool:
        ...
    
    @is_full_path_link.setter
    def is_full_path_link(self, value : bool):
        ...
    
    @property
    def export_worksheet_css_separately(self) -> bool:
        ...
    
    @export_worksheet_css_separately.setter
    def export_worksheet_css_separately(self, value : bool):
        ...
    
    @property
    def export_similar_border_style(self) -> bool:
        ...
    
    @export_similar_border_style.setter
    def export_similar_border_style(self, value : bool):
        ...
    
    @property
    def merge_empty_td_forcely(self) -> bool:
        ...
    
    @merge_empty_td_forcely.setter
    def merge_empty_td_forcely(self, value : bool):
        ...
    
    @property
    def export_cell_coordinate(self) -> bool:
        ...
    
    @export_cell_coordinate.setter
    def export_cell_coordinate(self, value : bool):
        ...
    
    @property
    def export_extra_headings(self) -> bool:
        ...
    
    @export_extra_headings.setter
    def export_extra_headings(self, value : bool):
        ...
    
    @property
    def export_headings(self) -> bool:
        ...
    
    @export_headings.setter
    def export_headings(self, value : bool):
        ...
    
    @property
    def export_row_column_headings(self) -> bool:
        ...
    
    @export_row_column_headings.setter
    def export_row_column_headings(self, value : bool):
        ...
    
    @property
    def export_formula(self) -> bool:
        ...
    
    @export_formula.setter
    def export_formula(self, value : bool):
        ...
    
    @property
    def add_tooltip_text(self) -> bool:
        ...
    
    @add_tooltip_text.setter
    def add_tooltip_text(self, value : bool):
        ...
    
    @property
    def export_grid_lines(self) -> bool:
        ...
    
    @export_grid_lines.setter
    def export_grid_lines(self, value : bool):
        ...
    
    @property
    def export_bogus_row_data(self) -> bool:
        ...
    
    @export_bogus_row_data.setter
    def export_bogus_row_data(self, value : bool):
        ...
    
    @property
    def exclude_unused_styles(self) -> bool:
        ...
    
    @exclude_unused_styles.setter
    def exclude_unused_styles(self, value : bool):
        ...
    
    @property
    def export_document_properties(self) -> bool:
        ...
    
    @export_document_properties.setter
    def export_document_properties(self, value : bool):
        ...
    
    @property
    def export_worksheet_properties(self) -> bool:
        ...
    
    @export_worksheet_properties.setter
    def export_worksheet_properties(self, value : bool):
        ...
    
    @property
    def export_workbook_properties(self) -> bool:
        ...
    
    @export_workbook_properties.setter
    def export_workbook_properties(self, value : bool):
        ...
    
    @property
    def export_frame_scripts_and_properties(self) -> bool:
        ...
    
    @export_frame_scripts_and_properties.setter
    def export_frame_scripts_and_properties(self, value : bool):
        ...
    
    @property
    def export_data_options(self) -> aspose.cells.HtmlExportDataOptions:
        ...
    
    @export_data_options.setter
    def export_data_options(self, value : aspose.cells.HtmlExportDataOptions):
        ...
    
    @property
    def link_target_type(self) -> aspose.cells.HtmlLinkTargetType:
        ...
    
    @link_target_type.setter
    def link_target_type(self, value : aspose.cells.HtmlLinkTargetType):
        ...
    
    @property
    def is_ie_compatible(self) -> bool:
        ...
    
    @is_ie_compatible.setter
    def is_ie_compatible(self, value : bool):
        ...
    
    ...

class SqlScriptColumnTypeMap:
    '''Represents column type map.'''
    
    def get_string_type(self) -> str:
        '''Gets string type in the database.'''
        ...
    
    def get_numberic_type(self) -> str:
        '''Gets numeric type in the database.'''
        ...
    
    ...

class SqlScriptSaveOptions(aspose.cells.SaveOptions):
    '''Represents the options of saving sql.'''
    
    @property
    def save_format(self) -> aspose.cells.SaveFormat:
        ...
    
    @property
    def clear_data(self) -> bool:
        ...
    
    @clear_data.setter
    def clear_data(self, value : bool):
        ...
    
    @property
    def cached_file_folder(self) -> str:
        ...
    
    @cached_file_folder.setter
    def cached_file_folder(self, value : str):
        ...
    
    @property
    def validate_merged_areas(self) -> bool:
        ...
    
    @validate_merged_areas.setter
    def validate_merged_areas(self, value : bool):
        ...
    
    @property
    def merge_areas(self) -> bool:
        ...
    
    @merge_areas.setter
    def merge_areas(self, value : bool):
        ...
    
    @property
    def create_directory(self) -> bool:
        ...
    
    @create_directory.setter
    def create_directory(self, value : bool):
        ...
    
    @property
    def sort_names(self) -> bool:
        ...
    
    @sort_names.setter
    def sort_names(self, value : bool):
        ...
    
    @property
    def sort_external_names(self) -> bool:
        ...
    
    @sort_external_names.setter
    def sort_external_names(self, value : bool):
        ...
    
    @property
    def refresh_chart_cache(self) -> bool:
        ...
    
    @refresh_chart_cache.setter
    def refresh_chart_cache(self, value : bool):
        ...
    
    @property
    def warning_callback(self) -> aspose.cells.IWarningCallback:
        ...
    
    @warning_callback.setter
    def warning_callback(self, value : aspose.cells.IWarningCallback):
        ...
    
    @property
    def update_smart_art(self) -> bool:
        ...
    
    @update_smart_art.setter
    def update_smart_art(self, value : bool):
        ...
    
    @property
    def check_if_table_exists(self) -> bool:
        ...
    
    @check_if_table_exists.setter
    def check_if_table_exists(self, value : bool):
        ...
    
    @property
    def column_type_map(self) -> aspose.cells.saving.SqlScriptColumnTypeMap:
        ...
    
    @column_type_map.setter
    def column_type_map(self, value : aspose.cells.saving.SqlScriptColumnTypeMap):
        ...
    
    @property
    def check_all_data_for_column_type(self) -> bool:
        ...
    
    @check_all_data_for_column_type.setter
    def check_all_data_for_column_type(self, value : bool):
        ...
    
    @property
    def add_blank_line_between_rows(self) -> bool:
        ...
    
    @add_blank_line_between_rows.setter
    def add_blank_line_between_rows(self, value : bool):
        ...
    
    @property
    def separator(self) -> char:
        '''Gets and sets character separator of sql script.'''
        ...
    
    @separator.setter
    def separator(self, value : char):
        '''Gets and sets character separator of sql script.'''
        ...
    
    @property
    def operator_type(self) -> aspose.cells.saving.SqlScriptOperatorType:
        ...
    
    @operator_type.setter
    def operator_type(self, value : aspose.cells.saving.SqlScriptOperatorType):
        ...
    
    @property
    def primary_key(self) -> int:
        ...
    
    @primary_key.setter
    def primary_key(self, value : int):
        ...
    
    @property
    def create_table(self) -> bool:
        ...
    
    @create_table.setter
    def create_table(self, value : bool):
        ...
    
    @property
    def id_name(self) -> str:
        ...
    
    @id_name.setter
    def id_name(self, value : str):
        ...
    
    @property
    def start_id(self) -> int:
        ...
    
    @start_id.setter
    def start_id(self, value : int):
        ...
    
    @property
    def table_name(self) -> str:
        ...
    
    @table_name.setter
    def table_name(self, value : str):
        ...
    
    @property
    def export_as_string(self) -> bool:
        ...
    
    @export_as_string.setter
    def export_as_string(self, value : bool):
        ...
    
    @property
    def sheet_indexes(self) -> List[int]:
        ...
    
    @sheet_indexes.setter
    def sheet_indexes(self, value : List[int]):
        ...
    
    @property
    def export_area(self) -> aspose.cells.CellArea:
        ...
    
    @export_area.setter
    def export_area(self, value : aspose.cells.CellArea):
        ...
    
    @property
    def has_header_row(self) -> bool:
        ...
    
    @has_header_row.setter
    def has_header_row(self, value : bool):
        ...
    
    ...

class SqlScriptOperatorType:
    '''Represents the type of operating data.'''
    
    @classmethod
    @property
    def INSERT(cls) -> SqlScriptOperatorType:
        '''Insert data.'''
        ...
    
    @classmethod
    @property
    def UPDATE(cls) -> SqlScriptOperatorType:
        '''Update data.'''
        ...
    
    @classmethod
    @property
    def DELETE(cls) -> SqlScriptOperatorType:
        '''Delete data.'''
        ...
    
    ...

