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

class ActiveXControl(ActiveXControlBase):
    '''Represents the ActiveX control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    ...

class ActiveXControlBase:
    '''Represents the ActiveX control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    ...

class CheckBoxActiveXControl(ActiveXControl):
    '''Represents a CheckBox ActiveX control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def group_name(self) -> str:
        ...
    
    @group_name.setter
    def group_name(self, value : str):
        ...
    
    @property
    def alignment(self) -> aspose.cells.drawing.activexcontrols.ControlCaptionAlignmentType:
        '''Gets and set the position of the Caption relative to the control.'''
        ...
    
    @alignment.setter
    def alignment(self, value : aspose.cells.drawing.activexcontrols.ControlCaptionAlignmentType):
        '''Gets and set the position of the Caption relative to the control.'''
        ...
    
    @property
    def is_word_wrapped(self) -> bool:
        ...
    
    @is_word_wrapped.setter
    def is_word_wrapped(self, value : bool):
        ...
    
    @property
    def caption(self) -> str:
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @caption.setter
    def caption(self, value : str):
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @property
    def picture_position(self) -> aspose.cells.drawing.activexcontrols.ControlPicturePositionType:
        ...
    
    @picture_position.setter
    def picture_position(self, value : aspose.cells.drawing.activexcontrols.ControlPicturePositionType):
        ...
    
    @property
    def special_effect(self) -> aspose.cells.drawing.activexcontrols.ControlSpecialEffectType:
        ...
    
    @special_effect.setter
    def special_effect(self, value : aspose.cells.drawing.activexcontrols.ControlSpecialEffectType):
        ...
    
    @property
    def picture(self) -> bytes:
        '''Gets and sets the data of the picture.'''
        ...
    
    @picture.setter
    def picture(self, value : bytes):
        '''Gets and sets the data of the picture.'''
        ...
    
    @property
    def accelerator(self) -> char:
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @accelerator.setter
    def accelerator(self, value : char):
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @property
    def value(self) -> aspose.cells.drawing.CheckValueType:
        '''Indicates if the control is checked or not.'''
        ...
    
    @value.setter
    def value(self, value : aspose.cells.drawing.CheckValueType):
        '''Indicates if the control is checked or not.'''
        ...
    
    @property
    def is_triple_state(self) -> bool:
        ...
    
    @is_triple_state.setter
    def is_triple_state(self, value : bool):
        ...
    
    ...

class ComboBoxActiveXControl(ActiveXControl):
    '''Represents a ComboBox ActiveX control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def max_length(self) -> int:
        ...
    
    @max_length.setter
    def max_length(self, value : int):
        ...
    
    @property
    def list_width(self) -> float:
        ...
    
    @list_width.setter
    def list_width(self, value : float):
        ...
    
    @property
    def bound_column(self) -> int:
        ...
    
    @bound_column.setter
    def bound_column(self, value : int):
        ...
    
    @property
    def text_column(self) -> int:
        ...
    
    @text_column.setter
    def text_column(self, value : int):
        ...
    
    @property
    def column_count(self) -> int:
        ...
    
    @column_count.setter
    def column_count(self, value : int):
        ...
    
    @property
    def list_rows(self) -> int:
        ...
    
    @list_rows.setter
    def list_rows(self, value : int):
        ...
    
    @property
    def match_entry(self) -> aspose.cells.drawing.activexcontrols.ControlMatchEntryType:
        ...
    
    @match_entry.setter
    def match_entry(self, value : aspose.cells.drawing.activexcontrols.ControlMatchEntryType):
        ...
    
    @property
    def drop_button_style(self) -> aspose.cells.drawing.activexcontrols.DropButtonStyle:
        ...
    
    @drop_button_style.setter
    def drop_button_style(self, value : aspose.cells.drawing.activexcontrols.DropButtonStyle):
        ...
    
    @property
    def show_drop_button_type_when(self) -> aspose.cells.drawing.activexcontrols.ShowDropButtonType:
        ...
    
    @show_drop_button_type_when.setter
    def show_drop_button_type_when(self, value : aspose.cells.drawing.activexcontrols.ShowDropButtonType):
        ...
    
    @property
    def list_style(self) -> aspose.cells.drawing.activexcontrols.ControlListStyle:
        ...
    
    @list_style.setter
    def list_style(self, value : aspose.cells.drawing.activexcontrols.ControlListStyle):
        ...
    
    @property
    def border_style(self) -> aspose.cells.drawing.activexcontrols.ControlBorderType:
        ...
    
    @border_style.setter
    def border_style(self, value : aspose.cells.drawing.activexcontrols.ControlBorderType):
        ...
    
    @property
    def border_ole_color(self) -> int:
        ...
    
    @border_ole_color.setter
    def border_ole_color(self, value : int):
        ...
    
    @property
    def special_effect(self) -> aspose.cells.drawing.activexcontrols.ControlSpecialEffectType:
        ...
    
    @special_effect.setter
    def special_effect(self, value : aspose.cells.drawing.activexcontrols.ControlSpecialEffectType):
        ...
    
    @property
    def is_editable(self) -> bool:
        ...
    
    @is_editable.setter
    def is_editable(self, value : bool):
        ...
    
    @property
    def show_column_heads(self) -> bool:
        ...
    
    @show_column_heads.setter
    def show_column_heads(self, value : bool):
        ...
    
    @property
    def is_drag_behavior_enabled(self) -> bool:
        ...
    
    @is_drag_behavior_enabled.setter
    def is_drag_behavior_enabled(self, value : bool):
        ...
    
    @property
    def enter_field_behavior(self) -> bool:
        ...
    
    @enter_field_behavior.setter
    def enter_field_behavior(self, value : bool):
        ...
    
    @property
    def is_auto_word_selected(self) -> bool:
        ...
    
    @is_auto_word_selected.setter
    def is_auto_word_selected(self, value : bool):
        ...
    
    @property
    def selection_margin(self) -> bool:
        ...
    
    @selection_margin.setter
    def selection_margin(self, value : bool):
        ...
    
    @property
    def value(self) -> str:
        '''Gets and sets the value of the control.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Gets and sets the value of the control.'''
        ...
    
    @property
    def hide_selection(self) -> bool:
        ...
    
    @hide_selection.setter
    def hide_selection(self, value : bool):
        ...
    
    @property
    def column_widths(self) -> float:
        ...
    
    @column_widths.setter
    def column_widths(self, value : float):
        ...
    
    ...

