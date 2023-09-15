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

class AutoNumberedBulletValue(BulletValue):
    '''Represents automatic numbered bullet.'''
    
    @property
    def type(self) -> aspose.cells.drawing.texts.BulletType:
        '''Gets the type of the bullet.'''
        ...
    
    @property
    def start_at(self) -> int:
        ...
    
    @start_at.setter
    def start_at(self, value : int):
        ...
    
    @property
    def autonumber_scheme(self) -> aspose.cells.drawing.texts.TextAutonumberScheme:
        ...
    
    @autonumber_scheme.setter
    def autonumber_scheme(self, value : aspose.cells.drawing.texts.TextAutonumberScheme):
        ...
    
    ...

class Bullet:
    '''Represents the bullet points should be applied to a paragraph.'''
    
    @property
    def bullet_value(self) -> aspose.cells.drawing.texts.BulletValue:
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.BulletType:
        '''Gets and sets the type of bullet.'''
        ...
    
    @type.setter
    def type(self, value : aspose.cells.drawing.texts.BulletType):
        '''Gets and sets the type of bullet.'''
        ...
    
    @property
    def font_name(self) -> str:
        ...
    
    @font_name.setter
    def font_name(self, value : str):
        ...
    
    ...

class BulletValue:
    '''Represents the value of the bullet.'''
    
    @property
    def type(self) -> aspose.cells.drawing.texts.BulletType:
        '''Gets the type of the bullet's value.'''
        ...
    
    ...

class CharacterBulletValue(BulletValue):
    '''Represents the character bullet.'''
    
    @property
    def type(self) -> aspose.cells.drawing.texts.BulletType:
        '''Gets the type of the bullet.'''
        ...
    
    @property
    def character(self) -> char:
        '''Gets and sets character of the bullet.'''
        ...
    
    @character.setter
    def character(self, value : char):
        '''Gets and sets character of the bullet.'''
        ...
    
    ...

class FontSettingCollection:
    '''Represents the list of :py:class:`aspose.cells.FontSetting`.'''
    
    @overload
    def replace(self, index : int, count : int, text : str):
        '''Replace the text.
        
        :param index: The start index.
        :param count: The count of characters.
        :param text: The text.'''
        ...
    
    @overload
    def replace(self, old_value : str, new_value : str):
        '''Replace the text.
        
        :param old_value: The old text.
        :param new_value: The new text.'''
        ...
    
    @overload
    def copy_to(self, array : List[aspose.cells.FontSetting]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.FontSetting], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.FontSetting, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.FontSetting, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.FontSetting) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.FontSetting, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.FontSetting, index : int, count : int) -> int:
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def get_paragraph_enumerator(self) -> collections.abc.Iterator:
        '''Gets the enumerator of the paragraphs.'''
        ...
    
    def append_text(self, text : str):
        '''Appends the text.
        
        :param text: The text.'''
        ...
    
    def insert_text(self, index : int, text : str):
        '''Insert index at the position.
        
        :param index: The start index.
        :param text: The text.'''
        ...
    
    def delete_text(self, index : int, count : int):
        '''Delete some characters.
        
        :param index: The start index.
        :param count: The count of characters.'''
        ...
    
    def format(self, start_index : int, length : int, font : aspose.cells.Font, flag : aspose.cells.StyleFlag):
        '''Format the text with font setting.
        
        :param start_index: The start index.
        :param length: The length.
        :param font: The font.
        :param flag: The flags of the font.'''
        ...
    
    def binary_search(self, item : aspose.cells.FontSetting) -> int:
        ...
    
    @property
    def text_alignment(self) -> aspose.cells.drawing.texts.ShapeTextAlignment:
        ...
    
    @property
    def text_paragraphs(self) -> aspose.cells.drawing.texts.TextParagraphCollection:
        ...
    
    @property
    def text(self) -> str:
        '''Gets and sets the text of the shape.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Gets and sets the text of the shape.'''
        ...
    
    @property
    def html_string(self) -> str:
        ...
    
    @html_string.setter
    def html_string(self, value : str):
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class NoneBulletValue(BulletValue):
    '''Represents no bullet.'''
    
    @property
    def type(self) -> aspose.cells.drawing.texts.BulletType:
        '''Gets the type of the bullet's value.'''
        ...
    
    ...

