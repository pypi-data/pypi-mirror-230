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

class Axis:
    '''Encapsulates the object that represents an axis of chart.'''
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.Axis.area`.'''
        ...
    
    @property
    def is_automatic_min_value(self) -> bool:
        ...
    
    @is_automatic_min_value.setter
    def is_automatic_min_value(self, value : bool):
        ...
    
    @property
    def min_value(self) -> any:
        ...
    
    @min_value.setter
    def min_value(self, value : any):
        ...
    
    @property
    def is_automatic_max_value(self) -> bool:
        ...
    
    @is_automatic_max_value.setter
    def is_automatic_max_value(self, value : bool):
        ...
    
    @property
    def max_value(self) -> any:
        ...
    
    @max_value.setter
    def max_value(self, value : any):
        ...
    
    @property
    def is_automatic_major_unit(self) -> bool:
        ...
    
    @is_automatic_major_unit.setter
    def is_automatic_major_unit(self, value : bool):
        ...
    
    @property
    def major_unit(self) -> float:
        ...
    
    @major_unit.setter
    def major_unit(self, value : float):
        ...
    
    @property
    def is_automatic_minor_unit(self) -> bool:
        ...
    
    @is_automatic_minor_unit.setter
    def is_automatic_minor_unit(self, value : bool):
        ...
    
    @property
    def minor_unit(self) -> float:
        ...
    
    @minor_unit.setter
    def minor_unit(self, value : float):
        ...
    
    @property
    def axis_line(self) -> aspose.cells.drawing.Line:
        ...
    
    @property
    def major_tick_mark(self) -> aspose.cells.charts.TickMarkType:
        ...
    
    @major_tick_mark.setter
    def major_tick_mark(self, value : aspose.cells.charts.TickMarkType):
        ...
    
    @property
    def minor_tick_mark(self) -> aspose.cells.charts.TickMarkType:
        ...
    
    @minor_tick_mark.setter
    def minor_tick_mark(self, value : aspose.cells.charts.TickMarkType):
        ...
    
    @property
    def tick_label_position(self) -> aspose.cells.charts.TickLabelPositionType:
        ...
    
    @tick_label_position.setter
    def tick_label_position(self, value : aspose.cells.charts.TickLabelPositionType):
        ...
    
    @property
    def cross_at(self) -> float:
        ...
    
    @cross_at.setter
    def cross_at(self, value : float):
        ...
    
    @property
    def cross_type(self) -> aspose.cells.charts.CrossType:
        ...
    
    @cross_type.setter
    def cross_type(self, value : aspose.cells.charts.CrossType):
        ...
    
    @property
    def log_base(self) -> float:
        ...
    
    @log_base.setter
    def log_base(self, value : float):
        ...
    
    @property
    def is_logarithmic(self) -> bool:
        ...
    
    @is_logarithmic.setter
    def is_logarithmic(self, value : bool):
        ...
    
    @property
    def is_plot_order_reversed(self) -> bool:
        ...
    
    @is_plot_order_reversed.setter
    def is_plot_order_reversed(self, value : bool):
        ...
    
    @property
    def axis_between_categories(self) -> bool:
        ...
    
    @axis_between_categories.setter
    def axis_between_categories(self, value : bool):
        ...
    
    @property
    def tick_labels(self) -> aspose.cells.charts.TickLabels:
        ...
    
    @property
    def tick_label_spacing(self) -> int:
        ...
    
    @tick_label_spacing.setter
    def tick_label_spacing(self, value : int):
        ...
    
    @property
    def is_auto_tick_label_spacing(self) -> bool:
        ...
    
    @is_auto_tick_label_spacing.setter
    def is_auto_tick_label_spacing(self, value : bool):
        ...
    
    @property
    def tick_mark_spacing(self) -> int:
        ...
    
    @tick_mark_spacing.setter
    def tick_mark_spacing(self, value : int):
        ...
    
    @property
    def display_unit(self) -> aspose.cells.charts.DisplayUnitType:
        ...
    
    @display_unit.setter
    def display_unit(self, value : aspose.cells.charts.DisplayUnitType):
        ...
    
    @property
    def cust_unit(self) -> int:
        ...
    
    @cust_unit.setter
    def cust_unit(self, value : int):
        ...
    
    @property
    def custom_unit(self) -> int:
        ...
    
    @custom_unit.setter
    def custom_unit(self, value : int):
        ...
    
    @property
    def display_unit_label(self) -> aspose.cells.charts.DisplayUnitLabel:
        ...
    
    @property
    def is_display_unit_label_shown(self) -> bool:
        ...
    
    @is_display_unit_label_shown.setter
    def is_display_unit_label_shown(self, value : bool):
        ...
    
    @property
    def title(self) -> aspose.cells.charts.Title:
        '''Gets the axis' title.'''
        ...
    
    @property
    def category_type(self) -> aspose.cells.charts.CategoryType:
        ...
    
    @category_type.setter
    def category_type(self, value : aspose.cells.charts.CategoryType):
        ...
    
    @property
    def base_unit_scale(self) -> aspose.cells.charts.TimeUnit:
        ...
    
    @base_unit_scale.setter
    def base_unit_scale(self, value : aspose.cells.charts.TimeUnit):
        ...
    
    @property
    def major_unit_scale(self) -> aspose.cells.charts.TimeUnit:
        ...
    
    @major_unit_scale.setter
    def major_unit_scale(self, value : aspose.cells.charts.TimeUnit):
        ...
    
    @property
    def minor_unit_scale(self) -> aspose.cells.charts.TimeUnit:
        ...
    
    @minor_unit_scale.setter
    def minor_unit_scale(self, value : aspose.cells.charts.TimeUnit):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def major_grid_lines(self) -> aspose.cells.drawing.Line:
        ...
    
    @property
    def minor_grid_lines(self) -> aspose.cells.drawing.Line:
        ...
    
    @property
    def has_multi_level_labels(self) -> bool:
        ...
    
    @has_multi_level_labels.setter
    def has_multi_level_labels(self, value : bool):
        ...
    
    @property
    def axis_labels(self) -> list:
        ...
    
    @property
    def bins(self) -> aspose.cells.charts.AxisBins:
        '''Represents bins on a chart(Histogram/Pareto) axis'''
        ...
    
    ...

class AxisBins:
    '''Represents axis bins'''
    
    def reset_overflow(self):
        '''Reset the overflow'''
        ...
    
    def reset_underflow(self):
        '''Reset the underflow'''
        ...
    
    @property
    def is_by_category(self) -> bool:
        ...
    
    @is_by_category.setter
    def is_by_category(self, value : bool):
        ...
    
    @property
    def is_automatic(self) -> bool:
        ...
    
    @is_automatic.setter
    def is_automatic(self, value : bool):
        ...
    
    @property
    def width(self) -> float:
        '''Gets the width of axis bin'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the width of axis bin'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets or set the count of axis bins'''
        ...
    
    @count.setter
    def count(self, value : int):
        '''Set the count of axis bins'''
        ...
    
    @property
    def overflow(self) -> float:
        '''Gets or set the overflow of axis bins'''
        ...
    
    @overflow.setter
    def overflow(self, value : float):
        '''Set the overflow of axis bins'''
        ...
    
    @property
    def underflow(self) -> float:
        '''Gets or set the underflow of axis bins'''
        ...
    
    @underflow.setter
    def underflow(self, value : float):
        '''Set the underflow of axis bins'''
        ...
    
    ...

class Chart:
    '''Encapsulates the object that represents a single Excel chart.'''
    
    @overload
    def to_image(self, image_file : str):
        '''Creates the chart image and saves it to a file.
        The extension of the file name determines the format of the image.
        
        :param image_file: The image file name with full path.'''
        ...
    
    @overload
    def to_image(self, image_file : str, image_type : aspose.cells.drawing.ImageType):
        '''Creates the chart image and saves it to a file in the specified image type.
        
        :param image_file: The image file name with full path.
        :param image_type: The image type in which to save the image.'''
        ...
    
    @overload
    def to_image(self, image_file : str, jpeg_quality : int):
        '''Creates the chart image and saves it to a file in the Jpeg format.
        
        :param image_file: The image file name with full path.
        :param jpeg_quality: Jpeg quality.'''
        ...
    
    @overload
    def to_image(self, stream : io.RawIOBase, jpeg_quality : int):
        '''Creates the chart image and saves it to a stream in the Jpeg format.
        
        :param stream: The output stream.
        :param jpeg_quality: Jpeg quality.'''
        ...
    
    @overload
    def to_image(self, stream : io.RawIOBase, image_type : aspose.cells.drawing.ImageType):
        '''Creates the chart image and saves it to a stream in the specified format.
        
        :param stream: The output stream.
        :param image_type: The image type in which to save the image.'''
        ...
    
    @overload
    def to_image(self, image_file : str, options : aspose.cells.rendering.ImageOrPrintOptions):
        '''Creates the chart image and saves it to a file.
        The extension of the file name determines the format of the image.
        
        :param image_file: The image file name with full path.
        :param options: Additional image creation options'''
        ...
    
    @overload
    def to_image(self, stream : io.RawIOBase, options : aspose.cells.rendering.ImageOrPrintOptions):
        '''Creates the chart image and saves it to a stream in the specified format.
        
        :param stream: The output stream.
        :param options: Additional image creation options'''
        ...
    
    @overload
    def to_pdf(self, file_name : str):
        '''Saves the chart to a pdf file.
        
        :param file_name: the pdf file name with full path'''
        ...
    
    @overload
    def to_pdf(self, file_name : str, desired_page_width : float, desired_page_height : float, h_alignment_type : aspose.cells.PageLayoutAlignmentType, v_alignment_type : aspose.cells.PageLayoutAlignmentType):
        '''Saves the chart to a pdf file.
        
        :param file_name: the pdf file name with full path
        :param desired_page_width: The desired page width in inches.
        :param desired_page_height: The desired page height in inches.
        :param h_alignment_type: The chart horizontal alignment type in the output page.
        :param v_alignment_type: The chart vertical alignment type in the output page.'''
        ...
    
    @overload
    def to_pdf(self, stream : io.RawIOBase):
        '''Creates the chart pdf and saves it to a stream.
        
        :param stream: The output stream.'''
        ...
    
    @overload
    def to_pdf(self, stream : io.RawIOBase, desired_page_width : float, desired_page_height : float, h_alignment_type : aspose.cells.PageLayoutAlignmentType, v_alignment_type : aspose.cells.PageLayoutAlignmentType):
        '''Creates the chart pdf and saves it to a stream.
        
        :param stream: The output stream.
        :param desired_page_width: The desired page width in inches.
        :param desired_page_height: The desired page height in inches.
        :param h_alignment_type: The chart horizontal alignment type in the output page.
        :param v_alignment_type: The chart vertical alignment type in the output page.'''
        ...
    
    def is_refered_by_chart(self, row_index : int, column_index : int) -> bool:
        '''Returns whether the cell refered by the chart.
        
        :param row_index: The row index
        :param column_index: The column index'''
        ...
    
    def is_cell_refered_by_chart(self, sheet_index : int, row_index : int, column_index : int) -> bool:
        '''Returns whether the cell refered by the chart.
        
        :param sheet_index: The sheet Index.-1 means the worksheet which contains current chart.
        :param row_index: The row index
        :param column_index: The column index'''
        ...
    
    def is_chart_data_changed(self) -> bool:
        '''Detects if a chart's data source has changed.
        
        :returns: Returns true if the chart has changed otherwise returns false'''
        ...
    
    def refresh_pivot_data(self):
        '''Refreshes pivot chart's data  from it's pivot data source.'''
        ...
    
    def change_template(self, data : bytes):
        '''Change chart type with preset template.
        
        :param data: The data of chart template file(.crtx).'''
        ...
    
    def move(self, upper_left_row : int, upper_left_column : int, lower_right_row : int, lower_right_column : int):
        '''Moves the chart to a specified location.
        
        :param upper_left_column: Upper left column index.
        :param upper_left_row: Upper left row index.
        :param lower_right_column: Lower right column index
        :param lower_right_row: Lower right row index'''
        ...
    
    def calculate(self):
        '''Calculates the custom position of plot area, axes if the position of them are auto assigned.'''
        ...
    
    def get_actual_size(self) -> List[int]:
        '''Gets actual size of chart in unit of pixels.
        
        :returns: Actual size in an array(width and height).
        [0] is width; [1] is height.'''
        ...
    
    def has_axis(self, aixs_type : aspose.cells.charts.AxisType, is_primary : bool) -> bool:
        '''Returns which axes exist on the chart.'''
        ...
    
    def switch_row_column(self) -> bool:
        '''Switches row/column.
        
        :returns: False means switching row/column fails.'''
        ...
    
    def get_chart_data_range(self) -> str:
        '''Gets the data source range of the chart.
        
        :returns: The data source.'''
        ...
    
    def set_chart_data_range(self, area : str, is_vertical : bool):
        '''Specifies data range for a chart.
        
        :param area: Specifies values from which to plot the data series
        :param is_vertical: Specifies whether to plot the series from a range of cell values by row or by column.'''
        ...
    
    @property
    def style(self) -> int:
        '''Gets and sets the builtin style.'''
        ...
    
    @style.setter
    def style(self, value : int):
        '''Gets and sets the builtin style.'''
        ...
    
    @property
    def chart_object(self) -> aspose.cells.drawing.ChartShape:
        ...
    
    @property
    def hide_pivot_field_buttons(self) -> bool:
        ...
    
    @hide_pivot_field_buttons.setter
    def hide_pivot_field_buttons(self, value : bool):
        ...
    
    @property
    def pivot_options(self) -> aspose.cells.charts.PivotOptions:
        ...
    
    @property
    def pivot_source(self) -> str:
        ...
    
    @pivot_source.setter
    def pivot_source(self, value : str):
        ...
    
    @property
    def plot_by(self) -> aspose.cells.charts.PlotDataByType:
        ...
    
    @property
    def plot_empty_cells_type(self) -> aspose.cells.charts.PlotEmptyCellsType:
        ...
    
    @plot_empty_cells_type.setter
    def plot_empty_cells_type(self, value : aspose.cells.charts.PlotEmptyCellsType):
        ...
    
    @property
    def plot_visible_cells(self) -> bool:
        ...
    
    @plot_visible_cells.setter
    def plot_visible_cells(self, value : bool):
        ...
    
    @property
    def plot_visible_cells_only(self) -> bool:
        ...
    
    @plot_visible_cells_only.setter
    def plot_visible_cells_only(self, value : bool):
        ...
    
    @property
    def display_na_as_blank(self) -> bool:
        ...
    
    @display_na_as_blank.setter
    def display_na_as_blank(self, value : bool):
        ...
    
    @property
    def name(self) -> str:
        '''Gets and sets the name of the chart.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and sets the name of the chart.'''
        ...
    
    @property
    def size_with_window(self) -> bool:
        ...
    
    @size_with_window.setter
    def size_with_window(self, value : bool):
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet which contains this chart.'''
        ...
    
    @property
    def shapes(self) -> aspose.cells.drawing.ShapeCollection:
        '''Returns all drawing shapes in this chart.'''
        ...
    
    @property
    def print_size(self) -> aspose.cells.PrintSizeType:
        ...
    
    @print_size.setter
    def print_size(self, value : aspose.cells.PrintSizeType):
        ...
    
    @property
    def type(self) -> aspose.cells.charts.ChartType:
        '''Gets a chart's type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.charts.ChartType):
        '''Sets a chart's type.'''
        ...
    
    @property
    def n_series(self) -> aspose.cells.charts.SeriesCollection:
        ...
    
    @property
    def filtered_n_series(self) -> aspose.cells.charts.SeriesCollection:
        ...
    
    @property
    def title(self) -> aspose.cells.charts.Title:
        '''Gets the chart's title.'''
        ...
    
    @property
    def sub_title(self) -> aspose.cells.charts.Title:
        ...
    
    @property
    def plot_area(self) -> aspose.cells.charts.PlotArea:
        ...
    
    @property
    def chart_area(self) -> aspose.cells.charts.ChartArea:
        ...
    
    @property
    def category_axis(self) -> aspose.cells.charts.Axis:
        ...
    
    @property
    def value_axis(self) -> aspose.cells.charts.Axis:
        ...
    
    @property
    def second_value_axis(self) -> aspose.cells.charts.Axis:
        ...
    
    @property
    def second_category_axis(self) -> aspose.cells.charts.Axis:
        ...
    
    @property
    def series_axis(self) -> aspose.cells.charts.Axis:
        ...
    
    @property
    def legend(self) -> aspose.cells.charts.Legend:
        '''Gets the chart legend.'''
        ...
    
    @property
    def chart_data_table(self) -> aspose.cells.charts.ChartDataTable:
        ...
    
    @property
    def show_legend(self) -> bool:
        ...
    
    @show_legend.setter
    def show_legend(self, value : bool):
        ...
    
    @property
    def is_rectangular_cornered(self) -> bool:
        ...
    
    @is_rectangular_cornered.setter
    def is_rectangular_cornered(self, value : bool):
        ...
    
    @property
    def show_data_table(self) -> bool:
        ...
    
    @show_data_table.setter
    def show_data_table(self, value : bool):
        ...
    
    @property
    def first_slice_angle(self) -> int:
        ...
    
    @first_slice_angle.setter
    def first_slice_angle(self, value : int):
        ...
    
    @property
    def gap_width(self) -> int:
        ...
    
    @gap_width.setter
    def gap_width(self, value : int):
        ...
    
    @property
    def gap_depth(self) -> int:
        ...
    
    @gap_depth.setter
    def gap_depth(self, value : int):
        ...
    
    @property
    def floor(self) -> aspose.cells.charts.Floor:
        '''Returns a :py:attr:`aspose.cells.charts.Chart.floor` object that represents the walls of a 3-D chart.'''
        ...
    
    @property
    def walls(self) -> aspose.cells.charts.Walls:
        '''Returns a :py:attr:`aspose.cells.charts.Chart.walls` object that represents the walls of a 3-D chart.'''
        ...
    
    @property
    def back_wall(self) -> aspose.cells.charts.Walls:
        ...
    
    @property
    def side_wall(self) -> aspose.cells.charts.Walls:
        ...
    
    @property
    def walls_and_gridlines_2d(self) -> bool:
        ...
    
    @walls_and_gridlines_2d.setter
    def walls_and_gridlines_2d(self, value : bool):
        ...
    
    @property
    def rotation_angle(self) -> int:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : int):
        ...
    
    @property
    def elevation(self) -> int:
        '''Represents the elevation of the 3-D chart view, in degrees.'''
        ...
    
    @elevation.setter
    def elevation(self, value : int):
        '''Represents the elevation of the 3-D chart view, in degrees.'''
        ...
    
    @property
    def right_angle_axes(self) -> bool:
        ...
    
    @right_angle_axes.setter
    def right_angle_axes(self, value : bool):
        ...
    
    @property
    def auto_scaling(self) -> bool:
        ...
    
    @auto_scaling.setter
    def auto_scaling(self, value : bool):
        ...
    
    @property
    def height_percent(self) -> int:
        ...
    
    @height_percent.setter
    def height_percent(self, value : int):
        ...
    
    @property
    def perspective(self) -> int:
        '''Returns the perspective for the 3-D chart view. Must be between 0 and 100.
        This property is ignored if the RightAngleAxes property is True.'''
        ...
    
    @perspective.setter
    def perspective(self, value : int):
        '''Returns or sets the perspective for the 3-D chart view. Must be between 0 and 100.
        This property is ignored if the RightAngleAxes property is True.'''
        ...
    
    @property
    def is_3d(self) -> bool:
        ...
    
    @property
    def depth_percent(self) -> int:
        ...
    
    @depth_percent.setter
    def depth_percent(self, value : int):
        ...
    
    @property
    def actual_chart_size(self) -> aspose.pydrawing.Size:
        ...
    
    @property
    def placement(self) -> aspose.cells.drawing.PlacementType:
        '''Represents the way the chart is attached to the cells below it.'''
        ...
    
    @placement.setter
    def placement(self, value : aspose.cells.drawing.PlacementType):
        '''Represents the way the chart is attached to the cells below it.'''
        ...
    
    @property
    def page_setup(self) -> aspose.cells.PageSetup:
        ...
    
    @property
    def line(self) -> aspose.cells.drawing.Line:
        '''Gets the line.'''
        ...
    
    ...

class ChartArea(ChartFrame):
    '''Encapsulates the object that represents the chart area in the worksheet.'''
    
    def set_position_auto(self):
        '''Set position of the frame to automatic'''
        ...
    
    @property
    def is_inner_mode(self) -> bool:
        ...
    
    @is_inner_mode.setter
    def is_inner_mode(self, value : bool):
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.ChartFrame.area`.'''
        ...
    
    @property
    def text_font(self) -> aspose.cells.Font:
        ...
    
    @property
    def text_options(self) -> aspose.cells.drawing.texts.TextOptions:
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets a :py:attr:`aspose.cells.charts.ChartArea.font` object of the specified chartarea object.'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def is_automatic_size(self) -> bool:
        ...
    
    @is_automatic_size.setter
    def is_automatic_size(self, value : bool):
        ...
    
    @property
    def x(self) -> int:
        '''Gets or gets the horizontal offset from its upper left corner column.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Gets or gets the horizontal offset from its upper left corner column.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets or gets the vertical offset from its upper left corner row.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Gets or gets the vertical offset from its upper left corner row.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the vertical offset from its lower right corner row.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the vertical offset from its lower right corner row.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the horizontal offset from its lower right corner column.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the horizontal offset from its lower right corner column.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the frame has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the frame has a shadow.'''
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    @property
    def is_default_pos_be_set(self) -> bool:
        ...
    
    @property
    def default_x(self) -> int:
        ...
    
    @property
    def default_y(self) -> int:
        ...
    
    @property
    def default_width(self) -> int:
        ...
    
    @property
    def default_height(self) -> int:
        ...
    
    ...

class ChartCollection:
    '''Encapsulates a collection of :py:class:`aspose.cells.charts.Chart` objects.'''
    
    @overload
    def add(self, type : aspose.cells.charts.ChartType, upper_left_row : int, upper_left_column : int, lower_right_row : int, lower_right_column : int) -> int:
        '''Adds a chart to the collection.
        
        :param type: Chart type
        :param upper_left_row: Upper left row index.
        :param upper_left_column: Upper left column index.
        :param lower_right_row: Lower right row index
        :param lower_right_column: Lower right column index
        :returns: :py:class:`aspose.cells.charts.Chart` object index.'''
        ...
    
    @overload
    def add(self, type : aspose.cells.charts.ChartType, data_range : str, top_row : int, left_column : int, right_row : int, bottom_column : int) -> int:
        '''Adds a chart to the collection.
        
        :param type: Chart type
        :param data_range: Specifies the data range of the chart
        :param top_row: Upper left row index.
        :param left_column: Upper left column index.
        :param right_row: Lower right row index
        :param bottom_column: Lower right column index
        :returns: :py:class:`aspose.cells.charts.Chart` object index.'''
        ...
    
    @overload
    def add(self, data : bytes, data_range : str, is_vertical : bool, top_row : int, left_column : int, right_row : int, bottom_column : int) -> int:
        '''Adds a chart with preset template.
        
        :param data: The data of chart template file(.crtx).
        :param data_range: Specifies the data range of the chart
        :param is_vertical: Specifies whether to plot the series from a range of cell values by row or by column.
        :param top_row: Upper left row index.
        :param left_column: Upper left column index.
        :param right_row: Lower right row index
        :param bottom_column: Lower right column index
        :returns: :py:class:`aspose.cells.charts.Chart` object index.'''
        ...
    
    @overload
    def add(self, type : aspose.cells.charts.ChartType, data_range : str, is_vertical : bool, top_row : int, left_column : int, right_row : int, bottom_column : int) -> int:
        '''Adds a chart to the collection.
        
        :param type: Chart type
        :param data_range: Specifies the data range of the chart
        :param is_vertical: Specifies whether to plot the series from a range of cell values by row or by column.
        :param top_row: Upper left row index.
        :param left_column: Upper left column index.
        :param right_row: Lower right row index
        :param bottom_column: Lower right column index
        :returns: :py:class:`aspose.cells.charts.Chart` object index.'''
        ...
    
    @overload
    def get(self, index : int) -> aspose.cells.charts.Chart:
        '''Add API for Python Via .Net.since this[int index] is unsupported
        
        :param index: The zero based index of the element.'''
        ...
    
    @overload
    def get(self, name : str) -> aspose.cells.charts.Chart:
        '''Add API for Python Via .Net.since this[string Chart] is unsupported
        
        :param name: Chart name'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.charts.Chart]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.charts.Chart], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.Chart, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.Chart, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Chart) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Chart, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Chart, index : int, count : int) -> int:
        ...
    
    def add_floating_chart(self, type : aspose.cells.charts.ChartType, left : int, top : int, width : int, height : int) -> int:
        '''Adds a chart to the collection.
        
        :param type: Chart type
        :param left: The x offset to corner
        :param top: The y offset to corner
        :param width: The chart width
        :param height: The chart height
        :returns: :py:class:`aspose.cells.charts.Chart` object index.'''
        ...
    
    def binary_search(self, item : aspose.cells.charts.Chart) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class ChartDataTable:
    '''Represents a chart data table.'''
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets a :py:attr:`aspose.cells.charts.ChartDataTable.font` object which represents the font setting of the specified chart data table.'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def has_border_horizontal(self) -> bool:
        ...
    
    @has_border_horizontal.setter
    def has_border_horizontal(self, value : bool):
        ...
    
    @property
    def has_border_vertical(self) -> bool:
        ...
    
    @has_border_vertical.setter
    def has_border_vertical(self, value : bool):
        ...
    
    @property
    def has_border_outline(self) -> bool:
        ...
    
    @has_border_outline.setter
    def has_border_outline(self, value : bool):
        ...
    
    @property
    def show_legend_key(self) -> bool:
        ...
    
    @show_legend_key.setter
    def show_legend_key(self, value : bool):
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Returns a Border object that represents the border of the object'''
        ...
    
    ...

class ChartFrame:
    '''Encapsulates the object that represents the frame object in a chart.'''
    
    def set_position_auto(self):
        '''Set position of the frame to automatic'''
        ...
    
    @property
    def is_inner_mode(self) -> bool:
        ...
    
    @is_inner_mode.setter
    def is_inner_mode(self, value : bool):
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.ChartFrame.area`.'''
        ...
    
    @property
    def text_font(self) -> aspose.cells.Font:
        ...
    
    @property
    def text_options(self) -> aspose.cells.drawing.texts.TextOptions:
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets a :py:attr:`aspose.cells.charts.ChartFrame.font` object of the specified ChartFrame object.'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def is_automatic_size(self) -> bool:
        ...
    
    @is_automatic_size.setter
    def is_automatic_size(self, value : bool):
        ...
    
    @property
    def x(self) -> int:
        '''Gets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Sets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Sets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the frame has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the frame has a shadow.'''
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    @property
    def is_default_pos_be_set(self) -> bool:
        ...
    
    @property
    def default_x(self) -> int:
        ...
    
    @property
    def default_y(self) -> int:
        ...
    
    @property
    def default_width(self) -> int:
        ...
    
    @property
    def default_height(self) -> int:
        ...
    
    ...

