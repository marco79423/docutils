#! /usr/bin/env python

"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Command-line and common processing for Docutils front-ends.
"""

__docformat__ = 'reStructuredText'

import ConfigParser as CP
import docutils
from docutils import optik


class OptionParser(optik.OptionParser):

    """
    Parser for command-line and library use.  The `cmdline_options` specification here and in other Docutils components are merged
    """

    threshold_choices = 'info 1 warning 2 error 3 severe 4 none 5'.split()
    """Possible inputs for for --report and --halt threshold values."""

    thresholds = {'info': 1, 'warning': 2, 'error': 3, 'severe': 4, 'none': 5}
    """Lookup table for --report and --halt threshold values."""

    cmdline_options = (
        'General Docutils Options',
        None,
        (('Include a "Generated by Docutils" credit with a link, at the end '
          'of the document.',
          ['--generator', '-g'], {'action': 'store_true'}),
         ('Do not include a generator credit.',
          ['--no-generator'], {'action': 'store_false', 'dest': 'generator'}),
         ('Include the date at the end of the document (UTC).',
          ['--date', '-d'], {'action': 'store_const', 'const': '%Y-%m-%d',
                             'dest': 'datestamp'}),
         ('Include the time & date at the end of the document (UTC).',
          ['--time', '-t'], {'action': 'store_const',
                             'const': '%Y-%m-%d %H:%M UTC',
                             'dest': 'datestamp'}),
         ('Do not include a datestamp of any kind.',
          ['--no-datestamp'], {'action': 'store_const', 'const': None,
                               'dest': 'datestamp'}),
         ('Include a "View document source." link.',
          ['--source-link', '-s'], {'action': 'store_true'}),
         ('Do not include a "(View document source)" link.',
          ['--no-source-link'], {'action': 'store_false',
                                 'dest': 'source_link'}),
         ('Set verbosity threshold; report system messages at or higher than '
          '<level> (by name or number: "info" or "1", warning/2, error/3, '
          'severe/4; also, "none" or "5").  Default is 2 (warning).',
          ['--report', '-r'], {'choices': threshold_choices, 'default': 2,
                               'dest': 'report_level', 'metavar': '<level>'}),
         ('Report all system messages, info-level and higher.  (Same as '
          '"--report=info".)',
          ['--verbose', '-v'], {'action': 'store_const', 'const': 'info',
                                'dest': 'report_level'}),
         ('Set the threshold (<level>) at or above which system messages are '
          'converted to exceptions, halting execution immediately.  Levels '
          'as in --report.  Default is 4 (severe).',
          ['--halt'], {'choices': threshold_choices, 'dest': 'halt_level',
                       'default': 4, 'metavar': '<level>'}),
         ('Same as "--halt=info": halt processing at the slightest problem.',
          ['--strict'], {'action': 'store_const', 'const': 'info',
                         'dest': 'halt_level'}),
         ('Report debug-level system messages.',
          ['--debug'], {'action': 'store_true'}),
         ('Do not report debug-level system messages.',
          ['--no-debug'], {'action': 'store_false', 'dest': 'debug'}),
         ('Send the output of system messages (warnings) to <file>.',
          ['--warnings'], {'dest': 'warning_stream', 'metavar': '<file>'}),
         ('Specify the encoding of input text.  Default is locale-dependent.',
          ['--input-encoding', '-i'], {'metavar': '<name>'}),
         ('Specify the encoding for output.  Default is UTF-8.',
          ['--output-encoding', '-o'],
          {'metavar': '<name>', 'default': 'utf-8'}),
         ('Specify the language of input text (ISO 639 2-letter identifier).'
          '  Default is "en" (English).',
          ['--language', '-l'], {'dest': 'language_code', 'default': 'en',
                                 'metavar': '<name>'}),
         ("Show this program's version number and exit.",
          ['--version'], {'action': 'version'}),
         ('Show this help message and exit.',
          ['--help', '-h'], {'action': 'help'}),
         # Hidden options, for development use only:
         (optik.SUPPRESS_HELP,
          ['--dump-internal-document-attributes'],
          {'action': 'store_true'}),))
    """Command-line option specifications, common to all Docutils front-ends.
    One or more sets of option group title, description, and a
    list/tuple of tuples: ``('help text', [list of option strings],
    {keyword arguments})``.  Group title and/or description may be
    `None`; no group title implies no group, just a list of single
    options.  Option specs from Docutils components are also used (see
    `populate_from_components()`)."""

    version_template = '%%prog (Docutils %s)' % docutils.__version__

    def __init__(self, components=(), *args, **kwargs):
        """
        `components` is a list of Docutils components each containing a
        ``.cmdline_options`` attribute.  `defaults` is a mapping of option
        default overrides.
        """
        optik.OptionParser.__init__(self, help=None, format=optik.Titled(),
                                    *args, **kwargs)
        if not self.version:
            self.version = self.version_template
        self.populate_from_components(tuple(components) + (self,))

    def populate_from_components(self, components):
        for component in components:
            if component is not None:
                i = 0
                cmdline_options = component.cmdline_options
                while i < len(cmdline_options):
                    title, description, option_spec = cmdline_options[i:i+3]
                    if title:
                        group = optik.OptionGroup(self, title, description)
                        self.add_option_group(group)
                    else:
                        group = self        # single options
                    for (help_text, option_strings, kwargs) in option_spec:
                        group.add_option(help=help_text, *option_strings,
                                         **kwargs)
                    i += 3

    def check_values(self, values, args):
        values.report_level = self.check_threshold(values.report_level)
        values.halt_level = self.check_threshold(values.halt_level)
        source, destination = self.check_args(args)
        return values, source, destination

    def check_threshold(self, level):
        try:
            return int(level)
        except ValueError:
            try:
                return self.thresholds[level.lower()]
            except (KeyError, AttributeError):
                self.error('Unknown threshold: %r.' % level)

    def check_args(self, args):
        source = destination = None
        if args:
            source = args.pop(0)
        if args:
            destination = args.pop(0)
        if args:
            self.error('Maximum 2 arguments allowed.')
        return source, destination


class ConfigParser(CP.ConfigParser):

    def optionxform(self, optionstr):
        """
        Transform '-' to '_' so the cmdline form of option names can be used.
        """
        return optionstr.lower().replace('-', '_')
