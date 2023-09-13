
""" `ReDocparse <https://github.com/lapraswastaken/redocparse>` is a small library that aims to make transforming large amounts of text easier.

    It introduces a :class:`~redocparse.matcher.Matcher` class that matches a chunk of text via regex, runs the matched text through a callback function, then sends the matched text through each of its nested Matchers.

    In short, it's a more ergonomic way to use regex recursively. """