class CommandButtonActiveXControl(ActiveXControl):
    '''Represents a command button.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def caption(self) -> str:
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @caption.setter
    def caption(self, value : str):
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @property
    def picture_position(self) -> aspose.cells.drawing.activexcontrols.ControlPicturePositionType:
        ...
    
    @picture_position.setter
    def picture_position(self, value : aspose.cells.drawing.activexcontrols.ControlPicturePositionType):
        ...
    
    @property
    def picture(self) -> bytes:
        '''Gets and sets the data of the picture.'''
        ...
    
    @picture.setter
    def picture(self, value : bytes):
        '''Gets and sets the data of the picture.'''
        ...
    
    @property
    def accelerator(self) -> char:
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @accelerator.setter
    def accelerator(self, value : char):
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @property
    def take_focus_on_click(self) -> bool:
        ...
    
    @take_focus_on_click.setter
    def take_focus_on_click(self, value : bool):
        ...
    
    @property
    def is_word_wrapped(self) -> bool:
        ...
    
    @is_word_wrapped.setter
    def is_word_wrapped(self, value : bool):
        ...
    
    ...

class ImageActiveXControl(ActiveXControl):
    '''Represents the image control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def border_ole_color(self) -> int:
        ...
    
    @border_ole_color.setter
    def border_ole_color(self, value : int):
        ...
    
    @property
    def border_style(self) -> aspose.cells.drawing.activexcontrols.ControlBorderType:
        ...
    
    @border_style.setter
    def border_style(self, value : aspose.cells.drawing.activexcontrols.ControlBorderType):
        ...
    
    @property
    def picture_size_mode(self) -> aspose.cells.drawing.activexcontrols.ControlPictureSizeMode:
        ...
    
    @picture_size_mode.setter
    def picture_size_mode(self, value : aspose.cells.drawing.activexcontrols.ControlPictureSizeMode):
        ...
    
    @property
    def special_effect(self) -> aspose.cells.drawing.activexcontrols.ControlSpecialEffectType:
        ...
    
    @special_effect.setter
    def special_effect(self, value : aspose.cells.drawing.activexcontrols.ControlSpecialEffectType):
        ...
    
    @property
    def picture(self) -> bytes:
        '''Gets and sets the data of the picture.'''
        ...
    
    @picture.setter
    def picture(self, value : bytes):
        '''Gets and sets the data of the picture.'''
        ...
    
    @property
    def picture_alignment(self) -> aspose.cells.drawing.activexcontrols.ControlPictureAlignmentType:
        ...
    
    @picture_alignment.setter
    def picture_alignment(self, value : aspose.cells.drawing.activexcontrols.ControlPictureAlignmentType):
        ...
    
    @property
    def is_tiled(self) -> bool:
        ...
    
    @is_tiled.setter
    def is_tiled(self, value : bool):
        ...
    
    ...

