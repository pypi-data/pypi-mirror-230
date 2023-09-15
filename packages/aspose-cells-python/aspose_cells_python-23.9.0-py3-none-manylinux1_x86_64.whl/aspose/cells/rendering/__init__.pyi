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

class DrawObject:
    '''DrawObject will be initialized and returned when rendering.'''
    
    @property
    def cell(self) -> aspose.cells.Cell:
        '''Indicates the Cell object when rendering.
        All properties of cell can be accessed.'''
        ...
    
    @property
    def shape(self) -> aspose.cells.drawing.Shape:
        '''Indicates the Shape object when rendering.
        All properties of shape can be accessed.'''
        ...
    
    @property
    def image_bytes(self) -> bytes:
        ...
    
    @property
    def type(self) -> aspose.cells.rendering.DrawObjectEnum:
        '''Indicates the type of DrawObject.'''
        ...
    
    @property
    def current_page(self) -> int:
        ...
    
    @property
    def total_pages(self) -> int:
        ...
    
    @property
    def sheet_index(self) -> int:
        ...
    
    ...

class DrawObjectEventHandler:
    '''Interface to get DrawObject and Bound when rendering.'''
    
    def draw(self, draw_object : aspose.cells.rendering.DrawObject, x : float, y : float, width : float, height : float):
        '''Implements this interface to get DrawObject and Bound when rendering.
        
        :param draw_object: DrawObject will be initialized and returned when rendering
        :param x: Left of DrawObject
        :param y: Top of DrawObject
        :param width: Width of DrawObject
        :param height: Height of DrawObject'''
        ...
    
    ...

class IPageSavingCallback:
    '''Control/Indicate progress of page saving process.'''
    
    def page_start_saving(self, args : aspose.cells.rendering.PageStartSavingArgs):
        '''Control/Indicate a page starts to be output.
        
        :param args: Info for a page starts saving process.'''
        ...
    
    def page_end_saving(self, args : aspose.cells.rendering.PageEndSavingArgs):
        '''Control/Indicate a page ends to be output.
        
        :param args: Info for a page ends saving process.'''
        ...
    
    ...

