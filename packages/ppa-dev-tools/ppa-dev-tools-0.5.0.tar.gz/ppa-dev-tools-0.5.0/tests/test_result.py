#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2022 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Results class tests."""

import os
import sys
import time

import gzip
import json
import pytest

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
DATA_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "data"))

from ppa.result import Result


def test_object():
    """Checks that Result objects can be instantiated."""
    timestamp = time.strptime('20030201_040506', "%Y%m%d_%H%M%S")
    result = Result('url', timestamp, 'b', 'c', 'd')
    assert result
    assert result.url == 'url'
    assert result.time == timestamp
    assert result.series == 'b'
    assert result.arch == 'c'
    assert result.source == 'd'
    assert not result.error_message


def test_repr():
    """Checks Result object representation."""
    result = Result('url', None, 'b', 'c', 'd')
    # TODO: Should this include the full set of args?
    assert repr(result) == "Result(url='url')"


def test_str():
    """Checks Result object textual presentation."""
    timestamp = time.strptime('20030201_040506', "%Y%m%d_%H%M%S")
    result = Result('url', timestamp, 'b', 'c', 'd')
    assert f"{result}" == 'd on b for c       @ 01.02.03 04:05:06'


def test_timestamp():
    """Checks Result object formats the result's time correctly."""
    timestamp = time.strptime('20030201_040506', "%Y%m%d_%H%M%S")
    result = Result('url', timestamp, 'b', 'c', 'd')
    assert f"{result.timestamp}" == '01.02.03 04:05:06'


def test_log(tmp_path):
    """Checks that the log content of a Result is available."""
    f = tmp_path / "result.log.gz"
    compressed_text = gzip.compress(bytes('abcde', 'utf-8'))
    f.write_bytes(compressed_text)

    result = Result(f"file://{f}", None, None, None, None)
    assert result.log == "abcde"


def test_triggers():
    """Checks that autopkgtest triggers can be extracted from test result logs."""
    result = Result(f"file://{DATA_DIR}/results-six-s390x.log.gz", None, None, None, None)
    assert result.triggers == ['pygobject/3.42.2-2', 'six/1.16.0-4']


@pytest.mark.parametrize('log_text, subtest_name, expected', [
    ('', None, {}),
    (
        (
            "x: @@@@@@@@@@@@@@@@@@@@ summary\n"
            "test-a          PASS\n"
            "test-b          FAIL ignorable-note\n"
            "test-c          NoTaVaLiDsTaTuS\n"
        ),
        None,
        {'test-a': 'PASS', 'test-b': 'FAIL'}
    ),
    (
        (
            "autopkgtest [21:13:56]: starting date: 2022-11-18\n"
            "The following packages have unmet dependencies:\n"
            " builddeps:.../12-autopkgtest-satdep.dsc:i386 : Depends: gcc:i386 but it is not installable\n"
            "E: Unable to correct problems, you have held broken packages.\n"
            "chroot               FAIL badpkg\n"
            "blame: apache2\n"
            "badpkg: Test dependencies are unsatisfiable. A common reason is ...\n"
            "autopkgtest [21:48:03]: @@@@@@@@@@@@@@@@@@@@ summary\n"
            "run-test-suite       FAIL badpkg\n"
            "blame: apache2\n"
            "badpkg: Test dependencies are unsatisfiable. A common reason is...\n"
            "duplicate-module-load PASS\n"
            "default-mods         PASS\n"
            "run-htcacheclean     PASS\n"
            "ssl-passphrase       PASS\n"
            "check-http2          PASS\n"
            "run-chroot           FAIL badpkg\n"
            "blame: apache2\n"
        ),
        'run-',
        {
            'run-test-suite': 'FAIL',
            'run-htcacheclean': 'PASS',
            'run-chroot': 'FAIL',
        }
    ),
    (
        (
            "3657s rm: cannot remove '.../mountpoint': Device or resource busy\n"
            "3661s autopkgtest [03:41:43]: test minimized: -----------------------]\n"
            "3663s autopkgtest [03:41:45]: test minimized:  - - - - - - - - - - results - - - - - - - - - -\n"
            "3663s minimized            FAIL non-zero exit status 1\n"
            "3663s autopkgtest [03:41:45]: test minimized:  - - - - - - - - - - stderr - - - - - - - - - -\n"
            "3663s rm: cannot remove '.../mountpoint': Device or resource busy\n"
            "3664s autopkgtest [03:41:46]: @@@@@@@@@@@@@@@@@@@@ summary\n"
            "3664s default-bootstraps   FAIL non-zero exit status 1\n"
            "3664s minimized            FAIL non-zero exit status 1'\n"
        ),
        None,
        {
            'default-bootstraps': 'FAIL',
            'minimized': 'FAIL'
        }
    ),
])
def test_get_subtests(tmp_path, log_text: str, subtest_name: str, expected: dict[str]):
    """Checks retrieval of Subtest objects from autopkgtest results.

    This test exercises the parser that extracts subtest information out
    of autopkgtest logs of various formats.  It also verifies the
    parameter to get_subtests() is handled correctly.

    :param fixture tmp_path: Temp dir.
    :param str log_text: Text to write into the log file.
    :param str subtest_name: Only retrieve subtests starting with this text.
    :param dict[str] expected: Dictionary of subtest names to pass/fail status.
    """
    f = tmp_path / "result.log.gz"
    compressed_text = gzip.compress(bytes(log_text, 'utf-8'))
    f.write_bytes(compressed_text)

    result = Result(f"file://{f}", None, None, None, None)
    subtests = result.get_subtests(subtest_name)
    assert {s.desc: s.status for s in subtests} == expected


@pytest.mark.parametrize('log_text, series, arch, source, expected_dict', [
    ('x', 'x', 'x', 'x', {})
])
def test_to_dict(tmp_path, log_text, series, arch, source, expected_dict):
    """Checks Result object structural representation."""
    f = tmp_path / "result.log.gz"
    f.write_bytes(gzip.compress(bytes(log_text, 'utf-8')))
    timestamp = time.strptime('20030201_040506', "%Y%m%d_%H%M%S")
    result = Result(f"file://{f}", timestamp, series, arch, source)
    expected_keys = [
        'url', 'timestamp', 'series', 'arch', 'source',
        'error_message', 'log', 'triggers', 'subtests', 'status',
        'status_icon'
    ]
    expected_types = [str, type(None), list]

    d = result.to_dict()
    assert isinstance(d, dict), f"type of d is {type(d)} not dict"

    # Verify expected keys are present
    assert sorted(d.keys()) == sorted(expected_keys)

    # Verify values are within set of expected types
    for k, v in d.items():
        assert type(v) in expected_types, f"'{k}={v}' is unexpected type {type(v)}"

    # Verify full dict can be written as JSON
    try:
        assert json.dumps(d)
    except UnicodeDecodeError as e:
        assert False, f"Wrong UTF codec detected: {e}"
    except json.JSONDecodeError as e:
        assert False, f"JSON decoding error: {e.msg}, {e.doc}, {e.pos}"