class LabelActiveXControl(ActiveXControl):
    '''Represents the label ActiveX control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def caption(self) -> str:
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @caption.setter
    def caption(self, value : str):
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @property
    def picture_position(self) -> aspose.cells.drawing.activexcontrols.ControlPicturePositionType:
        ...
    
    @picture_position.setter
    def picture_position(self, value : aspose.cells.drawing.activexcontrols.ControlPicturePositionType):
        ...
    
    @property
    def border_ole_color(self) -> int:
        ...
    
    @border_ole_color.setter
    def border_ole_color(self, value : int):
        ...
    
    @property
    def border_style(self) -> aspose.cells.drawing.activexcontrols.ControlBorderType:
        ...
    
    @border_style.setter
    def border_style(self, value : aspose.cells.drawing.activexcontrols.ControlBorderType):
        ...
    
    @property
    def special_effect(self) -> aspose.cells.drawing.activexcontrols.ControlSpecialEffectType:
        ...
    
    @special_effect.setter
    def special_effect(self, value : aspose.cells.drawing.activexcontrols.ControlSpecialEffectType):
        ...
    
    @property
    def picture(self) -> bytes:
        '''Gets and sets the data of the picture.'''
        ...
    
    @picture.setter
    def picture(self, value : bytes):
        '''Gets and sets the data of the picture.'''
        ...
    
    @property
    def accelerator(self) -> char:
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @accelerator.setter
    def accelerator(self, value : char):
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @property
    def is_word_wrapped(self) -> bool:
        ...
    
    @is_word_wrapped.setter
    def is_word_wrapped(self, value : bool):
        ...
    
    ...

class ListBoxActiveXControl(ActiveXControl):
    '''Represents a ListBox ActiveX control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def scroll_bars(self) -> aspose.cells.drawing.activexcontrols.ControlScrollBarType:
        ...
    
    @scroll_bars.setter
    def scroll_bars(self, value : aspose.cells.drawing.activexcontrols.ControlScrollBarType):
        ...
    
    @property
    def list_width(self) -> float:
        ...
    
    @list_width.setter
    def list_width(self, value : float):
        ...
    
    @property
    def bound_column(self) -> int:
        ...
    
    @bound_column.setter
    def bound_column(self, value : int):
        ...
    
    @property
    def text_column(self) -> int:
        ...
    
    @text_column.setter
    def text_column(self, value : int):
        ...
    
    @property
    def column_count(self) -> int:
        ...
    
    @column_count.setter
    def column_count(self, value : int):
        ...
    
    @property
    def match_entry(self) -> aspose.cells.drawing.activexcontrols.ControlMatchEntryType:
        ...
    
    @match_entry.setter
    def match_entry(self, value : aspose.cells.drawing.activexcontrols.ControlMatchEntryType):
        ...
    
    @property
    def list_style(self) -> aspose.cells.drawing.activexcontrols.ControlListStyle:
        ...
    
    @list_style.setter
    def list_style(self, value : aspose.cells.drawing.activexcontrols.ControlListStyle):
        ...
    
    @property
    def selection_type(self) -> aspose.cells.drawing.SelectionType:
        ...
    
    @selection_type.setter
    def selection_type(self, value : aspose.cells.drawing.SelectionType):
        ...
    
    @property
    def value(self) -> str:
        '''Gets and sets the value of the control.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Gets and sets the value of the control.'''
        ...
    
    @property
    def border_style(self) -> aspose.cells.drawing.activexcontrols.ControlBorderType:
        ...
    
    @border_style.setter
    def border_style(self, value : aspose.cells.drawing.activexcontrols.ControlBorderType):
        ...
    
    @property
    def border_ole_color(self) -> int:
        ...
    
    @border_ole_color.setter
    def border_ole_color(self, value : int):
        ...
    
    @property
    def special_effect(self) -> aspose.cells.drawing.activexcontrols.ControlSpecialEffectType:
        ...
    
    @special_effect.setter
    def special_effect(self, value : aspose.cells.drawing.activexcontrols.ControlSpecialEffectType):
        ...
    
    @property
    def show_column_heads(self) -> bool:
        ...
    
    @show_column_heads.setter
    def show_column_heads(self, value : bool):
        ...
    
    @property
    def integral_height(self) -> bool:
        ...
    
    @integral_height.setter
    def integral_height(self, value : bool):
        ...
    
    @property
    def column_widths(self) -> float:
        ...
    
    @column_widths.setter
    def column_widths(self, value : float):
        ...
    
    ...

class RadioButtonActiveXControl(ToggleButtonActiveXControl):
    '''Represents a RadioButton ActiveX control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def caption(self) -> str:
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @caption.setter
    def caption(self, value : str):
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @property
    def picture_position(self) -> aspose.cells.drawing.activexcontrols.ControlPicturePositionType:
        ...
    
    @picture_position.setter
    def picture_position(self, value : aspose.cells.drawing.activexcontrols.ControlPicturePositionType):
        ...
    
    @property
    def special_effect(self) -> aspose.cells.drawing.activexcontrols.ControlSpecialEffectType:
        ...
    
    @special_effect.setter
    def special_effect(self, value : aspose.cells.drawing.activexcontrols.ControlSpecialEffectType):
        ...
    
    @property
    def picture(self) -> bytes:
        '''Gets and sets the data of the picture.'''
        ...
    
    @picture.setter
    def picture(self, value : bytes):
        '''Gets and sets the data of the picture.'''
        ...
    
    @property
    def accelerator(self) -> char:
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @accelerator.setter
    def accelerator(self, value : char):
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @property
    def value(self) -> aspose.cells.drawing.CheckValueType:
        '''Indicates if the control is checked or not.'''
        ...
    
    @value.setter
    def value(self, value : aspose.cells.drawing.CheckValueType):
        '''Indicates if the control is checked or not.'''
        ...
    
    @property
    def is_triple_state(self) -> bool:
        ...
    
    @is_triple_state.setter
    def is_triple_state(self, value : bool):
        ...
    
    @property
    def group_name(self) -> str:
        ...
    
    @group_name.setter
    def group_name(self, value : str):
        ...
    
    @property
    def alignment(self) -> aspose.cells.drawing.activexcontrols.ControlCaptionAlignmentType:
        '''Gets and set the position of the Caption relative to the control.'''
        ...
    
    @alignment.setter
    def alignment(self, value : aspose.cells.drawing.activexcontrols.ControlCaptionAlignmentType):
        '''Gets and set the position of the Caption relative to the control.'''
        ...
    
    @property
    def is_word_wrapped(self) -> bool:
        ...
    
    @is_word_wrapped.setter
    def is_word_wrapped(self, value : bool):
        ...
    
    ...

class ScrollBarActiveXControl(SpinButtonActiveXControl):
    '''Represents the ScrollBar control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def min(self) -> int:
        '''Gets and sets the minimum acceptable value.'''
        ...
    
    @min.setter
    def min(self, value : int):
        '''Gets and sets the minimum acceptable value.'''
        ...
    
    @property
    def max(self) -> int:
        '''Gets and sets the maximum acceptable value.'''
        ...
    
    @max.setter
    def max(self, value : int):
        '''Gets and sets the maximum acceptable value.'''
        ...
    
    @property
    def position(self) -> int:
        '''Gets and sets the value.'''
        ...
    
    @position.setter
    def position(self, value : int):
        '''Gets and sets the value.'''
        ...
    
    @property
    def small_change(self) -> int:
        ...
    
    @small_change.setter
    def small_change(self, value : int):
        ...
    
    @property
    def orientation(self) -> aspose.cells.drawing.activexcontrols.ControlScrollOrientation:
        '''Gets and sets whether the SpinButton or ScrollBar is oriented vertically or horizontally.'''
        ...
    
    @orientation.setter
    def orientation(self, value : aspose.cells.drawing.activexcontrols.ControlScrollOrientation):
        '''Gets and sets whether the SpinButton or ScrollBar is oriented vertically or horizontally.'''
        ...
    
    @property
    def large_change(self) -> int:
        ...
    
    @large_change.setter
    def large_change(self, value : int):
        ...
    
    ...

