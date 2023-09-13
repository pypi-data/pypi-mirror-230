
from __future__ import annotations

import dataclasses as dc
import os
import re
import typing as t

from redocparse import logs

t_Logging = t.TypeVar("t_Logging", logs.Log, None)
""" This type makes sure that all :meth:`Matcher.process` methods return a :class:`~redocparse.logs.Log` if one was given or ``None`` if not. """

@dc.dataclass
class MatchEntry(logs.Entry):
    """ Stores information about a :class:`re.Match` and how it was handled by a :class:`Matcher`. """

    matcher: str
    begin: int
    pat: str
    full: str
    processed: str | None = dc.field(kw_only=True, default=None)

    def as_str(self):
        return f"""
matcher: {self.matcher}
re:
  r"{self.pat}"
full match:
  {logs.yaml_single_line(self.full)}
processed:
  {self.processed and logs.yaml_single_line(self.processed) or "Not processed"}
"""

@dc.dataclass
class Matcher:
    r""" Allows for recursive pattern matching.
    
        Its main function is the :meth:`process` method, which uses its nested :attr:`group_matchers` and :attr:`inner_matchers` to process parts of matched text.
    
        Instances of this class can be used as decorators around functions - this will set the decorated function as that instance's :attr:`on_match` callback. """


    match_pattern_str: dc.InitVar[str]
    r""" The string pattern that will be used to match text for this :class:`Matcher` to :meth:`process`. Upon instantiation, the pattern is compiled using :func:`re.compile` and set to :attr:`match_pattern`.
    
        The default pattern matches all characters. """
    
    use_name: dc.InitVar[str | None] = None
    r""" An optional name for this :class:`Matcher`. This will be displayed when logging whenever :attr:`match_pattern` matches. 
    
        This value goes directly into :attr:`name`. If not specified, :attr:`name` will be the ``.__name__`` of the :attr:`on_match` function. """
    
    name: str = dc.field(init=False)
    r""" The name for this :class:`Matcher`. """

    on_match: t.Callable[..., str] = dc.field(init=False)
    r""" Returns a processed string.
        
        The positional arguments to this callback function must match the number of unnamed groups in the instance's :attr:`match_pattern`, and the keyword arguments must match the named groups in that pattern. """

    inner_matchers: list[Matcher] = dc.field(init=False, default_factory=list)
    r""" Each item :meth:`process`\ es the entirety of the :attr:`match_pattern`'s match.
    
        This list should be populated using the :meth:`matcher` decorator method. """
    
    group_matchers: dict[str, MatcherList] = dc.field(init=False, default_factory=dict)
    r""" Each :class:`MatcherList` takes a single named group in the :attr:`match_pattern`, :meth:`process`\ es it, and returns the processed text to be given to the :attr:`on_match` callback as a keyword argument.
    
        This dict should be populated using the :meth:`group` decorator method. """

    match_pattern: re.Pattern[str] = dc.field(init=False)
    r""" The compiled version of :attr:`match_pattern_str`. """

    def __post_init__(self, take_pat: str, use_name: str | None):
        self.match_pattern = re.compile(take_pat)
        self.name = use_name or "no name"
    
    def __call__(self, callback: t.Callable[..., str]):
        self.on_match = callback
        if self.name == "no name":
            self.name = callback.__name__
        return self

    def group(self, groupname: str, use_name: str | None=None):
        r""" Returns a :class:`MatcherList` that has been added to the instance's :attr:`group_matchers` under the given ``groupname``.
        
            A :class:`MatcherList` should exist for each named group in the :attr:`match_pattern`. Unnamed groups will be passed to the :attr:`on_match` callback, in order and unchanged . """

        self.group_matchers[groupname] = MatcherList(use_name and use_name or groupname)
        return self.group_matchers[groupname]
    
    def matcher(self, match_pattern_str: str, use_name: str | None=None):
        r""" Returns a new :class:`Matcher` that has been added to the instance's list of :attr:`inner_matchers`. """

        self.inner_matchers.append(Matcher(match_pattern_str, use_name))
        return self.inner_matchers[-1]
    
    def add(self, matchers: list[Matcher]):
        r""" Adds a collection of :class:`Matcher`\ s to :attr:`.inner_matchers`."""

        self.inner_matchers += matchers

    def process(self, text: str, *, log: t_Logging=None) -> str:
        r""" Returns text that has been processed by the :attr:`on_match` callback and each matching one within.
        
            The input string is matched against the :attr:`match_pattern` using :meth:`~re.Pattern.finditer`, and each resulting :class:`re.Match`'s :meth:`~re.Match.groups` is :meth:`process`\ ed by one of the :attr:`group_matchers` to correct the :meth:`~re.Match.groups` for the :attr:`on_match` callback.
            
            The processed text is collected, then appended to by calling all of the :attr:`inner_matchers`' :meth:`process` methods on the entirety of the :class:`re.Match`'s match :meth:`~re.Match.group`.
            
            If specified, ``log`` is a :class:`~redocparse.logs.Log` instance into which :class:`MatchEntry` items will be inserted for each :class:`re.Match`. """

        processed = ""
        matches = list(self.match_pattern.finditer(text))

        for re_match in matches:
            entry = None
            if log:
                entry = MatchEntry(
                    self.name,
                    re_match.start(),
                    re_match.re.pattern,
                    re_match.group()
                )
                log.add(entry) # type: ignore Why can't Pylance know that ``log`` is not ``None`` here?
            inner_processed = self.process_match(re_match, log and log.inner()) # type: ignore
            if entry:
                entry.processed = inner_processed
            processed += inner_processed
        
        return processed
    
    def process_match(self, re_match: re.Match[str], log: t_Logging):
        """ Internal method for processing a single :class:`re.Match`.
        
            Arranges the arguments that go into :attr:`.on_match`, calls :attr:`.on_match` with those arguments, then calls the :meth:`.process` method of each item in :attr:`.inner_matchers`. """

        named_groups = re_match.groupdict()
        unnamed_groups = [
            group
            for group in re_match.groups()
            if not group in named_groups.values()
        ]
        kwarg_groups = {
            groupname: self.group_matchers[groupname].process(
                group,
                log = log
            )
            for groupname, group in named_groups.items()
        }

        processed = self.on_match(*unnamed_groups, **kwarg_groups)

        for inner_matcher in self.inner_matchers:
            got = inner_matcher.process(
                re_match.group(),
                log=log
            )
            processed += got

        return processed

