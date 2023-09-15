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

class AccentEquationNode(EquationNode):
    '''This class specifies an accent equation, consisting of a base component and a combining diacritic.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def accent_character(self) -> str:
        ...
    
    @accent_character.setter
    def accent_character(self, value : str):
        ...
    
    @property
    def accent_character_type(self) -> aspose.cells.drawing.equations.EquationCombiningCharacterType:
        ...
    
    @accent_character_type.setter
    def accent_character_type(self, value : aspose.cells.drawing.equations.EquationCombiningCharacterType):
        ...
    
    ...

class BarEquationNode(EquationNode):
    '''This class specifies the bar equation, consisting of a base argument and an overbar or underbar.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def bar_position(self) -> aspose.cells.drawing.equations.EquationCharacterPositionType:
        ...
    
    @bar_position.setter
    def bar_position(self, value : aspose.cells.drawing.equations.EquationCharacterPositionType):
        ...
    
    ...

class BorderBoxEquationNode(EquationNode):
    '''This class specifies the Border Box function, consisting of a border drawn around an equation.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    ...

class BoxEquationNode(EquationNode):
    '''This class specifies the box function, which is used to group components of an equation.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    ...

class DelimiterEquationNode(EquationNode):
    '''This class specifies the delimiter equation, consisting of opening and closing delimiters (such as parentheses, braces, brackets, and vertical bars), and a component contained inside.
    The delimiter may have more than one component, with a designated separator character between each component.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def begin_char(self) -> str:
        ...
    
    @begin_char.setter
    def begin_char(self, value : str):
        ...
    
    @property
    def end_char(self) -> str:
        ...
    
    @end_char.setter
    def end_char(self, value : str):
        ...
    
    @property
    def nary_grow(self) -> bool:
        ...
    
    @nary_grow.setter
    def nary_grow(self, value : bool):
        ...
    
    @property
    def separator_char(self) -> str:
        ...
    
    @separator_char.setter
    def separator_char(self, value : str):
        ...
    
    @property
    def delimiter_shape(self) -> aspose.cells.drawing.equations.EquationDelimiterShapeType:
        ...
    
    @delimiter_shape.setter
    def delimiter_shape(self, value : aspose.cells.drawing.equations.EquationDelimiterShapeType):
        ...
    
    ...

class EquationComponentNode(EquationNode):
    '''This class specifies the components of an equation or mathematical expression.
    Different types of components combined into different equations.
    For example, a fraction consists of two parts, a numerator component and a denominator component.
    For more component types, please refer to 'EquationNodeType'.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    ...

class EquationNode(aspose.cells.FontSetting):
    '''Abstract class for deriving other equation nodes.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    ...

class EquationNodeParagraph(EquationNode):
    '''This class specifies a mathematical paragraph containing one or more MathEquationNode(OMath) elements.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def justification(self) -> aspose.cells.drawing.equations.EquationHorizontalJustificationType:
        '''This specifies justification of the math paragraph (a series of adjacent equations within the same paragraph). A math paragraph can be Left Justified, Right Justified, Centered, or Centered as Group. By default, the math paragraph is Centered as Group. This means that the equations can be aligned with respect to each other, but the entire group of equations is centered as a whole.'''
        ...
    
    @justification.setter
    def justification(self, value : aspose.cells.drawing.equations.EquationHorizontalJustificationType):
        '''This specifies justification of the math paragraph (a series of adjacent equations within the same paragraph). A math paragraph can be Left Justified, Right Justified, Centered, or Centered as Group. By default, the math paragraph is Centered as Group. This means that the equations can be aligned with respect to each other, but the entire group of equations is centered as a whole.'''
        ...
    
    ...

