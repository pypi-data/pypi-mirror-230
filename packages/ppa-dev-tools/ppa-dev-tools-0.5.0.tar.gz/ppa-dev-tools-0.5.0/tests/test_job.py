#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Author:  Bryce Harrington <bryce@canonical.com>
#
# Copyright (C) 2022 Bryce W. Harrington
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.

"""Job class tests."""

import os
import sys

import json

sys.path.insert(0, os.path.realpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))

from ppa.job import Job, get_running, get_waiting
from tests.helpers import RequestResponseMock


def test_object():
    """Checks that Job objects can be instantiated."""
    job = Job(0, '', '', '', '')
    assert job


def test_init():
    """Checks the initialization of a Job object."""
    job = Job(0, 'a', 'b', 'c', 'd')
    assert job.number == 0
    assert job.submit_time == 'a'
    assert job.source_package == 'b'
    assert job.series == 'c'
    assert job.arch == 'd'


def test_repr():
    """Checks Job object machine-parsable representation."""
    job = Job(0, 'a', 'b', 'c', 'd')
    assert repr(job) == "Job(source_package='b', series='c', arch='d')"


def test_str():
    """Checks Job object textual presentation."""
    job = Job(0, 'a', 'b', 'c', 'd')
    assert f"{job}" == 'b c (d)'


def test_to_dict():
    """Checks Job object structural representation."""
    job = Job(0, 'a', 'b', 'c', 'd')
    expected_keys = [
        'number', 'submit_time', 'source_package_name',
        'series', 'arch', 'triggers', 'ppas'
    ]
    expected_types = [str, int, list]

    d = job.to_dict()
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


def test_triggers():
    """Checks Job object's triggers."""
    job = Job(0, '', '', '', '', triggers=['a/1', 'b/2'])
    assert job.triggers == ['a/1', 'b/2']


def test_ppas():
    """Checks Job object textual presentation."""
    job = Job(0, '', '', '', '', ppas=['ppa:a/b', 'ppa:c/d'])
    assert job.ppas == ['ppa:a/b', 'ppa:c/d']


def test_request_url():
    """Checks Job object textual presentation."""
    jobinfo = {
        'triggers': ['t/1'],
        'ppas': ['ppa:a/b', 'ppa:c/d']
    }
    job = Job(0, 'a', 'b', 'c', 'd', jobinfo['triggers'], jobinfo['ppas'])
    assert job.request_url.startswith("https://autopkgtest.ubuntu.com/request.cgi")
    assert job.request_url.endswith("?release=c&arch=d&package=b&trigger=t/1")


def test_get_running():
    """Checks output from the get_running() command."""
    json_text = ('{"mypackage": {"my-job-id": {"focal": { "arm64": ['
                 '{"submit-time": "2022-08-19 20:59:01", '
                 '"triggers": ["yourpackage/1.2.3"], '
                 '"ppas": ["ppa:me/myppa"]}, '
                 '1234, '
                 '"Log Output Here"'
                 '] } } } }')
    fake_response = RequestResponseMock(json_text)
    job = next(get_running(fake_response, releases=['focal'], ppa='ppa:me/myppa'))
    assert repr(job) == "Job(source_package='mypackage', series='focal', arch='arm64')"
    assert job.triggers == ["yourpackage/1.2.3"]
    assert job.ppas == ["ppa:me/myppa"]


def test_get_waiting():
    """Checks output from the get_waiting() command."""
    # TODO: I think ppas need to be in "ppa" instead of under "ubuntu" but need to doublecheck.
    json_text = ('{ "ubuntu": { "focal": { "amd64": ['
                 ' "a\\n{\\"requester\\":   \\"you\\",'
                 '      \\"submit-time\\": \\"2022-08-19 07:37:56\\",'
                 '      \\"triggers\\":    [ \\"a/1.2-3\\", \\"b/1-1\\" ] }",'
                 ' "b\\n{\\"requester\\":   \\"you\\",'
                 '      \\"submit-time\\": \\"2022-08-19 07:37:57\\",'
                 '      \\"ppas\\":        [ \\"ppa:me/myppa\\" ],'
                 '      \\"triggers\\":    [ \\"c/3.2-1\\", \\"d/2-2\\" ] }"'
                 '] } } }')
    fake_response = RequestResponseMock(json_text)
    job = next(get_waiting(fake_response, releases=['focal'], ppa='ppa:me/myppa'))
    assert job
    assert job.source_package == "b"
    assert job.ppas == ['ppa:me/myppa']
    assert job.triggers == ['c/3.2-1', 'd/2-2']
