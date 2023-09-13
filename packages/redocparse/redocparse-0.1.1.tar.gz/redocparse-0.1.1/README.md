
# ReDocparse

ReDocparse is a small library that aims to make transforming large amounts of text easier.

It introduces a `redocparse.matcher.Matcher` class that matches a chunk of text via regex,
 runs the matched text through an optional callback function,
 then sends the matched text through each of its nested Matchers.

In short, it's a more ergonomic way to use regex recursively.

## Discord

Included in this repository is src/discord, which is an application of ReDocparse aimed at creating Python dataclasses from the Discord API Documentation (specifically for use with [DubiousDiscord](https://github.com/lapraswastaken/dubiousdiscord)).

discord.parse_discord requires [Inflect](https://github.com/jaraco/inflect) to run.