class ImageOrPrintOptions:
    '''Allows to specify options when rendering worksheet to images, printing worksheet or rendering chart to image.'''
    
    @overload
    def set_desired_size(self, desired_width : int, desired_height : int):
        '''Sets desired width and height of image.
        
        :param desired_width: desired width in pixels
        :param desired_height: desired height in pixels'''
        ...
    
    @overload
    def set_desired_size(self, desired_width : int, desired_height : int, keep_aspect_ratio : bool):
        '''Sets desired width and height of image.
        
        :param desired_width: desired width in pixels
        :param desired_height: desired height in pixels
        :param keep_aspect_ratio: whether to keep aspect ratio of origin image'''
        ...
    
    @property
    def save_format(self) -> aspose.cells.SaveFormat:
        ...
    
    @save_format.setter
    def save_format(self, value : aspose.cells.SaveFormat):
        ...
    
    @property
    def print_with_status_dialog(self) -> bool:
        ...
    
    @print_with_status_dialog.setter
    def print_with_status_dialog(self, value : bool):
        ...
    
    @property
    def horizontal_resolution(self) -> int:
        ...
    
    @horizontal_resolution.setter
    def horizontal_resolution(self, value : int):
        ...
    
    @property
    def vertical_resolution(self) -> int:
        ...
    
    @vertical_resolution.setter
    def vertical_resolution(self, value : int):
        ...
    
    @property
    def tiff_compression(self) -> aspose.cells.rendering.TiffCompression:
        ...
    
    @tiff_compression.setter
    def tiff_compression(self, value : aspose.cells.rendering.TiffCompression):
        ...
    
    @property
    def tiff_color_depth(self) -> aspose.cells.rendering.ColorDepth:
        ...
    
    @tiff_color_depth.setter
    def tiff_color_depth(self, value : aspose.cells.rendering.ColorDepth):
        ...
    
    @property
    def tiff_binarization_method(self) -> aspose.cells.rendering.ImageBinarizationMethod:
        ...
    
    @tiff_binarization_method.setter
    def tiff_binarization_method(self, value : aspose.cells.rendering.ImageBinarizationMethod):
        ...
    
    @property
    def printing_page(self) -> aspose.cells.PrintingPageType:
        ...
    
    @printing_page.setter
    def printing_page(self, value : aspose.cells.PrintingPageType):
        ...
    
    @property
    def quality(self) -> int:
        '''Gets a value determining the quality of the generated  images
        to apply only when saving pages to the ``Jpeg`` format. The default value is 100'''
        ...
    
    @quality.setter
    def quality(self, value : int):
        '''Sets a value determining the quality of the generated  images
        to apply only when saving pages to the ``Jpeg`` format. The default value is 100'''
        ...
    
    @property
    def image_type(self) -> aspose.cells.drawing.ImageType:
        ...
    
    @image_type.setter
    def image_type(self, value : aspose.cells.drawing.ImageType):
        ...
    
    @property
    def is_cell_auto_fit(self) -> bool:
        ...
    
    @is_cell_auto_fit.setter
    def is_cell_auto_fit(self, value : bool):
        ...
    
    @property
    def one_page_per_sheet(self) -> bool:
        ...
    
    @one_page_per_sheet.setter
    def one_page_per_sheet(self, value : bool):
        ...
    
    @property
    def all_columns_in_one_page_per_sheet(self) -> bool:
        ...
    
    @all_columns_in_one_page_per_sheet.setter
    def all_columns_in_one_page_per_sheet(self, value : bool):
        ...
    
    @property
    def draw_object_event_handler(self) -> aspose.cells.rendering.DrawObjectEventHandler:
        ...
    
    @draw_object_event_handler.setter
    def draw_object_event_handler(self, value : aspose.cells.rendering.DrawObjectEventHandler):
        ...
    
    @property
    def chart_image_type(self) -> aspose.pydrawing.imaging.ImageFormat:
        ...
    
    @chart_image_type.setter
    def chart_image_type(self, value : aspose.pydrawing.imaging.ImageFormat):
        ...
    
    @property
    def embeded_image_name_in_svg(self) -> str:
        ...
    
    @embeded_image_name_in_svg.setter
    def embeded_image_name_in_svg(self, value : str):
        ...
    
    @property
    def svg_fit_to_view_port(self) -> bool:
        ...
    
    @svg_fit_to_view_port.setter
    def svg_fit_to_view_port(self, value : bool):
        ...
    
    @property
    def only_area(self) -> bool:
        ...
    
    @only_area.setter
    def only_area(self, value : bool):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.pydrawing.text.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.pydrawing.text.TextRenderingHint):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.pydrawing.drawing2d.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.pydrawing.drawing2d.SmoothingMode):
        ...
    
    @property
    def transparent(self) -> bool:
        '''Indicates if the background of generated image should be transparent.'''
        ...
    
    @transparent.setter
    def transparent(self, value : bool):
        '''Indicates if the background of generated image should be transparent.'''
        ...
    
    @property
    def pixel_format(self) -> aspose.pydrawing.imaging.PixelFormat:
        ...
    
    @pixel_format.setter
    def pixel_format(self, value : aspose.pydrawing.imaging.PixelFormat):
        ...
    
    @property
    def warning_callback(self) -> aspose.cells.IWarningCallback:
        ...
    
    @warning_callback.setter
    def warning_callback(self, value : aspose.cells.IWarningCallback):
        ...
    
    @property
    def page_saving_callback(self) -> aspose.cells.rendering.IPageSavingCallback:
        ...
    
    @page_saving_callback.setter
    def page_saving_callback(self, value : aspose.cells.rendering.IPageSavingCallback):
        ...
    
    @property
    def is_font_substitution_char_granularity(self) -> bool:
        ...
    
    @is_font_substitution_char_granularity.setter
    def is_font_substitution_char_granularity(self, value : bool):
        ...
    
    @property
    def page_index(self) -> int:
        ...
    
    @page_index.setter
    def page_index(self, value : int):
        ...
    
    @property
    def page_count(self) -> int:
        ...
    
    @page_count.setter
    def page_count(self, value : int):
        ...
    
    @property
    def is_optimized(self) -> bool:
        ...
    
    @is_optimized.setter
    def is_optimized(self, value : bool):
        ...
    
    @property
    def default_font(self) -> str:
        ...
    
    @default_font.setter
    def default_font(self, value : str):
        ...
    
    @property
    def check_workbook_default_font(self) -> bool:
        ...
    
    @check_workbook_default_font.setter
    def check_workbook_default_font(self, value : bool):
        ...
    
    @property
    def output_blank_page_when_nothing_to_print(self) -> bool:
        ...
    
    @output_blank_page_when_nothing_to_print.setter
    def output_blank_page_when_nothing_to_print(self, value : bool):
        ...
    
    @property
    def gridline_type(self) -> aspose.cells.GridlineType:
        ...
    
    @gridline_type.setter
    def gridline_type(self, value : aspose.cells.GridlineType):
        ...
    
    @property
    def text_cross_type(self) -> aspose.cells.TextCrossType:
        ...
    
    @text_cross_type.setter
    def text_cross_type(self, value : aspose.cells.TextCrossType):
        ...
    
    @property
    def emf_type(self) -> aspose.pydrawing.imaging.EmfType:
        ...
    
    @emf_type.setter
    def emf_type(self, value : aspose.pydrawing.imaging.EmfType):
        ...
    
    @property
    def default_edit_language(self) -> aspose.cells.DefaultEditLanguage:
        ...
    
    @default_edit_language.setter
    def default_edit_language(self, value : aspose.cells.DefaultEditLanguage):
        ...
    
    @property
    def sheet_set(self) -> aspose.cells.rendering.SheetSet:
        ...
    
    @sheet_set.setter
    def sheet_set(self, value : aspose.cells.rendering.SheetSet):
        ...
    
    ...

