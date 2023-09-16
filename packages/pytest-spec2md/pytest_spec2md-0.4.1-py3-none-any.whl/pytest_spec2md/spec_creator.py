import datetime
import importlib
import inspect
import os
import sys
import typing
import warnings

import _pytest.nodes
import _pytest.reports
import pytest

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum


class TestType(StrEnum):
    UNIT = "Unit Test"
    INTEGRATION = "Integration Test"
    SYSTEM = "System Test"
    ACCEPTANCE = "Acceptance Test"

    USABILITY = "Usability Test"
    PERFORMANCE = "Performance Test"
    SECURITY = "Security Test"


class TestcaseSorter:

    def __init__(self, items: typing.List[pytest.Item]):
        self._items = items

    @staticmethod
    def split_name_of_item_by_path(item: pytest.Item):
        return item.nodeid.split('::', maxsplit=1)

    @staticmethod
    def rename_for_sorting(entry: str, splitter: str = '/'):
        depth = entry.count(splitter)
        if depth == 0:
            return f'{0}_'
        split_entry = entry.split(splitter)
        return '1_' + "_1_".join(split_entry[:-1]) + f'{splitter}{0}_'

    def sort_by_layer(self):
        self._items.sort(
            key=lambda x:
            self.rename_for_sorting(self.split_name_of_item_by_path(x)[0]) +
            self.rename_for_sorting(self.split_name_of_item_by_path(x)[1], '::')
        )

    @property
    def items(self):
        return self._items


class SpecWriter:
    _act_writers: dict[type, 'SpecWriter'] = {}

    def __init__(self, config):
        self._config = config

    def write_node_to_file(self, report: _pytest.reports.TestReport):
        raise NotImplemented

    @classmethod
    def clear_writer(cls):
        cls._act_writers.clear()

    @classmethod
    def get_writer(cls, writer_type: type, config):
        if config and config.option.spec2md:
            if writer_type not in cls._act_writers:
                cls._act_writers[writer_type] = writer_type(config)

        return cls._act_writers.get(writer_type, None)

    @classmethod
    def delete_existing_specification_file(cls, config):
        filenames = config.getini('test_spec_target_file'), config.getini('spec_target_file')
        for filename in filenames:
            if os.path.exists(filename):
                os.remove(filename)

        cls._act_writer = None

    @classmethod
    def create_specification_documents(cls, config, report: _pytest.reports.TestReport):
        if not config.option.spec2md:
            return

        cls.get_writer(TestSpecWriter, config)
        cls.get_writer(SpecWithTestsWriter, config)

        for writer in cls._act_writers.values():
            writer.write_node_to_file(report)

    @staticmethod
    def split_scope(test_node):
        data = [i for i in test_node.split('::') if i != '()']
        if data[-1].endswith("]"):
            data[-1] = data[-1].split("[")[0]
        return data

    @staticmethod
    def format_test_name(name: str):
        if name is not str:
            name = str(name)
        if name.endswith("["):
            name = name[:name.find("[")]
        return name.replace('test_', '', 1).replace('_', ' ')

    @staticmethod
    def format_class_name(name: str):
        if name is not str:
            name = str(name.__name__)
        name = name.replace('Test', '', 1)
        return ''.join(' ' + x if x.isupper() else x for x in name)

    @staticmethod
    def format_doc_string(doc_string: str):
        if not doc_string:
            return []
        return [x.strip() for x in doc_string.split("\n") if x.strip()]


class TestSpecWriter(SpecWriter):

    def __init__(self, config):
        super().__init__(config)
        self._last_parents: list = []
        self._last_node_content: _pytest.reports.TestReport = None
        self._filename = config.getini('test_spec_target_file')
        self._create_spec_file_if_not_exists()

    @property
    def filename(self):
        return self._filename

    def _create_spec_file_if_not_exists(self):
        if os.path.exists(self.filename):
            return

        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        with open(self.filename, 'w') as file:
            file.writelines([
                '# Specification\n',
                'Automatically generated using pytest_spec2md  \n'
                f'Generated: {datetime.datetime.now()}  \n'
                f'\n',
            ])

    def write_node_to_file(self, node_content: _pytest.reports.TestReport):
        self._create_spec_file_if_not_exists()

        parents = getattr(node_content, "node_parents", [])

        last_module = self.split_scope(self._last_node_content.nodeid)[0] if self._last_node_content else ""
        act_module = self.split_scope(node_content.nodeid)[0]

        last_tc_name = self.split_scope(self._last_node_content.nodeid)[-1] if self._last_node_content else ""
        act_tc_name = self.split_scope(node_content.nodeid)[-1]

        longnewline = "  \n  "
        shortnewline = "\n"
        print_testcase = False

        with open(self.filename, 'a') as file:
            if not last_module or last_module != act_module:  # changed test file
                self._write_module_info_to_file(act_module, file)

            if len(parents) == 0:
                if last_module != act_module:
                    file.write(
                        f'\n'
                        f'### General\n'
                        f'\n'
                    )
                    print_testcase = True
            else:
                show_recursive = False
                line_start = '###'
                last_parents = self._last_parents.copy()
                last_parents.extend(["" for _ in range(len(parents) - len(last_parents))])
                for act, last in zip(parents, last_parents):
                    if show_recursive or act != last:
                        show_recursive = True
                        doc_lines = self.format_doc_string(getattr(act, "__doc__"))
                        file.write(
                            f'\n'
                            f'{line_start}{self.format_class_name(act)}\n' +
                            (f'  {shortnewline.join(doc_lines)}  \n' if doc_lines else '')
                        )
                        self._write_references(node_content, act, file)
                        file.write(f'\n')

                        print_testcase = True
                    line_start += '#'

            if print_testcase or act_tc_name != last_tc_name:
                tc = getattr(node_content, "node_obj", None)
                doc_lines = self.format_doc_string(getattr(tc, "__doc__"))

                file.write(
                    f' - **{self.format_test_name(act_tc_name)}**  \n' +
                    (f'  {longnewline.join(doc_lines)}\n' if doc_lines else '')
                )
                self._write_references(node_content, tc, file)

        self._last_parents = parents
        self._last_node_content = node_content

    def _write_module_info_to_file(self, act_module, file):
        module_name = act_module.replace('/', '.')[:-3]
        mod = importlib.import_module(module_name)
        doc_lines = self.format_doc_string(mod.__doc__)
        shortnewline = "\n"

        file.write(
            f'## Spec from {act_module}\n' +
            (f'{shortnewline.join(doc_lines)}  \n' if doc_lines else '')
        )

    def _write_references(self, node_content, act_obj, file):
        longnewline = "  \n  "
        references = getattr(node_content, "reference_docs", [])
        for target, reference in references:
            if target.obj == act_obj:
                file.write(
                    (f'  Tests: *{reference[0]}*  \n' if reference[0] else '') +
                    (f'  {longnewline.join(self.format_doc_string(reference[1]))}\n' if len(reference) > 1 else '')
                )