class FractionEquationNode(EquationNode):
    '''This class  specifies the fraction equation, consisting of a numerator and denominator separated by a fraction bar. The fraction bar can be horizontal or diagonal, depending on the fraction properties. The fraction equation is also used to represent the stack function, which places one element above another, with no fraction bar.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def fraction_type(self) -> aspose.cells.drawing.equations.EquationFractionType:
        ...
    
    @fraction_type.setter
    def fraction_type(self, value : aspose.cells.drawing.equations.EquationFractionType):
        ...
    
    ...

class FunctionEquationNode(EquationNode):
    '''This class specifies the Function-Apply equation, which consists of a function name and an argument acted upon.
    The types of the name and argument components are 'EquationNodeType.FunctionName' and 'EquationNodeType.Base' respectively.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    ...

class GroupCharacterEquationNode(EquationNode):
    '''This class specifies the Group-Character function, consisting of a character drawn above or below text, often with the purpose of visually grouping items.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def group_chr(self) -> str:
        ...
    
    @group_chr.setter
    def group_chr(self, value : str):
        ...
    
    @property
    def chr_type(self) -> aspose.cells.drawing.equations.EquationCombiningCharacterType:
        ...
    
    @chr_type.setter
    def chr_type(self, value : aspose.cells.drawing.equations.EquationCombiningCharacterType):
        ...
    
    @property
    def position(self) -> aspose.cells.drawing.equations.EquationCharacterPositionType:
        '''This attribute specifies the position of the character in the object'''
        ...
    
    @position.setter
    def position(self, value : aspose.cells.drawing.equations.EquationCharacterPositionType):
        '''This attribute specifies the position of the character in the object'''
        ...
    
    @property
    def vert_jc(self) -> aspose.cells.drawing.equations.EquationCharacterPositionType:
        ...
    
    @vert_jc.setter
    def vert_jc(self, value : aspose.cells.drawing.equations.EquationCharacterPositionType):
        ...
    
    ...

class MathematicalEquationNode(EquationNode):
    '''This class specifies an equation or mathematical expression. All mathematical text of equations or mathematical expressions are contained by this class.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    ...

class MatrixEquationNode(EquationNode):
    '''This class specifies the Matrix equation, consisting of one or more elements laid out in one or more rows and one or more columns.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def base_jc(self) -> aspose.cells.drawing.equations.EquationVerticalJustificationType:
        ...
    
    @base_jc.setter
    def base_jc(self, value : aspose.cells.drawing.equations.EquationVerticalJustificationType):
        ...
    
    @property
    def is_hide_placeholder(self) -> bool:
        ...
    
    @is_hide_placeholder.setter
    def is_hide_placeholder(self, value : bool):
        ...
    
    ...

class NaryEquationNode(EquationNode):
    '''This class specifies an n-ary operator equation consisting of an n-ary operator, a base (or operand), and optional upper and lower bounds.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def is_hide_subscript(self) -> bool:
        ...
    
    @is_hide_subscript.setter
    def is_hide_subscript(self, value : bool):
        ...
    
    @property
    def is_hide_superscript(self) -> bool:
        ...
    
    @is_hide_superscript.setter
    def is_hide_superscript(self, value : bool):
        ...
    
    @property
    def limit_location(self) -> aspose.cells.drawing.equations.EquationLimitLocationType:
        ...
    
    @limit_location.setter
    def limit_location(self, value : aspose.cells.drawing.equations.EquationLimitLocationType):
        ...
    
    @property
    def nary_operator(self) -> str:
        ...
    
    @nary_operator.setter
    def nary_operator(self, value : str):
        ...
    
    @property
    def nary_operator_type(self) -> aspose.cells.drawing.equations.EquationMathematicalOperatorType:
        ...
    
    @nary_operator_type.setter
    def nary_operator_type(self, value : aspose.cells.drawing.equations.EquationMathematicalOperatorType):
        ...
    
    @property
    def nary_grow(self) -> bool:
        ...
    
    @nary_grow.setter
    def nary_grow(self, value : bool):
        ...
    
    ...

