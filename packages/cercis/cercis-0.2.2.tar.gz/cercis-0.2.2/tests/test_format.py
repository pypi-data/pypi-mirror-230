import itertools
import re
from dataclasses import replace
from typing import Any, Iterator
from unittest.mock import patch

import pytest

import cercis
from cercis import TargetVersion
from tests.util import (
    DEFAULT_MODE,
    PY36_VERSIONS,
    all_data_cases,
    assert_format,
    dump_to_stderr,
    read_data,
)


def _override_single_quote_for_cleaner_future_rebase(mode: cercis.Mode) -> None:
    mode.single_quote = False


def _use_line_length_of_88_for_cleaner_future_rebase(mode: cercis.Mode) -> None:
    mode.line_length = 88


@pytest.fixture(autouse=True)
def patch_dump_to_file(request: Any) -> Iterator[None]:
    with patch("cercis.dump_to_file", dump_to_stderr):
        yield


def check_file(
        subdir: str, filename: str, mode: cercis.Mode, *, data: bool = True
) -> None:
    source, expected = read_data(subdir, filename, data=data)
    assert_format(source, expected, mode, fast=False)


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
@pytest.mark.parametrize("filename", all_data_cases("simple_cases"))
def test_simple_format(filename: str) -> None:
    magic_trailing_comma = filename != "skip_magic_trailing_comma"
    single_quote = filename == "expression"
    mode = cercis.Mode(
        magic_trailing_comma=magic_trailing_comma,
        wrap_line_with_long_string=True,
        collapse_nested_brackets=False,
        single_quote=single_quote,
        wrap_comments=True,
        wrap_pragma_comments=True,
        keep_blank_lines_in_brackets=False,
        line_length=88,
        is_pyi=filename.endswith("_pyi"),
    )
    check_file("simple_cases", filename, mode)


@pytest.mark.parametrize("filename", all_data_cases("preview"))
def test_preview_format(filename: str) -> None:
    mode = cercis.Mode(
        preview=True,
        wrap_line_with_long_string=True,
        collapse_nested_brackets=False,
        wrap_comments=True,
        wrap_pragma_comments=True,
        line_length=88,
    )
    _override_single_quote_for_cleaner_future_rebase(mode)
    check_file("preview", filename, mode)


def test_preview_context_managers_targeting_py38() -> None:
    source, expected = read_data("preview_context_managers", "targeting_py38.py")
    mode = cercis.Mode(preview=True, target_versions={cercis.TargetVersion.PY38})
    _override_single_quote_for_cleaner_future_rebase(mode)
    assert_format(source, expected, mode, minimum_version=(3, 8))


def test_preview_context_managers_targeting_py39() -> None:
    source, expected = read_data("preview_context_managers", "targeting_py39.py")
    mode = cercis.Mode(preview=True, target_versions={cercis.TargetVersion.PY39})
    _override_single_quote_for_cleaner_future_rebase(mode)
    _use_line_length_of_88_for_cleaner_future_rebase(mode)
    assert_format(source, expected, mode, minimum_version=(3, 9))


@pytest.mark.parametrize("filename", all_data_cases("preview_py_310"))
def test_preview_python_310(filename: str) -> None:
    source, expected = read_data("preview_py_310", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY310}, preview=True)
    assert_format(source, expected, mode, minimum_version=(3, 10))


@pytest.mark.parametrize(
    "filename", all_data_cases("preview_context_managers/auto_detect")
)
def test_preview_context_managers_auto_detect(filename: str) -> None:
    match = re.match(r"features_3_(\d+)", filename)
    assert match is not None, "Unexpected filename format: %s" % filename
    source, expected = read_data("preview_context_managers/auto_detect", filename)
    mode = cercis.Mode(preview=True)
    _override_single_quote_for_cleaner_future_rebase(mode)
    assert_format(source, expected, mode, minimum_version=(3, int(match.group(1))))


# =============== #
# Complex cases
# ============= #


def test_empty() -> None:
    source = expected = ""
    assert_format(source, expected)


@pytest.mark.parametrize("filename", all_data_cases("py_36"))
def test_python_36(filename: str) -> None:
    source, expected = read_data("py_36", filename)
    mode = cercis.Mode(target_versions=PY36_VERSIONS)
    assert_format(source, expected, mode, minimum_version=(3, 6))