class ChartGlobalizationSettings:
    '''Represents the globalization settings for chart.'''
    
    def get_series_name(self) -> str:
        '''Gets the name of Series in the Chart.'''
        ...
    
    def get_chart_title_name(self) -> str:
        '''Gets the name of Chart Title.'''
        ...
    
    def get_legend_increase_name(self) -> str:
        '''Gets the name of increase for Legend.'''
        ...
    
    def get_legend_decrease_name(self) -> str:
        '''Gets the name of Decrease for Legend.'''
        ...
    
    def get_legend_total_name(self) -> str:
        '''Gets the name of Total for Legend.'''
        ...
    
    def get_axis_title_name(self) -> str:
        '''Gets the name of Title for Axis.'''
        ...
    
    def get_other_name(self) -> str:
        '''Gets the name of "Other" labels for Chart.'''
        ...
    
    def get_axis_unit_name(self, type : aspose.cells.charts.DisplayUnitType) -> str:
        '''Gets the Name of Axis Unit.'''
        ...
    
    ...

class ChartPoint:
    '''Represents a single point in a series in a chart.'''
    
    def get_top_point_count(self) -> int:
        '''Gets the number of top points after calls Chart.Calculate() method.'''
        ...
    
    def get_top_point_x_px(self, index : int) -> float:
        '''Gets x-coordinate of the top point of shape after calls Chart.Calculate() method.
        Applies 3D charts: Column3D, Bar3D, Cone, Cylinder, Pyramid and Area3D'''
        ...
    
    def get_top_point_y_px(self, index : int) -> float:
        '''Gets y-coordinate of the top point of shape after calls Chart.Calculate() method.
        Applies 3D charts: Column3D, Bar3D, Cone, Cylinder, Pyramid and Area3D'''
        ...
    
    def get_bottom_point_count(self) -> int:
        '''Gets the number of bottom points  after calls Chart.Calculate() method.'''
        ...
    
    def get_bottom_point_x_px(self, index : int) -> float:
        '''Gets x-coordinate of the bottom point of shape after calls Chart.Calculate() method.
        Applies 3D charts: Column3D, Bar3D, Cone, Cylinder, Pyramid'''
        ...
    
    def get_bottom_point_y_px(self, index : int) -> float:
        '''Gets y-coordinate of the bottom point of shape  after calls Chart.Calculate() method.
        Applies 3D charts: Column3D, Bar3D, Cone, Cylinder, Pyramid'''
        ...
    
    def get_on_category_axis_point_count(self) -> int:
        '''Gets the number of the points on category axis after calls Chart.Calculate() method. Only applies to area chart.'''
        ...
    
    def get_on_category_axis_point_x_px(self, index : int) -> float:
        '''Gets x-coordinate of the point on category axis after calls Chart.Calculate() method. Only applies to Area chart.'''
        ...
    
    def get_on_category_axis_point_y_px(self, index : int) -> float:
        '''Gets y-coordinate of the point on category axis after calls Chart.Calculate() method. Only applies to Area chart.'''
        ...
    
    @property
    def explosion(self) -> int:
        '''The distance of an open pie slice from the center of the pie chart is expressed as a percentage of the pie diameter.'''
        ...
    
    @explosion.setter
    def explosion(self, value : int):
        '''The distance of an open pie slice from the center of the pie chart is expressed as a percentage of the pie diameter.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the chartpoint has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the chartpoint has a shadow.'''
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.ChartPoint.area`.'''
        ...
    
    @property
    def marker(self) -> aspose.cells.charts.Marker:
        '''Gets the :py:attr:`aspose.cells.charts.ChartPoint.marker`.'''
        ...
    
    @property
    def data_labels(self) -> aspose.cells.charts.DataLabels:
        ...
    
    @property
    def y_value(self) -> any:
        ...
    
    @y_value.setter
    def y_value(self, value : any):
        ...
    
    @property
    def y_value_type(self) -> aspose.cells.CellValueType:
        ...
    
    @property
    def x_value(self) -> any:
        ...
    
    @x_value.setter
    def x_value(self, value : any):
        ...
    
    @property
    def x_value_type(self) -> aspose.cells.CellValueType:
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    @property
    def is_in_secondary_plot(self) -> bool:
        ...
    
    @is_in_secondary_plot.setter
    def is_in_secondary_plot(self, value : bool):
        ...
    
    @property
    def shape_x(self) -> int:
        ...
    
    @property
    def shape_y(self) -> int:
        ...
    
    @property
    def shape_width(self) -> int:
        ...
    
    @property
    def shape_height(self) -> int:
        ...
    
    @property
    def shape_x_px(self) -> int:
        ...
    
    @property
    def shape_y_px(self) -> int:
        ...
    
    @property
    def shape_width_px(self) -> int:
        ...
    
    @property
    def shape_height_px(self) -> int:
        ...
    
    @property
    def border_width_px(self) -> int:
        ...
    
    @property
    def radius_px(self) -> int:
        ...
    
    @property
    def inner_radius_px(self) -> int:
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @property
    def end_angle(self) -> float:
        ...
    
    @property
    def arc_start_point_x_px(self) -> float:
        ...
    
    @property
    def arc_start_point_y_px(self) -> float:
        ...
    
    @property
    def arc_end_point_x_px(self) -> float:
        ...
    
    @property
    def arc_end_point_y_px(self) -> float:
        ...
    
    @property
    def inner_arc_start_point_x_px(self) -> float:
        ...
    
    @property
    def inner_arc_start_point_y_px(self) -> float:
        ...
    
    @property
    def inner_arc_end_point_x_px(self) -> float:
        ...
    
    @property
    def inner_arc_end_point_y_px(self) -> float:
        ...
    
    ...

class ChartPointCollection:
    '''Represents a collection that contains all the points in one series.'''
    
    def get_enumerator(self) -> collections.abc.Iterator:
        '''Returns an enumerator for the entire :py:class:`aspose.cells.charts.ChartPointCollection`.'''
        ...
    
    def clear(self):
        '''Remove all setting of the chart points.'''
        ...
    
    def remove_at(self, index : int):
        '''Removes point at the index of the series..
        
        :param index: The index of the point.'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of the chart point.'''
        ...
    
    def __getitem__(self, key : int) -> aspose.cells.charts.ChartPoint:
        '''Gets the :py:class:`aspose.cells.charts.ChartPoint` element at the specified index in the series.'''
        ...
    
    ...

class ChartTextFrame(ChartFrame):
    '''Encapsulates the object that represents the frame object which contains text.'''
    
    def set_position_auto(self):
        '''Set position of the frame to automatic'''
        ...
    
    def characters(self, start_index : int, length : int) -> aspose.cells.FontSetting:
        '''Returns a Characters object that represents a range of characters within the text.
        
        :param start_index: The index of the start of the character.
        :param length: The number of characters.
        :returns: Characters object.'''
        ...
    
    @property
    def is_inner_mode(self) -> bool:
        ...
    
    @is_inner_mode.setter
    def is_inner_mode(self, value : bool):
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.ChartFrame.area`.'''
        ...
    
    @property
    def text_font(self) -> aspose.cells.Font:
        ...
    
    @property
    def text_options(self) -> aspose.cells.drawing.texts.TextOptions:
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets a :py:attr:`aspose.cells.charts.ChartFrame.font` object of the specified ChartFrame object.'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def is_automatic_size(self) -> bool:
        ...
    
    @is_automatic_size.setter
    def is_automatic_size(self, value : bool):
        ...
    
    @property
    def x(self) -> int:
        '''Gets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Sets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Sets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the frame has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the frame has a shadow.'''
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    @property
    def is_default_pos_be_set(self) -> bool:
        ...
    
    @property
    def default_x(self) -> int:
        ...
    
    @property
    def default_y(self) -> int:
        ...
    
    @property
    def default_width(self) -> int:
        ...
    
    @property
    def default_height(self) -> int:
        ...
    
    @property
    def is_auto_text(self) -> bool:
        ...
    
    @is_auto_text.setter
    def is_auto_text(self, value : bool):
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def text_horizontal_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_horizontal_alignment.setter
    def text_horizontal_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def text_vertical_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_vertical_alignment.setter
    def text_vertical_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def rotation_angle(self) -> int:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : int):
        ...
    
    @property
    def is_automatic_rotation(self) -> bool:
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text of a frame's title.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text of a frame's title.'''
        ...
    
    @property
    def linked_source(self) -> str:
        ...
    
    @linked_source.setter
    def linked_source(self, value : str):
        ...
    
    @property
    def text_direction(self) -> aspose.cells.TextDirectionType:
        ...
    
    @text_direction.setter
    def text_direction(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def reading_order(self) -> aspose.cells.TextDirectionType:
        ...
    
    @reading_order.setter
    def reading_order(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def direction_type(self) -> aspose.cells.charts.ChartTextDirectionType:
        ...
    
    @direction_type.setter
    def direction_type(self, value : aspose.cells.charts.ChartTextDirectionType):
        ...
    
    @property
    def is_text_wrapped(self) -> bool:
        ...
    
    @is_text_wrapped.setter
    def is_text_wrapped(self, value : bool):
        ...
    
    @property
    def is_resize_shape_to_fit_text(self) -> bool:
        ...
    
    @is_resize_shape_to_fit_text.setter
    def is_resize_shape_to_fit_text(self, value : bool):
        ...
    
    ...

class DataLabels(ChartTextFrame):
    '''Encapsulates a collection of all the DataLabel objects for the specified Series.'''
    
    def set_position_auto(self):
        '''Set position of the frame to automatic'''
        ...
    
    def characters(self, start_index : int, length : int) -> aspose.cells.FontSetting:
        '''Returns a Characters object that represents a range of characters within the text.
        
        :param start_index: The index of the start of the character.
        :param length: The number of characters.
        :returns: Characters object.'''
        ...
    
    @property
    def is_inner_mode(self) -> bool:
        ...
    
    @is_inner_mode.setter
    def is_inner_mode(self, value : bool):
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.DataLabels.area`.'''
        ...
    
    @property
    def text_font(self) -> aspose.cells.Font:
        ...
    
    @property
    def text_options(self) -> aspose.cells.drawing.texts.TextOptions:
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets the font of the DataLabels;'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def is_automatic_size(self) -> bool:
        ...
    
    @is_automatic_size.setter
    def is_automatic_size(self, value : bool):
        ...
    
    @property
    def x(self) -> int:
        '''Gets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Sets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Sets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the frame has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the frame has a shadow.'''
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    @property
    def is_default_pos_be_set(self) -> bool:
        ...
    
    @property
    def default_x(self) -> int:
        ...
    
    @property
    def default_y(self) -> int:
        ...
    
    @property
    def default_width(self) -> int:
        ...
    
    @property
    def default_height(self) -> int:
        ...
    
    @property
    def is_auto_text(self) -> bool:
        ...
    
    @is_auto_text.setter
    def is_auto_text(self, value : bool):
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def text_horizontal_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_horizontal_alignment.setter
    def text_horizontal_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def text_vertical_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_vertical_alignment.setter
    def text_vertical_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def rotation_angle(self) -> int:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : int):
        ...
    
    @property
    def is_automatic_rotation(self) -> bool:
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text of data label.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text of data label.'''
        ...
    
    @property
    def linked_source(self) -> str:
        ...
    
    @linked_source.setter
    def linked_source(self, value : str):
        ...
    
    @property
    def text_direction(self) -> aspose.cells.TextDirectionType:
        ...
    
    @text_direction.setter
    def text_direction(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def reading_order(self) -> aspose.cells.TextDirectionType:
        ...
    
    @reading_order.setter
    def reading_order(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def direction_type(self) -> aspose.cells.charts.ChartTextDirectionType:
        ...
    
    @direction_type.setter
    def direction_type(self, value : aspose.cells.charts.ChartTextDirectionType):
        ...
    
    @property
    def is_text_wrapped(self) -> bool:
        ...
    
    @is_text_wrapped.setter
    def is_text_wrapped(self, value : bool):
        ...
    
    @property
    def is_resize_shape_to_fit_text(self) -> bool:
        ...
    
    @is_resize_shape_to_fit_text.setter
    def is_resize_shape_to_fit_text(self, value : bool):
        ...
    
    @property
    def show_value(self) -> bool:
        ...
    
    @show_value.setter
    def show_value(self, value : bool):
        ...
    
    @property
    def show_cell_range(self) -> bool:
        ...
    
    @show_cell_range.setter
    def show_cell_range(self, value : bool):
        ...
    
    @property
    def show_percentage(self) -> bool:
        ...
    
    @show_percentage.setter
    def show_percentage(self, value : bool):
        ...
    
    @property
    def show_bubble_size(self) -> bool:
        ...
    
    @show_bubble_size.setter
    def show_bubble_size(self, value : bool):
        ...
    
    @property
    def show_category_name(self) -> bool:
        ...
    
    @show_category_name.setter
    def show_category_name(self, value : bool):
        ...
    
    @property
    def show_series_name(self) -> bool:
        ...
    
    @show_series_name.setter
    def show_series_name(self, value : bool):
        ...
    
    @property
    def show_legend_key(self) -> bool:
        ...
    
    @show_legend_key.setter
    def show_legend_key(self, value : bool):
        ...
    
    @property
    def number_format(self) -> str:
        ...
    
    @number_format.setter
    def number_format(self, value : str):
        ...
    
    @property
    def number(self) -> int:
        '''Gets and sets the built-in number format.'''
        ...
    
    @number.setter
    def number(self, value : int):
        '''Gets and sets the built-in number format.'''
        ...
    
    @property
    def number_format_linked(self) -> bool:
        ...
    
    @number_format_linked.setter
    def number_format_linked(self, value : bool):
        ...
    
    @property
    def separator(self) -> aspose.cells.charts.DataLablesSeparatorType:
        '''Gets the separator type used for the data labels on a chart.'''
        ...
    
    @separator.setter
    def separator(self, value : aspose.cells.charts.DataLablesSeparatorType):
        '''Sets the separator type used for the data labels on a chart.'''
        ...
    
    @property
    def separator_type(self) -> aspose.cells.charts.DataLabelsSeparatorType:
        ...
    
    @separator_type.setter
    def separator_type(self, value : aspose.cells.charts.DataLabelsSeparatorType):
        ...
    
    @property
    def separator_value(self) -> str:
        ...
    
    @separator_value.setter
    def separator_value(self, value : str):
        ...
    
    @property
    def position(self) -> aspose.cells.charts.LabelPositionType:
        '''Represents the position of the data label.'''
        ...
    
    @position.setter
    def position(self, value : aspose.cells.charts.LabelPositionType):
        '''Represents the position of the data label.'''
        ...
    
    @property
    def is_never_overlap(self) -> bool:
        ...
    
    @is_never_overlap.setter
    def is_never_overlap(self, value : bool):
        ...
    
    @property
    def shape_type(self) -> aspose.cells.drawing.DataLabelShapeType:
        ...
    
    @shape_type.setter
    def shape_type(self, value : aspose.cells.drawing.DataLabelShapeType):
        ...
    
    ...

class DisplayUnitLabel(ChartTextFrame):
    '''Represents the display unit label.'''
    
    def set_position_auto(self):
        '''Set position of the frame to automatic'''
        ...
    
    def characters(self, start_index : int, length : int) -> aspose.cells.FontSetting:
        '''Returns a Characters object that represents a range of characters within the text.
        
        :param start_index: The index of the start of the character.
        :param length: The number of characters.
        :returns: Characters object.'''
        ...
    
    @property
    def is_inner_mode(self) -> bool:
        ...
    
    @is_inner_mode.setter
    def is_inner_mode(self, value : bool):
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.ChartFrame.area`.'''
        ...
    
    @property
    def text_font(self) -> aspose.cells.Font:
        ...
    
    @property
    def text_options(self) -> aspose.cells.drawing.texts.TextOptions:
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets a :py:attr:`aspose.cells.charts.DisplayUnitLabel.font` object of the specified ChartFrame object.'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def is_automatic_size(self) -> bool:
        ...
    
    @is_automatic_size.setter
    def is_automatic_size(self, value : bool):
        ...
    
    @property
    def x(self) -> int:
        '''Gets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Sets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Sets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the frame has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the frame has a shadow.'''
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    @property
    def is_default_pos_be_set(self) -> bool:
        ...
    
    @property
    def default_x(self) -> int:
        ...
    
    @property
    def default_y(self) -> int:
        ...
    
    @property
    def default_width(self) -> int:
        ...
    
    @property
    def default_height(self) -> int:
        ...
    
    @property
    def is_auto_text(self) -> bool:
        ...
    
    @is_auto_text.setter
    def is_auto_text(self, value : bool):
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def text_horizontal_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_horizontal_alignment.setter
    def text_horizontal_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def text_vertical_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_vertical_alignment.setter
    def text_vertical_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def rotation_angle(self) -> int:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : int):
        ...
    
    @property
    def is_automatic_rotation(self) -> bool:
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text of display unit label.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text of display unit label.'''
        ...
    
    @property
    def linked_source(self) -> str:
        ...
    
    @linked_source.setter
    def linked_source(self, value : str):
        ...
    
    @property
    def text_direction(self) -> aspose.cells.TextDirectionType:
        ...
    
    @text_direction.setter
    def text_direction(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def reading_order(self) -> aspose.cells.TextDirectionType:
        ...
    
    @reading_order.setter
    def reading_order(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def direction_type(self) -> aspose.cells.charts.ChartTextDirectionType:
        ...
    
    @direction_type.setter
    def direction_type(self, value : aspose.cells.charts.ChartTextDirectionType):
        ...
    
    @property
    def is_text_wrapped(self) -> bool:
        ...
    
    @is_text_wrapped.setter
    def is_text_wrapped(self, value : bool):
        ...
    
    @property
    def is_resize_shape_to_fit_text(self) -> bool:
        ...
    
    @is_resize_shape_to_fit_text.setter
    def is_resize_shape_to_fit_text(self, value : bool):
        ...
    
    ...

class DropBars:
    '''Represents the up/down bars in a chart.'''
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the border :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.DropBars.area`.'''
        ...
    
    ...

class ErrorBar(aspose.cells.drawing.Line):
    '''Represents error bar of data series.'''
    
    @property
    def compound_type(self) -> aspose.cells.drawing.MsoLineStyle:
        ...
    
    @compound_type.setter
    def compound_type(self, value : aspose.cells.drawing.MsoLineStyle):
        ...
    
    @property
    def dash_type(self) -> aspose.cells.drawing.MsoLineDashStyle:
        ...
    
    @dash_type.setter
    def dash_type(self, value : aspose.cells.drawing.MsoLineDashStyle):
        ...
    
    @property
    def cap_type(self) -> aspose.cells.drawing.LineCapType:
        ...
    
    @cap_type.setter
    def cap_type(self, value : aspose.cells.drawing.LineCapType):
        ...
    
    @property
    def join_type(self) -> aspose.cells.drawing.LineJoinType:
        ...
    
    @join_type.setter
    def join_type(self, value : aspose.cells.drawing.LineJoinType):
        ...
    
    @property
    def begin_type(self) -> aspose.cells.drawing.MsoArrowheadStyle:
        ...
    
    @begin_type.setter
    def begin_type(self, value : aspose.cells.drawing.MsoArrowheadStyle):
        ...
    
    @property
    def end_type(self) -> aspose.cells.drawing.MsoArrowheadStyle:
        ...
    
    @end_type.setter
    def end_type(self, value : aspose.cells.drawing.MsoArrowheadStyle):
        ...
    
    @property
    def begin_arrow_length(self) -> aspose.cells.drawing.MsoArrowheadLength:
        ...
    
    @begin_arrow_length.setter
    def begin_arrow_length(self, value : aspose.cells.drawing.MsoArrowheadLength):
        ...
    
    @property
    def end_arrow_length(self) -> aspose.cells.drawing.MsoArrowheadLength:
        ...
    
    @end_arrow_length.setter
    def end_arrow_length(self, value : aspose.cells.drawing.MsoArrowheadLength):
        ...
    
    @property
    def begin_arrow_width(self) -> aspose.cells.drawing.MsoArrowheadWidth:
        ...
    
    @begin_arrow_width.setter
    def begin_arrow_width(self, value : aspose.cells.drawing.MsoArrowheadWidth):
        ...
    
    @property
    def end_arrow_width(self) -> aspose.cells.drawing.MsoArrowheadWidth:
        ...
    
    @end_arrow_width.setter
    def end_arrow_width(self, value : aspose.cells.drawing.MsoArrowheadWidth):
        ...
    
    @property
    def theme_color(self) -> aspose.cells.ThemeColor:
        ...
    
    @theme_color.setter
    def theme_color(self, value : aspose.cells.ThemeColor):
        ...
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Represents the :py:class:`aspose.pydrawing.Color` of the line.'''
        ...
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color):
        '''Represents the :py:class:`aspose.pydrawing.Color` of the line.'''
        ...
    
    @property
    def transparency(self) -> float:
        '''Returns the degree of transparency of the line as a value from 0.0 (opaque) through 1.0 (clear).'''
        ...
    
    @transparency.setter
    def transparency(self, value : float):
        '''Returns or sets the degree of transparency of the line as a value from 0.0 (opaque) through 1.0 (clear).'''
        ...
    
    @property
    def style(self) -> aspose.cells.drawing.LineType:
        '''Represents the style of the line.'''
        ...
    
    @style.setter
    def style(self, value : aspose.cells.drawing.LineType):
        '''Represents the style of the line.'''
        ...
    
    @property
    def weight(self) -> aspose.cells.drawing.WeightType:
        '''Gets the :py:class:`aspose.cells.drawing.WeightType` of the line.'''
        ...
    
    @weight.setter
    def weight(self, value : aspose.cells.drawing.WeightType):
        '''Sets the :py:class:`aspose.cells.drawing.WeightType` of the line.'''
        ...
    
    @property
    def weight_pt(self) -> float:
        ...
    
    @weight_pt.setter
    def weight_pt(self, value : float):
        ...
    
    @property
    def weight_px(self) -> float:
        ...
    
    @weight_px.setter
    def weight_px(self, value : float):
        ...
    
    @property
    def formatting_type(self) -> aspose.cells.charts.ChartLineFormattingType:
        ...
    
    @formatting_type.setter
    def formatting_type(self, value : aspose.cells.charts.ChartLineFormattingType):
        ...
    
    @property
    def is_automatic_color(self) -> bool:
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def is_auto(self) -> bool:
        ...
    
    @is_auto.setter
    def is_auto(self, value : bool):
        ...
    
    @property
    def gradient_fill(self) -> aspose.cells.drawing.GradientFill:
        ...
    
    @property
    def type(self) -> aspose.cells.charts.ErrorBarType:
        '''Represents error bar amount type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.charts.ErrorBarType):
        '''Represents error bar amount type.'''
        ...
    
    @property
    def display_type(self) -> aspose.cells.charts.ErrorBarDisplayType:
        ...
    
    @display_type.setter
    def display_type(self, value : aspose.cells.charts.ErrorBarDisplayType):
        ...
    
    @property
    def amount(self) -> float:
        '''Represents amount of error bar.'''
        ...
    
    @amount.setter
    def amount(self, value : float):
        '''Represents amount of error bar.'''
        ...
    
    @property
    def show_marker_t_top(self) -> bool:
        ...
    
    @show_marker_t_top.setter
    def show_marker_t_top(self, value : bool):
        ...
    
    @property
    def plus_value(self) -> str:
        ...
    
    @plus_value.setter
    def plus_value(self, value : str):
        ...
    
    @property
    def minus_value(self) -> str:
        ...
    
    @minus_value.setter
    def minus_value(self, value : str):
        ...
    
    ...

class Floor(aspose.cells.drawing.Area):
    '''Encapsulates the object that represents the floor of a 3-D chart.'''
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color):
        ...
    
    @property
    def foreground_color(self) -> aspose.pydrawing.Color:
        ...
    
    @foreground_color.setter
    def foreground_color(self, value : aspose.pydrawing.Color):
        ...
    
    @property
    def formatting(self) -> aspose.cells.charts.FormattingType:
        '''Represents the formatting of the area.'''
        ...
    
    @formatting.setter
    def formatting(self, value : aspose.cells.charts.FormattingType):
        '''Represents the formatting of the area.'''
        ...
    
    @property
    def invert_if_negative(self) -> bool:
        ...
    
    @invert_if_negative.setter
    def invert_if_negative(self, value : bool):
        ...
    
    @property
    def fill_format(self) -> aspose.cells.drawing.FillFormat:
        ...
    
    @property
    def transparency(self) -> float:
        '''Returns the degree of transparency of the area as a value from 0.0 (opaque) through 1.0 (clear).'''
        ...
    
    @transparency.setter
    def transparency(self, value : float):
        '''Returns or sets the degree of transparency of the area as a value from 0.0 (opaque) through 1.0 (clear).'''
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the border :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @border.setter
    def border(self, value : aspose.cells.drawing.Line):
        '''Sets the border :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    ...

class Legend(ChartTextFrame):
    '''Encapsulates the object that represents the chart legend.'''
    
    def set_position_auto(self):
        '''Set position of the frame to automatic'''
        ...
    
    def characters(self, start_index : int, length : int) -> aspose.cells.FontSetting:
        '''Returns a Characters object that represents a range of characters within the text.
        
        :param start_index: The index of the start of the character.
        :param length: The number of characters.
        :returns: Characters object.'''
        ...
    
    @property
    def is_inner_mode(self) -> bool:
        ...
    
    @is_inner_mode.setter
    def is_inner_mode(self, value : bool):
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.ChartFrame.area`.'''
        ...
    
    @property
    def text_font(self) -> aspose.cells.Font:
        ...
    
    @property
    def text_options(self) -> aspose.cells.drawing.texts.TextOptions:
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets a :py:attr:`aspose.cells.charts.ChartFrame.font` object of the specified ChartFrame object.'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def is_automatic_size(self) -> bool:
        ...
    
    @is_automatic_size.setter
    def is_automatic_size(self, value : bool):
        ...
    
    @property
    def x(self) -> int:
        '''Gets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Sets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Sets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the frame has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the frame has a shadow.'''
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    @property
    def is_default_pos_be_set(self) -> bool:
        ...
    
    @property
    def default_x(self) -> int:
        ...
    
    @property
    def default_y(self) -> int:
        ...
    
    @property
    def default_width(self) -> int:
        ...
    
    @property
    def default_height(self) -> int:
        ...
    
    @property
    def is_auto_text(self) -> bool:
        ...
    
    @is_auto_text.setter
    def is_auto_text(self, value : bool):
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def text_horizontal_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_horizontal_alignment.setter
    def text_horizontal_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def text_vertical_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_vertical_alignment.setter
    def text_vertical_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def rotation_angle(self) -> int:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : int):
        ...
    
    @property
    def is_automatic_rotation(self) -> bool:
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text of a frame's title.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text of a frame's title.'''
        ...
    
    @property
    def linked_source(self) -> str:
        ...
    
    @linked_source.setter
    def linked_source(self, value : str):
        ...
    
    @property
    def text_direction(self) -> aspose.cells.TextDirectionType:
        ...
    
    @text_direction.setter
    def text_direction(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def reading_order(self) -> aspose.cells.TextDirectionType:
        ...
    
    @reading_order.setter
    def reading_order(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def direction_type(self) -> aspose.cells.charts.ChartTextDirectionType:
        ...
    
    @direction_type.setter
    def direction_type(self, value : aspose.cells.charts.ChartTextDirectionType):
        ...
    
    @property
    def is_text_wrapped(self) -> bool:
        ...
    
    @is_text_wrapped.setter
    def is_text_wrapped(self, value : bool):
        ...
    
    @property
    def is_resize_shape_to_fit_text(self) -> bool:
        ...
    
    @is_resize_shape_to_fit_text.setter
    def is_resize_shape_to_fit_text(self, value : bool):
        ...
    
    @property
    def position(self) -> aspose.cells.charts.LegendPositionType:
        '''Gets the legend position type.'''
        ...
    
    @position.setter
    def position(self, value : aspose.cells.charts.LegendPositionType):
        '''Sets the legend position type.'''
        ...
    
    @property
    def legend_entries(self) -> aspose.cells.charts.LegendEntryCollection:
        ...
    
    @property
    def legend_entries_labels(self) -> list:
        ...
    
    @property
    def is_over_lay(self) -> bool:
        ...
    
    @is_over_lay.setter
    def is_over_lay(self, value : bool):
        ...
    
    ...

class LegendEntry:
    '''Represents a legend entry in a chart legend.'''
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets a :py:attr:`aspose.cells.charts.LegendEntry.font` object of the specified ChartFrame object.'''
        ...
    
    @property
    def text_font(self) -> aspose.cells.Font:
        ...
    
    @property
    def is_text_no_fill(self) -> bool:
        ...
    
    @is_text_no_fill.setter
    def is_text_no_fill(self, value : bool):
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    ...

class LegendEntryCollection:
    '''Represents a collection of all the :py:class:`aspose.cells.charts.LegendEntry` objects in the specified chart legend.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.charts.LegendEntry]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.charts.LegendEntry], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.LegendEntry, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.LegendEntry, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.LegendEntry) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.LegendEntry, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.LegendEntry, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.charts.LegendEntry) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class Marker:
    '''Represents the marker in a line chart, scatter chart, or radar chart.'''
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.Marker.area`.'''
        ...
    
    @property
    def marker_style(self) -> aspose.cells.charts.ChartMarkerType:
        ...
    
    @marker_style.setter
    def marker_style(self, value : aspose.cells.charts.ChartMarkerType):
        ...
    
    @property
    def marker_size(self) -> int:
        ...
    
    @marker_size.setter
    def marker_size(self, value : int):
        ...
    
    @property
    def marker_size_px(self) -> int:
        ...
    
    @marker_size_px.setter
    def marker_size_px(self, value : int):
        ...
    
    @property
    def foreground_color(self) -> aspose.pydrawing.Color:
        ...
    
    @foreground_color.setter
    def foreground_color(self, value : aspose.pydrawing.Color):
        ...
    
    @property
    def foreground_color_set_type(self) -> aspose.cells.charts.FormattingType:
        ...
    
    @foreground_color_set_type.setter
    def foreground_color_set_type(self, value : aspose.cells.charts.FormattingType):
        ...
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color):
        ...
    
    @property
    def background_color_set_type(self) -> aspose.cells.charts.FormattingType:
        ...
    
    @background_color_set_type.setter
    def background_color_set_type(self, value : aspose.cells.charts.FormattingType):
        ...
    
    ...

class PivotOptions:
    '''Represents a complex type that specifies the pivot controls that appear on the chart'''
    
    @property
    def drop_zone_filter(self) -> bool:
        ...
    
    @drop_zone_filter.setter
    def drop_zone_filter(self, value : bool):
        ...
    
    @property
    def drop_zone_categories(self) -> bool:
        ...
    
    @drop_zone_categories.setter
    def drop_zone_categories(self, value : bool):
        ...
    
    @property
    def drop_zone_data(self) -> bool:
        ...
    
    @drop_zone_data.setter
    def drop_zone_data(self, value : bool):
        ...
    
    @property
    def drop_zone_series(self) -> bool:
        ...
    
    @drop_zone_series.setter
    def drop_zone_series(self, value : bool):
        ...
    
    @property
    def drop_zones_visible(self) -> bool:
        ...
    
    @drop_zones_visible.setter
    def drop_zones_visible(self, value : bool):
        ...
    
    ...

class PlotArea(ChartFrame):
    '''Encapsulates the object that represents the plot area in a chart.'''
    
    def set_position_auto(self):
        '''Set position of the plot area to automatic'''
        ...
    
    @property
    def is_inner_mode(self) -> bool:
        ...
    
    @is_inner_mode.setter
    def is_inner_mode(self, value : bool):
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.ChartFrame.area`.'''
        ...
    
    @property
    def text_font(self) -> aspose.cells.Font:
        ...
    
    @property
    def text_options(self) -> aspose.cells.drawing.texts.TextOptions:
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets a :py:attr:`aspose.cells.charts.ChartFrame.font` object of the specified ChartFrame object.'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def is_automatic_size(self) -> bool:
        ...
    
    @is_automatic_size.setter
    def is_automatic_size(self, value : bool):
        ...
    
    @property
    def x(self) -> int:
        '''Gets or gets the x coordinate of the upper left corner of plot-area bounding box in units of 1/4000 of the chart area.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Gets or gets the x coordinate of the upper left corner of plot-area bounding box in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets or gets the y coordinate of the upper top corner  of plot-area bounding box in units of 1/4000 of the chart area.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Gets or gets the y coordinate of the upper top corner  of plot-area bounding box in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of plot-area bounding box in units of 1/4000 of the chart area.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of plot-area bounding box in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of plot-area bounding box in units of 1/4000 of the chart area.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of plot-area bounding box in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the frame has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the frame has a shadow.'''
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    @property
    def is_default_pos_be_set(self) -> bool:
        ...
    
    @property
    def default_x(self) -> int:
        ...
    
    @property
    def default_y(self) -> int:
        ...
    
    @property
    def default_width(self) -> int:
        ...
    
    @property
    def default_height(self) -> int:
        ...
    
    @property
    def inner_x(self) -> int:
        ...
    
    @inner_x.setter
    def inner_x(self, value : int):
        ...
    
    @property
    def inner_y(self) -> int:
        ...
    
    @inner_y.setter
    def inner_y(self, value : int):
        ...
    
    @property
    def inner_height(self) -> int:
        ...
    
    @inner_height.setter
    def inner_height(self, value : int):
        ...
    
    @property
    def inner_width(self) -> int:
        ...
    
    @inner_width.setter
    def inner_width(self, value : int):
        ...
    
    ...

class Series:
    '''Encapsulates the object that represents a single data series in a chart.'''
    
    def move(self, count : int):
        '''Moves the series up or down.
        
        :param count: The number of moving up or down.
        Move the series up if this is less than zero;
        Move the series down if this is greater than zero.'''
        ...
    
    @property
    def is_filtered(self) -> bool:
        ...
    
    @is_filtered.setter
    def is_filtered(self, value : bool):
        ...
    
    @property
    def layout_properties(self) -> aspose.cells.charts.SeriesLayoutProperties:
        ...
    
    @property
    def points(self) -> aspose.cells.charts.ChartPointCollection:
        '''Gets the collection of points in a series in a chart.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Represents the background area of Series object.'''
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Represents border of Series object.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of the data series.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name of the data series.'''
        ...
    
    @property
    def display_name(self) -> str:
        ...
    
    @property
    def count_of_data_values(self) -> int:
        ...
    
    @property
    def is_vertical_values(self) -> bool:
        ...
    
    @property
    def values(self) -> str:
        '''Represents the data of the chart series.'''
        ...
    
    @values.setter
    def values(self, value : str):
        '''Represents the data of the chart series.'''
        ...
    
    @property
    def values_format_code(self) -> str:
        ...
    
    @values_format_code.setter
    def values_format_code(self, value : str):
        ...
    
    @property
    def x_values(self) -> str:
        ...
    
    @x_values.setter
    def x_values(self, value : str):
        ...
    
    @property
    def bubble_sizes(self) -> str:
        ...
    
    @bubble_sizes.setter
    def bubble_sizes(self, value : str):
        ...
    
    @property
    def trend_lines(self) -> aspose.cells.charts.TrendlineCollection:
        ...
    
    @property
    def smooth(self) -> bool:
        '''Represents curve smoothing.
        True if curve smoothing is turned on for the line chart or scatter chart.
        Applies only to line and scatter connected by lines charts.'''
        ...
    
    @smooth.setter
    def smooth(self, value : bool):
        '''Represents curve smoothing.
        True if curve smoothing is turned on for the line chart or scatter chart.
        Applies only to line and scatter connected by lines charts.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the series has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the series has a shadow.'''
        ...
    
    @property
    def has_3d_effect(self) -> bool:
        ...
    
    @has_3d_effect.setter
    def has_3d_effect(self, value : bool):
        ...
    
    @property
    def bar_3d_shape_type(self) -> aspose.cells.charts.Bar3DShapeType:
        ...
    
    @bar_3d_shape_type.setter
    def bar_3d_shape_type(self, value : aspose.cells.charts.Bar3DShapeType):
        ...
    
    @property
    def data_labels(self) -> aspose.cells.charts.DataLabels:
        ...
    
    @property
    def type(self) -> aspose.cells.charts.ChartType:
        '''Gets a data series' type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.charts.ChartType):
        '''Sets a data series' type.'''
        ...
    
    @property
    def marker(self) -> aspose.cells.charts.Marker:
        '''Gets the :py:attr:`aspose.cells.charts.Series.marker`.'''
        ...
    
    @property
    def plot_on_second_axis(self) -> bool:
        ...
    
    @plot_on_second_axis.setter
    def plot_on_second_axis(self, value : bool):
        ...
    
    @property
    def x_error_bar(self) -> aspose.cells.charts.ErrorBar:
        ...
    
    @property
    def y_error_bar(self) -> aspose.cells.charts.ErrorBar:
        ...
    
    @property
    def has_hi_lo_lines(self) -> bool:
        ...
    
    @has_hi_lo_lines.setter
    def has_hi_lo_lines(self, value : bool):
        ...
    
    @property
    def hi_lo_lines(self) -> aspose.cells.drawing.Line:
        ...
    
    @property
    def has_series_lines(self) -> bool:
        ...
    
    @has_series_lines.setter
    def has_series_lines(self, value : bool):
        ...
    
    @property
    def series_lines(self) -> aspose.cells.drawing.Line:
        ...
    
    @property
    def has_drop_lines(self) -> bool:
        ...
    
    @has_drop_lines.setter
    def has_drop_lines(self, value : bool):
        ...
    
    @property
    def drop_lines(self) -> aspose.cells.drawing.Line:
        ...
    
    @property
    def has_up_down_bars(self) -> bool:
        ...
    
    @has_up_down_bars.setter
    def has_up_down_bars(self, value : bool):
        ...
    
    @property
    def up_bars(self) -> aspose.cells.charts.DropBars:
        ...
    
    @property
    def down_bars(self) -> aspose.cells.charts.DropBars:
        ...
    
    @property
    def is_color_varied(self) -> bool:
        ...
    
    @is_color_varied.setter
    def is_color_varied(self, value : bool):
        ...
    
    @property
    def gap_width(self) -> int:
        ...
    
    @gap_width.setter
    def gap_width(self, value : int):
        ...
    
    @property
    def first_slice_angle(self) -> int:
        ...
    
    @first_slice_angle.setter
    def first_slice_angle(self, value : int):
        ...
    
    @property
    def overlap(self) -> int:
        '''Specifies how bars and columns are positioned.
        Can be a value between – 100 and 100.
        Applies only to 2-D bar and 2-D column charts.'''
        ...
    
    @overlap.setter
    def overlap(self, value : int):
        '''Specifies how bars and columns are positioned.
        Can be a value between – 100 and 100.
        Applies only to 2-D bar and 2-D column charts.'''
        ...
    
    @property
    def second_plot_size(self) -> int:
        ...
    
    @second_plot_size.setter
    def second_plot_size(self, value : int):
        ...
    
    @property
    def split_type(self) -> aspose.cells.charts.ChartSplitType:
        ...
    
    @split_type.setter
    def split_type(self, value : aspose.cells.charts.ChartSplitType):
        ...
    
    @property
    def split_value(self) -> float:
        ...
    
    @split_value.setter
    def split_value(self, value : float):
        ...
    
    @property
    def is_auto_split(self) -> bool:
        ...
    
    @property
    def bubble_scale(self) -> int:
        ...
    
    @bubble_scale.setter
    def bubble_scale(self, value : int):
        ...
    
    @property
    def size_represents(self) -> aspose.cells.charts.BubbleSizeRepresents:
        ...
    
    @size_represents.setter
    def size_represents(self, value : aspose.cells.charts.BubbleSizeRepresents):
        ...
    
    @property
    def show_negative_bubbles(self) -> bool:
        ...
    
    @show_negative_bubbles.setter
    def show_negative_bubbles(self, value : bool):
        ...
    
    @property
    def doughnut_hole_size(self) -> int:
        ...
    
    @doughnut_hole_size.setter
    def doughnut_hole_size(self, value : int):
        ...
    
    @property
    def explosion(self) -> int:
        '''The distance of an open pie slice from the center of the pie chart is expressed as a percentage of the pie diameter.'''
        ...
    
    @explosion.setter
    def explosion(self, value : int):
        '''The distance of an open pie slice from the center of the pie chart is expressed as a percentage of the pie diameter.'''
        ...
    
    @property
    def has_radar_axis_labels(self) -> bool:
        ...
    
    @has_radar_axis_labels.setter
    def has_radar_axis_labels(self, value : bool):
        ...
    
    @property
    def has_leader_lines(self) -> bool:
        ...
    
    @has_leader_lines.setter
    def has_leader_lines(self, value : bool):
        ...
    
    @property
    def leader_lines(self) -> aspose.cells.drawing.Line:
        ...
    
    @property
    def legend_entry(self) -> aspose.cells.charts.LegendEntry:
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    ...

class SeriesCollection:
    '''Encapsulates a collection of :py:class:`aspose.cells.charts.Series` objects.'''
    
    @overload
    def add(self, area : str, is_vertical : bool) -> int:
        '''Adds the :py:class:`aspose.cells.charts.SeriesCollection` collection to a chart.
        
        :param area: Specifies values from which to plot the data series
        :param is_vertical: Specifies whether to plot the series from a range of cell values by row or by column.
        :returns: Return the first index of the added ASeries in the NSeries.'''
        ...
    
    @overload
    def add(self, area : str, is_vertical : bool, check_labels : bool) -> int:
        '''Adds the :py:class:`aspose.cells.charts.SeriesCollection` collection to a chart.
        
        :param area: Specifies values from which to plot the data series
        :param is_vertical: Specifies whether to plot the series from a range of cell values by row or by column.
        :param check_labels: Indicates whether the range contains series's name
        :returns: Return the first index of the added ASeries in the NSeries.'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.charts.Series]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.charts.Series], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.Series, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.Series, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Series) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Series, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Series, index : int, count : int) -> int:
        ...
    
    def get_series_by_order(self, order : int) -> aspose.cells.charts.Series:
        '''Gets the :py:class:`aspose.cells.charts.Series` element by order.
        
        :param order: The order of series
        :returns: The element series'''
        ...
    
    def change_series_order(self, source_index : int, dest_index : int):
        '''Directly changes the orders of the two series.
        
        :param source_index: The current index
        :param dest_index: The dest index'''
        ...
    
    def set_series_names(self, start_index : int, area : str, is_vertical : bool):
        '''Sets the name of all the serieses in the chart.
        
        :param start_index: The index of the first series which you want to set the name.
        :param area: Specifies the area for the series name.
        :param is_vertical: >Specifies whether to plot the series from a range of cell values by row or by column.'''
        ...
    
    def add_r1c1(self, area : str, is_vertical : bool) -> int:
        '''Adds the :py:class:`aspose.cells.charts.SeriesCollection` collection to a chart.
        
        :param area: Specifies values from which to plot the data series
        :param is_vertical: Specifies whether to plot the series from a range of cell values by row or by column.
        :returns: Return the first index of the added ASeries in the NSeries.'''
        ...
    
    def binary_search(self, item : aspose.cells.charts.Series) -> int:
        ...
    
    @property
    def category_data(self) -> str:
        ...
    
    @category_data.setter
    def category_data(self, value : str):
        ...
    
    @property
    def second_category_data(self) -> str:
        ...
    
    @second_category_data.setter
    def second_category_data(self, value : str):
        ...
    
    @property
    def is_color_varied(self) -> bool:
        ...
    
    @is_color_varied.setter
    def is_color_varied(self, value : bool):
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class SeriesLayoutProperties:
    '''Represents the properties of series layout.'''
    
    @property
    def show_connector_lines(self) -> bool:
        ...
    
    @show_connector_lines.setter
    def show_connector_lines(self, value : bool):
        ...
    
    @property
    def show_mean_line(self) -> bool:
        ...
    
    @show_mean_line.setter
    def show_mean_line(self, value : bool):
        ...
    
    @property
    def show_outlier_points(self) -> bool:
        ...
    
    @show_outlier_points.setter
    def show_outlier_points(self, value : bool):
        ...
    
    @property
    def show_mean_marker(self) -> bool:
        ...
    
    @show_mean_marker.setter
    def show_mean_marker(self, value : bool):
        ...
    
    @property
    def show_inner_points(self) -> bool:
        ...
    
    @show_inner_points.setter
    def show_inner_points(self, value : bool):
        ...
    
    @property
    def subtotals(self) -> List[int]:
        '''Represents the index of a subtotal data point.'''
        ...
    
    @subtotals.setter
    def subtotals(self, value : List[int]):
        '''Represents the index of a subtotal data point.'''
        ...
    
    @property
    def quartile_calculation(self) -> aspose.cells.charts.QuartileCalculationType:
        ...
    
    @quartile_calculation.setter
    def quartile_calculation(self, value : aspose.cells.charts.QuartileCalculationType):
        ...
    
    @property
    def map_label_layout(self) -> aspose.cells.charts.MapChartLabelLayout:
        ...
    
    @map_label_layout.setter
    def map_label_layout(self, value : aspose.cells.charts.MapChartLabelLayout):
        ...
    
    @property
    def is_interval_left_closed(self) -> bool:
        ...
    
    @is_interval_left_closed.setter
    def is_interval_left_closed(self, value : bool):
        ...
    
    @property
    def map_chart_region_type(self) -> aspose.cells.charts.MapChartRegionType:
        ...
    
    @map_chart_region_type.setter
    def map_chart_region_type(self, value : aspose.cells.charts.MapChartRegionType):
        ...
    
    @property
    def map_chart_projection_type(self) -> aspose.cells.charts.MapChartProjectionType:
        ...
    
    @map_chart_projection_type.setter
    def map_chart_projection_type(self, value : aspose.cells.charts.MapChartProjectionType):
        ...
    
    ...

class Sparkline:
    '''A sparkline represents a tiny chart or graphic in a worksheet cell that provides a visual representation of data.'''
    
    @overload
    def to_image(self, file_name : str, options : aspose.cells.rendering.ImageOrPrintOptions):
        '''Converts a sparkline to an image.
        
        :param file_name: The image file name.
        :param options: The image options'''
        ...
    
    @overload
    def to_image(self, stream : io.RawIOBase, options : aspose.cells.rendering.ImageOrPrintOptions):
        '''Converts a sparkline to an image.
        
        :param stream: The image stream.
        :param options: The image options.'''
        ...
    
    @property
    def data_range(self) -> str:
        ...
    
    @data_range.setter
    def data_range(self, value : str):
        ...
    
    @property
    def row(self) -> int:
        '''Gets the row index of the sparkline.'''
        ...
    
    @property
    def column(self) -> int:
        '''Gets the column index of the sparkline.'''
        ...
    
    ...

class SparklineCollection:
    '''Encapsulates a collection of :py:class:`aspose.cells.charts.Sparkline` objects.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.charts.Sparkline]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.charts.Sparkline], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.Sparkline, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.Sparkline, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Sparkline) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Sparkline, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Sparkline, index : int, count : int) -> int:
        ...
    
    def add(self, data_range : str, row : int, column : int) -> int:
        '''Add a sparkline.
        
        :param data_range: Specifies the new data range of the sparkline.
        :param row: The row index of the location.
        :param column: The column index of the location.'''
        ...
    
    def binary_search(self, item : aspose.cells.charts.Sparkline) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class SparklineGroup:
    ''':py:class:`aspose.cells.charts.Sparkline` is organized into sparkline group. A SparklineGroup contains a variable number of sparkline items.
    A sparkline group specifies the type, display settings and axis settings for the sparklines.'''
    
    def reset_ranges(self, data_range : str, is_vertical : bool, location_range : aspose.cells.CellArea):
        '''Resets the data range and location range of the sparkline group.
        This method will clear original sparkline items in the group and creates new sparkline items for the new ranges.
        
        :param data_range: Specifies the new data range of the sparkline group.
        :param is_vertical: Specifies whether to plot the sparklines from the new data range by row or by column.
        :param location_range: Specifies where the sparklines to be placed.'''
        ...
    
    @property
    def preset_style(self) -> aspose.cells.charts.SparklinePresetStyleType:
        ...
    
    @preset_style.setter
    def preset_style(self, value : aspose.cells.charts.SparklinePresetStyleType):
        ...
    
    @property
    def sparkline_collection(self) -> aspose.cells.charts.SparklineCollection:
        ...
    
    @property
    def sparklines(self) -> aspose.cells.charts.SparklineCollection:
        '''Gets the collection of :py:class:`aspose.cells.charts.Sparkline` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.charts.SparklineType:
        '''Indicates the sparkline type of the sparkline group.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.charts.SparklineType):
        '''Indicates the sparkline type of the sparkline group.'''
        ...
    
    @property
    def plot_empty_cells_type(self) -> aspose.cells.charts.PlotEmptyCellsType:
        ...
    
    @plot_empty_cells_type.setter
    def plot_empty_cells_type(self, value : aspose.cells.charts.PlotEmptyCellsType):
        ...
    
    @property
    def display_hidden(self) -> bool:
        ...
    
    @display_hidden.setter
    def display_hidden(self, value : bool):
        ...
    
    @property
    def show_high_point(self) -> bool:
        ...
    
    @show_high_point.setter
    def show_high_point(self, value : bool):
        ...
    
    @property
    def high_point_color(self) -> aspose.cells.CellsColor:
        ...
    
    @high_point_color.setter
    def high_point_color(self, value : aspose.cells.CellsColor):
        ...
    
    @property
    def show_low_point(self) -> bool:
        ...
    
    @show_low_point.setter
    def show_low_point(self, value : bool):
        ...
    
    @property
    def low_point_color(self) -> aspose.cells.CellsColor:
        ...
    
    @low_point_color.setter
    def low_point_color(self, value : aspose.cells.CellsColor):
        ...
    
    @property
    def show_negative_points(self) -> bool:
        ...
    
    @show_negative_points.setter
    def show_negative_points(self, value : bool):
        ...
    
    @property
    def negative_points_color(self) -> aspose.cells.CellsColor:
        ...
    
    @negative_points_color.setter
    def negative_points_color(self, value : aspose.cells.CellsColor):
        ...
    
    @property
    def show_first_point(self) -> bool:
        ...
    
    @show_first_point.setter
    def show_first_point(self, value : bool):
        ...
    
    @property
    def first_point_color(self) -> aspose.cells.CellsColor:
        ...
    
    @first_point_color.setter
    def first_point_color(self, value : aspose.cells.CellsColor):
        ...
    
    @property
    def show_last_point(self) -> bool:
        ...
    
    @show_last_point.setter
    def show_last_point(self, value : bool):
        ...
    
    @property
    def last_point_color(self) -> aspose.cells.CellsColor:
        ...
    
    @last_point_color.setter
    def last_point_color(self, value : aspose.cells.CellsColor):
        ...
    
    @property
    def show_markers(self) -> bool:
        ...
    
    @show_markers.setter
    def show_markers(self, value : bool):
        ...
    
    @property
    def markers_color(self) -> aspose.cells.CellsColor:
        ...
    
    @markers_color.setter
    def markers_color(self, value : aspose.cells.CellsColor):
        ...
    
    @property
    def series_color(self) -> aspose.cells.CellsColor:
        ...
    
    @series_color.setter
    def series_color(self, value : aspose.cells.CellsColor):
        ...
    
    @property
    def plot_right_to_left(self) -> bool:
        ...
    
    @plot_right_to_left.setter
    def plot_right_to_left(self, value : bool):
        ...
    
    @property
    def line_weight(self) -> float:
        ...
    
    @line_weight.setter
    def line_weight(self, value : float):
        ...
    
    @property
    def horizontal_axis_color(self) -> aspose.cells.CellsColor:
        ...
    
    @horizontal_axis_color.setter
    def horizontal_axis_color(self, value : aspose.cells.CellsColor):
        ...
    
    @property
    def show_horizontal_axis(self) -> bool:
        ...
    
    @show_horizontal_axis.setter
    def show_horizontal_axis(self, value : bool):
        ...
    
    @property
    def horizontal_axis_date_range(self) -> str:
        ...
    
    @horizontal_axis_date_range.setter
    def horizontal_axis_date_range(self, value : str):
        ...
    
    @property
    def vertical_axis_max_value_type(self) -> aspose.cells.charts.SparklineAxisMinMaxType:
        ...
    
    @vertical_axis_max_value_type.setter
    def vertical_axis_max_value_type(self, value : aspose.cells.charts.SparklineAxisMinMaxType):
        ...
    
    @property
    def vertical_axis_max_value(self) -> float:
        ...
    
    @vertical_axis_max_value.setter
    def vertical_axis_max_value(self, value : float):
        ...
    
    @property
    def vertical_axis_min_value_type(self) -> aspose.cells.charts.SparklineAxisMinMaxType:
        ...
    
    @vertical_axis_min_value_type.setter
    def vertical_axis_min_value_type(self, value : aspose.cells.charts.SparklineAxisMinMaxType):
        ...
    
    @property
    def vertical_axis_min_value(self) -> float:
        ...
    
    @vertical_axis_min_value.setter
    def vertical_axis_min_value(self, value : float):
        ...
    
    ...

