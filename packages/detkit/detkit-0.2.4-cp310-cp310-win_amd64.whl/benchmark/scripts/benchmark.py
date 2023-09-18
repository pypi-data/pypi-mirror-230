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

import sys
import os
from os.path import join
import getopt
import numpy
# from numpy.linalg import qr
import pickle
import multiprocessing
import platform
import subprocess
import re

from timer import Timer
from detkit import loggdet, logpdet, orthogonalize, covariance_matrix, \
        design_matrix, get_config, get_instructions_per_task


# ===============
# parse arguments
# ===============

def parse_arguments(argv):
    """
    Parses the argument of the executable.
    """

    # -----------
    # print usage
    # -----------

    def print_usage(exec_name):
        usage_string = "Usage: " + exec_name + " <arguments>"
        options_string = """
The following arguments are required:

    -n --size=[int]         Size of the matrix in log2. The size of matrix is 2
                            to the power of this number.
    -f --func=[str]         Type of function, which can be either "loggdet", or
                            "logpdet".

The following arguments are optional:

    -b --blas               Computes logdet using existing libraries in numpy
                            and scipy, otherwise, it uses the cython code.
    -r --repeat=[int]       Number of times the numerical experiment is
                            repeated. Default is 10.
    -l --num-ratios=[int]   Number of ratios (p/n) from 0 to 1 to be tested.
                            Default is 50.
    -v --verbose            Prints verbose output. Default is False.
    -h --help               Prints the help message.

Examples:

    1. Compute loggdet, set the matrix size to n=2**8=256, the array of 50
       ratios p/n from 0 to 1, i.e. linspace(0, 1, 50), and repeat each
       experiment 3 times:

       $ %s -n 8 -f loggdet -r 3 -l 50 -v

    2. Compute logpdet, set the matrix size to n=2**9=512, the array of 100
       ratios p/n from 0 to 1, i.e. linspace(0, 1, 100), and repeat each
       experiment 5 times:

       $ %s -n 9 -f logpdet -r 5 -l 100 -v
        """ % (argv[0], argv[0])

        print(usage_string)
        print(options_string)

    # -----------------

    # Initialize variables (defaults)
    arguments = {
        'n': None,
        'func': None,  # can be "loggdet" or "logpdet"
        'repeat': 10,
        'num_ratios': 50,
        'verbose': False,
        'use_blas': False,
    }

    # Get options
    try:
        opts, args = getopt.getopt(argv[1:], "n:f:r:t:bvh",
                                   ["size=", "func=", "repeat=", "num-ratios=",
                                    "blas", "verbose", "help"])
    except getopt.GetoptError:
        print_usage(argv[0])
        sys.exit(2)

    # Assign options
    for opt, arg in opts:
        if opt in ('-n', '--size'):
            arguments['n'] = int(arg)
        elif opt in ('-f', '--func'):
            arguments['func'] = arg
        elif opt in ('-r', '--repeat'):
            arguments['repeat'] = int(arg)
        elif opt in ('-l', '--num-ratios'):
            arguments['num_ratios'] = int(arg)
        elif opt in ('-b', '--blas'):
            arguments['use_blas'] = True
        elif opt in ('-v', '--verbose'):
            arguments['verbose'] = True
        elif opt in ('-h', '--help'):
            print_usage(argv[0])
            sys.exit()

    if arguments['n'] is None:
        print('ERROR: argument "-n" is required.')
        print('')
        print_usage(argv[0])
        sys.exit()
    if arguments['func'] not in ['loggdet', 'logpdet']:
        print('ERROR: argument "-f" is required and should be equal to ' +
              'either "loggdet" or "logpdet".')
        print('')
        print_usage(argv[0])
        sys.exit()

    return arguments


# ==================
# get processor name
# ==================

