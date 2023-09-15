import _pytest.nodes
import _pytest.terminal
import pytest
from pytest_spec2md.spec_creator import TestType

import pytest_spec2md.spec_creator


def pytest_addoption(parser):
    group = parser.getgroup('general')
    group.addoption(
        '--spec2md',
        action='store_true',
        dest='spec2md',
        help='Creates multiple specification document in markdown format.'
    )

    group = parser.getgroup("spec2md", "Options for spec2md plugin")
    group.addoption(
        '--spec2md-version',
        default='unknown',
        dest='spec2md_version',
        help='Version to be used to document tested version'
    )

    parser.addini(
        'test_spec_target_file',
        default='docs/test_spec.md',
        help='The target file to save the generated test specification.'
    )

    parser.addini(
        'spec_source_file',
        default='docs/spec.md',
        help='The specification file used to generate a spec with test infos.'
    )

    parser.addini(
        'spec_target_file',
        default='docs/spec_with_tests.md',
        help='The target file for spec with test infos.'
    )

    parser.addini(
        'spec_indent',
        default='  ',
        help='Indention of spec in console.'
    )


_act_config = None


def pytest_configure(config):
    global _act_config
    _act_config = config

    pytest_spec2md.spec_creator.SpecWriter.clear_writer()

    if config.option.spec2md:
        pytest_spec2md.spec_creator.TestSpecWriter.delete_existing_specification_file(config)

    config.addinivalue_line(
        "markers", "func_reference(name, docstring): mark specification reference for the test"
    )
    config.addinivalue_line(
        "markers", "spec_identifier(identifiers): identifiers used in specification document"
    )
    config.addinivalue_line(
        "markers", "test_type(types): Types for test. TestType Enum could be used."
    )

    pytest_spec2md.spec_creator.SpecWriter.get_writer(pytest_spec2md.spec_creator.SpecWithTestsWriter, config)


def pytest_itemcollected(item: _pytest.nodes.Item):
    for marker in item.own_markers:
        if marker.name != 'spec_identifier':
            continue

        writer = pytest_spec2md.spec_creator.SpecWriter.get_writer(pytest_spec2md.spec_creator.SpecWithTestsWriter,
                                                                   None)
        for arg in marker.args:
            writer.add_test(arg, item)


@pytest.hookimpl(hookwrapper=True)
def pytest_collection_modifyitems(items):
    outcome = yield
    sorter = pytest_spec2md.spec_creator.TestcaseSorter(items)
    sorter.sort_by_layer()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Adds docstring to the item usage in report"""
    outcome = yield
    pytest_spec2md.spec_creator.ItemEnhancer.enhance(outcome, item)


@pytest.hookimpl(trylast=True)
def pytest_runtest_logreport(report):
    if report.when == 'call':
        pytest_spec2md.spec_creator.SpecWriter.create_specification_documents(
            config=_act_config, report=report)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    writer = pytest_spec2md.spec_creator.SpecWriter.get_writer(pytest_spec2md.spec_creator.SpecWithTestsWriter, None)

    writer.write_final_report()
