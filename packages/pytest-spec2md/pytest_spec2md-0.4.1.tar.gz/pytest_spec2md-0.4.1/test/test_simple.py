import os

import deepdiff
import pytest
import xml.etree.ElementTree as et


@pytest.fixture
def pytester_simple(request, pytester):
    test_data_dir = os.path.join(request.config.rootdir, 'pytester_cases', 'case_simple')
    TestUseCaseSimple.test_data_dir = test_data_dir

    pytester.syspathinsert(os.path.join(request.config.rootdir, 'pytest_spec2md'))

    with open(os.path.join(request.config.rootdir, 'pytester_cases', 'conftest.py')) as file_content:
        source = "".join(file_content.readlines())
        pytester.makeconftest(source=source)

    with open(os.path.join(test_data_dir, 'test_simple.py')) as file_content:
        source = "".join(file_content.readlines())
        pytester.makepyfile(source)

    with open(os.path.join(request.config.rootdir, 'pytester_cases', 'pytester.config')) as file_content:
        source = "".join(file_content.readlines())
        pytester.getinicfg(source)

    return pytester


class TestUseCaseSimple:
    test_data_dir = ""

    def test_runs_4_successful_tests(self, pytester_simple: pytest.Pytester):
        result = pytester_simple.runpytest()
        result.assert_outcomes(passed=4)

    def test_creates_13_lines_of_documentation(self, pytester_simple: pytest.Pytester):
        pytester_simple.runpytest()

        with open(os.path.join(pytester_simple.path, 'docs/test_spec.md')) as spec_file:
            spec = spec_file.readlines()

        assert len(spec) == 13

    def test_creates_markdown_as_provided(self, pytester_simple: pytest.Pytester):
        pytester_simple.runpytest()

        with open(os.path.join(TestUseCaseSimple.test_data_dir, 'result.md')) as expected:
            expected_result = expected.readlines()

        with open(os.path.join(pytester_simple.path, 'docs/test_spec.md')) as spec_file:
            actual_result = spec_file.readlines()

        diff = [(x, y) for (x, y) in zip(expected_result, actual_result) if (x != y) and str(x).find('XXXX') == -1]
        assert not diff

    def test_spec_created_using_junit(self, pytester_simple: pytest.Pytester):
        result = pytester_simple.runpytest("--junitxml=junit.xml")

        assert result.ret == 0
        assert os.path.exists(os.path.join(pytester_simple.path, 'docs/test_spec.md'))


def test_junitxml_creates_4_testcases(pytester_simple: pytest.Pytester):
    pytester_simple.runpytest("--junitxml=junit.xml")

    root_node = et.parse(os.path.join(pytester_simple.path, 'junit.xml')).getroot()
    test_cases = root_node.findall('.//*')
    assert sum(x.tag == 'testsuite' for x in test_cases) == 1
    assert sum(x.tag == 'testcase' for x in test_cases) == 4


def test_uses_default_output_on_console(pytester_simple: pytest.Pytester):
    default_result = pytester_simple.runpytest()
    spec_result = pytester_simple.runpytest()

    assert len(default_result.stdout.lines) == len(spec_result.stdout.lines)
    assert not deepdiff.DeepDiff(default_result.stdout.lines[1:-1], spec_result.stdout.lines[1:-1])