class PictureBulletValue(BulletValue):
    '''Represents the value of the image bullet.'''
    
    @property
    def type(self) -> aspose.cells.drawing.texts.BulletType:
        '''Gets the type of the bullet's value.'''
        ...
    
    @property
    def image_data(self) -> bytes:
        ...
    
    @image_data.setter
    def image_data(self, value : bytes):
        ...
    
    ...

class ShapeTextAlignment:
    '''Represents the setting of shape's text alignment;'''
    
    @property
    def is_text_wrapped(self) -> bool:
        ...
    
    @is_text_wrapped.setter
    def is_text_wrapped(self, value : bool):
        ...
    
    @property
    def rotate_text_with_shape(self) -> bool:
        ...
    
    @rotate_text_with_shape.setter
    def rotate_text_with_shape(self, value : bool):
        ...
    
    @property
    def text_vertical_overflow(self) -> aspose.cells.drawing.TextOverflowType:
        ...
    
    @text_vertical_overflow.setter
    def text_vertical_overflow(self, value : aspose.cells.drawing.TextOverflowType):
        ...
    
    @property
    def text_horizontal_overflow(self) -> aspose.cells.drawing.TextOverflowType:
        ...
    
    @text_horizontal_overflow.setter
    def text_horizontal_overflow(self, value : aspose.cells.drawing.TextOverflowType):
        ...
    
    @property
    def rotation_angle(self) -> float:
        ...
    
    @rotation_angle.setter
    def rotation_angle(self, value : float):
        ...
    
    @property
    def text_vertical_type(self) -> aspose.cells.drawing.texts.TextVerticalType:
        ...
    
    @text_vertical_type.setter
    def text_vertical_type(self, value : aspose.cells.drawing.texts.TextVerticalType):
        ...
    
    @property
    def is_locked_text(self) -> bool:
        ...
    
    @is_locked_text.setter
    def is_locked_text(self, value : bool):
        ...
    
    @property
    def auto_size(self) -> bool:
        ...
    
    @auto_size.setter
    def auto_size(self, value : bool):
        ...
    
    @property
    def text_shape_type(self) -> aspose.cells.drawing.AutoShapeType:
        ...
    
    @text_shape_type.setter
    def text_shape_type(self, value : aspose.cells.drawing.AutoShapeType):
        ...
    
    @property
    def top_margin_pt(self) -> float:
        ...
    
    @top_margin_pt.setter
    def top_margin_pt(self, value : float):
        ...
    
    @property
    def bottom_margin_pt(self) -> float:
        ...
    
    @bottom_margin_pt.setter
    def bottom_margin_pt(self, value : float):
        ...
    
    @property
    def left_margin_pt(self) -> float:
        ...
    
    @left_margin_pt.setter
    def left_margin_pt(self, value : float):
        ...
    
    @property
    def right_margin_pt(self) -> float:
        ...
    
    @right_margin_pt.setter
    def right_margin_pt(self, value : float):
        ...
    
    @property
    def is_auto_margin(self) -> bool:
        ...
    
    @is_auto_margin.setter
    def is_auto_margin(self, value : bool):
        ...
    
    @property
    def number_of_columns(self) -> int:
        ...
    
    @number_of_columns.setter
    def number_of_columns(self, value : int):
        ...
    
    ...

