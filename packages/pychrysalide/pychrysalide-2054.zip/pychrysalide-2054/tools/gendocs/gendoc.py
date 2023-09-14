#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys


def validate_coverage(target):

    result = False

    for mod in sys.argv[1:]:
        result = target.startswith(mod)
        if result:
            break

    return result


if __name__ == '__main__':

    if os.environ.get('PYWIKIBOT2_DIR') is None:
        print('Environment variable "PYWIKIBOT2_DIR" is not set!')
        sys.exit(1)

    if len(sys.argv) == 1:
        print('Usage: %s <module>' % sys.argv[0])
        sys.exit(1)

    from exporters.html import HtmlExporter
    from exporters.mediawiki import MWExporter
    from sources.python import PythonReader

    for mod in sys.argv[1:]:
        reader = PythonReader(None, mod, MWExporter)
        reader.build(validate_coverage)
