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

class DataMashup:
    '''Represents mashup data.'''
    
    @property
    def power_query_formulas(self) -> aspose.cells.querytables.PowerQueryFormulaCollection:
        ...
    
    @property
    def power_query_formula_parameters(self) -> aspose.cells.querytables.PowerQueryFormulaParameterCollection:
        ...
    
    ...

class PowerQueryFormula:
    '''Represents the definition of power query formula.'''
    
    @property
    def formula_definition(self) -> str:
        ...
    
    @property
    def name(self) -> str:
        '''Gets and sets the name of the power query formula.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and sets the name of the power query formula.'''
        ...
    
    @property
    def power_query_formula_items(self) -> aspose.cells.querytables.PowerQueryFormulaItemCollection:
        ...
    
    ...

class PowerQueryFormulaCollection:
    '''Represents all power query formulas in the mashup data.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.querytables.PowerQueryFormula]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.querytables.PowerQueryFormula], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.querytables.PowerQueryFormula, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.querytables.PowerQueryFormula, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.querytables.PowerQueryFormula) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.querytables.PowerQueryFormula, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.querytables.PowerQueryFormula, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.querytables.PowerQueryFormula) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class PowerQueryFormulaFunction(PowerQueryFormula):
    '''Represents the function of power query.'''
    
    @property
    def formula_definition(self) -> str:
        ...
    
    @property
    def name(self) -> str:
        '''Gets and sets the name of the power query formula.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets and sets the name of the power query formula.'''
        ...
    
    @property
    def power_query_formula_items(self) -> aspose.cells.querytables.PowerQueryFormulaItemCollection:
        ...
    
    @property
    def f(self) -> str:
        '''Gets and sets the definition of function.'''
        ...
    
    @f.setter
    def f(self, value : str):
        '''Gets and sets the definition of function.'''
        ...
    
    ...

class PowerQueryFormulaItem:
    '''Represents the item of the power query formula.'''
    
    @property
    def name(self) -> str:
        '''Gets the name of the item.'''
        ...
    
    @property
    def value(self) -> str:
        '''Gets the value of the item.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Gets the value of the item.'''
        ...
    
    ...

class PowerQueryFormulaItemCollection:
    '''Represents all item of the power query formula.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.querytables.PowerQueryFormulaItem]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.querytables.PowerQueryFormulaItem], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.querytables.PowerQueryFormulaItem, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.querytables.PowerQueryFormulaItem, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.querytables.PowerQueryFormulaItem) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.querytables.PowerQueryFormulaItem, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.querytables.PowerQueryFormulaItem, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.querytables.PowerQueryFormulaItem) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class PowerQueryFormulaParameter:
    '''Represents the parameter of power query formula.'''
    
    @property
    def name(self) -> str:
        '''Gets the name of parameter.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Gets the name of parameter.'''
        ...
    
    @property
    def value(self) -> str:
        '''Gets the value of parameter.'''
        ...
    
    @value.setter
    def value(self, value : str):
        '''Gets the value of parameter.'''
        ...
    
    @property
    def parameter_definition(self) -> str:
        ...
    
    ...

class PowerQueryFormulaParameterCollection:
    '''Represents the'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.querytables.PowerQueryFormulaParameter]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.querytables.PowerQueryFormulaParameter], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.querytables.PowerQueryFormulaParameter, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.querytables.PowerQueryFormulaParameter, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.querytables.PowerQueryFormulaParameter) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.querytables.PowerQueryFormulaParameter, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.querytables.PowerQueryFormulaParameter, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.querytables.PowerQueryFormulaParameter) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

