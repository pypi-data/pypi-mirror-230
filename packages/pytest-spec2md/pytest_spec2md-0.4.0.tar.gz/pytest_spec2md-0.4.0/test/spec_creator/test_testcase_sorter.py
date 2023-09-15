from collections import namedtuple

from pytest_spec2md.spec_creator import TestcaseSorter

Item = namedtuple("Item", ["nodeid", ])


class TestSplitNameByPath:

    def test_split_in_file(self):
        item = Item(nodeid="abc.py::test_abc")

        assert TestcaseSorter.split_name_of_item_by_path(item) == ['abc.py', 'test_abc']

    def test_split_in_class(self):
        item = Item(nodeid="a.py::TestClass::test_abc")

        assert TestcaseSorter.split_name_of_item_by_path(item) == ['a.py', 'TestClass::test_abc']

    def test_split_subfolder(self):
        item = Item(nodeid="x/a.py::test_123")

        assert TestcaseSorter.split_name_of_item_by_path(item) == ['x/a.py', 'test_123']


class TestSortByLayer:

    def test_in_same_file_nothing_happens(self):
        items = [Item(nodeid='a.py::test_2'), Item(nodeid='a.py::test_1')]
        tcs = TestcaseSorter(items.copy())

        tcs.sort_by_layer()

        assert tcs.items == items

    def test_in_same_directory_nothing_happens(self):
        items = [Item(nodeid='b.py::test_2'), Item(nodeid='a.py::test_1')]
        tcs = TestcaseSorter(items.copy())

        tcs.sort_by_layer()

        assert tcs.items == items

    def test_in_sub_directory_follows_test_in_main_directory(self):
        items = [Item(nodeid='test_b.py::test_2'), Item(nodeid='dir/test_a.py::test_1')]
        tcs = TestcaseSorter(items.copy())

        tcs.sort_by_layer()
        assert tcs.items == items
