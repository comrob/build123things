"""
Implements exporting a Thing to MuJoCo file format.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any
import build123d as bd
import colored
from build123things import Thing, TransformResolver
from xml.etree.ElementTree import Element, ElementTree
import xml.etree.ElementTree
from functools import singledispatch
from build123things.joints import Revolute, Rigid

def fmt_scale(how:float):
    def fmt_inner(what:float):
        return f"{what * how:.4f}"
    return fmt_inner

@singledispatch
def fmt (sth:Any) -> str:
    return str(sth)

@fmt.register
def _ (x:float) -> str:
    return f"{x:.4f}"

NAMESPACE_SEPARATOR = ":"

HACK_MINIMAL_INERTIA = "0.00001"

def export(thing:Thing, target_dir:Path):
    """ """

    thing_instance_counter:dict[int,int] = defaultdict(int)
    """ Lookup of already encountered Things; each Thing retains a count of how many times it is inthe design. """

    @singledispatch
    def process(joint:Any, name:str) -> None:
        raise NotImplementedError(f"Exporting type {type(joint)} to MJCF is not supported.")

    @process.register
    def _(thing:Thing) -> None:

        if id(thing) in thing_instance_counter:
            return
        else:
            thing_instance_counter[id(thing)] += 1

        # Start with exporting the mesh.
        mesh_name = thing.codename()
        res = thing.result()
        stl_file = target_dir / (mesh_name + ".stl")
        stl_file.parent.mkdir(exist_ok=True, parents=True)
        if res is not None:
            res.export_stl(str(stl_file))
        for mounted_as, transform_resolver in thing.enumerate_assembly():
            process(transform_resolver._wrapped)

    process(thing)

if __name__ == "__main__":
    import argparse
    import importlib
    from datetime import datetime

    argp = argparse.ArgumentParser(description="Export a Thing to ")
    argp.add_argument("module", help="Identify the module containing the thing.")
    argp.add_argument("thing", help="Identify the thing in the module.")
    argp.add_argument("--param-file", "-p", default=None, type=Path, help="Yaml file containing args and kwargs to pass to thing constructor. Expects two documents (separated by ---) in the file, the first with array (args) and the second with dict (kwargs).")
    argp.add_argument("--target-dir", "-d", default=None, type=Path, help="Target directory.")
    args = argp.parse_args()

    pymod = importlib.import_module(args.module)
    thing_cls = getattr(pymod, args.thing)
    if args.param_file is None:
        thing:Thing = thing_cls()
    else:
        raise NotImplementedError("TODO: Parse the yaml and instantiate.")

    if args.target_dir is None:
        target_dir:Path = Path.cwd() / "build" / (datetime.now().isoformat()[:19].replace(":","-") + "-" + thing.codename())
    else:
        target_dir:Path = args.target_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    export(thing, target_dir)
