
from __future__ import annotations

import dataclasses as dc
import typing as t
import os

from redocparse import logs, matcher

@dc.dataclass
class FileIndex:
    r""" A small :func:`~dataclasses.dataclass` that holds information about a file relative to a single string of consecutive files' contents. """

    begin: int
    name: str
    contents: str

ta_DocsFiles = dict[str, "str | list[str] | ta_DocsFiles"]
""" A recursive :class:`dict` meant to outline the folder structure of the desired files. See :func:`read_files` for info on how to create a files :class:`dict`. """

@dc.dataclass
class FileEntry(matcher.MatchEntry):
    """ Contains extra information about where a :class:`~redocparse.matcher.MatchEntry` occurred. """

    filename: str
    line: int

    def as_str(self):
        return f"""
match in: {self.filename}
line: {self.line}
link: file:{os.path.pathsep*2}{os.path.abspath(self.filename)}#{self.line}
{super().as_str()}"""

def read_files(docsfiles: ta_DocsFiles, *, _outer_root: str="") -> dict[str, str]:
    r""" Flattens the ``docsfiles`` :class:`dict` (which potentially has nested :class:`dict`\ s denoting inner folder paths), reads the specified files, and returns a :class:`dict` with each filepath mapped to that file's content.
    
        The ``docsfiles`` :class:`dict` is a map of filepaths. Each key denotes a folder name. A folder name can be mapped to a :class:`str`, a :class:`list`, or another ``docsfiles`` :class:`dict`.
        
        * When the mapped value is a string,
        
        * * if that string is "*", all of the files in the folder are read.
        
        * * If that string is anything else, it reads the string as a specific file in the folder.
        
        * When the mapped value is a :class:`list`, each of the :class:`list`'s items is a specific file within that folder.
        
        * When the mapped value is a :class:`dict`, recurse. 

        The ``_outer_root`` internal argument is meant only for recursion - it is prepended to each path when reading files. """

    file_contents: dict[str, str] = {}
    for inner_root, files in docsfiles.items():
        root = os.path.join(_outer_root, inner_root)
        if isinstance(files, str):
            if files == "*":
                for file in os.listdir(root):
                    path = os.path.join(root, file)
                    with open(path, "r") as f:
                        file_contents[path] = f.read()
            else:
                path = os.path.join(root, files)
                with open(path, "r") as f:
                    file_contents[path] = f.read()
        elif isinstance(files, list):
            for file in files:
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    file_contents[path] = f.read()
        else:
            file_contents |= read_files(files, _outer_root=root)
    return file_contents

@dc.dataclass
class Contents:
    r""" A :func:`~dataclasses.dataclass` that holds the content of a collection of files. Stores where each file starts using instances of :class:`FileIndex`. """
    
    file_contents: dc.InitVar[ta_DocsFiles]
    """ A collection of folders mapped to desired files. See :func:`read_files` for details on how to structure this :class:`dict`. """

    separator: dc.InitVar[str] = ""
    """ The character by which to separate each file's contents, if necessary. """

    all_contents: str = dc.field(init=False, default="")
    """ All contents of each file in :attr:`.file_contents`, joined by :attr:`.separator`. """

    indices: list[FileIndex] = dc.field(init=False, default_factory=list)
    """ Each item stores the position of one of the files relative to :attr:`.all_contents`. """

    def __post_init__(self, docs: ta_DocsFiles, separator: str):
        total_chars = 0
        files_contents = read_files(docs)
        for filename, contents in files_contents.items():
            self.indices.append(FileIndex(total_chars, filename, contents))
            with_sep = contents + separator
            self.all_contents += with_sep
            total_chars += len(with_sep)
    
    def get_current_file(self, current_index: int):
        """ Gets a :class:`FileIndex` in :attr:`.indices` based on the index of a character in :attr:`.all_contents`. """

        return [
            fileindex
            for fileindex in self.indices
            if fileindex.begin <= current_index
        ].pop()
    
    def transform_log(self, log: logs.Log, *, _new_log: logs.Log | None=None):
        r""" Takes a :class:`~redocparse.logs.Log` of :class:`~redocparse.matcher.MatchEntry` items and creates a new log with added information about which file coresponds to those entries.
        
            If the ``log`` has :class:`~redocparse.logs.Entry` items that aren't :class:`~redocparse.matcher.MatchEntry` instances, it adds them to the new log unchanged.
            
            ``_new_log`` is an internal argument that doesn't need to be set - since :class:`~redocparse.logs.Log`\ s are recursive, this method needs to be recursive as well. """

        _new_log = _new_log or logs.Log()
        index = 0
        for item in log.entries:
            if isinstance(item, logs.Entry):
                if isinstance(item, matcher.MatchEntry):
                    current_file = self.get_current_file(index := index + item.begin)
                    _new_log.add(FileEntry(
                        filename=current_file.name,
                        **{field.name: getattr(item, field.name) for field in dc.fields(item)}
                    ))
                else:
                    _new_log.add(item)
            else:
                self.transform_log(item, _new_log=_new_log.inner())
        return _new_log