class TextOptions(aspose.cells.Font):
    '''Represents the text options.'''
    
    def equals(self, font : aspose.cells.Font) -> bool:
        '''Checks if two fonts are equals.
        
        :param font: Compared font object.
        :returns: True if equal to the compared font object.'''
        ...
    
    @property
    def charset(self) -> int:
        '''Represent the character set.'''
        ...
    
    @charset.setter
    def charset(self, value : int):
        '''Represent the character set.'''
        ...
    
    @property
    def is_italic(self) -> bool:
        ...
    
    @is_italic.setter
    def is_italic(self, value : bool):
        ...
    
    @property
    def is_bold(self) -> bool:
        ...
    
    @is_bold.setter
    def is_bold(self, value : bool):
        ...
    
    @property
    def caps_type(self) -> aspose.cells.TextCapsType:
        ...
    
    @caps_type.setter
    def caps_type(self, value : aspose.cells.TextCapsType):
        ...
    
    @property
    def strike_type(self) -> aspose.cells.TextStrikeType:
        ...
    
    @strike_type.setter
    def strike_type(self, value : aspose.cells.TextStrikeType):
        ...
    
    @property
    def is_strikeout(self) -> bool:
        ...
    
    @is_strikeout.setter
    def is_strikeout(self, value : bool):
        ...
    
    @property
    def script_offset(self) -> float:
        ...
    
    @script_offset.setter
    def script_offset(self, value : float):
        ...
    
    @property
    def is_superscript(self) -> bool:
        ...
    
    @is_superscript.setter
    def is_superscript(self, value : bool):
        ...
    
    @property
    def is_subscript(self) -> bool:
        ...
    
    @is_subscript.setter
    def is_subscript(self, value : bool):
        ...
    
    @property
    def underline(self) -> aspose.cells.FontUnderlineType:
        '''Gets the font underline type.'''
        ...
    
    @underline.setter
    def underline(self, value : aspose.cells.FontUnderlineType):
        '''Sets the font underline type.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets and sets the name of the shape.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and sets the name of the shape.'''
        ...
    
    @property
    def double_size(self) -> float:
        ...
    
    @double_size.setter
    def double_size(self, value : float):
        ...
    
    @property
    def size(self) -> int:
        '''Gets the size of the font.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets the size of the font.'''
        ...
    
    @property
    def theme_color(self) -> aspose.cells.ThemeColor:
        ...
    
    @theme_color.setter
    def theme_color(self, value : aspose.cells.ThemeColor):
        ...
    
    @property
    def color(self) -> aspose.pydrawing.Color:
        '''Gets the :py:class:`aspose.pydrawing.Color` of the font.'''
        ...
    
    @color.setter
    def color(self, value : aspose.pydrawing.Color):
        '''Sets the :py:class:`aspose.pydrawing.Color` of the font.'''
        ...
    
    @property
    def argb_color(self) -> int:
        ...
    
    @argb_color.setter
    def argb_color(self, value : int):
        ...
    
    @property
    def is_normalize_heights(self) -> bool:
        ...
    
    @is_normalize_heights.setter
    def is_normalize_heights(self, value : bool):
        ...
    
    @property
    def scheme_type(self) -> aspose.cells.FontSchemeType:
        ...
    
    @scheme_type.setter
    def scheme_type(self, value : aspose.cells.FontSchemeType):
        ...
    
    @property
    def language_code(self) -> aspose.cells.CountryCode:
        ...
    
    @language_code.setter
    def language_code(self, value : aspose.cells.CountryCode):
        ...
    
    @property
    def latin_name(self) -> str:
        ...
    
    @latin_name.setter
    def latin_name(self, value : str):
        ...
    
    @property
    def far_east_name(self) -> str:
        ...
    
    @far_east_name.setter
    def far_east_name(self, value : str):
        ...
    
    @property
    def fill(self) -> aspose.cells.drawing.FillFormat:
        '''Represents the fill format of the text.'''
        ...
    
    @property
    def outline(self) -> aspose.cells.drawing.LineFormat:
        '''Represents the outline format of the text.'''
        ...
    
    @property
    def shadow(self) -> aspose.cells.drawing.ShadowEffect:
        '''Represents a :py:class:`aspose.cells.drawing.ShadowEffect` object that specifies shadow effect for the chart element or shape.'''
        ...
    
    @property
    def underline_color(self) -> aspose.cells.CellsColor:
        ...
    
    @underline_color.setter
    def underline_color(self, value : aspose.cells.CellsColor):
        ...
    
    @property
    def kerning(self) -> float:
        '''Specifies the minimum font size at which character kerning will occur for this text run.'''
        ...
    
    @kerning.setter
    def kerning(self, value : float):
        '''Specifies the minimum font size at which character kerning will occur for this text run.'''
        ...
    
    @property
    def spacing(self) -> float:
        '''Specifies the spacing between characters within a text run.'''
        ...
    
    @spacing.setter
    def spacing(self, value : float):
        '''Specifies the spacing between characters within a text run.'''
        ...
    
    ...