class SpinButtonActiveXControl(ActiveXControl):
    '''Represents the SpinButton control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def min(self) -> int:
        '''Gets and sets the minimum acceptable value.'''
        ...
    
    @min.setter
    def min(self, value : int):
        '''Gets and sets the minimum acceptable value.'''
        ...
    
    @property
    def max(self) -> int:
        '''Gets and sets the maximum acceptable value.'''
        ...
    
    @max.setter
    def max(self, value : int):
        '''Gets and sets the maximum acceptable value.'''
        ...
    
    @property
    def position(self) -> int:
        '''Gets and sets the value.'''
        ...
    
    @position.setter
    def position(self, value : int):
        '''Gets and sets the value.'''
        ...
    
    @property
    def small_change(self) -> int:
        ...
    
    @small_change.setter
    def small_change(self, value : int):
        ...
    
    @property
    def orientation(self) -> aspose.cells.drawing.activexcontrols.ControlScrollOrientation:
        '''Gets and sets whether the SpinButton or ScrollBar is oriented vertically or horizontally.'''
        ...
    
    @orientation.setter
    def orientation(self, value : aspose.cells.drawing.activexcontrols.ControlScrollOrientation):
        '''Gets and sets whether the SpinButton or ScrollBar is oriented vertically or horizontally.'''
        ...
    
    ...

class TextBoxActiveXControl(ActiveXControl):
    '''Represents a text box ActiveX control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def border_style(self) -> aspose.cells.drawing.activexcontrols.ControlBorderType:
        ...
    
    @border_style.setter
    def border_style(self, value : aspose.cells.drawing.activexcontrols.ControlBorderType):
        ...
    
    @property
    def border_ole_color(self) -> int:
        ...
    
    @border_ole_color.setter
    def border_ole_color(self, value : int):
        ...
    
    @property
    def special_effect(self) -> aspose.cells.drawing.activexcontrols.ControlSpecialEffectType:
        ...
    
    @special_effect.setter
    def special_effect(self, value : aspose.cells.drawing.activexcontrols.ControlSpecialEffectType):
        ...
    
    @property
    def max_length(self) -> int:
        ...
    
    @max_length.setter
    def max_length(self, value : int):
        ...
    
    @property
    def scroll_bars(self) -> aspose.cells.drawing.activexcontrols.ControlScrollBarType:
        ...
    
    @scroll_bars.setter
    def scroll_bars(self, value : aspose.cells.drawing.activexcontrols.ControlScrollBarType):
        ...
    
    @property
    def password_char(self) -> char:
        ...
    
    @password_char.setter
    def password_char(self, value : char):
        ...
    
    @property
    def is_editable(self) -> bool:
        ...
    
    @is_editable.setter
    def is_editable(self, value : bool):
        ...
    
    @property
    def integral_height(self) -> bool:
        ...
    
    @integral_height.setter
    def integral_height(self, value : bool):
        ...
    
    @property
    def is_drag_behavior_enabled(self) -> bool:
        ...
    
    @is_drag_behavior_enabled.setter
    def is_drag_behavior_enabled(self, value : bool):
        ...
    
    @property
    def enter_key_behavior(self) -> bool:
        ...
    
    @enter_key_behavior.setter
    def enter_key_behavior(self, value : bool):
        ...
    
    @property
    def enter_field_behavior(self) -> bool:
        ...
    
    @enter_field_behavior.setter
    def enter_field_behavior(self, value : bool):
        ...
    
    @property
    def tab_key_behavior(self) -> bool:
        ...
    
    @tab_key_behavior.setter
    def tab_key_behavior(self, value : bool):
        ...
    
    @property
    def hide_selection(self) -> bool:
        ...
    
    @hide_selection.setter
    def hide_selection(self, value : bool):
        ...
    
    @property
    def is_auto_tab(self) -> bool:
        ...
    
    @is_auto_tab.setter
    def is_auto_tab(self, value : bool):
        ...
    
    @property
    def is_multi_line(self) -> bool:
        ...
    
    @is_multi_line.setter
    def is_multi_line(self, value : bool):
        ...
    
    @property
    def is_auto_word_selected(self) -> bool:
        ...
    
    @is_auto_word_selected.setter
    def is_auto_word_selected(self, value : bool):
        ...
    
    @property
    def is_word_wrapped(self) -> bool:
        ...
    
    @is_word_wrapped.setter
    def is_word_wrapped(self, value : bool):
        ...
    
    @property
    def text(self) -> str:
        '''Gets and set text of the control.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Gets and set text of the control.'''
        ...
    
    @property
    def drop_button_style(self) -> aspose.cells.drawing.activexcontrols.DropButtonStyle:
        ...
    
    @drop_button_style.setter
    def drop_button_style(self, value : aspose.cells.drawing.activexcontrols.DropButtonStyle):
        ...
    
    @property
    def show_drop_button_type_when(self) -> aspose.cells.drawing.activexcontrols.ShowDropButtonType:
        ...
    
    @show_drop_button_type_when.setter
    def show_drop_button_type_when(self, value : aspose.cells.drawing.activexcontrols.ShowDropButtonType):
        ...
    
    ...

