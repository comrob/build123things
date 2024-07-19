#!/usr/bin/env python3

from abc import ABCMeta
import argparse
from typing import Callable, Any, Dict, NoReturn, Set
import build123d as bd
from colored import Fore, Style
import build123things
from pprint import pformat, pprint
import copy
from random import choices
import string
from pathlib import Path
import inspect

DEBUG:Set[str] = set()
#DEBUG.add("memoize")
MEMOIZATION_CACHE = dict()

def random_tmp_fname(ext:str, where:str="/tmp/", k:int=10, alphabet:str=string.ascii_uppercase + string.digits):
    return where + ''.join(choices(alphabet, k=10)) + ext

def memoize(fnc_orig:Callable):
    # TODO: Replace with functools.cache? It would require all objects hashable, which I do not thing is going to happen.
    # If so, then import as memoize for compatibility. Or maybe combine hash if possible with repr or id by default.
    def memoized(*args, **kwargs):
        #signature = tuple([a.__hash__() for a in args] + [a.__hash__() for a in kwargs.keys()] + [a.__hash__() for a in kwargs.values()]).__hash__()
        signature = str(args) + str(kwargs)
        if signature not in MEMOIZATION_CACHE:
            MEMOIZATION_CACHE[signature] = fnc_orig(*args, **kwargs)
            fire = True
        else:
            fire = False
        ret = MEMOIZATION_CACHE[signature]
        if "memoize" in DEBUG:
            if not fire:
                #print(f"{Fore.light_green}{Style.bold}MEMOIZATION RETRIEVED CACHED value {Fore.cyan} {repr(ret)}{Style.reset}. Fnc. signature: ", signature)
                print(f"{Fore.light_green}{Style.bold}MEMOIZATION RETRIEVED CACHED value {Fore.cyan} {repr(ret)}{Style.reset}.")
                try:
                    code_context = inspect.stack()[1].code_context[0].strip()[:100] # type: ignore
                except:
                    code_context = "<code context not available>"
                print(f" {Fore.rgb(100,100,100)}\\_> ...{inspect.stack()[1].filename[-20:]}:{inspect.stack()[1].lineno}   {code_context}{Style.reset}")
            else:
                #print(f"{Fore.light_red}{Style.bold}MEMOIZATION FAILED. Fnc. signature: {Style.reset}", signature)
                print(f"{Fore.light_red}{Style.bold}MEMOIZATION FAILED.")
                #print(f" ... Available signatures: ")
                #pprint(cache)
                try:
                    code_context = inspect.stack()[1].code_context[0].strip()[:100] # type: ignore
                except:
                    code_context = "<code context not available>"
                print(f" {Fore.rgb(100,100,100)}\\_> ...{inspect.stack()[1].filename[-20:]}:{inspect.stack()[1].lineno}   {code_context}{Style.reset}")
        return ret
    return memoized

def neighbourhood_4_main():
    for i in ((1,0),(-1,0),(0,1),(0,-1)):
        yield i

def neighbourhood_4_diag():
    for i in ((1,1),(-1,1),(1,-1),(-1,-1)):
        yield i

def neighbourhood_8():
    for g in (neighbourhood_4_diag() , neighbourhood_4_main()):
        for i in g:
            yield i

class CQEditAwareArgumentParser(argparse.ArgumentParser):
    def error(self, msg):
        if not "show_object" in globals().keys():
            raise SystemExit(msg)

def is_in_cq_editor() -> bool:
    return Path(inspect.stack()[-1].filename).stem == "cq-editor"