class TextParagraph(aspose.cells.FontSetting):
    '''Represents the text paragraph setting.'''
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Gets the type of text node.'''
        ...
    
    @property
    def start_index(self) -> int:
        ...
    
    @property
    def length(self) -> int:
        '''Gets the length of the characters.'''
        ...
    
    @property
    def font(self) -> aspose.cells.Font:
        '''Returns the font of this object.'''
        ...
    
    @property
    def text_options(self) -> aspose.cells.drawing.texts.TextOptions:
        ...
    
    @property
    def bullet(self) -> aspose.cells.drawing.texts.Bullet:
        '''Gets the bullet.'''
        ...
    
    @property
    def line_space_size_type(self) -> aspose.cells.drawing.texts.LineSpaceSizeType:
        ...
    
    @line_space_size_type.setter
    def line_space_size_type(self, value : aspose.cells.drawing.texts.LineSpaceSizeType):
        ...
    
    @property
    def line_space(self) -> float:
        ...
    
    @line_space.setter
    def line_space(self, value : float):
        ...
    
    @property
    def space_after_size_type(self) -> aspose.cells.drawing.texts.LineSpaceSizeType:
        ...
    
    @space_after_size_type.setter
    def space_after_size_type(self, value : aspose.cells.drawing.texts.LineSpaceSizeType):
        ...
    
    @property
    def space_after(self) -> float:
        ...
    
    @space_after.setter
    def space_after(self, value : float):
        ...
    
    @property
    def space_before_size_type(self) -> aspose.cells.drawing.texts.LineSpaceSizeType:
        ...
    
    @space_before_size_type.setter
    def space_before_size_type(self, value : aspose.cells.drawing.texts.LineSpaceSizeType):
        ...
    
    @property
    def space_before(self) -> float:
        ...
    
    @space_before.setter
    def space_before(self, value : float):
        ...
    
    @property
    def stops(self) -> aspose.cells.drawing.texts.TextTabStopCollection:
        '''Gets tab stop list.'''
        ...
    
    @property
    def is_latin_line_break(self) -> bool:
        ...
    
    @is_latin_line_break.setter
    def is_latin_line_break(self, value : bool):
        ...
    
    @property
    def is_east_asian_line_break(self) -> bool:
        ...
    
    @is_east_asian_line_break.setter
    def is_east_asian_line_break(self, value : bool):
        ...
    
    @property
    def is_hanging_punctuation(self) -> bool:
        ...
    
    @is_hanging_punctuation.setter
    def is_hanging_punctuation(self, value : bool):
        ...
    
    @property
    def right_margin(self) -> float:
        ...
    
    @right_margin.setter
    def right_margin(self, value : float):
        ...
    
    @property
    def left_margin(self) -> float:
        ...
    
    @left_margin.setter
    def left_margin(self, value : float):
        ...
    
    @property
    def first_line_indent(self) -> float:
        ...
    
    @first_line_indent.setter
    def first_line_indent(self, value : float):
        ...
    
    @property
    def font_align_type(self) -> aspose.cells.drawing.texts.TextFontAlignType:
        ...
    
    @font_align_type.setter
    def font_align_type(self, value : aspose.cells.drawing.texts.TextFontAlignType):
        ...
    
    @property
    def alignment_type(self) -> aspose.cells.TextAlignmentType:
        ...
    
    @alignment_type.setter
    def alignment_type(self, value : aspose.cells.TextAlignmentType):
        ...
    
    @property
    def default_tab_size(self) -> float:
        ...
    
    @default_tab_size.setter
    def default_tab_size(self, value : float):
        ...
    
    @property
    def children(self) -> List[aspose.cells.FontSetting]:
        '''Gets all text runs in this paragraph.
        If this paragraph is empty, return paragraph itself.'''
        ...
    
    ...

class TextParagraphCollection:
    '''Represents all text paragraph.'''
    
    def get_enumerator(self) -> collections.abc.Iterator:
        '''Gets the enumerator of the paragraphs.'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of text paragraphs.'''
        ...
    
    def __getitem__(self, key : int) -> aspose.cells.drawing.texts.TextParagraph:
        '''Gets the :py:class:`aspose.cells.drawing.texts.TextParagraph` object at specific index.'''
        ...
    
    ...

class TextTabStop:
    '''Represents tab stop.'''
    
    @property
    def tab_alignment(self) -> aspose.cells.drawing.texts.TextTabAlignmentType:
        ...
    
    @tab_alignment.setter
    def tab_alignment(self, value : aspose.cells.drawing.texts.TextTabAlignmentType):
        ...
    
    @property
    def tab_position(self) -> float:
        ...
    
    @tab_position.setter
    def tab_position(self, value : float):
        ...
    
    ...