class SparklineGroupCollection:
    '''Encapsulates a collection of :py:class:`aspose.cells.charts.SparklineGroup` objects.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.charts.SparklineGroup]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.charts.SparklineGroup], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.SparklineGroup, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.SparklineGroup, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.SparklineGroup) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.SparklineGroup, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.SparklineGroup, index : int, count : int) -> int:
        ...
    
    def add(self, type : aspose.cells.charts.SparklineType, data_range : str, is_vertical : bool, location_range : aspose.cells.CellArea) -> int:
        '''Adds an :py:class:`aspose.cells.charts.SparklineGroup` item to the collection.
        
        :param type: Specifies the type of the Sparkline group.
        :param data_range: Specifies the data range of the sparkline group.
        :param is_vertical: Specifies whether to plot the sparklines from the data range by row or by column.
        :param location_range: Specifies where the sparklines to be placed.
        :returns: :py:class:`aspose.cells.charts.SparklineGroup` object index.'''
        ...
    
    def clear_sparklines(self, cell_area : aspose.cells.CellArea):
        '''Clears the sparklines that is inside an area of cells.
        
        :param cell_area: Specifies the area of cells'''
        ...
    
    def clear_sparkline_groups(self, cell_area : aspose.cells.CellArea):
        '''Clears the sparkline groups that overlaps an area of cells.
        
        :param cell_area: Specifies the area of cells'''
        ...
    
    def binary_search(self, item : aspose.cells.charts.SparklineGroup) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class TickLabelItem:
    '''Include information of a Ticklabel item'''
    
    @property
    def x(self) -> float:
        '''X coordinates of Ticklabel item in ratio of chart width.'''
        ...
    
    @property
    def y(self) -> float:
        '''Y coordinates of Ticklabel item in ratio of chart height.'''
        ...
    
    @property
    def width(self) -> float:
        '''Width of Ticklabel item in ratio of chart width.'''
        ...
    
    @property
    def height(self) -> float:
        '''Height of Ticklabel item in ratio of chart height.'''
        ...
    
    ...

class TickLabels:
    '''Represents the tick-mark labels associated with tick marks on a chart axis.'''
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Returns a :py:attr:`aspose.cells.charts.TickLabels.font` object that represents the font of the specified TickLabels object.'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def rotation_angle(self) -> int:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : int):
        ...
    
    @property
    def is_automatic_rotation(self) -> bool:
        ...
    
    @is_automatic_rotation.setter
    def is_automatic_rotation(self, value : bool):
        ...
    
    @property
    def number_format(self) -> str:
        ...
    
    @number_format.setter
    def number_format(self, value : str):
        ...
    
    @property
    def number(self) -> int:
        '''Represents the format number for the TickLabels object.'''
        ...
    
    @number.setter
    def number(self, value : int):
        '''Represents the format number for the TickLabels object.'''
        ...
    
    @property
    def number_format_linked(self) -> bool:
        ...
    
    @number_format_linked.setter
    def number_format_linked(self, value : bool):
        ...
    
    @property
    def display_number_format(self) -> str:
        ...
    
    @property
    def offset(self) -> int:
        '''Gets and sets the distance of labels from the axis.'''
        ...
    
    @offset.setter
    def offset(self, value : int):
        '''Gets and sets the distance of labels from the axis.'''
        ...
    
    @property
    def text_direction(self) -> aspose.cells.TextDirectionType:
        ...
    
    @text_direction.setter
    def text_direction(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def reading_order(self) -> aspose.cells.TextDirectionType:
        ...
    
    @reading_order.setter
    def reading_order(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def direction_type(self) -> aspose.cells.charts.ChartTextDirectionType:
        ...
    
    @direction_type.setter
    def direction_type(self, value : aspose.cells.charts.ChartTextDirectionType):
        ...
    
    @property
    def tick_label_items(self) -> List[aspose.cells.charts.TickLabelItem]:
        ...
    
    ...

class Title(ChartTextFrame):
    '''Encapsulates the object that represents the title of chart or axis.'''
    
    @overload
    def characters(self) -> List[aspose.cells.FontSetting]:
        '''Gets rich text formatting of this Title.
        
        :returns: returns FontSetting array'''
        ...
    
    @overload
    def characters(self, start_index : int, length : int) -> aspose.cells.FontSetting:
        '''Returns a Characters object that represents a range of characters within the text.
        
        :param start_index: The index of the start of the character.
        :param length: The number of characters.
        :returns: Characters object.'''
        ...
    
    def set_position_auto(self):
        '''Set position of the frame to automatic'''
        ...
    
    @property
    def is_inner_mode(self) -> bool:
        ...
    
    @is_inner_mode.setter
    def is_inner_mode(self, value : bool):
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def area(self) -> aspose.cells.drawing.Area:
        '''Gets the :py:attr:`aspose.cells.charts.ChartFrame.area`.'''
        ...
    
    @property
    def text_font(self) -> aspose.cells.Font:
        ...
    
    @property
    def text_options(self) -> aspose.cells.drawing.texts.TextOptions:
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Gets a :py:attr:`aspose.cells.charts.ChartFrame.font` object of the specified ChartFrame object.'''
        ...
    
    @property
    def auto_scale_font(self) -> bool:
        ...
    
    @auto_scale_font.setter
    def auto_scale_font(self, value : bool):
        ...
    
    @property
    def background_mode(self) -> aspose.cells.charts.BackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.cells.charts.BackgroundMode):
        ...
    
    @property
    def background(self) -> aspose.cells.charts.BackgroundMode:
        '''Gets and sets the display mode of the background'''
        ...
    
    @background.setter
    def background(self, value : aspose.cells.charts.BackgroundMode):
        '''Gets and sets the display mode of the background'''
        ...
    
    @property
    def is_automatic_size(self) -> bool:
        ...
    
    @is_automatic_size.setter
    def is_automatic_size(self, value : bool):
        ...
    
    @property
    def x(self) -> int:
        '''Gets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Sets the x coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Sets the y coordinate of the upper left corner in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of frame in units of 1/4000 of the chart area.'''
        ...
    
    @property
    def shadow(self) -> bool:
        '''True if the frame has a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''True if the frame has a shadow.'''
        ...
    
    @property
    def shape_properties(self) -> aspose.cells.drawing.ShapePropertyCollection:
        ...
    
    @property
    def is_default_pos_be_set(self) -> bool:
        ...
    
    @property
    def default_x(self) -> int:
        ...
    
    @property
    def default_y(self) -> int:
        ...
    
    @property
    def default_width(self) -> int:
        ...
    
    @property
    def default_height(self) -> int:
        ...
    
    @property
    def is_auto_text(self) -> bool:
        ...
    
    @is_auto_text.setter
    def is_auto_text(self, value : bool):
        ...
    
    @property
    def is_deleted(self) -> bool:
        ...
    
    @is_deleted.setter
    def is_deleted(self, value : bool):
        ...
    
    @property
    def text_horizontal_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_horizontal_alignment.setter
    def text_horizontal_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def text_vertical_alignment(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_vertical_alignment.setter
    def text_vertical_alignment(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def rotation_angle(self) -> int:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : int):
        ...
    
    @property
    def is_automatic_rotation(self) -> bool:
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text of display unit label.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text of display unit label.'''
        ...
    
    @property
    def linked_source(self) -> str:
        ...
    
    @linked_source.setter
    def linked_source(self, value : str):
        ...
    
    @property
    def text_direction(self) -> aspose.cells.TextDirectionType:
        ...
    
    @text_direction.setter
    def text_direction(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def reading_order(self) -> aspose.cells.TextDirectionType:
        ...
    
    @reading_order.setter
    def reading_order(self, value : aspose.cells.TextDirectionType):
        ...
    
    @property
    def direction_type(self) -> aspose.cells.charts.ChartTextDirectionType:
        ...
    
    @direction_type.setter
    def direction_type(self, value : aspose.cells.charts.ChartTextDirectionType):
        ...
    
    @property
    def is_text_wrapped(self) -> bool:
        ...
    
    @is_text_wrapped.setter
    def is_text_wrapped(self, value : bool):
        ...
    
    @property
    def is_resize_shape_to_fit_text(self) -> bool:
        ...
    
    @is_resize_shape_to_fit_text.setter
    def is_resize_shape_to_fit_text(self, value : bool):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def over_lay(self) -> bool:
        ...
    
    @over_lay.setter
    def over_lay(self, value : bool):
        ...
    
    ...

class Trendline(aspose.cells.drawing.Line):
    '''Represents a trendline in a chart.'''
    
    @property
    def compound_type(self) -> aspose.cells.drawing.MsoLineStyle:
        ...
    
    @compound_type.setter
    def compound_type(self, value : aspose.cells.drawing.MsoLineStyle):
        ...
    
    @property
    def dash_type(self) -> aspose.cells.drawing.MsoLineDashStyle:
        ...
    
    @dash_type.setter
    def dash_type(self, value : aspose.cells.drawing.MsoLineDashStyle):
        ...
    
    @property
    def cap_type(self) -> aspose.cells.drawing.LineCapType:
        ...
    
    @cap_type.setter
    def cap_type(self, value : aspose.cells.drawing.LineCapType):
        ...
    
    @property
    def join_type(self) -> aspose.cells.drawing.LineJoinType:
        ...
    
    @join_type.setter
    def join_type(self, value : aspose.cells.drawing.LineJoinType):
        ...
    
    @property
    def begin_type(self) -> aspose.cells.drawing.MsoArrowheadStyle:
        ...
    
    @begin_type.setter
    def begin_type(self, value : aspose.cells.drawing.MsoArrowheadStyle):
        ...
    
    @property
    def end_type(self) -> aspose.cells.drawing.MsoArrowheadStyle:
        ...
    
    @end_type.setter
    def end_type(self, value : aspose.cells.drawing.MsoArrowheadStyle):
        ...
    
    @property
    def begin_arrow_length(self) -> aspose.cells.drawing.MsoArrowheadLength:
        ...
    
    @begin_arrow_length.setter
    def begin_arrow_length(self, value : aspose.cells.drawing.MsoArrowheadLength):
        ...
    
    @property
    def end_arrow_length(self) -> aspose.cells.drawing.MsoArrowheadLength:
        ...
    
    @end_arrow_length.setter
    def end_arrow_length(self, value : aspose.cells.drawing.MsoArrowheadLength):
        ...
    
    @property
    def begin_arrow_width(self) -> aspose.cells.drawing.MsoArrowheadWidth:
        ...
    
    @begin_arrow_width.setter
    def begin_arrow_width(self, value : aspose.cells.drawing.MsoArrowheadWidth):
        ...
    
    @property
    def end_arrow_width(self) -> aspose.cells.drawing.MsoArrowheadWidth:
        ...
    
    @end_arrow_width.setter
    def end_arrow_width(self, value : aspose.cells.drawing.MsoArrowheadWidth):
        ...
    
    @property
    def theme_color(self) -> aspose.cells.ThemeColor:
        ...
    
    @theme_color.setter
    def theme_color(self, value : aspose.cells.ThemeColor):
        ...
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Represents the :py:class:`aspose.pydrawing.Color` of the line.'''
        ...
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color):
        '''Represents the :py:class:`aspose.pydrawing.Color` of the line.'''
        ...
    
    @property
    def transparency(self) -> float:
        '''Returns the degree of transparency of the line as a value from 0.0 (opaque) through 1.0 (clear).'''
        ...
    
    @transparency.setter
    def transparency(self, value : float):
        '''Returns or sets the degree of transparency of the line as a value from 0.0 (opaque) through 1.0 (clear).'''
        ...
    
    @property
    def style(self) -> aspose.cells.drawing.LineType:
        '''Represents the style of the line.'''
        ...
    
    @style.setter
    def style(self, value : aspose.cells.drawing.LineType):
        '''Represents the style of the line.'''
        ...
    
    @property
    def weight(self) -> aspose.cells.drawing.WeightType:
        '''Gets the :py:class:`aspose.cells.drawing.WeightType` of the line.'''
        ...
    
    @weight.setter
    def weight(self, value : aspose.cells.drawing.WeightType):
        '''Sets the :py:class:`aspose.cells.drawing.WeightType` of the line.'''
        ...
    
    @property
    def weight_pt(self) -> float:
        ...
    
    @weight_pt.setter
    def weight_pt(self, value : float):
        ...
    
    @property
    def weight_px(self) -> float:
        ...
    
    @weight_px.setter
    def weight_px(self, value : float):
        ...
    
    @property
    def formatting_type(self) -> aspose.cells.charts.ChartLineFormattingType:
        ...
    
    @formatting_type.setter
    def formatting_type(self, value : aspose.cells.charts.ChartLineFormattingType):
        ...
    
    @property
    def is_automatic_color(self) -> bool:
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def is_auto(self) -> bool:
        ...
    
    @is_auto.setter
    def is_auto(self, value : bool):
        ...
    
    @property
    def gradient_fill(self) -> aspose.cells.drawing.GradientFill:
        ...
    
    @property
    def is_name_auto(self) -> bool:
        ...
    
    @is_name_auto.setter
    def is_name_auto(self, value : bool):
        ...
    
    @property
    def type(self) -> aspose.cells.charts.TrendlineType:
        '''Returns the trendline type.'''
        ...
    
    @property
    def name(self) -> str:
        '''Returns the name of the trendline.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Returns the name of the trendline.'''
        ...
    
    @property
    def order(self) -> int:
        '''Returns the trendline order (an integer greater than 1) when the trendline type is Polynomial.
        The order must be between 2 and 6.'''
        ...
    
    @order.setter
    def order(self, value : int):
        '''Returns or sets the trendline order (an integer greater than 1) when the trendline type is Polynomial.
        The order must be between 2 and 6.'''
        ...
    
    @property
    def period(self) -> int:
        '''Returns the period for the moving-average trendline.'''
        ...
    
    @period.setter
    def period(self, value : int):
        '''Returns or sets the period for the moving-average trendline.'''
        ...
    
    @property
    def forward(self) -> float:
        '''Returns the number of periods (or units on a scatter chart) that the trendline extends forward.
        The number of periods must be greater than or equal to zero.'''
        ...
    
    @forward.setter
    def forward(self, value : float):
        '''Returns or sets the number of periods (or units on a scatter chart) that the trendline extends forward.
        The number of periods must be greater than or equal to zero.'''
        ...
    
    @property
    def backward(self) -> float:
        '''Returns the number of periods (or units on a scatter chart) that the trendline extends backward.
        The number of periods must be greater than or equal to zero.
        If the chart type is column ,the number of periods must be between 0 and 0.5'''
        ...
    
    @backward.setter
    def backward(self, value : float):
        '''Returns or sets the number of periods (or units on a scatter chart) that the trendline extends backward.
        The number of periods must be greater than or equal to zero.
        If the chart type is column ,the number of periods must be between 0 and 0.5'''
        ...
    
    @property
    def display_equation(self) -> bool:
        ...
    
    @display_equation.setter
    def display_equation(self, value : bool):
        ...
    
    @property
    def display_r_squared(self) -> bool:
        ...
    
    @display_r_squared.setter
    def display_r_squared(self, value : bool):
        ...
    
    @property
    def intercept(self) -> float:
        '''Returns the point where the trendline crosses the value axis.'''
        ...
    
    @intercept.setter
    def intercept(self, value : float):
        '''Returns or sets the point where the trendline crosses the value axis.'''
        ...
    
    @property
    def data_labels(self) -> aspose.cells.charts.DataLabels:
        ...
    
    @property
    def legend_entry(self) -> aspose.cells.charts.LegendEntry:
        ...
    
    ...