class PageEndSavingArgs(PageSavingArgs):
    '''Info for a page ends saving process.'''
    
    @property
    def page_index(self) -> int:
        ...
    
    @property
    def page_count(self) -> int:
        ...
    
    @property
    def has_more_pages(self) -> bool:
        ...
    
    @has_more_pages.setter
    def has_more_pages(self, value : bool):
        ...
    
    ...

class PageSavingArgs:
    '''Info for a page saving process.'''
    
    @property
    def page_index(self) -> int:
        ...
    
    @property
    def page_count(self) -> int:
        ...
    
    ...

class PageStartSavingArgs(PageSavingArgs):
    '''Info for a page starts saving process.'''
    
    @property
    def page_index(self) -> int:
        ...
    
    @property
    def page_count(self) -> int:
        ...
    
    @property
    def is_to_output(self) -> bool:
        ...
    
    @is_to_output.setter
    def is_to_output(self, value : bool):
        ...
    
    ...

class PdfBookmarkEntry:
    '''PdfBookmarkEntry is an entry in pdf bookmark.
    if Text property of current instance is null or "",
    current instance will be hidden and children will be inserted on current level.'''
    
    @property
    def text(self) -> str:
        '''Title of a bookmark.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Title of a bookmark.'''
        ...
    
    @property
    def destination(self) -> aspose.cells.Cell:
        '''The cell to which the bookmark link.'''
        ...
    
    @destination.setter
    def destination(self, value : aspose.cells.Cell):
        '''The cell to which the bookmark link.'''
        ...
    
    @property
    def destination_name(self) -> str:
        ...
    
    @destination_name.setter
    def destination_name(self, value : str):
        ...
    
    @property
    def sub_entry(self) -> list:
        ...
    
    @sub_entry.setter
    def sub_entry(self, value : list):
        ...
    
    @property
    def is_open(self) -> bool:
        ...
    
    @is_open.setter
    def is_open(self, value : bool):
        ...
    
    @property
    def is_collapse(self) -> bool:
        ...
    
    @is_collapse.setter
    def is_collapse(self, value : bool):
        ...
    
    ...

