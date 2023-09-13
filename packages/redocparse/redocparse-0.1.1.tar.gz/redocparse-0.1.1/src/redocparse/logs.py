
from __future__ import annotations
import abc

import dataclasses as dc
import typing as t
import os

def yaml_single_line(s: str, limit: int=400):
    return "'" + s.replace("\n", r"\n").replace("'", r",")[:limit] + "'"

class Entry(abc.ABC):
    @abc.abstractmethod
    def as_str(self) -> str: ...

@dc.dataclass
class Log:
    """ This debugging tool collects in order a :class:`list` of :class:`Entry` or :class:`Log` objects that outline what's happening in a nested scope. """

    entries: list[Entry | Log] = dc.field(default_factory=list)
    indent_str: str = "  "
    
    def inner(self):
        new = self.__class__()
        self.entries.append(new)
        return new

    def add(self, entry: Entry):
        self.entries.append(entry)
        return self

    def as_str(self, indent=0):
        string = ""
        for line in self.entries:
            if isinstance(line, Entry):
                string += "".join(f"{self.indent_str * (indent)}{line}\n" for line in "\n".split(line.as_str()))
            else:
                string += line.as_str(indent+1)
        return string

def write_logfile(logfolder: str, content: str):
    r""" Creates a new file in the folder at the specified path and writes the given contents to that file. If the specified path isn't a folder, creates a folder at that path.
    
        The created file will have a number as its filename. """

    if not os.path.isdir(logfolder):
        if os.path.exists(logfolder):
            raise Exception(f"Tried to use '{logfolder}' as a folder for storing logfiles, but it already exists and isn't a directory. ")
        os.mkdir(logfolder)
    oldlogs_folder = os.path.join(logfolder, "old")
    if not os.path.exists(oldlogs_folder):
        os.mkdir(oldlogs_folder)
    
    logfile = os.path.join(logfolder, "log.yaml")
    if os.path.exists(logfile):
        logfiles = os.listdir(oldlogs_folder)
        lognumber = int(logfiles[-1][:-5]) if logfiles else 0
        with open(os.path.join(logfolder, str(lognumber + 1) + ".yaml"), "w") as f:
            with open(logfile, "r") as lf:
                f.write(lf.read())
    
    with open(logfile, "w") as f:
        f.write(content)