class TrendlineCollection:
    '''Represents a collection of all the :py:class:`aspose.cells.charts.Trendline` objects for the specified data series.'''
    
    @overload
    def add(self, type : aspose.cells.charts.TrendlineType) -> int:
        '''Adds a :py:class:`aspose.cells.charts.Trendline` object to this collection with specified type.
        
        :param type: Trendline type.
        :returns: :py:class:`aspose.cells.charts.Trendline` object index.'''
        ...
    
    @overload
    def add(self, type : aspose.cells.charts.TrendlineType, name : str) -> int:
        '''Adds a :py:class:`aspose.cells.charts.Trendline` object to this collection with specified type and name.
        
        :param type: Trendline type.
        :param name: Trendline name.
        :returns: :py:class:`aspose.cells.charts.Trendline` object index.'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.charts.Trendline]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.charts.Trendline], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.Trendline, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.charts.Trendline, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Trendline) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Trendline, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.charts.Trendline, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.charts.Trendline) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class Walls(Floor):
    '''Encapsulates the object that represents the walls of a 3-D chart.'''
    
    def get_cube_point_count(self) -> int:
        '''Gets the number of cube points after calls Chart.Calculate() method.'''
        ...
    
    def get_cube_point_x_px(self, index : int) -> float:
        '''Gets x-coordinate of the apex point of walls cube after calls Chart.Calculate() method.
        The number of apex points of walls cube is eight'''
        ...
    
    def get_cube_point_y_px(self, index : int) -> float:
        '''Gets y-coordinate of the apex point of walls cube after calls Chart.Calculate() method.
        The number of apex points of walls cube is eight.'''
        ...
    
    @property
    def background_color(self) -> aspose.pydrawing.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.pydrawing.Color):
        ...
    
    @property
    def foreground_color(self) -> aspose.pydrawing.Color:
        ...
    
    @foreground_color.setter
    def foreground_color(self, value : aspose.pydrawing.Color):
        ...
    
    @property
    def formatting(self) -> aspose.cells.charts.FormattingType:
        '''Represents the formatting of the area.'''
        ...
    
    @formatting.setter
    def formatting(self, value : aspose.cells.charts.FormattingType):
        '''Represents the formatting of the area.'''
        ...
    
    @property
    def invert_if_negative(self) -> bool:
        ...
    
    @invert_if_negative.setter
    def invert_if_negative(self, value : bool):
        ...
    
    @property
    def fill_format(self) -> aspose.cells.drawing.FillFormat:
        ...
    
    @property
    def transparency(self) -> float:
        '''Returns the degree of transparency of the area as a value from 0.0 (opaque) through 1.0 (clear).'''
        ...
    
    @transparency.setter
    def transparency(self, value : float):
        '''Returns or sets the degree of transparency of the area as a value from 0.0 (opaque) through 1.0 (clear).'''
        ...
    
    @property
    def border(self) -> aspose.cells.drawing.Line:
        '''Gets the border :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @border.setter
    def border(self, value : aspose.cells.drawing.Line):
        '''Sets the border :py:class:`aspose.cells.drawing.Line`.'''
        ...
    
    @property
    def center_x(self) -> int:
        ...
    
    @property
    def center_y(self) -> int:
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of left to right in units of 1/4000 of chart's width after calls Chart.Calculate() method.'''
        ...
    
    @property
    def depth(self) -> int:
        '''Gets the depth front to back in units of 1/4000 of chart's width after calls Chart.Calculate() method.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of top to bottom in units of 1/4000 of chart's height after calls Chart.Calculate() method.'''
        ...
    
    @property
    def center_x_px(self) -> int:
        ...
    
    @property
    def center_y_px(self) -> int:
        ...
    
    @property
    def width_px(self) -> int:
        ...
    
    @property
    def depth_px(self) -> int:
        ...
    
    @property
    def height_px(self) -> int:
        ...
    
    ...