class RenderingFont:
    '''Font for rendering.'''
    
    @property
    def name(self) -> str:
        '''Gets name of the font.'''
        ...
    
    @property
    def size(self) -> float:
        '''Gets size of the font in points.'''
        ...
    
    @property
    def bold(self) -> bool:
        '''Gets bold for the font.'''
        ...
    
    @bold.setter
    def bold(self, value : bool):
        '''Sets bold for the font.'''
        ...
    
    @property
    def italic(self) -> bool:
        '''Gets italic for the font.'''
        ...
    
    @italic.setter
    def italic(self, value : bool):
        '''Sets italic for the font.'''
        ...
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Gets color for the font.'''
        ...
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color):
        '''Sets color for the font.'''
        ...
    
    ...

class RenderingWatermark:
    '''Watermark for rendering.'''
    
    @property
    def rotation(self) -> float:
        '''Gets roation of the watermark in degrees.'''
        ...
    
    @rotation.setter
    def rotation(self, value : float):
        '''Sets roation of the watermark in degrees.'''
        ...
    
    @property
    def scale_to_page_percent(self) -> int:
        ...
    
    @scale_to_page_percent.setter
    def scale_to_page_percent(self, value : int):
        ...
    
    @property
    def opacity(self) -> float:
        '''Gets opacity of the watermark in range [0, 1].'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets opacity of the watermark in range [0, 1].'''
        ...
    
    @property
    def is_background(self) -> bool:
        ...
    
    @is_background.setter
    def is_background(self, value : bool):
        ...
    
    @property
    def text(self) -> str:
        '''Gets text of the watermark.'''
        ...
    
    @property
    def font(self) -> aspose.cells.rendering.RenderingFont:
        '''Gets font of the watermark.'''
        ...
    
    @property
    def image(self) -> bytes:
        '''Gets image of the watermark.'''
        ...
    
    @property
    def h_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @h_alignment.setter
    def h_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def v_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @v_alignment.setter
    def v_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def offset_x(self) -> float:
        ...
    
    @offset_x.setter
    def offset_x(self, value : float):
        ...
    
    @property
    def offset_y(self) -> float:
        ...
    
    @offset_y.setter
    def offset_y(self, value : float):
        ...
    
    ...

class SheetPrintingPreview:
    '''Worksheet printing preview.'''
    
    @property
    def evaluated_page_count(self) -> int:
        ...
    
    ...