def get_processor_name():
    """
    Gets the name of CPU.

    For windows operating system, this function still does not get the full
    brand name of the cpu.
    """

    if platform.system() == "Windows":
        return platform.processor()

    elif platform.system() == "Darwin":
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
        command = "sysctl -n machdep.cpu.brand_string"
        return subprocess.getoutput(command).strip()

    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.getoutput(command).strip()
        for line in all_info.split("\n"):
            if "model name" in line:
                return re.sub(".*model name.*:", "", line, 1)[1:]

    return ""


# =============
# legacy method
# =============

def legacy_method(func, K, X, sym_pos=False, X_orth=False, use_blas=False):
    """
    Computes determinant using the standard method. Note that for this method,
    the X_orth should always be False.
    """

    timer = Timer()
    timer.tic()
    loggdet_, _, inst = func(K, X, method='legacy', sym_pos=sym_pos,
                             X_orth=X_orth, flops=True, use_scipy=use_blas)
    timer.toc()

    # Time of computing loggdet
    wall_time = timer.wall_time
    proc_time = timer.proc_time

    return loggdet_, wall_time, proc_time, inst


# ===============
# proj method gen
# ===============

def proj_method_gen(func, K, X, use_blas=False):
    """
    Computes determinant using the presented method. Note that for this method,
    the sym_pos should always be False.
    """

    timer = Timer()
    timer.tic()
    loggdet_, _, inst = func(K, X, method='proj', sym_pos=False, X_orth=False,
                             flops=True, use_scipy=use_blas)
    timer.toc()

    # Time of computing loggdet
    wall_time = timer.wall_time
    proc_time = timer.proc_time

    return loggdet_, wall_time, proc_time, inst


# ===============
# proj method ort
# ===============

def proj_method_ort(func, K, X, use_blas=False):
    """
    Computes determinant using the presented method. Note that for this method,
    the sym_pos should always be False.
    """

    # Orthogonalize X_
    timer = Timer()
    timer.tic()
    orthogonalize(X)
    timer.toc()

    # Preprocessing time of orthogonalizing X_
    wall_time_pre = timer.wall_time
    proc_time_pre = timer.proc_time

    timer.reset()

    # Compute loggdet
    timer.tic()
    loggdet_, _, inst = func(K, X, method='proj', sym_pos=False, X_orth=True,
                             flops=True, use_scipy=use_blas)
    timer.toc()

    # Time of computing loggdet
    wall_time = timer.wall_time
    proc_time = timer.proc_time

    return loggdet_, wall_time_pre, proc_time_pre, wall_time, proc_time, inst


# ===========
# comp method
# ===========

def comp_method(func, K, X, Xp=None, sym_pos=False, X_orth=False,
                use_blas=False):
    """
    Computes determinant using the presented method. Note that for this method,
    the sym_pos should always be False.
    """

    timer = Timer()

    # Compute loggdet
    timer.tic()
    loggdet_, _, inst = func(K, X, Xp=Xp, method='comp', sym_pos=sym_pos,
                             X_orth=X_orth, flops=True, use_scipy=use_blas)
    timer.toc()

    # Time of computing loggdet
    wall_time = timer.wall_time
    proc_time = timer.proc_time

    # return loggdet_, wall_time_pre, proc_time_pre, wall_time, proc_time, inst
    return loggdet_, wall_time, proc_time, inst


# =========
# benchmark
# =========