@pytest.mark.parametrize("filename", all_data_cases("py_37"))
def test_python_37(filename: str) -> None:
    source, expected = read_data("py_37", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY37})
    assert_format(source, expected, mode, minimum_version=(3, 7))


@pytest.mark.parametrize("filename", all_data_cases("py_38"))
def test_python_38(filename: str) -> None:
    source, expected = read_data("py_38", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY38})
    _override_single_quote_for_cleaner_future_rebase(mode)
    assert_format(source, expected, mode, minimum_version=(3, 8))


@pytest.mark.parametrize("filename", all_data_cases("py_39"))
def test_python_39(filename: str) -> None:
    source, expected = read_data("py_39", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY39})
    _override_single_quote_for_cleaner_future_rebase(mode)
    assert_format(source, expected, mode, minimum_version=(3, 9))


@pytest.mark.parametrize("filename", all_data_cases("py_310"))
def test_python_310(filename: str) -> None:
    source, expected = read_data("py_310", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY310})
    _override_single_quote_for_cleaner_future_rebase(mode)
    _use_line_length_of_88_for_cleaner_future_rebase(mode)
    assert_format(source, expected, mode, minimum_version=(3, 10))


@pytest.mark.parametrize("filename", all_data_cases("py_310"))
def test_python_310_without_target_version(filename: str) -> None:
    source, expected = read_data("py_310", filename)
    mode = cercis.Mode()
    _override_single_quote_for_cleaner_future_rebase(mode)
    _use_line_length_of_88_for_cleaner_future_rebase(mode)
    assert_format(source, expected, mode, minimum_version=(3, 10))


def test_patma_invalid() -> None:
    source, expected = read_data("miscellaneous", "pattern_matching_invalid")
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY310})
    with pytest.raises(cercis.parsing.InvalidInput) as exc_info:
        assert_format(source, expected, mode, minimum_version=(3, 10))

    exc_info.match("Cannot parse: 10:11")


@pytest.mark.parametrize("filename", all_data_cases("py_311"))
def test_python_311(filename: str) -> None:
    source, expected = read_data("py_311", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY311})
    _override_single_quote_for_cleaner_future_rebase(mode)
    assert_format(source, expected, mode, minimum_version=(3, 11))


@pytest.mark.parametrize("filename", all_data_cases("py_312"))
def test_python_312(filename: str) -> None:
    source, expected = read_data("py_312", filename)
    mode = cercis.Mode(target_versions={cercis.TargetVersion.PY312})
    _override_single_quote_for_cleaner_future_rebase(mode)
    mode.function_definition_extra_indent = False
    assert_format(source, expected, mode, minimum_version=(3, 12))


@pytest.mark.parametrize("filename", all_data_cases("fast"))
def test_fast_cases(filename: str) -> None:
    source, expected = read_data("fast", filename)
    assert_format(source, expected, fast=True)


def test_python_2_hint() -> None:
    with pytest.raises(cercis.parsing.InvalidInput) as exc_info:
        assert_format("print 'daylily'", "print 'daylily'")
    exc_info.match(cercis.parsing.PY2_HINT)


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
def test_docstring_no_string_normalization() -> None:
    """Like test_docstring but with string normalization off."""
    source, expected = read_data("miscellaneous", "docstring_no_string_normalization")
    mode = replace(DEFAULT_MODE, string_normalization=False)
    assert_format(source, expected, mode)


def test_docstring_line_length_6() -> None:
    """Like test_docstring but with line length set to 6."""
    source, expected = read_data("miscellaneous", "linelength6")
    mode = cercis.Mode(line_length=6)
    assert_format(source, expected, mode)


def test_preview_docstring_no_string_normalization() -> None:
    """
    Like test_docstring but with string normalization off *and* the preview style
    enabled.
    """
    source, expected = read_data(
        "miscellaneous", "docstring_preview_no_string_normalization"
    )
    mode = replace(DEFAULT_MODE, string_normalization=False, preview=True)
    assert_format(source, expected, mode)


def test_long_strings_flag_disabled() -> None:
    """Tests for turning off the string processing logic."""
    source, expected = read_data("miscellaneous", "long_strings_flag_disabled")
    mode = replace(
        DEFAULT_MODE,
        experimental_string_processing=False,
        wrap_line_with_long_string=True,
    )
    _override_single_quote_for_cleaner_future_rebase(mode)
    assert_format(source, expected, mode)