class SheetRender:
    '''Represents a worksheet render which can render worksheet to various images such as (BMP, PNG, JPEG, TIFF..)
    The constructor of this class , must be used after modification of pagesetup, cell style.'''
    
    @overload
    def to_image(self, page_index : int, file_name : str):
        '''Render certain page to a file.
        
        :param page_index: indicate which page is to be converted
        :param file_name: filename of the output image'''
        ...
    
    @overload
    def to_image(self, page_index : int, stream : io.RawIOBase):
        '''Render certain page to a stream.
        
        :param page_index: indicate which page is to be converted
        :param stream: the stream of the output image'''
        ...
    
    @overload
    def to_tiff(self, stream : io.RawIOBase):
        '''Render whole worksheet as Tiff Image to stream.
        
        :param stream: the stream of the output image'''
        ...
    
    @overload
    def to_tiff(self, filename : str):
        '''Render whole worksheet as Tiff Image to a file.
        
        :param filename: the filename of the output image'''
        ...
    
    @overload
    def to_printer(self, printer_name : str):
        '''Render worksheet to Printer
        
        :param printer_name: the name of the printer , for example: "Microsoft Office Document Image Writer"'''
        ...
    
    @overload
    def to_printer(self, printer_name : str, job_name : str):
        '''Render worksheet to Printer
        
        :param printer_name: the name of the printer , for example: "Microsoft Office Document Image Writer"
        :param job_name: set the print job name'''
        ...
    
    @overload
    def to_printer(self, printer_settings : aspose.pydrawing.printing.PrinterSettings):
        '''Render worksheet to Printer
        
        :param printer_settings: the settings of printer, e.g. PrinterName, Duplex'''
        ...
    
    @overload
    def to_printer(self, printer_settings : aspose.pydrawing.printing.PrinterSettings, job_name : str):
        '''Render worksheet to Printer
        
        :param printer_settings: the settings of printer, e.g. PrinterName, Duplex
        :param job_name: set the print job name'''
        ...
    
    @overload
    def to_printer(self, printer_name : str, print_page_index : int, print_page_count : int):
        '''Render worksheet to Printer
        
        :param printer_name: the name of the printer , for example: "Microsoft Office Document Image Writer"
        :param print_page_index: the 0-based index of the first page to print, it must be in Range [0, SheetRender.PageCount-1]
        :param print_page_count: the number of pages to print, it must be greater than zero'''
        ...
    
    def get_page_size_inch(self, page_index : int) -> List[float]:
        '''Get page size in inch of output image.
        
        :param page_index: The page index is based on zero.
        :returns: Page size of image, [0] for width and [1] for height'''
        ...
    
    def custom_print(self, next_page_after_print : bool, print_page_event_args : aspose.pydrawing.printing.PrintPageEventArgs) -> int:
        '''Client can control page setting of printer when print each page using this function.
        
        :param next_page_after_print: If true , printer will go to next page after print current page
        :param print_page_event_args: System.Drawing.Printing.PrintPageEventArgs
        :returns: Indirect next page index,  based on zero'''
        ...
    
    def dispose(self):
        '''Releases resources created and used for rendering.'''
        ...
    
    @property
    def page_count(self) -> int:
        ...
    
    @property
    def page_scale(self) -> float:
        ...
    
    ...

class SheetSet:
    '''Describes a set of sheets.'''
    
    @classmethod
    @property
    def active(cls) -> aspose.cells.rendering.SheetSet:
        '''Gets a set with active sheet of the workbook.'''
        ...
    
    @classmethod
    @property
    def visible(cls) -> aspose.cells.rendering.SheetSet:
        '''Gets a set with visible sheets of the workbook in their original order.'''
        ...
    
    @classmethod
    @property
    def all(cls) -> aspose.cells.rendering.SheetSet:
        '''Gets a set with all sheets of the workbook in their original order.'''
        ...
    
    ...

class WorkbookPrintingPreview:
    '''Workbook printing preview.'''
    
    @property
    def evaluated_page_count(self) -> int:
        ...
    
    ...

