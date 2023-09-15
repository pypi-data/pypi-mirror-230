# -*- coding: utf-8 -*-
"""some basic helper functions
Author  : NextPCG
"""

import inspect


def get_fun_name():
    return inspect.stack()[1][3]