class RadicalEquationNode(EquationNode):
    '''This class specifies the radical equation, consisting of an optional degree deg(EquationNodeType.Degree) and a base.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def is_deg_hide(self) -> bool:
        ...
    
    @is_deg_hide.setter
    def is_deg_hide(self, value : bool):
        ...
    
    ...

class SubSupEquationNode(EquationNode):
    '''This class specifies an equation that can optionally be superscript or subscript.
    There are four main forms of this equation, superscript，subscript，superscript and subscript placed to the left of the base, superscript and subscript placed to the right of the base.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    ...

class TextRunEquationNode(EquationNode):
    '''This class in the equation node is used to store the actual content(a sequence of mathematical text) of the equation.
    Usually a node object per character.'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    @property
    def text(self) -> str:
        '''Set the content of the text node(Usually a node object per character).'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Set the content of the text node(Usually a node object per character).'''
        ...
    
    ...

class UnknowEquationNode(EquationNode):
    '''Equation node class of unknown type'''
    
    @overload
    def add_child(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Insert a node of the specified type at the end of the child node list of the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @overload
    def add_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Inserts the specified node at the end of the current node's list of child nodes.
        
        :param node: The specified node'''
        ...
    
    @overload
    def remove_child(self, node : aspose.cells.drawing.equations.EquationNode):
        '''Removes the specified node from the current node's children.
        
        :param node: Node to be deleted.'''
        ...
    
    @overload
    def remove_child(self, index : int):
        '''Removes the node at the specified index from the current node's children.
        
        :param index: Index of the node'''
        ...
    
    def set_word_art_style(self, style : aspose.cells.drawing.PresetWordArtStyle):
        '''Sets the preset WordArt style.
        
        :param style: The preset WordArt style.'''
        ...
    
    def insert_child(self, index : int, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts a node of the specified type at the specified index position in the current node's child node list.
        
        :param index: index value
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_after(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node after the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def insert_before(self, equation_type : aspose.cells.drawing.equations.EquationNodeType) -> aspose.cells.drawing.equations.EquationNode:
        '''Inserts the specified node before the current node.
        
        :param equation_type: Types of Equation Nodes
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    def get_child(self, index : int) -> aspose.cells.drawing.equations.EquationNode:
        '''Returns the node at the specified index among the children of the current node.
        
        :param index: Index of the node
        :returns: Returns the corresponding node if the specified node exists, otherwise returns null.'''
        ...
    
    def remove(self):
        '''Removes itself from the parent.'''
        ...
    
    def remove_all_children(self):
        '''Removes all the child nodes of the current node.'''
        ...
    
    @staticmethod
    def create_node(equation_type : aspose.cells.drawing.equations.EquationNodeTypeworkbook : aspose.cells.Workbook, parent : aspose.cells.drawing.equations.EquationNode) -> aspose.cells.drawing.equations.EquationNode:
        '''Create a node of the specified type.
        
        :param equation_type: Types of Equation Nodes
        :param workbook: The workbook object associated with the equation
        :param parent: The parent node where this node is located
        :returns: If the specified type exists, the corresponding node is returned, and if the type does not exist, a node of unknown type is returned.'''
        ...
    
    @property
    def type(self) -> aspose.cells.drawing.texts.TextNodeType:
        '''Represents the type of the node.'''
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
    def parent_node(self) -> aspose.cells.drawing.equations.EquationNode:
        ...
    
    @parent_node.setter
    def parent_node(self, value : aspose.cells.drawing.equations.EquationNode):
        ...
    
    @property
    def equation_type(self) -> aspose.cells.drawing.equations.EquationNodeType:
        ...
    
    ...

class EquationCharacterPositionType:
    '''Specifies the position of a particular subobject within its parent'''
    
    @classmethod
    @property
    def TOP(cls) -> EquationCharacterPositionType:
        '''At the top of the parent object'''
        ...
    
    @classmethod
    @property
    def BOTTOM(cls) -> EquationCharacterPositionType:
        '''At the bottom of the parent object'''
        ...
    
    ...

class EquationCombiningCharacterType:
    '''Type of combining characters.'''
    
    @classmethod
    @property
    def UNKNOWN(cls) -> EquationCombiningCharacterType:
        '''Use unknown type when not found in existing type.'''
        ...
    
    @classmethod
    @property
    def DOT_ABOVE(cls) -> EquationCombiningCharacterType:
        '''"̇" Unicode: u0307
        Combining Dot Above'''
        ...
    
    @classmethod
    @property
    def DIAERESIS(cls) -> EquationCombiningCharacterType:
        '''"̈" Unicode: u0308
        Combining Diaeresis'''
        ...
    
    @classmethod
    @property
    def THREE_DOTS_ABOVE(cls) -> EquationCombiningCharacterType:
        '''"⃛" Unicode: u20db
        Combining Three Dots Above'''
        ...
    
    @classmethod
    @property
    def CIRCUMFLEX_ACCENT(cls) -> EquationCombiningCharacterType:
        '''"̂" Unicode: u0302
        Combining Circumflex Accent'''
        ...
    
    @classmethod
    @property
    def CARON(cls) -> EquationCombiningCharacterType:
        '''"̌" Unicode: u030c
        Combining Caron'''
        ...
    
    @classmethod
    @property
    def ACUTE_ACCENT(cls) -> EquationCombiningCharacterType:
        '''"́" Unicode: u0301
        Combining Acute Accent'''
        ...
    
    @classmethod
    @property
    def GRAVE_ACCENT(cls) -> EquationCombiningCharacterType:
        '''"̀" Unicode: u0300
        Combining Grave Accent'''
        ...
    
    @classmethod
    @property
    def BREVE(cls) -> EquationCombiningCharacterType:
        '''"̆" Unicode: u0306
        Combining Combining Breve'''
        ...
    
    @classmethod
    @property
    def TILDE(cls) -> EquationCombiningCharacterType:
        '''"̃" Unicode: u0303
        Combining Tilde'''
        ...
    
    @classmethod
    @property
    def OVERLINE(cls) -> EquationCombiningCharacterType:
        '''"̅" Unicode: u0305
        Combining Overline'''
        ...
    
    @classmethod
    @property
    def DOUBLE_OVERLINE(cls) -> EquationCombiningCharacterType:
        '''"̿" Unicode: u033f
        Combining Double Overline'''
        ...
    
    @classmethod
    @property
    def TOP_CURLY_BRACKET(cls) -> EquationCombiningCharacterType:
        '''"⏞" Unicode: u23de
        Combining Top Curly Bracket'''
        ...
    
    @classmethod
    @property
    def BOTTOM_CURLY_BRACKET(cls) -> EquationCombiningCharacterType:
        '''"⏟" Unicode: u23df
        Combining Bottom Curly Bracket'''
        ...
    
    @classmethod
    @property
    def LEFT_ARROW_ABOVE(cls) -> EquationCombiningCharacterType:
        '''"⃖" Unicode: u20d6
        Combining Left Arrow Above'''
        ...
    
    @classmethod
    @property
    def RIGHT_ARROW_ABOVE(cls) -> EquationCombiningCharacterType:
        '''"⃗" Unicode: u20d7
        Combining Right Arrow Above'''
        ...
    
    @classmethod
    @property
    def LEFT_RIGHT_ARROW_ABOVE(cls) -> EquationCombiningCharacterType:
        '''"⃡" Unicode: u20e1
        Combining Left Right Arrow Above'''
        ...
    
    @classmethod
    @property
    def LEFT_HARPOON_ABOVE(cls) -> EquationCombiningCharacterType:
        '''"⃐" Unicode: u20d0
        Combining Left Harpoon Above'''
        ...
    
    @classmethod
    @property
    def RIGHT_HARPOON_ABOVE(cls) -> EquationCombiningCharacterType:
        '''"⃑" Unicode: u20d1
        Combining Right Harpoon Above'''
        ...
    
    @classmethod
    @property
    def LEFTWARDS_ARROW(cls) -> EquationCombiningCharacterType:
        '''"←" Unicode: u2190
        Leftwards Arrow'''
        ...
    
    @classmethod
    @property
    def RIGHTWARDS_ARROW(cls) -> EquationCombiningCharacterType:
        '''"→" Unicode: u2192
        Rightwards Arrow'''
        ...
    
    @classmethod
    @property
    def LEFT_RIGHT_ARROW(cls) -> EquationCombiningCharacterType:
        '''"↔" Unicode: u2194
        Left Right Arrow'''
        ...
    
    @classmethod
    @property
    def LEFTWARDS_DOUBLE_ARROW(cls) -> EquationCombiningCharacterType:
        '''"⇐" Unicode: u21d0
        Leftwards Double Arrow'''
        ...
    
    @classmethod
    @property
    def RIGHTWARDS_DOUBLE_ARROW(cls) -> EquationCombiningCharacterType:
        '''"⇒" Unicode: u21d2
        Rightwards Double Arrow'''
        ...
    
    @classmethod
    @property
    def LEFT_RIGHT_DOUBLE_ARROW(cls) -> EquationCombiningCharacterType:
        '''"⇔" Unicode: u21d4
        Left Right Double Arrow'''
        ...
    
    ...

class EquationDelimiterShapeType:
    '''This specifies the shape of delimiters in the delimiter object.'''
    
    @classmethod
    @property
    def CENTERED(cls) -> EquationDelimiterShapeType:
        '''The divider is centered around the entire height of its content.'''
        ...
    
    @classmethod
    @property
    def MATCH(cls) -> EquationDelimiterShapeType:
        '''The divider is altered to exactly match their contents' height.'''
        ...
    
    ...

class EquationFractionType:
    '''This specifies the display style of the fraction bar.'''
    
    @classmethod
    @property
    def BAR(cls) -> EquationFractionType:
        '''This specifies that the numerator is above and the denominator below is separated by a bar in the middle.'''
        ...
    
    @classmethod
    @property
    def NO_BAR(cls) -> EquationFractionType:
        '''This specifies that the numerator is above and the denominator below is not separated by a bar in the middle.'''
        ...
    
    @classmethod
    @property
    def LINEAR(cls) -> EquationFractionType:
        '''This specifies that the numerator is on the left and the denominator is on the right, separated by a '/' in between.'''
        ...
    
    @classmethod
    @property
    def SKEWED(cls) -> EquationFractionType:
        '''This specifies that the numerator is on the upper left and the denominator is on the lower right, separated by a "/".'''
        ...
    
    ...

class EquationHorizontalJustificationType:
    '''This specifies the default horizontal justification of equations in the document.'''
    
    @classmethod
    @property
    def CENTER(cls) -> EquationHorizontalJustificationType:
        '''Centered'''
        ...
    
    @classmethod
    @property
    def CENTER_GROUP(cls) -> EquationHorizontalJustificationType:
        '''Centered as Group'''
        ...
    
    @classmethod
    @property
    def LEFT(cls) -> EquationHorizontalJustificationType:
        '''Left Justified'''
        ...
    
    @classmethod
    @property
    def RIGHT(cls) -> EquationHorizontalJustificationType:
        '''Right Justified'''
        ...
    
    ...

class EquationLimitLocationType:
    '''Specifies the limit location on an operator.'''
    
    @classmethod
    @property
    def UND_OVR(cls) -> EquationLimitLocationType:
        '''Specifies that the limit is centered above or below the operator.'''
        ...
    
    @classmethod
    @property
    def SUB_SUP(cls) -> EquationLimitLocationType:
        '''Specifies that the limit is on the right side of the operator.'''
        ...
    
    ...

class EquationMathematicalOperatorType:
    '''Mathematical Operators Type'''
    
    @classmethod
    @property
    def UNKNOWN(cls) -> EquationMathematicalOperatorType:
        '''Use unknown type when not found in existing type.'''
        ...
    
    @classmethod
    @property
    def FOR_ALL(cls) -> EquationMathematicalOperatorType:
        '''"∀" Unicode:\u2200'''
        ...
    
    @classmethod
    @property
    def COMPLEMENT(cls) -> EquationMathematicalOperatorType:
        '''"∁" Unicode:\u2201'''
        ...
    
    @classmethod
    @property
    def PARTIAL_DIFFERENTIAL(cls) -> EquationMathematicalOperatorType:
        '''"∂" Unicode:\u2202'''
        ...
    
    @classmethod
    @property
    def EXISTS(cls) -> EquationMathematicalOperatorType:
        '''"∃" Unicode:\u2203'''
        ...
    
    @classmethod
    @property
    def NOT_EXISTS(cls) -> EquationMathematicalOperatorType:
        '''"∄" Unicode:\u2204'''
        ...
    
    @classmethod
    @property
    def EMPTY_SET(cls) -> EquationMathematicalOperatorType:
        '''"∅" Unicode:\u2205'''
        ...
    
    @classmethod
    @property
    def INCREMENT(cls) -> EquationMathematicalOperatorType:
        '''"∆" Unicode:\u2206'''
        ...
    
    @classmethod
    @property
    def NABLA(cls) -> EquationMathematicalOperatorType:
        '''"∇" Unicode:\u2207'''
        ...
    
    @classmethod
    @property
    def ELEMENT_OF(cls) -> EquationMathematicalOperatorType:
        '''"∈" Unicode:\u2208'''
        ...
    
    @classmethod
    @property
    def NOT_AN_ELEMENT_OF(cls) -> EquationMathematicalOperatorType:
        '''"∉" Unicode:\u2209'''
        ...
    
    @classmethod
    @property
    def SMALL_ELEMENT_OF(cls) -> EquationMathematicalOperatorType:
        '''"∊" Unicode:\u220a'''
        ...
    
    @classmethod
    @property
    def CONTAIN(cls) -> EquationMathematicalOperatorType:
        '''"∋" Unicode:\u220b'''
        ...
    
    @classmethod
    @property
    def NOT_CONTAIN(cls) -> EquationMathematicalOperatorType:
        '''"∌" Unicode:\u220c'''
        ...
    
    @classmethod
    @property
    def SMALL_CONTAIN(cls) -> EquationMathematicalOperatorType:
        '''"∍" Unicode:\u220d'''
        ...
    
    @classmethod
    @property
    def END_OF_PROOF(cls) -> EquationMathematicalOperatorType:
        '''"∎" Unicode:\u220e'''
        ...
    
    @classmethod
    @property
    def NARY_PRODUCT(cls) -> EquationMathematicalOperatorType:
        '''"∏" Unicode:\u220f'''
        ...
    
    @classmethod
    @property
    def NARY_COPRODUCT(cls) -> EquationMathematicalOperatorType:
        '''"∐" Unicode:\u2210'''
        ...
    
    @classmethod
    @property
    def NARY_SUMMATION(cls) -> EquationMathematicalOperatorType:
        '''"∑" Unicode:\u2211'''
        ...
    
    @classmethod
    @property
    def LOGICAL_AND(cls) -> EquationMathematicalOperatorType:
        '''"∧" Unicode:\u2227'''
        ...
    
    @classmethod
    @property
    def LOGICAL_OR(cls) -> EquationMathematicalOperatorType:
        '''"∨" Unicode:\u2228'''
        ...
    
    @classmethod
    @property
    def INTERSECTION(cls) -> EquationMathematicalOperatorType:
        '''"∩" Unicode:\u2229'''
        ...
    
    @classmethod
    @property
    def UNION(cls) -> EquationMathematicalOperatorType:
        '''"∪" Unicode:\u222a'''
        ...
    
    @classmethod
    @property
    def INTEGRAL(cls) -> EquationMathematicalOperatorType:
        '''"∫" Unicode:\u222b'''
        ...
    
    @classmethod
    @property
    def DOUBLE_INTEGRAL(cls) -> EquationMathematicalOperatorType:
        '''"∬" Unicode:\u222c'''
        ...
    
    @classmethod
    @property
    def TRIPLE_INTEGRAL(cls) -> EquationMathematicalOperatorType:
        '''"∭" Unicode:\u222d'''
        ...
    
    @classmethod
    @property
    def CONTOUR_INTEGRAL(cls) -> EquationMathematicalOperatorType:
        '''"∮" Unicode:\u222e'''
        ...
    
    @classmethod
    @property
    def SURFACE_INTEGRAL(cls) -> EquationMathematicalOperatorType:
        '''"∯" Unicode:\u222f'''
        ...
    
    @classmethod
    @property
    def VOLUME_INTEGRAL(cls) -> EquationMathematicalOperatorType:
        '''"∰" Unicode:\u2230'''
        ...
    
    @classmethod
    @property
    def CLOCKWISE(cls) -> EquationMathematicalOperatorType:
        '''"∱" Unicode:\u2231'''
        ...
    
    @classmethod
    @property
    def CLOCKWISE_CONTOUR_INTEGRAL(cls) -> EquationMathematicalOperatorType:
        '''"∲" Unicode:\u2232'''
        ...
    
    @classmethod
    @property
    def ANTICLOCKWISE_CONTOUR_INTEGRAL(cls) -> EquationMathematicalOperatorType:
        '''"∳" Unicode:\u2233'''
        ...
    
    @classmethod
    @property
    def NARY_LOGICAL_AND(cls) -> EquationMathematicalOperatorType:
        '''"⋀" Unicode:\u22c0'''
        ...
    
    @classmethod
    @property
    def NARY_LOGICAL_OR(cls) -> EquationMathematicalOperatorType:
        '''"⋁" Unicode:\u22c1'''
        ...
    
    @classmethod
    @property
    def NARY_INTERSECTION(cls) -> EquationMathematicalOperatorType:
        '''"⋂" Unicode:\u22c2'''
        ...
    
    @classmethod
    @property
    def NARY_UNION(cls) -> EquationMathematicalOperatorType:
        '''"⋃" Unicode:\u22c3'''
        ...
    
    ...

class EquationNodeType:
    '''Equation node type.
    Notice:
    (1)[1-99] Currently there is only one node in the scope, and its enumeration value is 1. The node it specifies is used to store mathematical text.
    (2)[100-199] Indicates that the node is a component of some special function nodes.
    (3)[200-] Indicates that the node has some special functions(Usually with 'Equation' suffix. 'EquationParagraph' is a special case.).'''
    
    @classmethod
    @property
    def UN_KNOW(cls) -> EquationNodeType:
        '''UnKnow'''
        ...
    
    @classmethod
    @property
    def TEXT(cls) -> EquationNodeType:
        '''specifies a node that stores math text'''
        ...
    
    @classmethod
    @property
    def BASE(cls) -> EquationNodeType:
        '''Specifies a component of type 'Base''''
        ...
    
    @classmethod
    @property
    def DENOMINATOR(cls) -> EquationNodeType:
        '''Specifies a component of type 'Denominator''''
        ...
    
    @classmethod
    @property
    def NUMERATOR(cls) -> EquationNodeType:
        '''Specifies a component of type 'Numerator''''
        ...
    
    @classmethod
    @property
    def FUNCTION_NAME(cls) -> EquationNodeType:
        '''Specifies a component of type 'FunctionName''''
        ...
    
    @classmethod
    @property
    def SUBSCRIPT(cls) -> EquationNodeType:
        '''Specifies a component of type 'Subscript''''
        ...
    
    @classmethod
    @property
    def SUPERSCRIPT(cls) -> EquationNodeType:
        '''Specifies a component of type 'Superscript''''
        ...
    
    @classmethod
    @property
    def DEGREE(cls) -> EquationNodeType:
        '''Specifies a component of type 'Degree''''
        ...
    
    @classmethod
    @property
    def MATRIX_ROW(cls) -> EquationNodeType:
        '''Specifies a component of type 'MatrixRow'.A single row of the matrix'''
        ...
    
    @classmethod
    @property
    def EQUATION_PARAGRAPH(cls) -> EquationNodeType:
        '''Specifies a mathematical paragraph(oMathPara).'''
        ...
    
    @classmethod
    @property
    def MATHEMATICAL_EQUATION(cls) -> EquationNodeType:
        '''Specifies an equation or mathematical expression(OMath).'''
        ...
    
    @classmethod
    @property
    def FRACTION_EQUATION(cls) -> EquationNodeType:
        '''Specifies fractional equation'''
        ...
    
    @classmethod
    @property
    def FUNCTION_EQUATION(cls) -> EquationNodeType:
        '''Specifies function equation'''
        ...
    
    @classmethod
    @property
    def DELIMITER_EQUATION(cls) -> EquationNodeType:
        '''Specifies delimiter equation'''
        ...
    
    @classmethod
    @property
    def NARY_EQUATION(cls) -> EquationNodeType:
        '''Specifies n-ary operator equation'''
        ...
    
    @classmethod
    @property
    def RADICAL_EQUATION(cls) -> EquationNodeType:
        '''Specifies the radical equation'''
        ...
    
    @classmethod
    @property
    def SUPERSCRIPT_EQUATION(cls) -> EquationNodeType:
        '''Specifies superscript equation'''
        ...
    
    @classmethod
    @property
    def SUBSCRIPT_EQUATION(cls) -> EquationNodeType:
        '''Specifies subscript equation'''
        ...
    
    @classmethod
    @property
    def SUB_SUP_EQUATION(cls) -> EquationNodeType:
        '''Specifies an equation with superscripts and subscripts to the right of the operands.'''
        ...
    
    @classmethod
    @property
    def PRE_SUB_SUP_EQUATION(cls) -> EquationNodeType:
        '''Specifies an equation with superscripts and subscripts to the left of the operands.'''
        ...
    
    @classmethod
    @property
    def ACCENT_EQUATION(cls) -> EquationNodeType:
        '''Specifies accent equation'''
        ...
    
    @classmethod
    @property
    def BAR_EQUATION(cls) -> EquationNodeType:
        '''Specifies bar equation'''
        ...
    
    @classmethod
    @property
    def BORDER_BOX_EQUATION(cls) -> EquationNodeType:
        '''Specifies border box equation'''
        ...
    
    @classmethod
    @property
    def BOX_EQUATION(cls) -> EquationNodeType:
        '''Specifies box equation'''
        ...
    
    @classmethod
    @property
    def GROUP_CHARACTER_EQUATION(cls) -> EquationNodeType:
        '''Specifies Group-Character equation'''
        ...
    
    @classmethod
    @property
    def MATRIX_EQUATION(cls) -> EquationNodeType:
        '''Specifies the Matrix equation,'''
        ...
    
    ...

class EquationVerticalJustificationType:
    '''This specifies the default vertical justification of equations in the document.'''
    
    @classmethod
    @property
    def TOP(cls) -> EquationVerticalJustificationType:
        '''top'''
        ...
    
    @classmethod
    @property
    def CENTER(cls) -> EquationVerticalJustificationType:
        '''center'''
        ...
    
    @classmethod
    @property
    def BOTTOM(cls) -> EquationVerticalJustificationType:
        '''bottom'''
        ...
    
    ...