class WorkbookRender:
    '''Represents a Workbook render.
    The constructor of this class , must be used after modification of pagesetup, cell style.'''
    
    @overload
    def to_image(self, stream : io.RawIOBase):
        '''Render whole workbook as Tiff Image to stream.
        
        :param stream: the stream of the output image'''
        ...
    
    @overload
    def to_image(self, filename : str):
        '''Render whole workbook as Tiff Image to a file.
        
        :param filename: the filename of the output image'''
        ...
    
    @overload
    def to_image(self, page_index : int, file_name : str):
        '''Render certain page to a file.
        
        :param page_index: indicate which page is to be converted
        :param file_name: filename of the output image'''
        ...
    
    @overload
    def to_image(self, page_index : int, stream : io.RawIOBase):
        '''Render certain page to a stream.
        
        :param page_index: indicate which page is to be converted
        :param stream: the stream of the output image'''
        ...
    
    @overload
    def to_printer(self, printer_name : str):
        '''Render workbook to Printer
        
        :param printer_name: the name of the printer , for example: "Microsoft Office Document Image Writer"'''
        ...
    
    @overload
    def to_printer(self, printer_name : str, job_name : str):
        '''Render workbook to Printer
        
        :param printer_name: the name of the printer , for example: "Microsoft Office Document Image Writer"
        :param job_name: set the print job name'''
        ...
    
    @overload
    def to_printer(self, printer_settings : aspose.pydrawing.printing.PrinterSettings):
        '''Render workbook to Printer
        
        :param printer_settings: the settings of printer, e.g. PrinterName, Duplex'''
        ...
    
    @overload
    def to_printer(self, printer_settings : aspose.pydrawing.printing.PrinterSettings, job_name : str):
        '''Render workbook to Printer
        
        :param printer_settings: the settings of printer, e.g. PrinterName, Duplex
        :param job_name: set the print job name'''
        ...
    
    @overload
    def to_printer(self, printer_name : str, print_page_index : int, print_page_count : int):
        '''Render workbook to Printer
        
        :param printer_name: the name of the printer , for example: "Microsoft Office Document Image Writer"
        :param print_page_index: the 0-based index of the first page to print, it must be in Range [0, WorkbookRender.PageCount-1]
        :param print_page_count: the number of pages to print, it must be greater than zero'''
        ...
    
    def get_page_size_inch(self, page_index : int) -> List[float]:
        '''Get page size in inch of output image.
        
        :param page_index: The page index is based on zero.
        :returns: Page size of image, [0] for width and [1] for height'''
        ...
    
    def custom_print(self, next_page_after_print : bool, print_page_event_args : aspose.pydrawing.printing.PrintPageEventArgs) -> int:
        '''Client can control page setting of printer when print each page using this function.
        
        :param next_page_after_print: If true , printer will go to next page after print current page
        :param print_page_event_args: System.Drawing.Printing.PrintPageEventArgs
        :returns: Indirect next page index,  based on zero'''
        ...
    
    def dispose(self):
        '''Releases resources created and used for rendering.'''
        ...
    
    @property
    def page_count(self) -> int:
        ...
    
    ...

class ColorDepth:
    '''Enumerates Bit Depth Type for tiff image.'''
    
    @classmethod
    @property
    def DEFAULT(cls) -> ColorDepth:
        '''Default value, not set value.'''
        ...
    
    @classmethod
    @property
    def FORMAT_1BPP(cls) -> ColorDepth:
        '''1 bit per pixel'''
        ...
    
    @classmethod
    @property
    def FORMAT_4BPP(cls) -> ColorDepth:
        '''4 bits per pixel'''
        ...
    
    @classmethod
    @property
    def FORMAT_8BPP(cls) -> ColorDepth:
        '''8 bits per pixel'''
        ...
    
    @classmethod
    @property
    def FORMAT_24BPP(cls) -> ColorDepth:
        '''24 bits per pixel'''
        ...
    
    @classmethod
    @property
    def FORMAT_32BPP(cls) -> ColorDepth:
        '''32 bits per pixel'''
        ...
    
    ...

class CommentTitleType:
    '''Represents comment title type while rendering when comment is set to display at end of sheet.'''
    
    @classmethod
    @property
    def CELL(cls) -> CommentTitleType:
        '''Represents comment title cell.'''
        ...
    
    @classmethod
    @property
    def COMMENT(cls) -> CommentTitleType:
        '''Represents comment title comment.'''
        ...
    
    @classmethod
    @property
    def NOTE(cls) -> CommentTitleType:
        '''Represents comment title note.'''
        ...
    
    @classmethod
    @property
    def REPLY(cls) -> CommentTitleType:
        '''Represents comment title reply.'''
        ...
    
    ...

class DrawObjectEnum:
    '''Indicate Cell or Image of DrawObject.'''
    
    @classmethod
    @property
    def IMAGE(cls) -> DrawObjectEnum:
        '''Indicate DrawObject is an Image'''
        ...
    
    @classmethod
    @property
    def CELL(cls) -> DrawObjectEnum:
        '''indicate DrawObject is an Cell'''
        ...
    
    ...