def test_stub() -> None:
    mode = replace(DEFAULT_MODE, is_pyi=True)
    source, expected = read_data("miscellaneous", "stub.pyi")
    assert_format(source, expected, mode)


def test_nested_stub() -> None:
    mode = replace(DEFAULT_MODE, is_pyi=True, preview=True, single_quote=False)
    source, expected = read_data("miscellaneous", "nested_stub.pyi")
    assert_format(source, expected, mode)


def test_power_op_newline() -> None:
    # requires line_length=0
    source, expected = read_data("miscellaneous", "power_op_newline")
    assert_format(source, expected, mode=cercis.Mode(line_length=0))


def test_type_comment_syntax_error() -> None:
    """Test that cercis is able to format python code with type comment syntax errors."""
    source, expected = read_data("type_comments", "type_comment_syntax_error")
    assert_format(source, expected)
    cercis.assert_equivalent(source, expected)


@pytest.mark.parametrize(
    "filename, extra_indent",
    [
        ("func_def_extra_indent.py", True),  # Cercis's default
        ("func_def_no_extra_indent.py", False),  # Black's default
    ],
)
def test_function_definition_extra_indent(filename: str, extra_indent: bool) -> None:
    mode = replace(
        DEFAULT_MODE,
        function_definition_extra_indent=extra_indent,
        # Adding trailing commas after *args etc. are only supported in py36+
        target_versions={TargetVersion.PY36},
    )
    check_file("configurable_cases/func_def_indent", filename, mode)


@pytest.mark.parametrize(
    "filename, extra_indent",
    [
        ("no_extra_indent.py", False),
        ("extra_indent.py", True),
    ],
)
def test_closing_bracket_extra_indent(filename: str, extra_indent: bool) -> None:
    mode = replace(
        DEFAULT_MODE,
        line_length=30,
        closing_bracket_extra_indent=extra_indent,
    )
    check_file("configurable_cases/closing_bracket_indent", filename, mode)


@pytest.mark.filterwarnings("ignore:invalid escape sequence.*:DeprecationWarning")
@pytest.mark.parametrize(
    "filename",
    all_data_cases("configurable_cases/single_quote"),
)
def test_single_quote(filename: str) -> None:
    mode = replace(
        DEFAULT_MODE,
        single_quote=True,
        wrap_line_with_long_string=True,
        collapse_nested_brackets=False,
        wrap_comments=True,
        wrap_pragma_comments=True,
        line_length=88,
    )
    check_file("configurable_cases/single_quote", filename, mode)


@pytest.mark.parametrize(
    "filename, wrap_line",
    [
        ("test_cases__Cercis_default.py", False),
        ("test_cases__Black_default.py", True),
        ("long_strings_flag_disabled__Cercis_default.py", False),
        ("long_strings_flag_disabled__Black_default.py", True),
        ("edge_cases.py", False),
        ("edge_cases.py", True),
    ],
)
def test_opt_out_of_wrapping(filename: str, wrap_line: bool) -> None:
    mode = replace(
        DEFAULT_MODE,
        wrap_line_with_long_string=wrap_line,
        wrap_comments=True,
    )
    _override_single_quote_for_cleaner_future_rebase(mode)
    _use_line_length_of_88_for_cleaner_future_rebase(mode)
    check_file("configurable_cases/line_with_long_string", filename, mode)


@pytest.mark.parametrize(
    "filename, collapse_nested_brackets",
    [
        ("nested_brackets__Cercis_default.py", True),
        ("nested_brackets__Black_default.py", False),
        ("nested_brackets_explodes__Cercis_default.py", True),
        ("nested_brackets_explodes__Black_default.py", False),
    ],
)
def test_nested_brackets(filename: str, collapse_nested_brackets: bool) -> None:
    mode = replace(DEFAULT_MODE, collapse_nested_brackets=collapse_nested_brackets)
    _override_single_quote_for_cleaner_future_rebase(mode)
    check_file("configurable_cases/nested_brackets", filename, mode)


@pytest.mark.parametrize(
    "filename, wrap",
    [
        ("Cercis_default.py", False),
        ("Cercis_default_2.py", False),
        ("Black_default.py", True),
        ("Black_default_2.py", True),
    ],
)
def test_wrap_pragma_comments(filename: str, wrap: bool) -> None:
    mode = replace(
        DEFAULT_MODE,
        wrap_comments=True,
        wrap_pragma_comments=wrap,
        line_length=80,
    )
    check_file("configurable_cases/pragma_comments", filename, mode)


