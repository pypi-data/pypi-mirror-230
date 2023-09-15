import pytest
import os


@pytest.fixture
def pytester_multiple(request, pytester):
    TestUseCaseMultiple.test_data_dir = os.path.join(request.config.rootdir, 'pytester_cases', 'case_multifile')

    pytester.syspathinsert(os.path.join(request.config.rootdir, 'pytest_spec2md'))

    with open(os.path.join(request.config.rootdir, 'pytester_cases', 'conftest.py')) as file_content:
        source = "".join(file_content.readlines())
        pytester.makeconftest(source=source)

    with open(os.path.join(request.config.rootdir, 'pytester_cases', 'pytester.config')) as file_content:
        source = "".join(file_content.readlines())
        pytester.getinicfg(source)

    pytester.copy_example(TestUseCaseMultiple.test_data_dir)

    return pytester


class TestUseCaseMultiple:
    test_data_dir = ""

    def test_run_10_tests(self, pytester_multiple):
        result = pytester_multiple.runpytest()

        result.assert_outcomes(passed=10)

    def test_results_as_in_markddown(self, pytester_multiple):
        pytester_multiple.runpytest()

        with open(os.path.join(TestUseCaseMultiple.test_data_dir, 'result.md')) as expected:
            expected_result = expected.readlines()

        with open(os.path.join(pytester_multiple.path, 'docs/test_spec.md')) as spec_file:
            actual_result = spec_file.readlines()

        diff = [(x, y) for (x, y) in zip(expected_result, actual_result) if (x != y) and str(x).find('XXXX') == -1]
        assert not diff
