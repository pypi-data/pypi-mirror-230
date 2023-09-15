#!/usr/bin/env python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

# Copyright (C) 2022 Authors
#
# Released under GNU GPLv2 or later, read the file 'LICENSE.GPLv2+' for
# more information.
#
# Authors:
#   Bryce Harrington <bryce@canonical.com>

"""Utilities for reading input and writing output to external locations."""

import sys
import urllib.request


def open_url(url, desc="data"):
    """Open a remote URL for reading.

    :rtype: urllib.request.Request
    :returns: A request object for the stream to read from, or None on error.
    """
    request = urllib.request.Request(url)
    request.add_header('Cache-Control', 'max-age=0')
    try:
        return urllib.request.urlopen(request)
    except urllib.error.HTTPError as e:
        # 401 here means nothing is published or ran yet.
        # This is a rather common case, so skip mention of it
        if e.code != 401:
            sys.stderr.write(f"Error: Could not retrieve {desc} from {url}: {e}")
        return None