class AxisType:
    '''Represents the axis type.'''
    
    @classmethod
    @property
    def CATEGORY(cls) -> AxisType:
        '''Category axis'''
        ...
    
    @classmethod
    @property
    def VALUE(cls) -> AxisType:
        '''Value axis'''
        ...
    
    @classmethod
    @property
    def SERIES(cls) -> AxisType:
        '''Series axis'''
        ...
    
    ...

class BackgroundMode:
    '''Represents the display mode of the background.'''
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> BackgroundMode:
        '''Automatic'''
        ...
    
    @classmethod
    @property
    def OPAQUE(cls) -> BackgroundMode:
        '''Opaque'''
        ...
    
    @classmethod
    @property
    def TRANSPARENT(cls) -> BackgroundMode:
        '''Transparent'''
        ...
    
    ...

class Bar3DShapeType:
    '''Represents the shape used with the 3-D bar or column chart.'''
    
    @classmethod
    @property
    def BOX(cls) -> Bar3DShapeType:
        '''Box'''
        ...
    
    @classmethod
    @property
    def PYRAMID_TO_POINT(cls) -> Bar3DShapeType:
        '''PyramidToPoint'''
        ...
    
    @classmethod
    @property
    def PYRAMID_TO_MAX(cls) -> Bar3DShapeType:
        '''PyramidToMax'''
        ...
    
    @classmethod
    @property
    def CYLINDER(cls) -> Bar3DShapeType:
        '''Cylinder'''
        ...
    
    @classmethod
    @property
    def CONE_TO_POINT(cls) -> Bar3DShapeType:
        '''ConeToPoint'''
        ...
    
    @classmethod
    @property
    def CONE_TO_MAX(cls) -> Bar3DShapeType:
        '''ConeToMax'''
        ...
    
    ...

