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

class HighlightChangesOptions:
    '''Represents options of highlighting revsions or changes of shared Excel files.'''
    
    ...

class Revision:
    '''Represents the revision.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Represents the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    ...

class RevisionAutoFormat(Revision):
    '''represents a revision record of information about a formatting change.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Gets the type of the revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def cell_area(self) -> aspose.cells.CellArea:
        ...
    
    ...

class RevisionCellChange(Revision):
    '''Represents the revision that changing cells.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Represents the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def cell_name(self) -> str:
        ...
    
    @property
    def row(self) -> int:
        '''Gets the row index of the cell.'''
        ...
    
    @property
    def column(self) -> int:
        '''Gets the column index of the cell.'''
        ...
    
    @property
    def is_new_formatted(self) -> bool:
        ...
    
    @property
    def is_old_formatted(self) -> bool:
        ...
    
    @property
    def old_formula(self) -> str:
        ...
    
    @property
    def old_value(self) -> any:
        ...
    
    @property
    def new_value(self) -> any:
        ...
    
    @property
    def new_formula(self) -> str:
        ...
    
    @property
    def new_style(self) -> aspose.cells.Style:
        ...
    
    @property
    def old_style(self) -> aspose.cells.Style:
        ...
    
    ...

class RevisionCellComment(Revision):
    '''Represents a revision record of a cell comment change.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Gets the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def row(self) -> int:
        '''Gets the row index of the which contains a comment.'''
        ...
    
    @property
    def column(self) -> int:
        '''Gets the column index of the which contains a comment.'''
        ...
    
    @property
    def cell_name(self) -> str:
        ...
    
    @cell_name.setter
    def cell_name(self, value : str):
        ...
    
    @property
    def action_type(self) -> aspose.cells.revisions.RevisionActionType:
        ...
    
    @property
    def is_old_comment(self) -> bool:
        ...
    
    @property
    def old_length(self) -> int:
        ...
    
    @property
    def new_length(self) -> int:
        ...
    
    ...

class RevisionCellMove(Revision):
    '''Represents a revision record on a cell(s) that moved.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Represents the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def source_area(self) -> aspose.cells.CellArea:
        ...
    
    @property
    def destination_area(self) -> aspose.cells.CellArea:
        ...
    
    @property
    def source_worksheet(self) -> aspose.cells.Worksheet:
        ...
    
    ...

class RevisionCollection:
    '''Represents all revision logs.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.revisions.Revision]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.revisions.Revision], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.revisions.Revision, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.revisions.Revision, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.revisions.Revision) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.revisions.Revision, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.revisions.Revision, index : int, count : int) -> int:
        ...
    
    def binary_search(self, item : aspose.cells.revisions.Revision) -> int:
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class RevisionCustomView(Revision):
    '''Represents a revision record of adding or removing a custom view to the workbook'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Gets the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def action_type(self) -> aspose.cells.revisions.RevisionActionType:
        ...
    
    @property
    def guid(self) -> Guid:
        '''Gets the globally unique identifier of the custom view.'''
        ...
    
    ...

class RevisionDefinedName(Revision):
    '''Represents a revision record of a defined name change.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Represents the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text of the defined name.'''
        ...
    
    @property
    def old_formula(self) -> str:
        ...
    
    @property
    def new_formula(self) -> str:
        ...
    
    ...

class RevisionFormat(Revision):
    '''Represents a revision record of information about a formatting change.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Gets the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def areas(self) -> List[aspose.cells.CellArea]:
        '''The range to which this formatting was applied.'''
        ...
    
    @property
    def style(self) -> aspose.cells.Style:
        '''Gets the applied style.'''
        ...
    
    ...

class RevisionHeader:
    '''Represents a list of specific changes that have taken place for this workbook.'''
    
    @property
    def saved_time(self) -> DateTime:
        ...
    
    @saved_time.setter
    def saved_time(self, value : DateTime):
        ...
    
    @property
    def user_name(self) -> str:
        ...
    
    @user_name.setter
    def user_name(self, value : str):
        ...
    
    ...