class ToggleButtonActiveXControl(ActiveXControl):
    '''Represents a ToggleButton ActiveX control.'''
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def caption(self) -> str:
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @caption.setter
    def caption(self, value : str):
        '''Gets and set the descriptive text that appears on a control.'''
        ...
    
    @property
    def picture_position(self) -> aspose.cells.drawing.activexcontrols.ControlPicturePositionType:
        ...
    
    @picture_position.setter
    def picture_position(self, value : aspose.cells.drawing.activexcontrols.ControlPicturePositionType):
        ...
    
    @property
    def special_effect(self) -> aspose.cells.drawing.activexcontrols.ControlSpecialEffectType:
        ...
    
    @special_effect.setter
    def special_effect(self, value : aspose.cells.drawing.activexcontrols.ControlSpecialEffectType):
        ...
    
    @property
    def picture(self) -> bytes:
        '''Gets and sets the data of the picture.'''
        ...
    
    @picture.setter
    def picture(self, value : bytes):
        '''Gets and sets the data of the picture.'''
        ...
    
    @property
    def accelerator(self) -> char:
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @accelerator.setter
    def accelerator(self, value : char):
        '''Gets and sets the accelerator key for the control.'''
        ...
    
    @property
    def value(self) -> aspose.cells.drawing.CheckValueType:
        '''Indicates if the control is checked or not.'''
        ...
    
    @value.setter
    def value(self, value : aspose.cells.drawing.CheckValueType):
        '''Indicates if the control is checked or not.'''
        ...
    
    @property
    def is_triple_state(self) -> bool:
        ...
    
    @is_triple_state.setter
    def is_triple_state(self, value : bool):
        ...
    
    ...