class BubbleSizeRepresents:
    '''Represents what the bubble size represents on a bubble chart.'''
    
    @classmethod
    @property
    def SIZE_IS_AREA(cls) -> BubbleSizeRepresents:
        '''Represents the value of :py:attr:`aspose.cells.charts.Series.bubble_sizes` is area of the bubble.'''
        ...
    
    @classmethod
    @property
    def SIZE_IS_WIDTH(cls) -> BubbleSizeRepresents:
        '''Represents the value of :py:attr:`aspose.cells.charts.Series.bubble_sizes` is width of the bubble.'''
        ...
    
    ...

class CategoryType:
    '''Represents the category axis type.'''
    
    @classmethod
    @property
    def AUTOMATIC_SCALE(cls) -> CategoryType:
        '''AutomaticScale'''
        ...
    
    @classmethod
    @property
    def CATEGORY_SCALE(cls) -> CategoryType:
        '''CategoryScale'''
        ...
    
    @classmethod
    @property
    def TIME_SCALE(cls) -> CategoryType:
        '''TimeScale'''
        ...
    
    ...

class ChartLineFormattingType:
    '''Represents line format type of chart line.'''
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> ChartLineFormattingType:
        '''Represents automatic formatting type.'''
        ...
    
    @classmethod
    @property
    def SOLID(cls) -> ChartLineFormattingType:
        '''Represents solid formatting type.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> ChartLineFormattingType:
        '''Represents none formatting type.'''
        ...
    
    @classmethod
    @property
    def GRADIENT(cls) -> ChartLineFormattingType:
        '''Gradient'''
        ...
    
    ...

class ChartMarkerType:
    '''Represents the marker style in a line chart, scatter chart, or radar chart.'''
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> ChartMarkerType:
        '''Automatic markers.'''
        ...
    
    @classmethod
    @property
    def CIRCLE(cls) -> ChartMarkerType:
        '''Circular markers.'''
        ...
    
    @classmethod
    @property
    def DASH(cls) -> ChartMarkerType:
        '''Long bar markers'''
        ...
    
    @classmethod
    @property
    def DIAMOND(cls) -> ChartMarkerType:
        '''Diamond-shaped markers.'''
        ...
    
    @classmethod
    @property
    def DOT(cls) -> ChartMarkerType:
        '''Short bar markers.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> ChartMarkerType:
        '''No markers.'''
        ...
    
    @classmethod
    @property
    def SQUARE_PLUS(cls) -> ChartMarkerType:
        '''Square markers with a plus sign.'''
        ...
    
    @classmethod
    @property
    def SQUARE(cls) -> ChartMarkerType:
        '''Square markers.'''
        ...
    
    @classmethod
    @property
    def SQUARE_STAR(cls) -> ChartMarkerType:
        '''Square markers with an asterisk.'''
        ...
    
    @classmethod
    @property
    def TRIANGLE(cls) -> ChartMarkerType:
        '''Triangular markers.'''
        ...
    
    @classmethod
    @property
    def SQUARE_X(cls) -> ChartMarkerType:
        '''Square markers with an X.'''
        ...
    
    @classmethod
    @property
    def PICTURE(cls) -> ChartMarkerType:
        '''Picture'''
        ...
    
    ...