class SpecIdentifierWarning(UserWarning):
    pass


class SpecWithTestsWriter(SpecWriter):

    def __init__(self, config):
        super().__init__(config)

        self._grouped_tests: dict[str, list[_pytest.nodes.Node]] = {}
        self._source_file = config.getini('spec_source_file')

        self._target_file = config.getini('spec_target_file')

        self._version = config.option.spec2md_version
        self._test_run_id = f'TestRun {datetime.datetime.now():%Y-%m-%d %H:%M}'

        self._results: dict[str, _pytest.reports.TestReport] = {}

    def write_node_to_file(self, report: _pytest.reports.TestReport):
        self._results[report.nodeid] = report

    def add_test(self, key: str, test: _pytest.nodes.Node):
        if key not in self._grouped_tests:
            self._grouped_tests[key] = []

        self._grouped_tests[key].append(test)

    def write_final_report(self):
        if not self._source_file or not self._target_file:
            return

        content = self._get_content()

        with open(self._target_file, 'w') as target:
            for line in content:
                target.write(line)

    def _get_content(self):
        if not self._source_file or not os.path.exists(self._source_file):
            return

        used_identifier = []

        with open(self._source_file) as source:
            for line in source.readlines():
                yield from self._process_line(line, used_identifier)

        self._check_for_usage(used_identifier)

    def _process_line(self, line, used_identifier):
        yield line

        line = line.strip()
        if line.startswith('<!-- TestRef:') and line.endswith('-->'):
            identifier = line[13:-3].strip()
            used_identifier.append(identifier)
            for entry in self._format_tests(identifier):
                yield entry

    def _check_for_usage(self, used_identifier):
        for key in self._grouped_tests:
            if key not in used_identifier:
                warnings.warn(Warning(f'Identifier {key} was not used in the spec document {self._source_file}.'))

    def _format_tests(self, identifier: str):
        if identifier not in self._grouped_tests:
            warnings.warn(Warning(f'Identifier {identifier} in file {self._source_file}'
                                    f' is not used in any test.'))
            yield f'> **No Proves found for Reference *{identifier}*** \n'
            return

        items = self._grouped_tests[identifier]

        yield f'> **Proved by Tests for Reference *{identifier}*** \n'
        yield '>\n'
        yield (f'> The following tests proved this feature in the test run *{self._test_run_id}* '
               f'on version {self._version}.\n')
        yield '>\n'

        yield '>>| # |   | Name | Type | Explanation | Path |  \n'
        yield '>>| --- | --- | --- | --- | --- | --- | \n'
        for index, item in enumerate(items):
            report = self._results[item.nodeid]
            yield (f">>| {index + 1} | "
                   f"{':heavy_check_mark:' if report.passed else ':x:'} | "
                   f"{self.format_test_name(item.name)} | "
                   f"{getattr(report, 'test_type') if hasattr(report, 'test_type') else TestType.UNIT} | "
                   f"{' '.join(self.format_doc_string(item.obj.__doc__))} | "
                   f"{item.nodeid} | "
                   f"\n")

        yield '\n'
        yield '\n'


class ItemEnhancer:

    @classmethod
    def enhance(cls, outcome, item):
        report = outcome.get_result()  # type: _pytest.reports.TestReport
        node = getattr(item, 'obj', None)
        if node:
            report.node_obj = node
            report.node_parents = []
            parent = cls.get_parent(node)
            while parent:
                report.node_parents.append(parent)
                parent = cls.get_parent(parent)
            report.node_parents.reverse()

            report.reference_docs = []
            for marker in item.iter_markers_with_node(name='func_reference'):
                report.reference_docs.append((marker[0], marker[1].args))

            for marker in item.iter_markers_with_node(name='test_type'):
                report.test_type = ", ".join(marker[1].args)

    @staticmethod
    def get_parent(obj):
        try:
            parents = obj.__qualname__.split(".")
            if len(parents) > 1 and "<locals>" not in parents:
                full_name = obj.__module__ + "." + ".".join(parents[:-1])
                script = \
                    f'exec("import {obj.__module__}") or {full_name}'
                x = eval(script, globals(), locals())
                return x

        except Exception as err:
            print(err)

        return None

    @staticmethod
    def _get_parent_doc(function):
        func = getattr(function, "__self__", None)
        if not func:
            return ""
        parent = getattr(func, "__class__", None)
        if not parent:
            return ""

        doc = inspect.getdoc(parent)
        return doc if doc is not None else ""
