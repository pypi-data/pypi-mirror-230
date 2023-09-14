#!/usr/bin/python
# -*- coding: utf-8 -*-

from .mitigations import ElfMitigations
from pychrysalide.core import log_message, LogMessageType
from pychrysalide.format.elf import ElfFormat
from pychrysalide.plugins import PluginModule


class CheckSec(PluginModule):
    """Check for Elf mititgations."""

    _name = 'CheckSec'
    _desc = 'Output the exploit mitigations compiled with a loaded binary'
    _version = '0.1'
    _url = 'https://www.chrysalide.re/'

    _actions = ( PluginModule.PluginAction.FORMAT_POST_ANALYSIS_ENDED, )


    def _handle_format_analysis(self, action, format, gid, status):
        """Get notified at the end of format analysis."""

        if type(format) == ElfFormat:

            m = ElfMitigations(format)

            msg = 'Elf mitigations: NX: <b>%s</b>  PIE: <b>%s</b>  RelRO: <b>%s</b>  Canary: <b>%s</b>' \
                  % (m._nx, m._pie, m._relro, m._canary)

            self.log_message(LogMessageType.INFO, msg)