class TextTabStopCollection:
    '''Represents the list of all tab stops.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.drawing.texts.TextTabStop]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.drawing.texts.TextTabStop], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.drawing.texts.TextTabStop, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.drawing.texts.TextTabStop, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.drawing.texts.TextTabStop) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.drawing.texts.TextTabStop, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.drawing.texts.TextTabStop, index : int, count : int) -> int:
        ...
    
    def add(self, tab_alignment : aspose.cells.drawing.texts.TextTabAlignmentType, tab_position : float) -> int:
        '''Adds a tab stop.'''
        ...
    
    def binary_search(self, item : aspose.cells.drawing.texts.TextTabStop) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class BulletType:
    '''Represents the type of the bullet.'''
    
    @classmethod
    @property
    def NONE(cls) -> BulletType:
        '''No bullet.'''
        ...
    
    @classmethod
    @property
    def CHARACTER(cls) -> BulletType:
        '''Character bullet.'''
        ...
    
    @classmethod
    @property
    def PICTURE(cls) -> BulletType:
        '''Image bullet.'''
        ...
    
    @classmethod
    @property
    def AUTO_NUMBERED(cls) -> BulletType:
        '''Automatic numbered bullet.'''
        ...
    
    ...

class LineSpaceSizeType:
    '''Represents the unit type of line space size.'''
    
    @classmethod
    @property
    def PERCENTAGE(cls) -> LineSpaceSizeType:
        '''Represents in unit of a percentage of the text size.'''
        ...
    
    @classmethod
    @property
    def POINTS(cls) -> LineSpaceSizeType:
        '''Represents in unit of points.'''
        ...
    
    ...

class TextAutonumberScheme:
    '''Represents all automatic number scheme.'''
    
    @classmethod
    @property
    def NONE(cls) -> TextAutonumberScheme:
        ...
    
    @classmethod
    @property
    def ALPHA_LC_PAREN_BOTH(cls) -> TextAutonumberScheme:
        '''(a), (b), (c), …'''
        ...
    
    @classmethod
    @property
    def ALPHA_LC_PAREN_R(cls) -> TextAutonumberScheme:
        '''a), b), c), …'''
        ...
    
    @classmethod
    @property
    def ALPHA_LC_PERIOD(cls) -> TextAutonumberScheme:
        '''a., b., c., …'''
        ...
    
    @classmethod
    @property
    def ALPHA_UC_PAREN_BOTH(cls) -> TextAutonumberScheme:
        '''(A), (B), (C), …'''
        ...
    
    @classmethod
    @property
    def ALPHA_UC_PAREN_R(cls) -> TextAutonumberScheme:
        '''A), B), C), …'''
        ...
    
    @classmethod
    @property
    def ALPHA_UC_PERIOD(cls) -> TextAutonumberScheme:
        '''A., B., C., …'''
        ...
    
    @classmethod
    @property
    def ARABIC_1_MINUS(cls) -> TextAutonumberScheme:
        '''Bidi Arabic 1 (AraAlpha) with ANSI minus symbol'''
        ...
    
    @classmethod
    @property
    def ARABIC_2_MINUS(cls) -> TextAutonumberScheme:
        '''Bidi Arabic 2 (AraAbjad) with ANSI minus symbol'''
        ...
    
    @classmethod
    @property
    def ARABIC_DB_PERIOD(cls) -> TextAutonumberScheme:
        '''Dbl-byte Arabic numbers w/ double-byte period'''
        ...
    
    @classmethod
    @property
    def ARABIC_DB_PLAIN(cls) -> TextAutonumberScheme:
        '''Dbl-byte Arabic numbers'''
        ...
    
    @classmethod
    @property
    def ARABIC_PAREN_BOTH(cls) -> TextAutonumberScheme:
        '''(1), (2), (3), …'''
        ...
    
    @classmethod
    @property
    def ARABIC_PAREN_R(cls) -> TextAutonumberScheme:
        '''1), 2), 3), …'''
        ...
    
    @classmethod
    @property
    def ARABIC_PERIOD(cls) -> TextAutonumberScheme:
        '''1., 2., 3., …'''
        ...
    
    @classmethod
    @property
    def ARABIC_PLAIN(cls) -> TextAutonumberScheme:
        '''1, 2, 3, …'''
        ...
    
    @classmethod
    @property
    def CIRCLE_NUM_DB_PLAIN(cls) -> TextAutonumberScheme:
        '''Dbl-byte circle numbers (1-10 circle[0x2460-], 11-arabic numbers)'''
        ...
    
    @classmethod
    @property
    def CIRCLE_NUM_WD_BLACK_PLAIN(cls) -> TextAutonumberScheme:
        '''Wingdings black circle numbers'''
        ...
    
    @classmethod
    @property
    def CIRCLE_NUM_WD_WHITE_PLAIN(cls) -> TextAutonumberScheme:
        '''Wingdings white circle numbers (0-10 circle[0x0080-],11- arabic numbers)'''
        ...
    
    @classmethod
    @property
    def EA_1_CHS_PERIOD(cls) -> TextAutonumberScheme:
        '''EA: Simplified Chinese w/ single-byte period'''
        ...
    
    @classmethod
    @property
    def EA_1_CHS_PLAIN(cls) -> TextAutonumberScheme:
        '''EA: Simplified Chinese (TypeA 1-99, TypeC 100-)'''
        ...
    
    @classmethod
    @property
    def EA_1_CHT_PERIOD(cls) -> TextAutonumberScheme:
        '''EA: Traditional Chinese w/ single-byte period'''
        ...
    
    @classmethod
    @property
    def EA_1_CHT_PLAIN(cls) -> TextAutonumberScheme:
        '''EA: Traditional Chinese (TypeA 1-19, TypeC 20-)'''
        ...
    
    @classmethod
    @property
    def EA_1_JPN_CHS_DB_PERIOD(cls) -> TextAutonumberScheme:
        '''EA: Japanese w/ double-byte period'''
        ...
    
    @classmethod
    @property
    def EA_1_JPN_KOR_PERIOD(cls) -> TextAutonumberScheme:
        '''EA: Japanese/Korean w/ single-byte period'''
        ...
    
    @classmethod
    @property
    def EA_1_JPN_KOR_PLAIN(cls) -> TextAutonumberScheme:
        '''EA: Japanese/Korean (TypeC 1-)'''
        ...
    
    @classmethod
    @property
    def HEBREW_2_MINUS(cls) -> TextAutonumberScheme:
        '''Bidi Hebrew 2 with ANSI minus symbol'''
        ...
    
    @classmethod
    @property
    def HINDI_ALPHA_1_PERIOD(cls) -> TextAutonumberScheme:
        '''Hindi alphabet period - consonants'''
        ...
    
    @classmethod
    @property
    def HINDI_ALPHA_PERIOD(cls) -> TextAutonumberScheme:
        '''Hindi alphabet period - vowels'''
        ...
    
    @classmethod
    @property
    def HINDI_NUM_PAREN_R(cls) -> TextAutonumberScheme:
        '''Hindi numerical parentheses - right'''
        ...
    
    @classmethod
    @property
    def HINDI_NUM_PERIOD(cls) -> TextAutonumberScheme:
        '''Hindi numerical period'''
        ...
    
    @classmethod
    @property
    def ROMAN_LC_PAREN_BOTH(cls) -> TextAutonumberScheme:
        '''(i), (ii), (iii), …'''
        ...
    
    @classmethod
    @property
    def ROMAN_LC_PAREN_R(cls) -> TextAutonumberScheme:
        '''i), ii), iii), …'''
        ...
    
    @classmethod
    @property
    def ROMAN_LC_PERIOD(cls) -> TextAutonumberScheme:
        '''i., ii., iii., …'''
        ...
    
    @classmethod
    @property
    def ROMAN_UC_PAREN_BOTH(cls) -> TextAutonumberScheme:
        '''(I), (II), (III), …'''
        ...
    
    @classmethod
    @property
    def ROMAN_UC_PAREN_R(cls) -> TextAutonumberScheme:
        '''I), II), III), …'''
        ...
    
    @classmethod
    @property
    def ROMAN_UC_PERIOD(cls) -> TextAutonumberScheme:
        '''I., II., III., …'''
        ...
    
    @classmethod
    @property
    def THAI_ALPHA_PAREN_BOTH(cls) -> TextAutonumberScheme:
        '''Thai alphabet parentheses - both'''
        ...
    
    @classmethod
    @property
    def THAI_ALPHA_PAREN_R(cls) -> TextAutonumberScheme:
        '''Thai alphabet parentheses - right'''
        ...
    
    @classmethod
    @property
    def THAI_ALPHA_PERIOD(cls) -> TextAutonumberScheme:
        '''Thai alphabet period'''
        ...
    
    @classmethod
    @property
    def THAI_NUM_PAREN_BOTH(cls) -> TextAutonumberScheme:
        '''Thai numerical parentheses - both'''
        ...
    
    @classmethod
    @property
    def THAI_NUM_PAREN_R(cls) -> TextAutonumberScheme:
        '''Thai numerical parentheses - right'''
        ...
    
    @classmethod
    @property
    def THAI_NUM_PERIOD(cls) -> TextAutonumberScheme:
        '''Thai numerical period'''
        ...
    
    ...

class TextFontAlignType:
    '''Represents the different types of font alignment.'''
    
    @classmethod
    @property
    def AUTOMATIC(cls) -> TextFontAlignType:
        '''When the text flow is horizontal or simple vertical same as fontBaseline
        but for other vertical modes same as fontCenter.'''
        ...
    
    @classmethod
    @property
    def BOTTOM(cls) -> TextFontAlignType:
        '''The letters are anchored to the very bottom of a single line.'''
        ...
    
    @classmethod
    @property
    def BASELINE(cls) -> TextFontAlignType:
        '''The letters are anchored to the bottom baseline of a single line.'''
        ...
    
    @classmethod
    @property
    def CENTER(cls) -> TextFontAlignType:
        '''The letters are anchored between the two baselines of a single line.'''
        ...
    
    @classmethod
    @property
    def TOP(cls) -> TextFontAlignType:
        '''The letters are anchored to the top baseline of a single line.'''
        ...
    
    ...

class TextNodeType:
    '''Represents the node type.'''
    
    @classmethod
    @property
    def TEXT_RUN(cls) -> TextNodeType:
        '''Represents the text node.'''
        ...
    
    @classmethod
    @property
    def TEXT_PARAGRAPH(cls) -> TextNodeType:
        '''Represents the text paragraph.'''
        ...
    
    @classmethod
    @property
    def EQUATION(cls) -> TextNodeType:
        '''Represents the equation text.'''
        ...
    
    ...

class TextTabAlignmentType:
    '''Represents the text tab alignment types.'''
    
    @classmethod
    @property
    def CENTER(cls) -> TextTabAlignmentType:
        '''The text at this tab stop is center aligned.'''
        ...
    
    @classmethod
    @property
    def DECIMAL(cls) -> TextTabAlignmentType:
        '''At this tab stop, the decimals are lined up.'''
        ...
    
    @classmethod
    @property
    def LEFT(cls) -> TextTabAlignmentType:
        '''The text at this tab stop is left aligned.'''
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> TextTabAlignmentType:
        '''The text at this tab stop is right aligned.'''
        ...
    
    ...

class TextVerticalType:
    '''Represents the text direct type.'''
    
    @classmethod
    @property
    def VERTICAL(cls) -> TextVerticalType:
        '''East Asian Vertical display.'''
        ...
    
    @classmethod
    @property
    def HORIZONTAL(cls) -> TextVerticalType:
        '''Horizontal text.'''
        ...
    
    @classmethod
    @property
    def VERTICAL_LEFT_TO_RIGHT(cls) -> TextVerticalType:
        '''Displayed vertical and the text flows top down then LEFT to RIGHT'''
        ...
    
    @classmethod
    @property
    def VERTICAL90(cls) -> TextVerticalType:
        '''Each line is 90 degrees rotated clockwise'''
        ...
    
    @classmethod
    @property
    def VERTICAL270(cls) -> TextVerticalType:
        '''Each line is 270 degrees rotated clockwise'''
        ...
    
    @classmethod
    @property
    def STACKED(cls) -> TextVerticalType:
        '''Determines if all of the text is vertical'''
        ...
    
    @classmethod
    @property
    def STACKED_RIGHT_TO_LEFT(cls) -> TextVerticalType:
        '''Specifies that vertical WordArt should be shown from right to left rather than left to right.'''
        ...
    
    ...

