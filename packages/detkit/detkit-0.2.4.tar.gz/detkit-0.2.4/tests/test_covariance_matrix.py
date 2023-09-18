#! /usr/bin/env python

# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

from detkit.datasets import covariance_matrix
import os
import sys


# ===========
# remove file
# ===========

def remove_file(filename):
    """
    Remove file.
    """

    if os.path.exists(filename):
        os.remove(filename)


# ======================
# test covariance matrix
# ======================

def test_covariance_matrix():
    """
    Test for `covariance_matrix` function.

    Note that this test can only be done on Python 3.8 and above.
    """

    # Find Python version
    py_major = sys.version_info.major
    py_minor = sys.version_info.minor

    # This test can only be done on Python 3.8 and above.
    if (py_major < 3) or (py_minor < 8):
        return

    covariance_matrix(size=2**9, sample=2, cor=False, ecg_start=0.0,
                      ecg_end=30.0, ecg_wrap=False, plot=True)
    covariance_matrix(size=2**9, sample=2, cor=False, ecg_start=0.0,
                      ecg_end=30.0, ecg_wrap=True, plot=True)
    covariance_matrix(size=2**9, sample=2, cor=True, ecg_start=0.0,
                      ecg_end=30.0, ecg_wrap=False, plot=True)

    remove_file('covariance_matrix.svg')
    remove_file('covariance_matrix.pdf')


# ===========
# Script main
# ===========

if __name__ == "__main__":
    test_covariance_matrix()
