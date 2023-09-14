#!/usr/bin/python
# -*- coding: utf-8 -*-

from pychrysalide.format.elf import ElfFormat


class ElfMitigations():

    def __init__(self, fmt):
        """Look for mitigations in a loaded Elf format."""

        self._fmt = fmt

        self._nx = self._get_nx_status()

        self._pie = self._get_pie_status()

        self._relro = self._get_reloc_status()

        self._canary = self._get_canary_status()


    def _get_nx_status(self):
        """Find information about the stack status."""

        # Cf. https://wiki.gentoo.org/wiki/Hardened/GNU_stack_quickstart
        # ...#Causes_of_executable_stack_markings

        # -Wl,-z,execstack / -Wl,-z,noexecstack

        stack = self._fmt.find_program_by_type(ElfFormat.ElfProgramHeaderType.PT_GNU_STACK)

        status = stack is None or stack.p_flags & ElfFormat.ElfProgramHeaderFlags.PF_X

        return 'No' if status else 'Yes'


    def _get_pie_status(self):
        """Check for taking advantage of ASLR."""

        # Cf. https://stackoverflow.com/questions/2463150/what-is-the-fpie-option-for-position-independent-executables-in-gcc-and-ld/5030518#5030518

        # -pie -fPIE

        hdr = self._fmt.get_header()

        status = hdr.e_type == ElfFormat.ElfHeaderType.ET_DYN

        return 'Yes' if status else 'No'


    def _get_reloc_status(self):
        """Track protections for the GOT."""

        # Cf. https://wiki.debian.org/Hardening
        # ...#DEB_BUILD_HARDENING_RELRO_.28ld_-z_relro.29

        # -Wl,-z,relro / -Wl,-z,now

        prgm = self._fmt.find_program_by_type(ElfFormat.ElfProgramHeaderType.PT_GNU_RELRO)

        entry = self._fmt.find_dynamic_item_by_type(ElfFormat.ElfSectionHeaderFlags.DT_BIND_NOW)

        if prgm is None and entry is None:
            status = 'No'

        elif not(prgm is None) and entry is None:
            status = 'Partial'

        elif prgm is None and not(entry is None):
            status = 'Full'

        else:
            status = 'Unknown'

        return status


    def _get_canary_status(self):
        """Look for a canary as stack protection."""

        # Cf. https://outflux.net/blog/archives/2014*01/24/fstack-protector-strong/

        # -fno-stack-protector / -fstack-protector / -fstack-protector-all / -fstack-protector-strong

        sym = self._fmt.find_symbol_by_label('__stack_chk_fail@plt')

        status = sym is None

        return 'No' if status else 'Yes'


    def __str__(self):
        """Output a mitigation summary."""

        desc = fmt.content.describe(True) + ':'

        desc += '\n'

        desc += '-' * (len(desc) - 1)

        desc += '\n'

        desc += 'NX: %s' % self._nx

        desc += '\n'

        desc += 'PIE: %s' % self._pie

        desc += '\n'

        desc += 'RelRO: %s' % self._relro

        desc += '\n'

        desc += 'Canary: %s' % self._canary

        return desc


if __name__ == '__main__':

    from pychrysalide.features import *
    import sys

    cnt = FileContent(sys.argv[1])
    fmt = ElfFormat(cnt)

    binary = LoadedBinary(fmt)

    status = binary.analyze_and_wait()

    if status :
        m = ElfMitigations(binary.format)
        print(m)
