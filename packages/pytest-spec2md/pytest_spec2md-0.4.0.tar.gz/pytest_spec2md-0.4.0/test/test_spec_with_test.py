import os

import pytest


@pytest.fixture
def pytester_spec_with_test(request, pytester):
    test_data_dir = os.path.join(request.config.rootdir, 'pytester_cases', 'case_with_spec')
    TestUseCaseWithSpec.test_data_dir = test_data_dir

    pytester.syspathinsert(os.path.join(request.config.rootdir, 'pytest_spec2md'))

    pytester.copy_example(os.path.join(request.config.rootdir, 'pytester_cases', 'dummy_spec.md'))

    with open(os.path.join(request.config.rootdir, 'pytester_cases', 'conftest.py')) as file_content:
        source = "".join(file_content.readlines())
        pytester.makeconftest(source=source)

    with open(os.path.join(test_data_dir, 'test_with_spec.py')) as file_content:
        source = "".join(file_content.readlines())
        pytester.makepyfile(source)

    with open(os.path.join(request.config.rootdir, 'pytester_cases', 'pytester_with_spec_file.config')) as file_content:
        source = "".join(file_content.readlines())
        pytester.getinicfg(source)

    return pytester


class TestUseCaseWithSpec:
    test_data_dir = ""

    def test_runs_5_successful_tests(self, pytester_spec_with_test: pytest.Pytester):
        result = pytester_spec_with_test.runpytest()
        result.assert_outcomes(passed=5, failed=1)

    def test_creates_doc_file(self, pytester_spec_with_test: pytest.Pytester):
        result = pytester_spec_with_test.runpytest()
        assert os.path.exists(os.path.join(pytester_spec_with_test.path, 'docs/spec_with_tests.md'))

    def test_contains_test_data(self, pytester_spec_with_test: pytest.Pytester):
        pytester_spec_with_test.runpytest()

        found_comment = False
        found_replacement = False
        with open(os.path.join(pytester_spec_with_test.path, 'docs/spec_with_tests.md')) as result:
            for line in result:
                if line.startswith('<!-- TestRef:'):
                    found_comment = True

                if line.startswith('> **Proved by Tests for Reference *'):
                    found_replacement = True

        assert found_comment is True

        assert found_replacement is True