class UnknownControl(ActiveXControl):
    '''Unknow control.'''
    
    def get_relationship_data(self, rel_id : str) -> bytes:
        '''Gets the related data.
        
        :param rel_id: The relationship id.
        :returns: Returns the related data.'''
        ...
    
    @property
    def workbook(self) -> aspose.cells.Workbook:
        '''Gets the :py:attr:`aspose.cells.drawing.activexcontrols.ActiveXControlBase.workbook` object.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.activexcontrols.ControlType:
        '''Gets the type of the ActiveX control.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Gets and sets the width of the control in unit of points.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Gets and sets the height of the control in unit of points.'''
        ...
    
    @property
    def mouse_icon(self) -> bytes:
        ...
    
    @mouse_icon.setter
    def mouse_icon(self, value : bytes):
        ...
    
    @property
    def mouse_pointer(self) -> aspose.cells.drawing.activexcontrols.ControlMousePointerType:
        ...
    
    @mouse_pointer.setter
    def mouse_pointer(self, value : aspose.cells.drawing.activexcontrols.ControlMousePointerType):
        ...
    
    @property
    def fore_ole_color(self) -> int:
        ...
    
    @fore_ole_color.setter
    def fore_ole_color(self, value : int):
        ...
    
    @property
    def back_ole_color(self) -> int:
        ...
    
    @back_ole_color.setter
    def back_ole_color(self, value : int):
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def shadow(self) -> bool:
        '''Indicates whether to show a shadow.'''
        ...
    
    @shadow.setter
    def shadow(self, value : bool):
        '''Indicates whether to show a shadow.'''
        ...
    
    @property
    def linked_cell(self) -> str:
        ...
    
    @linked_cell.setter
    def linked_cell(self, value : str):
        ...
    
    @property
    def list_fill_range(self) -> str:
        ...
    
    @list_fill_range.setter
    def list_fill_range(self, value : str):
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets and sets the binary data of the control.'''
        ...
    
    @property
    def is_enabled(self) -> bool:
        ...
    
    @is_enabled.setter
    def is_enabled(self, value : bool):
        ...
    
    @property
    def is_locked(self) -> bool:
        ...
    
    @is_locked.setter
    def is_locked(self, value : bool):
        ...
    
    @property
    def is_transparent(self) -> bool:
        ...
    
    @is_transparent.setter
    def is_transparent(self, value : bool):
        ...
    
    @property
    def is_auto_size(self) -> bool:
        ...
    
    @is_auto_size.setter
    def is_auto_size(self, value : bool):
        ...
    
    @property
    def ime_mode(self) -> aspose.cells.drawing.activexcontrols.InputMethodEditorMode:
        ...
    
    @ime_mode.setter
    def ime_mode(self, value : aspose.cells.drawing.activexcontrols.InputMethodEditorMode):
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Represents the font of the control.'''
        ...
    
    @property
    def text_align(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.cells.TextAlignmentType):
        ...
    
    ...

class ActiveXPersistenceType:
    '''Represents the persistence method to persist an ActiveX control.'''
    
    @classmethod
    @property
    def PROPERTY_BAG(cls) -> ActiveXPersistenceType:
        '''The data is stored as xml data.'''
        ...
    
    @classmethod
    @property
    def STORAGE(cls) -> ActiveXPersistenceType:
        '''The data is stored as a storage binary data.'''
        ...
    
    @classmethod
    @property
    def STREAM(cls) -> ActiveXPersistenceType:
        '''The data is stored as a stream binary data.'''
        ...
    
    @classmethod
    @property
    def STREAM_INIT(cls) -> ActiveXPersistenceType:
        '''The data is stored as a streaminit binary data.'''
        ...
    
    ...

class ControlBorderType:
    '''Represents the border type of the ActiveX control.'''
    
    @classmethod
    @property
    def NONE(cls) -> ControlBorderType:
        '''No border.'''
        ...
    
    @classmethod
    @property
    def SINGLE(cls) -> ControlBorderType:
        '''The single line.'''
        ...
    
    ...

class ControlCaptionAlignmentType:
    '''Represents the position of the Caption relative to the control.'''
    
    @classmethod
    @property
    def LEFT(cls) -> ControlCaptionAlignmentType:
        '''The left of the control.'''
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> ControlCaptionAlignmentType:
        '''The right of the control.'''
        ...
    
    ...

class ControlListStyle:
    '''Represents the visual appearance of the list in a ListBox or ComboBox.'''
    
    @classmethod
    @property
    def PLAIN(cls) -> ControlListStyle:
        '''Displays a list in which the background of an item is highlighted when it is selected.'''
        ...
    
    @classmethod
    @property
    def OPTION(cls) -> ControlListStyle:
        '''Displays a list in which an option button or a checkbox next to each entry displays the selection state of that item.'''
        ...
    
    ...

class ControlMatchEntryType:
    '''Represents how a ListBox or ComboBox searches its list as the user types.'''
    
    @classmethod
    @property
    def FIRST_LETTER(cls) -> ControlMatchEntryType:
        '''The control searches for the next entry that starts with the character entered.
        Repeatedly typing the same letter cycles through all entries beginning with that letter.'''
        ...
    
    @classmethod
    @property
    def COMPLETE(cls) -> ControlMatchEntryType:
        '''As each character is typed, the control searches for an entry matching all characters entered.'''
        ...
    
    @classmethod
    @property
    def NONE(cls) -> ControlMatchEntryType:
        '''The list will not be searched when characters are typed.'''
        ...
    
    ...

class ControlMousePointerType:
    '''Represents the type of icon displayed as the mouse pointer for the control.'''
    
    @classmethod
    @property
    def DEFAULT(cls) -> ControlMousePointerType:
        '''Standard pointer.'''
        ...
    
    @classmethod
    @property
    def ARROW(cls) -> ControlMousePointerType:
        '''Arrow.'''
        ...
    
    @classmethod
    @property
    def CROSS(cls) -> ControlMousePointerType:
        '''Cross-hair pointer.'''
        ...
    
    @classmethod
    @property
    def I_BEAM(cls) -> ControlMousePointerType:
        '''I-beam.'''
        ...
    
    @classmethod
    @property
    def SIZE_NESW(cls) -> ControlMousePointerType:
        '''Double arrow pointing northeast and southwest.'''
        ...
    
    @classmethod
    @property
    def SIZE_NS(cls) -> ControlMousePointerType:
        '''Double arrow pointing north and south.'''
        ...
    
    @classmethod
    @property
    def SIZE_NWSE(cls) -> ControlMousePointerType:
        '''Double arrow pointing northwest and southeast.'''
        ...
    
    @classmethod
    @property
    def SIZE_WE(cls) -> ControlMousePointerType:
        '''Double arrow pointing west and east.'''
        ...
    
    @classmethod
    @property
    def UP_ARROW(cls) -> ControlMousePointerType:
        '''Up arrow.'''
        ...
    
    @classmethod
    @property
    def HOUR_GLASS(cls) -> ControlMousePointerType:
        '''Hourglass.'''
        ...
    
    @classmethod
    @property
    def NO_DROP(cls) -> ControlMousePointerType:
        '''"Not” symbol (circle with a diagonal line) on top of the object being dragged.'''
        ...
    
    @classmethod
    @property
    def APP_STARTING(cls) -> ControlMousePointerType:
        '''Arrow with an hourglass.'''
        ...
    
    @classmethod
    @property
    def HELP(cls) -> ControlMousePointerType:
        '''Arrow with a question mark.'''
        ...
    
    @classmethod
    @property
    def SIZE_ALL(cls) -> ControlMousePointerType:
        '''"Size-all” cursor (arrows pointing north, south, east, and west).'''
        ...
    
    @classmethod
    @property
    def CUSTOM(cls) -> ControlMousePointerType:
        '''Uses the icon specified by the MouseIcon property.'''
        ...
    
    ...

