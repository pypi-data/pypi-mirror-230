#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


from chrysacase import ChrysalideTestCase
from pychrysalide.analysis import StudyProject
from pychrysalide.core import get_current_project, set_current_project


class TestCoreGlobal(ChrysalideTestCase):
    """TestCase for analysis.core.global."""

    def testProject(self):
        """Get and set the current project."""

        self.assertIsNone(get_current_project())

        prj = StudyProject()

        set_current_project(prj)

        self.assertEqual(get_current_project(), prj)