class ImageBinarizationMethod:
    '''Specifies the method used to binarize image.'''
    
    @classmethod
    @property
    def THRESHOLD(cls) -> ImageBinarizationMethod:
        '''Specifies threshold method.'''
        ...
    
    @classmethod
    @property
    def FLOYD_STEINBERG_DITHERING(cls) -> ImageBinarizationMethod:
        '''Specifies dithering using Floyd-Steinberg error diffusion method.'''
        ...
    
    ...

class PdfCompliance:
    '''Allowing user to set PDF conversion's Compatibility'''
    
    @classmethod
    @property
    def NONE(cls) -> PdfCompliance:
        '''Normal pdf format'''
        ...
    
    @classmethod
    @property
    def PDF_A1B(cls) -> PdfCompliance:
        '''Pdf format compatible with PDFA-1b'''
        ...
    
    @classmethod
    @property
    def PDF_A1A(cls) -> PdfCompliance:
        '''Pdf format compatible with PDFA-1a'''
        ...
    
    ...

class PdfCompressionCore:
    '''Specifies a type of compression applied to all content in the PDF file except images.'''
    
    @classmethod
    @property
    def NONE(cls) -> PdfCompressionCore:
        '''None'''
        ...
    
    @classmethod
    @property
    def RLE(cls) -> PdfCompressionCore:
        '''Rle'''
        ...
    
    @classmethod
    @property
    def LZW(cls) -> PdfCompressionCore:
        '''Lzw'''
        ...
    
    @classmethod
    @property
    def FLATE(cls) -> PdfCompressionCore:
        '''Flate'''
        ...
    
    ...

class PdfCustomPropertiesExport:
    '''Specifies the way :py:class:`aspose.cells.properties.CustomDocumentPropertyCollection` are exported to PDF file.'''
    
    @classmethod
    @property
    def NONE(cls) -> PdfCustomPropertiesExport:
        '''No custom properties are exported.'''
        ...
    
    @classmethod
    @property
    def STANDARD(cls) -> PdfCustomPropertiesExport:
        '''Custom properties are exported as entries in Info dictionary.'''
        ...
    
    ...

class PdfFontEncoding:
    '''Represents pdf embedded font encoding.'''
    
    @classmethod
    @property
    def IDENTITY(cls) -> PdfFontEncoding:
        '''Represents use Identity-H encoding for all embedded fonts in pdf.'''
        ...
    
    @classmethod
    @property
    def ANSI_PREFER(cls) -> PdfFontEncoding:
        '''Represents prefer to use WinAnsiEncoding for TrueType fonts with characters 32-127,
        otherwise, Identity-H encoding will be used for embedded fonts in pdf.'''
        ...
    
    ...

class PdfOptimizationType:
    '''Specifies a type of optimization.'''
    
    @classmethod
    @property
    def STANDARD(cls) -> PdfOptimizationType:
        '''High print quality'''
        ...
    
    @classmethod
    @property
    def MINIMUM_SIZE(cls) -> PdfOptimizationType:
        '''File size is more important than print quality'''
        ...
    
    ...

class TiffCompression:
    '''Specifies what type of compression to apply when saving images into TIFF format file.'''
    
    @classmethod
    @property
    def COMPRESSION_NONE(cls) -> TiffCompression:
        '''Specifies no compression.'''
        ...
    
    @classmethod
    @property
    def COMPRESSION_RLE(cls) -> TiffCompression:
        '''Specifies the RLE compression scheme.'''
        ...
    
    @classmethod
    @property
    def COMPRESSION_LZW(cls) -> TiffCompression:
        '''Specifies the LZW compression scheme.'''
        ...
    
    @classmethod
    @property
    def COMPRESSION_CCITT3(cls) -> TiffCompression:
        '''Specifies the CCITT3 compression scheme.'''
        ...
    
    @classmethod
    @property
    def COMPRESSION_CCITT4(cls) -> TiffCompression:
        '''Specifies the CCITT4 compression scheme.'''
        ...
    
    ...