class ControlPictureAlignmentType:
    '''Represents the alignment of the picture inside the Form or Image.'''
    
    @classmethod
    @property
    def TOP_LEFT(cls) -> ControlPictureAlignmentType:
        '''The top left corner.'''
        ...
    
    @classmethod
    @property
    def TOP_RIGHT(cls) -> ControlPictureAlignmentType:
        '''The top right corner.'''
        ...
    
    @classmethod
    @property
    def CENTER(cls) -> ControlPictureAlignmentType:
        '''The center.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_LEFT(cls) -> ControlPictureAlignmentType:
        '''The bottom left corner.'''
        ...
    
    @classmethod
    @property
    def BOTTOM_RIGHT(cls) -> ControlPictureAlignmentType:
        '''The bottom right corner.'''
        ...
    
    ...

class ControlPicturePositionType:
    '''Represents the location of the control's picture relative to its caption.'''
    
    @classmethod
    @property
    def LEFT_TOP(cls) -> ControlPicturePositionType:
        '''The picture appears to the left of the caption.
        The caption is aligned with the top of the picture.'''
        ...
    
    @classmethod
    @property
    def LEFT_CENTER(cls) -> ControlPicturePositionType:
        '''The picture appears to the left of the caption.
        The caption is centered relative to the picture.'''
        ...
    
    @classmethod
    @property
    def LEFT_BOTTOM(cls) -> ControlPicturePositionType:
        '''The picture appears to the left of the caption.
        The caption is aligned with the bottom of the picture.'''
        ...
    
    @classmethod
    @property
    def RIGHT_TOP(cls) -> ControlPicturePositionType:
        '''The picture appears to the right of the caption.
        The caption is aligned with the top of the picture.'''
        ...
    
    @classmethod
    @property
    def RIGHT_CENTER(cls) -> ControlPicturePositionType:
        '''The picture appears to the right of the caption.
        The caption is centered relative to the picture.'''
        ...
    
    @classmethod
    @property
    def RIGHT_BOTTOM(cls) -> ControlPicturePositionType:
        '''The picture appears to the right of the caption.
        The caption is aligned with the bottom of the picture.'''
        ...
    
    @classmethod
    @property
    def ABOVE_LEFT(cls) -> ControlPicturePositionType:
        '''The picture appears above the caption.
        The caption is aligned with the left edge of the picture.'''
        ...
    
    @classmethod
    @property
    def ABOVE_CENTER(cls) -> ControlPicturePositionType:
        '''The picture appears above the caption.
        The caption is centered below the picture.'''
        ...
    
    @classmethod
    @property
    def ABOVE_RIGHT(cls) -> ControlPicturePositionType:
        '''The picture appears above the caption.
        The caption is aligned with the right edge of the picture.'''
        ...
    
    @classmethod
    @property
    def BELOW_LEFT(cls) -> ControlPicturePositionType:
        '''The picture appears below the caption.
        The caption is aligned with the left edge of the picture.'''
        ...
    
    @classmethod
    @property
    def BELOW_CENTER(cls) -> ControlPicturePositionType:
        '''The picture appears below the caption.
        The caption is centered above the picture.'''
        ...
    
    @classmethod
    @property
    def BELOW_RIGHT(cls) -> ControlPicturePositionType:
        '''The picture appears below the caption.
        The caption is aligned with the right edge of the picture.'''
        ...
    
    @classmethod
    @property
    def CENTER(cls) -> ControlPicturePositionType:
        '''The picture appears in the center of the control.
        The caption is centered horizontally and vertically on top of the picture.'''
        ...
    
    ...

class ControlPictureSizeMode:
    '''Represents how to display the picture.'''
    
    @classmethod
    @property
    def CLIP(cls) -> ControlPictureSizeMode:
        '''Crops any part of the picture that is larger than the control's boundaries.'''
        ...
    
    @classmethod
    @property
    def STRETCH(cls) -> ControlPictureSizeMode:
        '''Stretches the picture to fill the control's area.
        This setting distorts the picture in either the horizontal or vertical direction.'''
        ...
    
    @classmethod
    @property
    def ZOOM(cls) -> ControlPictureSizeMode:
        '''Enlarges the picture, but does not distort the picture in either the horizontal or vertical direction.'''
        ...
    
    ...

class ControlScrollBarType:
    '''Represents the type of scroll bar.'''
    
    @classmethod
    @property
    def NONE(cls) -> ControlScrollBarType:
        '''Displays no scroll bars.'''
        ...
    
    @classmethod
    @property
    def HORIZONTAL(cls) -> ControlScrollBarType:
        '''Displays a horizontal scroll bar.'''
        ...
    
    @classmethod
    @property
    def BARS_VERTICAL(cls) -> ControlScrollBarType:
        '''Displays a vertical scroll bar.'''
        ...
    
    @classmethod
    @property
    def BARS_BOTH(cls) -> ControlScrollBarType:
        '''Displays both a horizontal and a vertical scroll bar.'''
        ...
    
    ...

class ControlScrollOrientation:
    '''Represents type of scroll orientation'''
    
    @classmethod
    @property
    def AUTO(cls) -> ControlScrollOrientation:
        '''Control is rendered horizontally when the control's width is greater than its height.
        Control is rendered vertically otherwise.'''
        ...
    
    @classmethod
    @property
    def VERTICAL(cls) -> ControlScrollOrientation:
        '''Control is rendered vertically.'''
        ...
    
    @classmethod
    @property
    def HORIZONTAL(cls) -> ControlScrollOrientation:
        '''Control is rendered horizontally.'''
        ...
    
    ...

