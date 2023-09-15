# -*- coding: utf-8 -*-
"""metaclass for general purpose
Author  : NextPCG
"""

import weakref

'''
Singleton
'''


class Singleton(type):
    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
            return cls.__instance
        else:
            return cls.__instance


'''
Cached
'''


class CachedMeta(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__cache = weakref.WeakValueDictionary()

    def __call__(cls, *args):
        if args in cls.__cache:
            return cls.__cache[args]
        else:
            obj = super().__call__(*args)
            cls.__cache[args] = obj
            return obj