@pytest.mark.parametrize(
    "filename, wrap_comments, wrap_pragma_comments",
    [
        ("case_False_False.py", False, False),
        ("case_True_False.py", True, False),
        ("case_True_True.py", True, True),
        ("case_False_True.py", False, True),
    ],
)
def test_wrap_comments(
        filename: str,
        wrap_comments: bool,
        wrap_pragma_comments: bool,
) -> None:
    mode = replace(
        DEFAULT_MODE,
        wrap_comments=wrap_comments,
        wrap_pragma_comments=wrap_pragma_comments,
        line_length=80,
    )
    check_file("configurable_cases/line_with_comments", filename, mode)


@pytest.mark.parametrize(
    "closing_bracket_extra_indent, base_indent_spaces, fdei, olcei",
    list(
        itertools.product(  # each list here corresponds to 1 argument above
            [False, True],
            [1, 2, 3, 4, 8],
            [False, True],
            [False, True],
        )
    ),
)
def test_indent_levels__use_spaces(
        closing_bracket_extra_indent: bool,
        base_indent_spaces: int,
        fdei: bool,
        olcei: bool,
) -> None:
    mode = replace(
        DEFAULT_MODE,
        line_length=80,
        base_indentation_spaces=base_indent_spaces,
        function_definition_extra_indent=fdei,
        other_line_continuation_extra_indent=olcei,
        closing_bracket_extra_indent=closing_bracket_extra_indent,
    )
    parent_folder = "configurable_cases/indentation/use_spaces"
    folder = (
        f"{parent_folder}/closing_bracket_extra_indent"
        if closing_bracket_extra_indent
        else f"{parent_folder}/closing_bracket_no_extra_indent"
    )
    check_file(
        f"{folder}/base_indent_spaces={base_indent_spaces}",
        f"fdei={fdei}_olcei={olcei}",
        mode,
    )


@pytest.mark.parametrize(
    "closing_bracket_extra_indent, fdei, olcei",
    list(
        itertools.product(  # each list here corresponds to 1 argument above
            [False, True],
            [False, True],
            [False, True],
        )
    ),
)
def test_indent_levels__use_tabs(
        closing_bracket_extra_indent: bool,
        fdei: bool,
        olcei: bool,
) -> None:
    mode = replace(
        DEFAULT_MODE,
        line_length=80,
        use_tabs=True,
        function_definition_extra_indent=fdei,
        other_line_continuation_extra_indent=olcei,
        closing_bracket_extra_indent=closing_bracket_extra_indent,
    )
    parent_folder = "use_tabs"
    folder = (
        f"{parent_folder}/closing_bracket_extra_indent"
        if closing_bracket_extra_indent
        else f"{parent_folder}/closing_bracket_no_extra_indent"
    )
    check_file(
        f"configurable_cases/indentation/{folder}",
        f"fdei={fdei}_olcei={olcei}",
        mode,
    )


@pytest.mark.parametrize(
    "tab_width",
    [1, 2, 3, 4, 5, 8],
)
def test_line_length_calculation_with_tabs(tab_width: int) -> None:
    mode = replace(
        DEFAULT_MODE,
        line_length=80,
        use_tabs=True,
        tab_width=tab_width,
        function_definition_extra_indent=False,
        other_line_continuation_extra_indent=False,
        closing_bracket_extra_indent=False,
    )
    filename = f"tab_width_{tab_width}"
    check_file(
        "configurable_cases/indentation/use_tabs/line_length_calculation",
        filename,
        mode,
    )


@pytest.mark.parametrize(
    "filename, kblib",
    [("true.py", True), ("false.py", False)],
)
def test_keep_blank_lines_in_brackets(filename: str, kblib: bool) -> None:
    mode = replace(
        DEFAULT_MODE,
        keep_blank_lines_in_brackets=kblib,
    )
    check_file(
        "configurable_cases/keep_blank_lines_in_brackets",
        filename,
        mode,
    )


def test_playground() -> None:
    mode = replace(
        DEFAULT_MODE,
        line_length=79,
    )
    filename = "playground/playground.py"
    check_file("configurable_cases", filename=filename, mode=mode)