def substitution_matchers(substitutions: dict[str, str | t.Callable[..., str]]):
    r""" Returns a collection of simple substitution :class:`Matcher`\ s.
    
        Each pair in ``substitutions`` should be:
        * A regex pattern string, mapped to 
        * * Either a replacement value or
        * * A lambda :attr:`Matcher.on_match` callback.
        
        Replacement strings will have any instances of an escaped number (e.g. ``r"\1"``) set to the value of the matched group at that index, similar to :func:`re.sub`. See :func:`re.sub`'s documentation for a further explanation. """
    
    matchers: list[Matcher] = []
    for regex, replacer in substitutions.items():
        substitutor: t.Callable[..., str] = substitution_cb(replacer) if isinstance(replacer, str) else replacer
        matchers.append(Matcher(regex, use_name=f'<r"{regex}"->r"{replacer}">')(substitutor))
    return matchers

def substitution_cb(replacer: str):
    def sub(*groups: str):
        return re.sub(r"\\(\d+)", lambda m: groups[int(m.group(1))-1], replacer)
    return sub

@dc.dataclass
class MatcherList:
    name: str
    """ A name used for debugging. Usually specified already by :meth:`Matcher.group` as the ``groupname`` for the group or the ``use_name`` argument if it exists. """

    matchers: list[Matcher] = dc.field(default_factory=list)
    """ The :class:`list` of matchers to be called in succession using :meth:`.process()`. """

    def matcher(self, match_pattern_str: str, use_name: str | None=None):
        """ Creates a new :class:`Matcher`, adds it to :attr:`.matchers`, and returns it. """

        self.matchers.append(Matcher(match_pattern_str, use_name))
        return self.matchers[-1]
    
    def process(self, text: str, *, log: t_Logging=None) -> str:
        """ Calls the :meth:`~Matcher.process` method of all items in :attr:`.matchers`. """

        processed = ""
        for matcher in self.matchers:
            processed += matcher.process(
                text,
                log=log
            )
        return processed
    
    def add(self, matchers: list[Matcher]):
        r""" Adds a :class:`list` of :class:`Matcher`\ s to :attr:`.matchers`. """

        self.matchers += matchers
        return self