class ChartSplitType:
    '''Represents the way the two sections of either a pie of pie chart or a bar of pie chart are split.'''
    
    @classmethod
    @property
    def POSITION(cls) -> ChartSplitType:
        '''Represents the data points shall be split between the pie
        and the second chart by putting the last Split Position
        of the data points in the second chart'''
        ...
    
    @classmethod
    @property
    def VALUE(cls) -> ChartSplitType:
        '''Represents the data points shall be split between the pie
        and the second chart by putting the data points with
        value less than Split Position in the second chart.'''
        ...
    
    @classmethod
    @property
    def PERCENT_VALUE(cls) -> ChartSplitType:
        '''Represents the data points shall be split between the pie
        and the second chart by putting the points with
        percentage less than Split Position percent in the
        second chart.'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> ChartSplitType:
        '''Represents the data points shall be split between the pie
        and the second chart according to the Custom Split
        values.'''
        ...
    
    @classmethod
    @property
    def AUTO(cls) -> ChartSplitType:
        '''Represents the data points shall be split using the default
        mechanism for this chart type.'''
        ...
    
    ...

class ChartTextDirectionType:
    '''Represents the text direction type of the chart.'''
    
    @classmethod
    @property
    def HORIZONTAL(cls) -> ChartTextDirectionType:
        '''Horizontal direction type.'''
        ...
    
    @classmethod
    @property
    def VERTICAL(cls) -> ChartTextDirectionType:
        '''Vertical direction type.'''
        ...
    
    @classmethod
    @property
    def ROTATE90(cls) -> ChartTextDirectionType:
        '''Rotate 90 angle.'''
        ...
    
    @classmethod
    @property
    def ROTATE270(cls) -> ChartTextDirectionType:
        '''Rotate 270 angle.'''
        ...
    
    @classmethod
    @property
    def STACKED(cls) -> ChartTextDirectionType:
        '''Stacked text.'''
        ...
    
    ...

class ChartType:
    '''Enumerates all chart types used in Excel.'''
    
    @classmethod
    @property
    def AREA(cls) -> ChartType:
        '''Represents Area Chart.'''
        ...
    
    @classmethod
    @property
    def AREA_STACKED(cls) -> ChartType:
        '''Represents Stacked Area Chart.'''
        ...
    
    @classmethod
    @property
    def AREA_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Area Chart.'''
        ...
    
    @classmethod
    @property
    def AREA_3D(cls) -> ChartType:
        '''Represents 3D Area Chart.'''
        ...
    
    @classmethod
    @property
    def AREA_3D_STACKED(cls) -> ChartType:
        '''Represents 3D Stacked Area Chart.'''
        ...
    
    @classmethod
    @property
    def AREA_3D100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 3D 100% Stacked Area Chart.'''
        ...
    
    @classmethod
    @property
    def BAR(cls) -> ChartType:
        '''Represents Bar Chart: Clustered Bar Chart.'''
        ...
    
    @classmethod
    @property
    def BAR_STACKED(cls) -> ChartType:
        '''Represents Stacked Bar Chart.'''
        ...
    
    @classmethod
    @property
    def BAR_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Bar Chart.'''
        ...
    
    @classmethod
    @property
    def BAR_3D_CLUSTERED(cls) -> ChartType:
        '''Represents 3D Clustered Bar Chart.'''
        ...
    
    @classmethod
    @property
    def BAR_3D_STACKED(cls) -> ChartType:
        '''Represents 3D Stacked Bar Chart.'''
        ...
    
    @classmethod
    @property
    def BAR_3D100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 3D 100% Stacked Bar Chart.'''
        ...
    
    @classmethod
    @property
    def BUBBLE(cls) -> ChartType:
        '''Represents Bubble Chart.'''
        ...
    
    @classmethod
    @property
    def BUBBLE_3D(cls) -> ChartType:
        '''Represents 3D Bubble Chart.'''
        ...
    
    @classmethod
    @property
    def COLUMN(cls) -> ChartType:
        '''Represents Column Chart: Clustered Column Chart.'''
        ...
    
    @classmethod
    @property
    def COLUMN_STACKED(cls) -> ChartType:
        '''Represents Stacked Column Chart.'''
        ...
    
    @classmethod
    @property
    def COLUMN_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Column Chart.'''
        ...
    
    @classmethod
    @property
    def COLUMN_3D(cls) -> ChartType:
        '''Represents 3D Column Chart.'''
        ...
    
    @classmethod
    @property
    def COLUMN_3D_CLUSTERED(cls) -> ChartType:
        '''Represents 3D Clustered Column Chart.'''
        ...
    
    @classmethod
    @property
    def COLUMN_3D_STACKED(cls) -> ChartType:
        '''Represents 3D Stacked Column Chart.'''
        ...
    
    @classmethod
    @property
    def COLUMN_3D100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 3D 100% Stacked Column Chart.'''
        ...
    
    @classmethod
    @property
    def CONE(cls) -> ChartType:
        '''Represents Cone Chart.'''
        ...
    
    @classmethod
    @property
    def CONE_STACKED(cls) -> ChartType:
        '''Represents Stacked Cone Chart.'''
        ...
    
    @classmethod
    @property
    def CONE_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Cone Chart.'''
        ...
    
    @classmethod
    @property
    def CONICAL_BAR(cls) -> ChartType:
        '''Represents Conical Bar Chart.'''
        ...
    
    @classmethod
    @property
    def CONICAL_BAR_STACKED(cls) -> ChartType:
        '''Represents Stacked Conical Bar Chart.'''
        ...
    
    @classmethod
    @property
    def CONICAL_BAR_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Conical Bar Chart.'''
        ...
    
    @classmethod
    @property
    def CONICAL_COLUMN_3D(cls) -> ChartType:
        '''Represents 3D Conical Column Chart.'''
        ...
    
    @classmethod
    @property
    def CYLINDER(cls) -> ChartType:
        '''Represents Cylinder Chart.'''
        ...
    
    @classmethod
    @property
    def CYLINDER_STACKED(cls) -> ChartType:
        '''Represents Stacked Cylinder Chart.'''
        ...
    
    @classmethod
    @property
    def CYLINDER_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Cylinder Chart.'''
        ...
    
    @classmethod
    @property
    def CYLINDRICAL_BAR(cls) -> ChartType:
        '''Represents Cylindrical Bar Chart.'''
        ...
    
    @classmethod
    @property
    def CYLINDRICAL_BAR_STACKED(cls) -> ChartType:
        '''Represents Stacked Cylindrical Bar Chart.'''
        ...
    
    @classmethod
    @property
    def CYLINDRICAL_BAR_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Cylindrical Bar Chart.'''
        ...
    
    @classmethod
    @property
    def CYLINDRICAL_COLUMN_3D(cls) -> ChartType:
        '''Represents 3D Cylindrical Column Chart.'''
        ...
    
    @classmethod
    @property
    def DOUGHNUT(cls) -> ChartType:
        '''Represents Doughnut Chart.'''
        ...
    
    @classmethod
    @property
    def DOUGHNUT_EXPLODED(cls) -> ChartType:
        '''Represents Exploded Doughnut Chart.'''
        ...
    
    @classmethod
    @property
    def LINE(cls) -> ChartType:
        '''Represents Line Chart.'''
        ...
    
    @classmethod
    @property
    def LINE_STACKED(cls) -> ChartType:
        '''Represents Stacked Line Chart.'''
        ...
    
    @classmethod
    @property
    def LINE_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Line Chart.'''
        ...
    
    @classmethod
    @property
    def LINE_WITH_DATA_MARKERS(cls) -> ChartType:
        '''Represents Line Chart with data markers.'''
        ...
    
    @classmethod
    @property
    def LINE_STACKED_WITH_DATA_MARKERS(cls) -> ChartType:
        '''Represents Stacked Line Chart with data markers.'''
        ...
    
    @classmethod
    @property
    def LINE_100_PERCENT_STACKED_WITH_DATA_MARKERS(cls) -> ChartType:
        '''Represents 100% Stacked Line Chart with data markers.'''
        ...
    
    @classmethod
    @property
    def LINE_3D(cls) -> ChartType:
        '''Represents 3D Line Chart.'''
        ...
    
    @classmethod
    @property
    def PIE(cls) -> ChartType:
        '''Represents Pie Chart.'''
        ...
    
    @classmethod
    @property
    def PIE_3D(cls) -> ChartType:
        '''Represents 3D Pie Chart.'''
        ...
    
    @classmethod
    @property
    def PIE_PIE(cls) -> ChartType:
        '''Represents Pie of Pie Chart.'''
        ...
    
    @classmethod
    @property
    def PIE_EXPLODED(cls) -> ChartType:
        '''Represents Exploded Pie Chart.'''
        ...
    
    @classmethod
    @property
    def PIE_3D_EXPLODED(cls) -> ChartType:
        '''Represents 3D Exploded Pie Chart.'''
        ...
    
    @classmethod
    @property
    def PIE_BAR(cls) -> ChartType:
        '''Represents Bar of Pie Chart.'''
        ...
    
    @classmethod
    @property
    def PYRAMID(cls) -> ChartType:
        '''Represents Pyramid Chart.'''
        ...
    
    @classmethod
    @property
    def PYRAMID_STACKED(cls) -> ChartType:
        '''Represents Stacked Pyramid Chart.'''
        ...
    
    @classmethod
    @property
    def PYRAMID_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Pyramid Chart.'''
        ...
    
    @classmethod
    @property
    def PYRAMID_BAR(cls) -> ChartType:
        '''Represents Pyramid Bar Chart.'''
        ...
    
    @classmethod
    @property
    def PYRAMID_BAR_STACKED(cls) -> ChartType:
        '''Represents Stacked Pyramid Bar Chart.'''
        ...
    
    @classmethod
    @property
    def PYRAMID_BAR_100_PERCENT_STACKED(cls) -> ChartType:
        '''Represents 100% Stacked Pyramid Bar Chart.'''
        ...
    
    @classmethod
    @property
    def PYRAMID_COLUMN_3D(cls) -> ChartType:
        '''Represents 3D Pyramid Column Chart.'''
        ...
    
    @classmethod
    @property
    def RADAR(cls) -> ChartType:
        '''Represents Radar Chart.'''
        ...
    
    @classmethod
    @property
    def RADAR_WITH_DATA_MARKERS(cls) -> ChartType:
        '''Represents Radar Chart with data markers.'''
        ...
    
    @classmethod
    @property
    def RADAR_FILLED(cls) -> ChartType:
        '''Represents Filled Radar Chart.'''
        ...
    
    @classmethod
    @property
    def SCATTER(cls) -> ChartType:
        '''Represents Scatter Chart.'''
        ...
    
    @classmethod
    @property
    def SCATTER_CONNECTED_BY_CURVES_WITH_DATA_MARKER(cls) -> ChartType:
        '''Represents Scatter Chart connected by curves, with data markers.'''
        ...
    
    @classmethod
    @property
    def SCATTER_CONNECTED_BY_CURVES_WITHOUT_DATA_MARKER(cls) -> ChartType:
        '''Represents Scatter Chart connected by curves, without data markers.'''
        ...
    
    @classmethod
    @property
    def SCATTER_CONNECTED_BY_LINES_WITH_DATA_MARKER(cls) -> ChartType:
        '''Represents Scatter Chart connected by lines, with data markers.'''
        ...
    
    @classmethod
    @property
    def SCATTER_CONNECTED_BY_LINES_WITHOUT_DATA_MARKER(cls) -> ChartType:
        '''Represents Scatter Chart connected by lines, without data markers.'''
        ...
    
    @classmethod
    @property
    def STOCK_HIGH_LOW_CLOSE(cls) -> ChartType:
        '''Represents High-Low-Close Stock Chart.'''
        ...
    
    @classmethod
    @property
    def STOCK_OPEN_HIGH_LOW_CLOSE(cls) -> ChartType:
        '''Represents Open-High-Low-Close Stock Chart.'''
        ...
    
    @classmethod
    @property
    def STOCK_VOLUME_HIGH_LOW_CLOSE(cls) -> ChartType:
        '''Represents Volume-High-Low-Close Stock Chart.'''
        ...
    
    @classmethod
    @property
    def STOCK_VOLUME_OPEN_HIGH_LOW_CLOSE(cls) -> ChartType:
        '''Represents Volume-Open-High-Low-Close Stock Chart.'''
        ...
    
    @classmethod
    @property
    def SURFACE_3D(cls) -> ChartType:
        '''Represents Surface Chart: 3D Surface Chart.'''
        ...
    
    @classmethod
    @property
    def SURFACE_WIREFRAME_3D(cls) -> ChartType:
        '''Represents Wireframe 3D Surface Chart.'''
        ...
    
    @classmethod
    @property
    def SURFACE_CONTOUR(cls) -> ChartType:
        '''Represents Contour Chart.'''
        ...
    
    @classmethod
    @property
    def SURFACE_CONTOUR_WIREFRAME(cls) -> ChartType:
        '''Represents Wireframe Contour Chart.'''
        ...
    
    @classmethod
    @property
    def BOX_WHISKER(cls) -> ChartType:
        '''The series is laid out as box and whisker.'''
        ...
    
    @classmethod
    @property
    def FUNNEL(cls) -> ChartType:
        '''The series is laid out as a funnel.'''
        ...
    
    @classmethod
    @property
    def PARETO_LINE(cls) -> ChartType:
        '''The series is laid out as pareto lines.'''
        ...
    
    @classmethod
    @property
    def SUNBURST(cls) -> ChartType:
        '''The series is laid out as a sunburst.'''
        ...
    
    @classmethod
    @property
    def TREEMAP(cls) -> ChartType:
        '''The series is laid out as a treemap.'''
        ...
    
    @classmethod
    @property
    def WATERFALL(cls) -> ChartType:
        '''The series is laid out as a waterfall.'''
        ...
    
    @classmethod
    @property
    def HISTOGRAM(cls) -> ChartType:
        '''The series is laid out as a histogram.'''
        ...
    
    @classmethod
    @property
    def MAP(cls) -> ChartType:
        '''The series is laid out as a region map.'''
        ...
    
    @classmethod
    @property
    def RADIAL_HISTOGRAM(cls) -> ChartType:
        '''The series is laid out as a radial historgram. It is used only for rendering'''
        ...
    
    ...

class CrossType:
    '''Represents the axis cross type.'''
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> CrossType:
        '''Microsoft Excel sets the axis crossing point.'''
        ...
    
    @classmethod
    @property
    def MAXIMUM(cls) -> CrossType:
        '''The axis crosses at the maximum value.'''
        ...
    
    @classmethod
    @property
    def MINIMUM(cls) -> CrossType:
        '''The axis crosses at the minimum value.'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> CrossType:
        '''The axis crosses at the custom value.'''
        ...
    
    ...

class DataLabelsSeparatorType:
    '''Represents the separator type of DataLabels.'''
    
    @classmethod
    @property
    def AUTO(cls) -> DataLabelsSeparatorType:
        '''Represents automatic separator'''
        ...
    
    @classmethod
    @property
    def SPACE(cls) -> DataLabelsSeparatorType:
        '''Represents space(" ")'''
        ...
    
    @classmethod
    @property
    def COMMA(cls) -> DataLabelsSeparatorType:
        '''Represents comma(",")'''
        ...
    
    @classmethod
    @property
    def SEMICOLON(cls) -> DataLabelsSeparatorType:
        '''Represents semicolon(";")'''
        ...
    
    @classmethod
    @property
    def PERIOD(cls) -> DataLabelsSeparatorType:
        '''Represents period(".")'''
        ...
    
    @classmethod
    @property
    def NEW_LINE(cls) -> DataLabelsSeparatorType:
        '''Represents newline("\n")'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> DataLabelsSeparatorType:
        '''Represents custom separator'''
        ...
    
    ...

class DataLablesSeparatorType:
    '''Represents the separator type of DataLabels.'''
    
    @classmethod
    @property
    def AUTO(cls) -> DataLablesSeparatorType:
        '''Represents automatic separator'''
        ...
    
    @classmethod
    @property
    def SPACE(cls) -> DataLablesSeparatorType:
        '''Represents space(" ")'''
        ...
    
    @classmethod
    @property
    def COMMA(cls) -> DataLablesSeparatorType:
        '''Represents comma(",")'''
        ...
    
    @classmethod
    @property
    def SEMICOLON(cls) -> DataLablesSeparatorType:
        '''Represents semicolon(";")'''
        ...
    
    @classmethod
    @property
    def PERIOD(cls) -> DataLablesSeparatorType:
        '''Represents period(".")'''
        ...
    
    @classmethod
    @property
    def NEW_LINE(cls) -> DataLablesSeparatorType:
        '''Represents newline("\n")'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> DataLablesSeparatorType:
        '''Represents custom separator'''
        ...
    
    ...