def benchmark(argv):
    """
    Benchmarks for computing determinant using the conventional verses the
    presented methods.
    """

    # Check if perf tool is installed (or user permission is set for perf)
    inst = get_instructions_per_task()
    if numpy.isnan(inst):
        raise RuntimeError('Perf tool is not installed or the user ' +
                           'permission is not set to run perf tool.')

    # get use input arguments from commandline
    arguments = parse_arguments(argv)

    # Determine the computing function
    if arguments['func'] == 'loggdet':
        func = loggdet
    elif arguments['func'] == 'logpdet':
        func = logpdet
    else:
        raise ValueError('Function should be wither "loggdet" or "logpdet".')

    # Extract settings from arguments
    n = 2**arguments['n']
    num_ratios = arguments['num_ratios']
    repeat = arguments['repeat']
    verbose = arguments['verbose']

    # detkit config
    detkit_config = get_config()

    # Config dictionary
    config = {
        'n': n,
        'ratios': numpy.linspace(0.001, 0.999, num_ratios),
        'repeat': repeat,
        'func': arguments['func'],
        'use_blas': arguments['use_blas'],
        'verbose': verbose
    }

    # Devices dictionary
    devices = {
        'cpu_name': get_processor_name(),
        'num_all_cpu_threads': multiprocessing.cpu_count(),
        'instructions_per_matmat': get_instructions_per_task(task='matmat'),
        'instructions_per_gramian': get_instructions_per_task(
            task='gramian'),
        'instructions_per_cholesky': get_instructions_per_task(
            task='cholesky'),
        'instructions_per_lu': get_instructions_per_task(task='lu'),
        'instructions_per_lup': get_instructions_per_task(task='lup')
    }

    n = config['n']
    ratios = config['ratios']
    repeat = config['repeat']

    # # Generate random matrices
    # K = numpy.random.randn(n, n)
    # X = numpy.random.randn(n, n)
    #
    # # Make K to be symmetric positive-definite (SPD)
    # K = K.T @ K
    #
    # # Orthogonalize X
    # Q, R = qr(X)
    # X = Q
    # # orthogonalize(X)

    # Generate covariance matrix from ECG signal
    K = covariance_matrix(n)

    # Generate orthonormal design matrix from sin, cos of various frequencies.
    # Note, We only need n-1 columns of X. However, X should be generated by
    # full n columns, as otherwise we will get "A is not sym pos" error later
    # in comp method.
    X = design_matrix(n, n, ortho=True)

    # Preallocate output arrays
    logdet_lgcy_gen_gen = numpy.zeros((ratios.size, repeat))
    logdet_lgcy_gen_ort = numpy.zeros((ratios.size, repeat))
    logdet_lgcy_spd_gen = numpy.zeros((ratios.size, repeat))
    logdet_lgcy_spd_ort = numpy.zeros((ratios.size, repeat))
    logdet_proj_gen = numpy.zeros((ratios.size, repeat))
    logdet_proj_ort = numpy.zeros((ratios.size, repeat))
    logdet_comp_gen_gen = numpy.zeros((ratios.size, repeat))
    logdet_comp_spd_gen = numpy.zeros((ratios.size, repeat))
    logdet_comp_gen_ort = numpy.zeros((ratios.size, repeat))
    logdet_comp_spd_ort = numpy.zeros((ratios.size, repeat))
    logdet_comp_gen_ort_xp = numpy.zeros((ratios.size, repeat))
    logdet_comp_spd_ort_xp = numpy.zeros((ratios.size, repeat))

    wall_time_lgcy_gen_gen = numpy.zeros((ratios.size, repeat))
    wall_time_lgcy_gen_ort = numpy.zeros((ratios.size, repeat))
    wall_time_lgcy_spd_gen = numpy.zeros((ratios.size, repeat))
    wall_time_lgcy_spd_ort = numpy.zeros((ratios.size, repeat))
    wall_time_proj_gen = numpy.zeros((ratios.size, repeat))
    wall_time_proj_ort_pre = numpy.zeros((ratios.size, repeat))
    wall_time_proj_ort = numpy.zeros((ratios.size, repeat))
    wall_time_comp_gen_gen = numpy.zeros((ratios.size, repeat))
    wall_time_comp_spd_gen = numpy.zeros((ratios.size, repeat))
    wall_time_comp_gen_ort = numpy.zeros((ratios.size, repeat))
    wall_time_comp_spd_ort = numpy.zeros((ratios.size, repeat))
    wall_time_comp_gen_ort_xp = numpy.zeros((ratios.size, repeat))
    wall_time_comp_spd_ort_xp = numpy.zeros((ratios.size, repeat))

    proc_time_lgcy_gen_gen = numpy.zeros((ratios.size, repeat))  # A gen, X gen
    proc_time_lgcy_gen_ort = numpy.zeros((ratios.size, repeat))  # A gen, X ort
    proc_time_lgcy_spd_gen = numpy.zeros((ratios.size, repeat))  # A spd, X gen
    proc_time_lgcy_spd_ort = numpy.zeros((ratios.size, repeat))  # A spd, X ort
    proc_time_proj_gen = numpy.zeros((ratios.size, repeat))      # A gen, X gen
    proc_time_proj_ort_pre = numpy.zeros((ratios.size, repeat))  # A gen, X ort
    proc_time_proj_ort = numpy.zeros((ratios.size, repeat))      # A gen, X ort
    proc_time_comp_gen_gen = numpy.zeros((ratios.size, repeat))  # A gen, X gen
    proc_time_comp_spd_gen = numpy.zeros((ratios.size, repeat))  # A spd, X gen
    proc_time_comp_gen_ort = numpy.zeros((ratios.size, repeat))  # A gen, X gen
    proc_time_comp_spd_ort = numpy.zeros((ratios.size, repeat))  # A spd, X gen
    proc_time_comp_gen_ort_xp = numpy.zeros((ratios.size, repeat))  # Xp known
    proc_time_comp_spd_ort_xp = numpy.zeros((ratios.size, repeat))  # Xp known

    flops_lgcy_gen_gen = numpy.zeros((ratios.size, repeat))
    flops_lgcy_gen_ort = numpy.zeros((ratios.size, repeat))
    flops_lgcy_spd_gen = numpy.zeros((ratios.size, repeat))
    flops_lgcy_spd_ort = numpy.zeros((ratios.size, repeat))
    flops_proj_gen = numpy.zeros((ratios.size, repeat))
    flops_proj_ort_pre = numpy.zeros((ratios.size, repeat))
    flops_proj_ort = numpy.zeros((ratios.size, repeat))
    flops_comp_gen_gen = numpy.zeros((ratios.size, repeat))
    flops_comp_spd_gen = numpy.zeros((ratios.size, repeat))
    flops_comp_gen_ort = numpy.zeros((ratios.size, repeat))
    flops_comp_spd_ort = numpy.zeros((ratios.size, repeat))
    flops_comp_gen_ort_xp = numpy.zeros((ratios.size, repeat))
    flops_comp_spd_ort_xp = numpy.zeros((ratios.size, repeat))

    # loop over ratios (Legacy and Proj methods only)
    for j in range(ratios.size):

        # Size of columns of X
        m = int(n * ratios[j])
        if m == 0:
            m = 1
        elif m == n:
            m = n-1

        # Print progress
        if config['verbose']:
            if int(numpy.log10(ratios.size)) < 3:
                print('ratios: %2d/%d ' % (j+1, ratios.size), end='',
                      flush=True)
            elif int(numpy.log10(ratios.size)) == 3:
                print('ratios: %3d/%d ' % (j+1, ratios.size), end='',
                      flush=True)
            elif int(numpy.log10(ratios.size)) > 3:
                print('ratios: %4d/%d ' % (j+1, ratios.size), end='',
                      flush=True)

        # Repeat experiment
        for i in range(repeat):

            X_ = numpy.copy(X[:, :m])
            Xp = numpy.copy(X[:, m:])

            if config['verbose']:
                print('.', end='', flush=True)

            # Legacy method, generic matrix K, non-orthogonal X
            logdet_lgcy_gen_gen[j, i], wall_time_lgcy_gen_gen[j, i], \
                proc_time_lgcy_gen_gen[j, i], flops_lgcy_gen_gen[j, i] = \
                legacy_method(
                        func, K, X_, sym_pos=False, X_orth=False,
                        use_blas=config['use_blas'])

            if config['func'] == 'logpdet':
                # Legacy method, generic matrix K, non-orthogonal X
                logdet_lgcy_gen_ort[j, i], wall_time_lgcy_gen_ort[j, i], \
                    proc_time_lgcy_gen_ort[j, i], flops_lgcy_gen_ort[j, i] = \
                    legacy_method(
                            func, K, X_, sym_pos=False, X_orth=True,
                            use_blas=config['use_blas'])

            # Legacy method, symmetric positive-definite matrix K, X not ort
            logdet_lgcy_spd_gen[j, i], wall_time_lgcy_spd_gen[j, i], \
                proc_time_lgcy_spd_gen[j, i], flops_lgcy_spd_gen[j, i] = \
                legacy_method(
                        func, K, X_, sym_pos=True, X_orth=False,
                        use_blas=config['use_blas'])

            if config['func'] == 'logpdet':
                # Legacy method, symmetric positive-definite matrix K, X ort
                logdet_lgcy_spd_ort[j, i], wall_time_lgcy_spd_ort[j, i], \
                    proc_time_lgcy_spd_ort[j, i], flops_lgcy_spd_ort[j, i] = \
                    legacy_method(
                            func, K, X_, sym_pos=True, X_orth=True,
                            use_blas=config['use_blas'])

            # Projection method with generic matrix X_
            logdet_proj_gen[j, i], wall_time_proj_gen[j, i], \
                proc_time_proj_gen[j, i], flops_proj_gen[j, i] = \
                proj_method_gen(func, K, X_, use_blas=config['use_blas'])

            # Projection method with orthogonal matrix X_ (X_ is overwritten)
            logdet_proj_ort[j, i], wall_time_proj_ort_pre[j, i], \
                proc_time_proj_ort_pre[j, i], wall_time_proj_ort[j, i], \
                proc_time_proj_ort[j, i], flops_proj_ort[j, i] = \
                proj_method_ort(func, K, X_, use_blas=config['use_blas'])

        if config['verbose']:
            print(' Done.', flush=True)

    # loop over ratios (Comp method only, With Xp). Note this loop is
    # separated from Legacy and Proj methods as measuring process time
    # of these methods interfere.
    for j in range(ratios.size):

        # Size of columns of X
        m = int(n * ratios[j])
        if m == 0:
            m = 1
        elif m == n:
            m = n-1

        # Print progress
        if config['verbose']:
            if int(numpy.log10(ratios.size)) < 3:
                print('ratios: %2d/%d ' % (j+1, ratios.size), end='',
                      flush=True)
            elif int(numpy.log10(ratios.size)) == 3:
                print('ratios: %3d/%d ' % (j+1, ratios.size), end='',
                      flush=True)
            elif int(numpy.log10(ratios.size)) > 3:
                print('ratios: %4d/%d ' % (j+1, ratios.size), end='',
                      flush=True)

        # Repeat experiment
        for i in range(repeat):

            X_ = numpy.copy(X[:, :m])
            Xp = numpy.copy(X[:, m:])

            if config['verbose']:
                print('.', end='', flush=True)

            # Compression method with generic A, orthonormal X, Xp known
            logdet_comp_gen_ort_xp[j, i], wall_time_comp_gen_ort_xp[j, i], \
                proc_time_comp_gen_ort_xp[j, i], \
                flops_comp_gen_ort_xp[j, i] = \
                comp_method(func, K, X_, Xp, sym_pos=False, X_orth=True,
                            use_blas=config['use_blas'])

            # Compression method with SPD matrix A, orthonormal X, Xp known
            logdet_comp_spd_ort_xp[j, i], wall_time_comp_spd_ort_xp[j, i], \
                proc_time_comp_spd_ort_xp[j, i], \
                flops_comp_spd_ort_xp[j, i] = \
                comp_method(func, K, X_, Xp, sym_pos=True, X_orth=True,
                            use_blas=config['use_blas'])

        if config['verbose']:
            print(' Done.', flush=True)

    # loop over ratios (Comp method only, Without Xp). Note this loop is
    # separated from Legacy and Proj methods as measuring process time
    # of these methods interfere.
    for j in range(ratios.size):

        # Size of columns of X
        m = int(n * ratios[j])
        if m == 0:
            m = 1
        elif m == n:
            m = n-1

        # Print progress
        if config['verbose']:
            if int(numpy.log10(ratios.size)) < 3:
                print('ratios: %2d/%d ' % (j+1, ratios.size), end='',
                      flush=True)
            elif int(numpy.log10(ratios.size)) == 3:
                print('ratios: %3d/%d ' % (j+1, ratios.size), end='',
                      flush=True)
            elif int(numpy.log10(ratios.size)) > 3:
                print('ratios: %4d/%d ' % (j+1, ratios.size), end='',
                      flush=True)

        # Repeat experiment
        for i in range(repeat):

            X_ = numpy.copy(X[:, :m])
            Xp = numpy.copy(X[:, m:])

            if config['verbose']:
                print('.', end='', flush=True)

            # Compression method with generic A, generic X
            logdet_comp_gen_gen[j, i], wall_time_comp_gen_gen[j, i], \
                proc_time_comp_gen_gen[j, i], flops_comp_gen_gen[j, i] = \
                comp_method(func, K, X_, sym_pos=False, X_orth=False,
                            use_blas=config['use_blas'])

            # Compression method with SPD matrix A, generic X
            logdet_comp_spd_gen[j, i], wall_time_comp_spd_gen[j, i], \
                proc_time_comp_spd_gen[j, i], flops_comp_spd_gen[j, i] = \
                comp_method(func, K, X_, sym_pos=True, X_orth=False,
                            use_blas=config['use_blas'])

            # Compression method with generic A, orthonormal X
            logdet_comp_gen_ort[j, i], wall_time_comp_gen_ort[j, i], \
                proc_time_comp_gen_ort[j, i], flops_comp_gen_ort[j, i] = \
                comp_method(func, K, X_, sym_pos=False, X_orth=True,
                            use_blas=config['use_blas'])

            # Compression method with SPD matrix A, orthonormal X
            logdet_comp_spd_ort[j, i], wall_time_comp_spd_ort[j, i], \
                proc_time_comp_spd_ort[j, i], flops_comp_spd_ort[j, i] = \
                comp_method(func, K, X_, sym_pos=True, X_orth=True,
                            use_blas=config['use_blas'])

        if config['verbose']:
            print(' Done.', flush=True)

    # Convert number of instructions to number of flops
    inst_per_matmat = devices['instructions_per_matmat']
    flops_lgcy_gen_gen /= inst_per_matmat
    flops_lgcy_gen_ort /= inst_per_matmat
    flops_lgcy_spd_gen /= inst_per_matmat
    flops_lgcy_spd_ort /= inst_per_matmat
    flops_proj_gen /= inst_per_matmat
    flops_proj_ort_pre /= inst_per_matmat
    flops_proj_ort /= inst_per_matmat
    flops_comp_gen_gen /= inst_per_matmat
    flops_comp_spd_gen /= inst_per_matmat
    flops_comp_gen_ort /= inst_per_matmat
    flops_comp_spd_ort /= inst_per_matmat
    flops_comp_gen_ort_xp /= inst_per_matmat
    flops_comp_spd_ort_xp /= inst_per_matmat

    # Dictionary of results
    results = {
        'logdet_lgcy_gen_gen': logdet_lgcy_gen_gen,
        'logdet_lgcy_gen_ort': logdet_lgcy_gen_ort,
        'logdet_lgcy_spd_gen': logdet_lgcy_spd_gen,
        'logdet_lgcy_spd_ort': logdet_lgcy_spd_ort,
        'logdet_proj_gen': logdet_proj_gen,
        'logdet_proj_ort': logdet_proj_ort,
        'logdet_comp_gen_gen': logdet_comp_gen_gen,
        'logdet_comp_spd_gen': logdet_comp_spd_gen,
        'logdet_comp_gen_ort': logdet_comp_gen_ort,
        'logdet_comp_spd_ort': logdet_comp_spd_ort,
        'logdet_comp_gen_ort_xp': logdet_comp_gen_ort_xp,
        'logdet_comp_spd_ort_xp': logdet_comp_spd_ort_xp,
        'wall_time_lgcy_gen_gen': wall_time_lgcy_gen_gen,
        'wall_time_lgcy_gen_ort': wall_time_lgcy_gen_ort,
        'wall_time_lgcy_spd_gen': wall_time_lgcy_spd_gen,
        'wall_time_lgcy_spd_ort': wall_time_lgcy_spd_ort,
        'wall_time_proj_gen': wall_time_proj_gen,
        'wall_time_proj_ort_pre': wall_time_proj_ort_pre,
        'wall_time_proj_ort': wall_time_proj_ort,
        'wall_time_comp_gen_gen': wall_time_comp_gen_gen,
        'wall_time_comp_spd_gen': wall_time_comp_spd_gen,
        'wall_time_comp_gen_ort': wall_time_comp_gen_ort,
        'wall_time_comp_spd_ort': wall_time_comp_spd_ort,
        'wall_time_comp_gen_ort_xp': wall_time_comp_gen_ort_xp,
        'wall_time_comp_spd_ort_xp': wall_time_comp_spd_ort_xp,
        'proc_time_lgcy_gen_gen': proc_time_lgcy_gen_gen,
        'proc_time_lgcy_gen_ort': proc_time_lgcy_gen_ort,
        'proc_time_lgcy_spd_gen': proc_time_lgcy_spd_gen,
        'proc_time_lgcy_spd_ort': proc_time_lgcy_spd_ort,
        'proc_time_proj_gen': proc_time_proj_gen,
        'proc_time_proj_ort_pre': proc_time_proj_ort_pre,
        'proc_time_proj_ort': proc_time_proj_ort,
        'proc_time_comp_gen_gen': proc_time_comp_gen_gen,
        'proc_time_comp_spd_gen': proc_time_comp_spd_gen,
        'proc_time_comp_gen_ort': proc_time_comp_gen_ort,
        'proc_time_comp_spd_ort': proc_time_comp_spd_ort,
        'proc_time_comp_gen_ort_xp': proc_time_comp_gen_ort_xp,
        'proc_time_comp_spd_ort_xp': proc_time_comp_spd_ort_xp,
        'flops_lgcy_gen_gen': flops_lgcy_gen_gen,
        'flops_lgcy_gen_ort': flops_lgcy_gen_ort,
        'flops_lgcy_spd_gen': flops_lgcy_spd_gen,
        'flops_lgcy_spd_ort': flops_lgcy_spd_ort,
        'flops_proj_gen': flops_proj_gen,
        'flops_proj_ort_pre': flops_proj_ort_pre,
        'flops_proj_ort': flops_proj_ort,
        'flops_comp_gen_gen': flops_comp_gen_gen,
        'flops_comp_spd_gen': flops_comp_spd_gen,
        'flops_comp_gen_ort': flops_comp_gen_ort,
        'flops_comp_spd_ort': flops_comp_spd_ort,
        'flops_comp_gen_ort_xp': flops_comp_gen_ort_xp,
        'flops_comp_spd_ort_xp': flops_comp_spd_ort_xp,
    }

    # Store all results
    benchmark_results = {
        'detkit_config': detkit_config,
        'config': config,
        'devices': devices,
        'results': results
    }

    # Save results
    benchmark_dir = '..'
    pickle_dir = 'pickle_results'
    base_dir = join(benchmark_dir, pickle_dir)
    if not os.path.isdir(base_dir):
        base_dir = '.'
    log_n_str = str(int(numpy.log2(config['n'])))
    if detkit_config['use_symmetry']:
        gramian_status = 'gram'
    else:
        gramian_status = 'no-gram'
    output_filename = 'benchmark-' + arguments['func'] + '-' + log_n_str + \
                      '-' + gramian_status + '.pickle'
    output_full_filename = join(base_dir, output_filename)
    with open(output_full_filename, 'wb') as file:
        pickle.dump(benchmark_results, file,
                    protocol=pickle.HIGHEST_PROTOCOL)
    print('Results saved to %s.' % output_full_filename)


# ===========
# Script main
# ===========

if __name__ == "__main__":
    benchmark(sys.argv)
