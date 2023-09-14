#!/usr/bin/python3-dbg
# -*- coding: utf-8 -*-


from chrysacase import ChrysalideTestCase
from pychrysalide import PluginModule
import gc


class TestPlugin(ChrysalideTestCase):
    """TestCase for GPluginModule."""


    def testGarbageCollecting(self):
        """Ensure the garbarge collector is working for plugin modules."""


        class MyPG_1(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( )
                }

                super(MyPG_1, self).__init__(**interface)


        pg = MyPG_1()
        self.assertIsNotNone(pg)


        class MyPG_2(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( )
                }

                super(MyPG_2, self).__init__(**interface)


        pg = MyPG_2()
        self.assertIsNotNone(pg)


        class MyPG_3(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( )
                }

                super(MyPG_3, self).__init__(**interface)


        pg = MyPG_3()
        self.assertIsNotNone(pg)


        class MyPG_4(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( )
                }

                super(MyPG_4, self).__init__(**interface)


        pg = MyPG_4()
        self.assertIsNotNone(pg)


        class MyPG_5(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( )
                }

                super(MyPG_5, self).__init__(**interface)


        pg = MyPG_5()
        self.assertIsNotNone(pg)


        gc.collect()


    def testCreation(self):
        """Validate PluginModule creation from Python."""


        class MyPG_0(PluginModule):
            pass


        # TypeError: Required argument 'name' (pos 1) not found
        with self.assertRaises(TypeError):
            pg = MyPG_0()


        class MyPG_1(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( )
                }

                super(MyPG_1, self).__init__(**interface)


        pg = MyPG_1()
        self.assertIsNotNone(pg)


        class MyPG_2(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( 'ABC', )
                }

                super(MyPG_2, self).__init__(**interface)


        # TypeError: Invalid type for plugin action.
        with self.assertRaises(TypeError):
            pg = MyPG_2()


        class MyPG_3(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( PluginModule.PGA_CONTENT_EXPLORER, )
                }

                super(MyPG_3, self).__init__(**interface)


        # TypeError: missing features for the declared actions.
        with self.assertRaises(TypeError):
            pg = MyPG_3()


        class MyPG_4(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name4',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( PluginModule.PGA_CONTENT_EXPLORER, )
                }

                super(MyPG_4, self).__init__(**interface)

            def handle_binary_content(self, action, content, wid, status):
                pass


        pg = MyPG_4()
        self.assertIsNotNone(pg)


    def testDoubleUsage(self):
        """Validate PluginModule double usage in Python."""


        class MyPG(PluginModule):

            def __init__(self):

                interface = {
                    'name' : 'some_name',
                    'desc' : 'Provide some information about the useless plugin',
                    'version' : '0.1',
                    'actions' : ( )
                }

                super(MyPG, self).__init__(**interface)


        pg1 = MyPG()
        self.assertIsNotNone(pg1)

        pg2 = MyPG()
        self.assertIsNotNone(pg2)