class ControlSpecialEffectType:
    '''Represents the type of special effect.'''
    
    @classmethod
    @property
    def FLAT(cls) -> ControlSpecialEffectType:
        '''Flat'''
        ...
    
    @classmethod
    @property
    def RAISED(cls) -> ControlSpecialEffectType:
        '''Raised'''
        ...
    
    @classmethod
    @property
    def SUNKEN(cls) -> ControlSpecialEffectType:
        '''Sunken'''
        ...
    
    @classmethod
    @property
    def ETCHED(cls) -> ControlSpecialEffectType:
        '''Etched'''
        ...
    
    @classmethod
    @property
    def BUMP(cls) -> ControlSpecialEffectType:
        '''Bump'''
        ...
    
    ...

class ControlType:
    '''Represents all type of ActiveX control.'''
    
    @classmethod
    @property
    def COMMAND_BUTTON(cls) -> ControlType:
        '''Button'''
        ...
    
    @classmethod
    @property
    def COMBO_BOX(cls) -> ControlType:
        '''ComboBox'''
        ...
    
    @classmethod
    @property
    def CHECK_BOX(cls) -> ControlType:
        '''CheckBox'''
        ...
    
    @classmethod
    @property
    def LIST_BOX(cls) -> ControlType:
        '''ListBox'''
        ...
    
    @classmethod
    @property
    def TEXT_BOX(cls) -> ControlType:
        '''TextBox'''
        ...
    
    @classmethod
    @property
    def SPIN_BUTTON(cls) -> ControlType:
        '''Spinner'''
        ...
    
    @classmethod
    @property
    def RADIO_BUTTON(cls) -> ControlType:
        '''RadioButton'''
        ...
    
    @classmethod
    @property
    def LABEL(cls) -> ControlType:
        '''Label'''
        ...
    
    @classmethod
    @property
    def IMAGE(cls) -> ControlType:
        '''Image'''
        ...
    
    @classmethod
    @property
    def TOGGLE_BUTTON(cls) -> ControlType:
        '''ToggleButton'''
        ...
    
    @classmethod
    @property
    def SCROLL_BAR(cls) -> ControlType:
        '''ScrollBar'''
        ...
    
    @classmethod
    @property
    def BAR_CODE(cls) -> ControlType:
        '''ScrollBar'''
        ...
    
    @classmethod
    @property
    def UNKNOWN(cls) -> ControlType:
        '''Unknown'''
        ...
    
    ...

class DropButtonStyle:
    '''Represents the symbol displayed on the drop button.'''
    
    @classmethod
    @property
    def PLAIN(cls) -> DropButtonStyle:
        '''Displays a button with no symbol.'''
        ...
    
    @classmethod
    @property
    def ARROW(cls) -> DropButtonStyle:
        '''Displays a button with a down arrow.'''
        ...
    
    @classmethod
    @property
    def ELLIPSIS(cls) -> DropButtonStyle:
        '''Displays a button with an ellipsis (...).'''
        ...
    
    @classmethod
    @property
    def REDUCE(cls) -> DropButtonStyle:
        '''Displays a button with a horizontal line like an underscore character.'''
        ...
    
    ...

class InputMethodEditorMode:
    '''Represents the default run-time mode of the Input Method Editor.'''
    
    @classmethod
    @property
    def NO_CONTROL(cls) -> InputMethodEditorMode:
        '''Does not control IME.'''
        ...
    
    @classmethod
    @property
    def ON(cls) -> InputMethodEditorMode:
        '''IME on.'''
        ...
    
    @classmethod
    @property
    def OFF(cls) -> InputMethodEditorMode:
        '''IME off. English mode.'''
        ...
    
    @classmethod
    @property
    def DISABLE(cls) -> InputMethodEditorMode:
        '''IME off.User can't turn on IME by keyboard.'''
        ...
    
    @classmethod
    @property
    def HIRAGANA(cls) -> InputMethodEditorMode:
        '''IME on with Full-width hiragana mode.'''
        ...
    
    @classmethod
    @property
    def KATAKANA(cls) -> InputMethodEditorMode:
        '''IME on with Full-width katakana mode.'''
        ...
    
    @classmethod
    @property
    def KATAKANA_HALF(cls) -> InputMethodEditorMode:
        '''IME on with Half-width katakana mode.'''
        ...
    
    @classmethod
    @property
    def ALPHA_FULL(cls) -> InputMethodEditorMode:
        '''IME on with Full-width Alphanumeric mode.'''
        ...
    
    @classmethod
    @property
    def ALPHA(cls) -> InputMethodEditorMode:
        '''IME on with Half-width Alphanumeric mode.'''
        ...
    
    @classmethod
    @property
    def HANGUL_FULL(cls) -> InputMethodEditorMode:
        '''IME on with Full-width hangul mode.'''
        ...
    
    @classmethod
    @property
    def HANGUL(cls) -> InputMethodEditorMode:
        '''IME on with Half-width hangul mode.'''
        ...
    
    @classmethod
    @property
    def HANZI_FULL(cls) -> InputMethodEditorMode:
        '''IME on with Full-width hanzi mode.'''
        ...
    
    @classmethod
    @property
    def HANZI(cls) -> InputMethodEditorMode:
        '''IME on with Half-width hanzi mode.'''
        ...
    
    ...

class ShowDropButtonType:
    '''Specifies when to show the drop button'''
    
    @classmethod
    @property
    def NEVER(cls) -> ShowDropButtonType:
        '''Never show the drop button.'''
        ...
    
    @classmethod
    @property
    def FOCUS(cls) -> ShowDropButtonType:
        '''Show the drop button when the control has the focus.'''
        ...
    
    @classmethod
    @property
    def ALWAYS(cls) -> ShowDropButtonType:
        '''Always show the drop button.'''
        ...
    
    ...