class RevisionInsertDelete(Revision):
    '''Represents a revision record of a row/column insert/delete action.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Represents the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def cell_area(self) -> aspose.cells.CellArea:
        ...
    
    @property
    def action_type(self) -> aspose.cells.revisions.RevisionActionType:
        ...
    
    @property
    def revisions(self) -> aspose.cells.revisions.RevisionCollection:
        '''Gets revision list by this operation.'''
        ...
    
    ...

class RevisionInsertSheet(Revision):
    '''Represents a revision record of a sheet that was inserted.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Gets the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def action_type(self) -> aspose.cells.revisions.RevisionActionType:
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of the worksheet.'''
        ...
    
    @property
    def sheet_position(self) -> int:
        ...
    
    ...

class RevisionLog:
    '''Represents the revision log.'''
    
    @property
    def metadata_table(self) -> aspose.cells.revisions.RevisionHeader:
        ...
    
    @property
    def revisions(self) -> aspose.cells.revisions.RevisionCollection:
        '''Gets all revisions in this log.'''
        ...
    
    ...

class RevisionLogCollection:
    '''Represents all revision logs.'''
    
    @overload
    def copy_to(self, array : List[aspose.cells.revisions.RevisionLog]):
        ...
    
    @overload
    def copy_to(self, index : int, array : List[aspose.cells.revisions.RevisionLog], array_index : int, count : int):
        ...
    
    @overload
    def index_of(self, item : aspose.cells.revisions.RevisionLog, index : int) -> int:
        ...
    
    @overload
    def index_of(self, item : aspose.cells.revisions.RevisionLog, index : int, count : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.revisions.RevisionLog) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.revisions.RevisionLog, index : int) -> int:
        ...
    
    @overload
    def last_index_of(self, item : aspose.cells.revisions.RevisionLog, index : int, count : int) -> int:
        ...
    
    def highlight_changes(self, options : aspose.cells.revisions.HighlightChangesOptions):
        '''Highlights changes of shared workbook.
        
        :param options: Set the options for filtering which changes should be tracked.'''
        ...
    
    def binary_search(self, item : aspose.cells.revisions.RevisionLog) -> int:
        ...
    
    @property
    def days_preserving_history(self) -> int:
        ...
    
    @days_preserving_history.setter
    def days_preserving_history(self, value : int):
        ...
    
    @property
    def capacity(self) -> int:
        ...
    
    @capacity.setter
    def capacity(self, value : int):
        ...
    
    ...

class RevisionMergeConflict(Revision):
    '''Represents a revision record which indicates that there was a merge conflict.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Gets the type of revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    ...

class RevisionQueryTable(Revision):
    '''Represents a revision of a query table field change.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Represents the type of the revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def cell_area(self) -> aspose.cells.CellArea:
        ...
    
    @property
    def field_id(self) -> int:
        ...
    
    ...

class RevisionRenameSheet(Revision):
    '''Represents a revision of renaming sheet.'''
    
    @property
    def type(self) -> aspose.cells.revisions.RevisionType:
        '''Represents the type of the revision.'''
        ...
    
    @property
    def worksheet(self) -> aspose.cells.Worksheet:
        '''Gets the worksheet.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the number of this revision.'''
        ...
    
    @property
    def old_name(self) -> str:
        ...
    
    @property
    def new_name(self) -> str:
        ...
    
    ...

class RevisionActionType:
    '''Represents the type of revision action.'''
    
    @classmethod
    @property
    def ADD(cls) -> RevisionActionType:
        '''Add revision.'''
        ...
    
    @classmethod
    @property
    def DELETE(cls) -> RevisionActionType:
        '''Delete revision.'''
        ...
    
    @classmethod
    @property
    def DELETE_COLUMN(cls) -> RevisionActionType:
        '''Column delete revision.'''
        ...
    
    @classmethod
    @property
    def DELETE_ROW(cls) -> RevisionActionType:
        '''Row delete revision.'''
        ...
    
    @classmethod
    @property
    def INSERT_COLUMN(cls) -> RevisionActionType:
        '''Column insert revision.'''
        ...
    
    @classmethod
    @property
    def INSERT_ROW(cls) -> RevisionActionType:
        '''Row insert revision.'''
        ...
    
    ...

class RevisionType:
    '''Represents the revision type.'''
    
    @classmethod
    @property
    def CUSTOM_VIEW(cls) -> RevisionType:
        '''Custom view.'''
        ...
    
    @classmethod
    @property
    def DEFINED_NAME(cls) -> RevisionType:
        '''Defined name.'''
        ...
    
    @classmethod
    @property
    def CHANGE_CELLS(cls) -> RevisionType:
        '''Cells change.'''
        ...
    
    @classmethod
    @property
    def AUTO_FORMAT(cls) -> RevisionType:
        '''Auto format.'''
        ...
    
    @classmethod
    @property
    def MERGE_CONFLICT(cls) -> RevisionType:
        '''Merge conflict.'''
        ...
    
    @classmethod
    @property
    def COMMENT(cls) -> RevisionType:
        '''Comment.'''
        ...
    
    @classmethod
    @property
    def FORMAT(cls) -> RevisionType:
        '''Format.'''
        ...
    
    @classmethod
    @property
    def INSERT_SHEET(cls) -> RevisionType:
        '''Insert worksheet.'''
        ...
    
    @classmethod
    @property
    def MOVE_CELLS(cls) -> RevisionType:
        '''Move cells.'''
        ...
    
    @classmethod
    @property
    def UNDO(cls) -> RevisionType:
        '''Undo.'''
        ...
    
    @classmethod
    @property
    def QUERY_TABLE(cls) -> RevisionType:
        '''Query table.'''
        ...
    
    @classmethod
    @property
    def INSERT_DELETE(cls) -> RevisionType:
        '''Inserting or deleting.'''
        ...
    
    @classmethod
    @property
    def RENAME_SHEET(cls) -> RevisionType:
        '''Rename worksheet.'''
        ...
    
    @classmethod
    @property
    def UNKNOWN(cls) -> RevisionType:
        '''Unknown.'''
        ...
    
    ...

