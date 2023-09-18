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

import time


# =====
# Timer
# =====

class Timer(object):
    """
    Measures elapsed wall time and elapsed process time.
    """

    # ====
    # init
    # ====

    def __init__(self):
        """
        Initializes the attributes.
        """

        self.init_wall_time = 0.0
        self.init_proc_time = 0.0
        self.wall_time = 0.0
        self.proc_time = 0.0

    # =====
    # reset
    # =====

    def reset(self):
        """
        Resets the timer for reuse.
        """

        self.init_wall_time = 0.0
        self.init_proc_time = 0.0
        self.wall_time = 0.0
        self.proc_time = 0.0

    # ===
    # tic
    # ===

    def tic(self):
        """
        Starts measuring time.
        """

        self.init_wall_time = time.time()
        self.init_proc_time = time.process_time()

    # ===
    # toc
    # ===

    def toc(self):
        """
        Stops measuring time.
        """

        self.wall_time = time.time() - self.init_wall_time
        self.proc_time = time.process_time() - self.init_proc_time

    # =====
    # print
    # =====

    def print(self):
        """
        Prints both wall and process time.
        """

        print('wall time: %0.3e, proc time: %0.3e'
              % (self.wall_time, self.proc_time))