class DisplayUnitType:
    '''Represents the type of display unit of chart's axis.'''
    
    @classmethod
    @property
    def NONE(cls) -> DisplayUnitType:
        '''Display unit is None.'''
        ...
    
    @classmethod
    @property
    def HUNDREDS(cls) -> DisplayUnitType:
        '''Specifies the values on the chart shall be divided by 100.'''
        ...
    
    @classmethod
    @property
    def THOUSANDS(cls) -> DisplayUnitType:
        '''Specifies the values on the chart shall be divided by 1,000.'''
        ...
    
    @classmethod
    @property
    def TEN_THOUSANDS(cls) -> DisplayUnitType:
        '''Specifies the values on the chart shall be divided by 10,000.'''
        ...
    
    @classmethod
    @property
    def HUNDRED_THOUSANDS(cls) -> DisplayUnitType:
        '''Specifies the values on the chart shall be divided by 100,000.'''
        ...
    
    @classmethod
    @property
    def MILLIONS(cls) -> DisplayUnitType:
        '''Specifies the values on the chart shall be divided by 1,000,000.'''
        ...
    
    @classmethod
    @property
    def TEN_MILLIONS(cls) -> DisplayUnitType:
        '''Specifies the values on the chart shall be divided by 10,000,000.'''
        ...
    
    @classmethod
    @property
    def HUNDRED_MILLIONS(cls) -> DisplayUnitType:
        '''Specifies the values on the chart shall be divided by 100,000,000.'''
        ...
    
    @classmethod
    @property
    def BILLIONS(cls) -> DisplayUnitType:
        '''Specifies the values on the chart shall be divided by 1,000,000,000.'''
        ...
    
    @classmethod
    @property
    def TRILLIONS(cls) -> DisplayUnitType:
        '''Specifies the values on the chart shall be divided by 1,000,000,000,000.'''
        ...
    
    @classmethod
    @property
    def PERCENTAGE(cls) -> DisplayUnitType:
        '''The values on the chart shall be divided by 0.01.'''
        ...
    
    @classmethod
    @property
    def CUST(cls) -> DisplayUnitType:
        '''specifies a custom value for the display unit.'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> DisplayUnitType:
        '''specifies a custom value for the display unit.'''
        ...
    
    ...

class ErrorBarDisplayType:
    '''Represents error bar display type.'''
    
    @classmethod
    @property
    def BOTH(cls) -> ErrorBarDisplayType:
        '''Both'''
        ...
    
    @classmethod
    @property
    def MINUS(cls) -> ErrorBarDisplayType:
        '''Minus'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> ErrorBarDisplayType:
        '''None'''
        ...
    
    @classmethod
    @property
    def PLUS(cls) -> ErrorBarDisplayType:
        '''Plus'''
        ...
    
    ...

class ErrorBarType:
    '''Represents error bar amount type.'''
    
    @classmethod
    @property
    def CUSTOM(cls) -> ErrorBarType:
        '''InnerCustom value type.'''
        ...
    
    @classmethod
    @property
    def FIXED_VALUE(cls) -> ErrorBarType:
        '''Fixed value type.'''
        ...
    
    @classmethod
    @property
    def PERCENT(cls) -> ErrorBarType:
        '''Percentage type'''
        ...
    
    @classmethod
    @property
    def ST_DEV(cls) -> ErrorBarType:
        '''Standard deviation type.'''
        ...
    
    @classmethod
    @property
    def ST_ERROR(cls) -> ErrorBarType:
        '''Standard error type.'''
        ...
    
    ...

class FormattingType:
    '''Represents the type of formatting applied to an :py:class:`aspose.cells.drawing.Area` object or a :py:class:`aspose.cells.drawing.Line` object.'''
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> FormattingType:
        '''Represents automatic formatting type.'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> FormattingType:
        '''Represents custom formatting type.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> FormattingType:
        '''Represents none formatting type.'''
        ...
    
    ...

class LabelPositionType:
    '''Represents data label position type.'''
    
    @classmethod
    @property
    def CENTER(cls) -> LabelPositionType:
        '''Applies only to bar, 2d/3d pie charts'''
        ...
    
    @classmethod
    @property
    def INSIDE_BASE(cls) -> LabelPositionType:
        '''Applies only to bar, 2d/3d pie charts'''
        ...
    
    @classmethod
    @property
    def INSIDE_END(cls) -> LabelPositionType:
        '''Applies only to bar charts'''
        ...
    
    @classmethod
    @property
    def OUTSIDE_END(cls) -> LabelPositionType:
        '''Applies only to bar, 2d/3d pie charts'''
        ...
    
    @classmethod
    @property
    def ABOVE(cls) -> LabelPositionType:
        '''Applies only to line charts'''
        ...
    
    @classmethod
    @property
    def BELOW(cls) -> LabelPositionType:
        '''Applies only to line charts'''
        ...
    
    @classmethod
    @property
    def LEFT(cls) -> LabelPositionType:
        '''Applies only to line charts'''
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> LabelPositionType:
        '''Applies only to line charts'''
        ...
    
    @classmethod
    @property
    def BEST_FIT(cls) -> LabelPositionType:
        '''Applies only to 2d/3d pie charts'''
        ...
    
    @classmethod
    @property
    def MOVED(cls) -> LabelPositionType:
        '''User moved the data labels, Only for reading chart from template file.'''
        ...
    
    ...

class LegendPositionType:
    '''Enumerates the legend position types.'''
    
    @classmethod
    @property
    def BOTTOM(cls) -> LegendPositionType:
        '''Displays the legend to the bottom of the chart's plot area.'''
        ...
    
    @classmethod
    @property
    def CORNER(cls) -> LegendPositionType:
        '''Displays the legend to the corner of the chart's plot area.'''
        ...
    
    @classmethod
    @property
    def LEFT(cls) -> LegendPositionType:
        '''Displays the legend to the left of the chart's plot area.'''
        ...
    
    @classmethod
    @property
    def NOT_DOCKED(cls) -> LegendPositionType:
        '''Represents that the legend is not docked.'''
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> LegendPositionType:
        '''Displays the legend to the right of the chart's plot area.'''
        ...
    
    @classmethod
    @property
    def TOP(cls) -> LegendPositionType:
        '''Displays the legend to the top of the chart's plot area.'''
        ...
    
    ...

class MapChartLabelLayout:
    '''Represents the layout of map chart's labels.'''
    
    @classmethod
    @property
    def BEST_FIT_ONLY(cls) -> MapChartLabelLayout:
        '''Only best fit.'''
        ...
    
    @classmethod
    @property
    def SHOW_ALL(cls) -> MapChartLabelLayout:
        '''Shows all labels.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> MapChartLabelLayout:
        '''No labels.'''
        ...
    
    ...

class MapChartProjectionType:
    '''Represents projection type of the map chart.'''
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> MapChartProjectionType:
        '''Automatic'''
        ...
    
    @classmethod
    @property
    def MERCATOR(cls) -> MapChartProjectionType:
        '''Mercator'''
        ...
    
    @classmethod
    @property
    def MILLER(cls) -> MapChartProjectionType:
        '''Miller'''
        ...
    
    @classmethod
    @property
    def ALBERS(cls) -> MapChartProjectionType:
        '''Albers'''
        ...
    
    ...

class MapChartRegionType:
    '''Represents the region type of the map chart.'''
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> MapChartRegionType:
        '''Automatic'''
        ...
    
    @classmethod
    @property
    def DATA_ONLY(cls) -> MapChartRegionType:
        '''Only Data.'''
        ...
    
    @classmethod
    @property
    def COUNTRY_REGION_LIST(cls) -> MapChartRegionType:
        '''Country region list.'''
        ...
    
    @classmethod
    @property
    def WORLD(cls) -> MapChartRegionType:
        '''World.'''
        ...
    
    ...

class PlotDataByType:
    '''Represents the type of data plot by row or column.'''
    
    @classmethod
    @property
    def ROW(cls) -> PlotDataByType:
        '''By row.'''
        ...
    
    @classmethod
    @property
    def COLUMN(cls) -> PlotDataByType:
        '''By column.'''
        ...
    
    ...

class PlotEmptyCellsType:
    '''Represents all plot empty cells type of a chart.'''
    
    @classmethod
    @property
    def NOT_PLOTTED(cls) -> PlotEmptyCellsType:
        '''Not plotted(leave gap)'''
        ...
    
    @classmethod
    @property
    def ZERO(cls) -> PlotEmptyCellsType:
        '''Zero'''
        ...
    
    @classmethod
    @property
    def INTERPOLATED(cls) -> PlotEmptyCellsType:
        '''Interpolated'''
        ...
    
    ...

class QuartileCalculationType:
    '''Represents quartile calculation methods.'''
    
    @classmethod
    @property
    def EXCLUSIVE(cls) -> QuartileCalculationType:
        '''The quartile calculation includes the median when splitting the dataset into quartiles.'''
        ...
    
    @classmethod
    @property
    def INCLUSIVE(cls) -> QuartileCalculationType:
        '''The quartile calculation excludes the median when splitting the dataset into quartiles.'''
        ...
    
    ...

class SparklineAxisMinMaxType:
    '''Represents the minimum and maximum value types for the sparkline vertical axis.'''
    
    @classmethod
    @property
    def AUTO_INDIVIDUAL(cls) -> SparklineAxisMinMaxType:
        '''Automatic for each sparkline.'''
        ...
    
    @classmethod
    @property
    def GROUP(cls) -> SparklineAxisMinMaxType:
        '''Same for all sparklines in the group.'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> SparklineAxisMinMaxType:
        '''Custom value for sparkline.'''
        ...
    
    ...

class SparklinePresetStyleType:
    '''Represents the preset style types for sparkline.'''
    
    @classmethod
    @property
    def STYLE1(cls) -> SparklinePresetStyleType:
        '''Style 1'''
        ...
    
    @classmethod
    @property
    def STYLE2(cls) -> SparklinePresetStyleType:
        '''Style 2'''
        ...
    
    @classmethod
    @property
    def STYLE3(cls) -> SparklinePresetStyleType:
        '''Style 3'''
        ...
    
    @classmethod
    @property
    def STYLE4(cls) -> SparklinePresetStyleType:
        '''Style 4'''
        ...
    
    @classmethod
    @property
    def STYLE5(cls) -> SparklinePresetStyleType:
        '''Style 5'''
        ...
    
    @classmethod
    @property
    def STYLE6(cls) -> SparklinePresetStyleType:
        '''Style 6'''
        ...
    
    @classmethod
    @property
    def STYLE7(cls) -> SparklinePresetStyleType:
        '''Style 7'''
        ...
    
    @classmethod
    @property
    def STYLE8(cls) -> SparklinePresetStyleType:
        '''Style 8'''
        ...
    
    @classmethod
    @property
    def STYLE9(cls) -> SparklinePresetStyleType:
        '''Style 9'''
        ...
    
    @classmethod
    @property
    def STYLE10(cls) -> SparklinePresetStyleType:
        '''Style 10'''
        ...
    
    @classmethod
    @property
    def STYLE11(cls) -> SparklinePresetStyleType:
        '''Style 11'''
        ...
    
    @classmethod
    @property
    def STYLE12(cls) -> SparklinePresetStyleType:
        '''Style 12'''
        ...
    
    @classmethod
    @property
    def STYLE13(cls) -> SparklinePresetStyleType:
        '''Style 13'''
        ...
    
    @classmethod
    @property
    def STYLE14(cls) -> SparklinePresetStyleType:
        '''Style 14'''
        ...
    
    @classmethod
    @property
    def STYLE15(cls) -> SparklinePresetStyleType:
        '''Style 15'''
        ...
    
    @classmethod
    @property
    def STYLE16(cls) -> SparklinePresetStyleType:
        '''Style 16'''
        ...
    
    @classmethod
    @property
    def STYLE17(cls) -> SparklinePresetStyleType:
        '''Style 17'''
        ...
    
    @classmethod
    @property
    def STYLE18(cls) -> SparklinePresetStyleType:
        '''Style 18'''
        ...
    
    @classmethod
    @property
    def STYLE19(cls) -> SparklinePresetStyleType:
        '''Style 19'''
        ...
    
    @classmethod
    @property
    def STYLE20(cls) -> SparklinePresetStyleType:
        '''Style 20'''
        ...
    
    @classmethod
    @property
    def STYLE21(cls) -> SparklinePresetStyleType:
        '''Style 21'''
        ...
    
    @classmethod
    @property
    def STYLE22(cls) -> SparklinePresetStyleType:
        '''Style 22'''
        ...
    
    @classmethod
    @property
    def STYLE23(cls) -> SparklinePresetStyleType:
        '''Style 23'''
        ...
    
    @classmethod
    @property
    def STYLE24(cls) -> SparklinePresetStyleType:
        '''Style 24'''
        ...
    
    @classmethod
    @property
    def STYLE25(cls) -> SparklinePresetStyleType:
        '''Style 25'''
        ...
    
    @classmethod
    @property
    def STYLE26(cls) -> SparklinePresetStyleType:
        '''Style 26'''
        ...
    
    @classmethod
    @property
    def STYLE27(cls) -> SparklinePresetStyleType:
        '''Style 27'''
        ...
    
    @classmethod
    @property
    def STYLE28(cls) -> SparklinePresetStyleType:
        '''Style 28'''
        ...
    
    @classmethod
    @property
    def STYLE29(cls) -> SparklinePresetStyleType:
        '''Style 29'''
        ...
    
    @classmethod
    @property
    def STYLE30(cls) -> SparklinePresetStyleType:
        '''Style 30'''
        ...
    
    @classmethod
    @property
    def STYLE31(cls) -> SparklinePresetStyleType:
        '''Style 31'''
        ...
    
    @classmethod
    @property
    def STYLE32(cls) -> SparklinePresetStyleType:
        '''Style 32'''
        ...
    
    @classmethod
    @property
    def STYLE33(cls) -> SparklinePresetStyleType:
        '''Style 33'''
        ...
    
    @classmethod
    @property
    def STYLE34(cls) -> SparklinePresetStyleType:
        '''Style 34'''
        ...
    
    @classmethod
    @property
    def STYLE35(cls) -> SparklinePresetStyleType:
        '''Style 35'''
        ...
    
    @classmethod
    @property
    def STYLE36(cls) -> SparklinePresetStyleType:
        '''Style 36'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> SparklinePresetStyleType:
        '''No preset style.'''
        ...
    
    ...

class SparklineType:
    '''Represents the sparkline types.'''
    
    @classmethod
    @property
    def LINE(cls) -> SparklineType:
        '''Line sparkline.'''
        ...
    
    @classmethod
    @property
    def COLUMN(cls) -> SparklineType:
        '''Column sparkline.'''
        ...
    
    @classmethod
    @property
    def STACKED(cls) -> SparklineType:
        '''Win/Loss sparkline.'''
        ...
    
    ...

class TickLabelPositionType:
    '''Represents the position type of tick-mark labels on the specified axis.'''
    
    @classmethod
    @property
    def HIGH(cls) -> TickLabelPositionType:
        '''Position type is high.'''
        ...
    
    @classmethod
    @property
    def LOW(cls) -> TickLabelPositionType:
        '''Position type is low.'''
        ...
    
    @classmethod
    @property
    def NEXT_TO_AXIS(cls) -> TickLabelPositionType:
        '''Position type is next to axis.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> TickLabelPositionType:
        '''Position type is none.'''
        ...
    
    ...

class TickMarkType:
    '''Represents the tick mark type for the specified axis.'''
    
    @classmethod
    @property
    def CROSS(cls) -> TickMarkType:
        '''Tick mark type is Cross.'''
        ...
    
    @classmethod
    @property
    def INSIDE(cls) -> TickMarkType:
        '''Tick mark type is Inside.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> TickMarkType:
        '''Tick mark type is None.'''
        ...
    
    @classmethod
    @property
    def OUTSIDE(cls) -> TickMarkType:
        '''Tick mark type is Outside'''
        ...
    
    ...

class TimeUnit:
    '''Represents the base unit for the category axis.'''
    
    @classmethod
    @property
    def DAYS(cls) -> TimeUnit:
        '''Days'''
        ...
    
    @classmethod
    @property
    def MONTHS(cls) -> TimeUnit:
        '''Months'''
        ...
    
    @classmethod
    @property
    def YEARS(cls) -> TimeUnit:
        '''Years'''
        ...
    
    ...

class TrendlineType:
    '''Represents the trendline type.'''
    
    @classmethod
    @property
    def EXPONENTIAL(cls) -> TrendlineType:
        '''Exponential'''
        ...
    
    @classmethod
    @property
    def LINEAR(cls) -> TrendlineType:
        '''Linear'''
        ...
    
    @classmethod
    @property
    def LOGARITHMIC(cls) -> TrendlineType:
        '''Logarithmic'''
        ...
    
    @classmethod
    @property
    def MOVING_AVERAGE(cls) -> TrendlineType:
        '''MovingAverage'''
        ...
    
    @classmethod
    @property
    def POLYNOMIAL(cls) -> TrendlineType:
        '''Polynomial'''
        ...
    
    @classmethod
    @property
    def POWER(cls) -> TrendlineType:
        '''Power'''
        ...
    
    ...

