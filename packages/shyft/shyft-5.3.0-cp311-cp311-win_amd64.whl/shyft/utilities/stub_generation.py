import inspect
import importlib
import logging
from mypy.stubgen import find_module_paths_using_imports
from pathlib import Path
import re
import sys
from typing import TextIO, Any, Optional, Dict, Tuple, List

logger = logging.getLogger(__name__)
doc_type_match = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]+:')


def _write_docs(o: TextIO, ii: str, docs: str):
    if docs is not None and docs != "":
        o.write(f'{ii}"""\n')
        doc_lines = docs.split('\n')
        for dl in doc_lines:
            o.write(f'{ii}{dl}\n')
        o.write(f'{ii}"""\n')


class BoostEnumInspect:
    """
    Class to extract from BoostEnum, information suitable for stubs
    """

    def __init__(self, c: Any):
        self.c = c

    @property
    def name(self) -> str:
        return self.c.__name__

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.name

    @property
    def doc(self) -> str:
        return inspect.getdoc(self.c)

    @property
    def enum_members(self) -> List[str]:
        return [v for v in self.c.names.keys()]

    def create_stub(self, o: TextIO, indent: int) -> None:
        i = ' '*indent*4
        ii = ' '*((indent + 1)*4)
        o.write(f'\n{i}class {self.name}(Enum):\n')
        _write_docs(o, ii, self.doc)
        for e in self.enum_members:
            o.write(f'{ii}{e}: int\n')
        o.write(f'\n')


def is_boost_enum(c: Any):
    """ returns true if c is a boost enum testing for the inheritance tree """
    mro = inspect.getmro(c)  # [ enumcls, bp.enum, int, class]
    return len(mro) > 3 and repr(mro[-3]).startswith("<class 'Boost.Python.enum'")


class BoostClassInspect:
    """
    Class to extract from BoostClass, information suitable for stubs
    """
    known_prop_types: Dict[str, str] = {
        '_ts.value': 'TimeSeries',
        '_time_axis.value': 'TimeAxis',
        '_t_xy_.value': 't_xy',
        '_t_xyz.value': 't_xyz',
        '_t_xyz_list.value': 't_xyz_list',
        '_turbine_description.value': 't_turbine_description',
        '_string.value': 'str',
        '_double.value': 'float',
        '_bool.value': 'bool',
        '_i64.value': 'int',
        '_i32.value': 'int',
        '_i16.value': 'int',
        '_i8.value': 'int',
        '_u16.value': 'int',
    }
    ops_included: set = {
        '__call__',
        '__abs__',
        '__round__',
        '__float__',
        '__int__',
        '__long__',
        # '__lt__',
        # '__le__',
        # '__gt__'
        # '__ge__',
        # '__eq__',
        # '__ne__',
        '__add__',
        '__radd__',
        '__sub__',
        '__rsub__',
        '__truediv__',
        '__rtruediv__',
        '__mod__',
        '__mul__',
        '__rmul__',
        '__neg__',
        '__floordiv__',
        '__rfloordiv__',
        '__or__',
        # list operations are needed
        '__getitem__',
        '__delitem__',
        '__setitem__',
        '__iter__',
        '__len__',
        '__contains__'
    }

    def __init__(self, c: Any):
        self.c = c

    @property
    def name(self) -> str:
        return self.c.__name__

    @property
    def module(self) -> str:
        return self.c.__module__

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.name

    @property
    def doc(self) -> str:
        return inspect.getdoc(self.c)

    @property
    def base_class(self) -> Any:
        mro = inspect.getmro(self.c)
        return mro[1] if not (repr(mro[1]).startswith("<class 'Boost.Python") or repr(mro[1]).startswith("<class 'object'")) else None

    @property
    def cls_props(self) -> List[Tuple[str, Any]]:
        return [(n, t.__class__.__name__) for n, t in inspect.getmembers(self.c, lambda o: not callable(o) and not inspect.ismethod(o) and not inspect.isbuiltin(o) and not isinstance(o, property)) if
                not n.startswith('__') and t.__class__.__name__ != 'class']
        # inspect does no have _static for some py installations: thus the below does not work
        # c_cls_props = inspect.getmembers_static(self.c, lambda o: isinstance(o, property) and repr(o).startswith("<Boost.Python.StaticProperty"))
        # return [(n, getattr(self.c, n).__class__.__name__) for n, _ in c_cls_props]

    @property
    def props(self) -> List[Tuple[str, Tuple[str, str], bool]]:
        def extract_type_doc(name: str, p: Any) -> Tuple[str, str]:
            """ name allow us to deduce/override type;doc for known properties"""
            doc = inspect.getdoc(p)
            p_type: str = self.known_prop_types.get(f'{self.name}.{name}', 'Any')
            if doc:  # and we use doc for properties to harvest the type, using doc like <type>: somedoc
                m = doc_type_match.match(doc)
                if m:
                    p_type = m[0][:-1]  # skip matched required : at the end
                    doc = doc[len(m[0]):]  # rip out the type from the doc string
            return p_type, doc

        c_props = inspect.getmembers(self.c, lambda o: isinstance(o, property))
        return [(n, extract_type_doc(n, p), p.fset is None) for n, p in c_props]

    @property
    def constructors(self) -> List[Tuple[str, Tuple[List[str], List[str]]]]:
        c_meth = inspect.getmembers(self.c, lambda o: callable(o) and o.__name__ == '__init__')
        return [(n, CStubGenerator.parse_boost_python_function(func_name=n, func=fx, cls_name=self.c.__name__, mod_path_replace=self.module + ".")) for n, fx in c_meth]

    @property
    def methods(self) -> List[Tuple[str, Tuple[List[str], List[str]]]]:
        c_meth = inspect.getmembers(self.c, lambda o: inspect.ismethoddescriptor(o) and ((o.__name__ in self.ops_included) or not o.__name__.startswith('__')))
        return [(n, CStubGenerator.parse_boost_python_function(func_name=n, func=fx, cls_name=self.c.__name__, mod_path_replace=self.module + ".")) for n, fx in c_meth if n != '__reduce__']

    @property
    def nested_classes(self) -> List["BoostClassInspect"]:
        c_nested_classes = [(n, o) for n, o in inspect.getmembers(self.c, inspect.isclass) if not n.startswith('__') and not is_boost_enum(o)]
        return [BoostClassInspect(t) for _, t in c_nested_classes if _ == t.__name__]

    @property
    def type_variables(self) -> List[Tuple[str, str]]:
        c_nested_classes = [(n, o) for n, o in inspect.getmembers(self.c, inspect.isclass) if not n.startswith('__') and not is_boost_enum(o)]
        return [(n, t.__name__) for n, t in c_nested_classes if n != t.__name__]  # type variables (usually) have variable name different from cls name, ref hydrology pt_gs_k

    @property
    def enums(self) -> List[BoostEnumInspect]:
        cls = inspect.getmembers(self.c, lambda o: inspect.isclass(o) and is_boost_enum(o))
        return [BoostEnumInspect(c) for _, c in cls]

    def create_stub(self, o: TextIO, indent: int) -> None:
        xi = ' '*indent*4
        xii = ' '*((indent + 1)*4)
        xiii = ' '*((indent + 2)*4)
        o.write(f'\n{xi}class {self.name}')
        if self.base_class:
            bc = self.base_class.__name__
            base_cls_name = bc if self.name != bc else f"core.{bc}"  # stm inherits from core, same name
            o.write(f'({base_cls_name})')
        o.write(':\n')
        _write_docs(o, xii, self.doc)

        for n, t in self.cls_props:  # roll out class properties name: type
            o.write(f'{xii}{n}: {t}\n')

        for e in self.enums:
            e.create_stub(o, indent)

        for nc in self.nested_classes:  # then nested classes
            nc.create_stub(o, indent + 1)

        for n, t in self.type_variables:  # type variables for the class
            o.write(f'{xii}{n}: {t}\n')

        for n, type_doc, read_only in self.props:  # properties
            t = type_doc[0]
            docs = type_doc[1]
            o.write(f'{xii}@property\n{xii}def {n}(self)->{t}:\n')
            _write_docs(o, xiii, docs)
            o.write(f'{xiii}...\n')
            if not read_only:
                o.write(f'{xii}@{n}.setter\n{xii}def {n}(self, value:{t})->None:\n')
                o.write(f'{xiii}...\n')

        for n, sig_doc_list in self.constructors:  # constructors
            # those ending with *Vector, usually(not always, but we aim at that..) also accepts list in the constructors
            n_sigs: int = len(sig_doc_list[0])
            if self.name.endswith("Vector") or self.name.endswith("List"):  # xxxList and xxxVector
                n_sigs += 1
                if n_sigs > 1:
                    o.write(f'{xii}@overload\n')
                o.write(f'{xii}def __init__(self, objects: List[Any]):\n')
                _write_docs(o, xiii, "Constructs a strongly typed list from a list of objects convertible to the list")
                o.write(f'{xiii}...\n')

            for sig, docs in zip(sig_doc_list[0], sig_doc_list[1]):
                if n_sigs > 1:
                    o.write(f'{xii}@overload\n')
                o.write(f'{xii}def {n}{sig}:\n')
                _write_docs(o, xiii, docs)
                o.write(f'{xiii}...\n')
            o.write(f'\n')

        for n, sig_doc_list in self.methods:  # methods
            for sig, docs in zip(sig_doc_list[0], sig_doc_list[1]):
                if n == 'get_item_old':
                    o.write(f'{xii}def __getitem__(self, ix: object) -> Any:\n')
                    _write_docs(o, xiii, "if ix is an int return the i-th object, if its a string, then return object with .id equal to the string")
                else:
                    if len(sig_doc_list[0]) > 1:
                        o.write(f'{xii}@overload\n')
                    if sig.startswith('()') or "self" not in sig:
                        o.write(f'{xii}@staticmethod\n')
                    o.write(f'{xii}def {n}{sig}:\n')
                    _write_docs(o, xiii, docs)
                o.write(f'{xiii}...\n')
            o.write(f'\n')
        o.write(f'\n')


class BoostModuleInspect:
    """
    Class to extract from a Boost module, information suitable for stubs
    """

    def __init__(self, c: Any):
        self.c: Any = c

    @property
    def name(self) -> str:
        return self.c.__name__

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return self.name

    @property
    def doc(self) -> str:
        return inspect.getdoc(self.c)

    @property
    def functions(self) -> List[Tuple[str, Tuple[List[str], List[str]]]]:
        c_funcs = inspect.getmembers(self.c, lambda o: callable(o) and not inspect.isclass(o) and repr(o).startswith("<Boost.Python.function"))
        return [(n, CStubGenerator.parse_boost_python_function(func_name=n, func=fx, cls_name=self.c.__name__, mod_path_replace=self.name + ".")) for n, fx in c_funcs]

    @property
    def classes(self) -> List[BoostClassInspect]:
        cls = inspect.getmembers(self.c, lambda o: inspect.isclass(o) and not is_boost_enum(o))
        return [BoostClassInspect(c) for _, c in cls]

    @property
    def enums(self) -> List[BoostEnumInspect]:
        cls = inspect.getmembers(self.c, lambda o: inspect.isclass(o) and is_boost_enum(o))
        return [BoostEnumInspect(c) for _, c in cls]

    @property
    def variables(self) -> List[Tuple[str, str]]:
        mvars = inspect.getmembers(self.c, lambda o: not inspect.isclass(o) and not callable(o))
        return [(n, t.__class__.__name__) for n, t in mvars if not n.startswith('__')]

    def create_stub(self, o: TextIO, indent: int) -> None:
        xi = ' '*indent*4
        xii = ' '*((indent + 1)*4)
        #  xiii = ' '*((indent + 2)*4)

        for e in self.enums:
            e.create_stub(o, indent)

        for cls in self.classes:
            cls.create_stub(o, indent)

        for n, t in self.variables:
            o.write(f'{xi}{n}: {t}\n')

        for n, sig_doc_list in self.functions:  # methods
            for sig, docs in zip(sig_doc_list[0], sig_doc_list[1]):
                if len(sig_doc_list[0]) > 1:
                    o.write(f'{xi}@overload\n')
                o.write(f'{xi}def {n}{sig}:\n')
                _write_docs(o, xii, docs)
                o.write(f'{xii}...\n')
            o.write(f'\n')


_utc_not_valid: str = "[not-valid-period>"
_time_zero: str = "time(0)"


class CStubGenerator:
    dunder_methods_included = ["__init__"]
    our_ignored_dunders = ["__package__", "__spec__", "__name__", "__loader__", "__file__", "__doc__", "__cached__",
                           "__builtins__", "__class__", "__delattr__", "__dict__"]
    math_operators: set = {
        '__abs__',
        '__add__',
        '__radd__',
        '__sub__',
        '__rsub__',
        '__truediv__',
        '__rtruediv__',
        '__mod__',
        '__mul__',
        '__rmul__',
        '__neg__',
        '__floordiv__',
        '__rfloordiv__'
    }
    # some signatures take objects in c++, so we need to help stub generation with 'known' signatures
    known_signatures: Dict[str, Tuple[str, str]] = {
        'Calendar.diff_units': ('self, t1:time, t2:time, delta_t:time', 'int'),
        'Calendar.add': ('self, t:time, delta_t:time, n:int', 'time'),
        'Calendar.calendar_units': ('t:time', 'YMDhms'),
        'Calendar.calendar_week_units': ('t:time', 'YWdhms'),
        # 'Calendar.to_string':('utctime:time','str'), needs more work to support overloaded specified/mixed signatures
        'Calendar.trim': ('t:time, delta_t:time', 'time'),
        'StmCase.__init__': ('self, id: int, name:str, create:time,json:str="", labels:StringVector=StringVector(),model_refs:ModelRefList=ModelRefList()', 'None'),
        'Reservoir.output_to': ('self, other: Waterway, role: ConnectionRole = ConnectionRole.main', 'Reservoir'),
        'StmTask.__init__': (
            'self, id: int, name: str, created: time, json: str = "", labels: StringVector =StringVector() , cases: StmCaseVector = StmCaseVector(), base_model: StmModelRef = StmModelRef(), task_name: str = ""', 'None'),
        # time needs some care as it accepts time, int/float or well defined iso like string for operators.
        'time.__add__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__radd__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__sub__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__rsub__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__truediv__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__rtruediv__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__mod__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__mul__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__rmul__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__neg__': ('self', 'time'),
        'time.__floordiv__': ('self,other: Union[time,float,int,str]', 'time'),
        'time.__rfloordiv__': ('self,other: Union[time,float,int,str]', 'time')
    }

    @staticmethod
    def is_boost_py_func(obj) -> bool:
        return "Boost.Python.function" in str(type(obj))

    @staticmethod
    def parse_boost_python_function(func_name: str, func: Any, cls_name: Optional[str] = None, mod_path_replace: Optional[str] = None) -> tuple[list[str], list[str]]:
        """ Get signature (with defaults and annotations) and documentation from a boost python function

        Examples: 
            - input : 'time( (Calendar)self, (int)Y [, (int)M=1 [, (int)D=1 ]]) -> time :'
            - goal : '(self, Y: int, M: int = 1, D: int = 1) -> time'
            
            - input: 'full_range() -> TimeAxisFixedDeltaT :'
            - goal: () -> TimeAxisFixedDeltaT
            
            - input: 'derivative( (TimeSeries)self [, (derivative_method)method=shyft.time_series._time_series.derivative_method.DEFAULT]) -> TimeSeries :'
            - goal: '(self, method: derivative_method = shyft.time_series._time_series.derivative_method.DEFAULT) -> TimeSeries'

        Returns:
            overload_sigs: List of signatures for each overload
            overload_docs: List of doc strings for each overload
        """

        docs = inspect.getdoc(func)
        if cls_name is not None and f'{cls_name}.{func_name}' in CStubGenerator.known_signatures:
            sig, return_type = CStubGenerator.known_signatures[f'{cls_name}.{func_name}']
            if func_name == "__init__":  # hack again, for StmCase
                docs = f"Construct {cls_name}"
                skip = 0
            else:
                skip = docs.find(") :\n")  # get rid of any signature since we provide the *one* needed
                if skip > 0:
                    skip = skip + 4
                else:
                    skip = 0
            return [f'({sig}) -> {return_type}'], [docs[skip:]]
        else:
            sig = "self, *args, **kwargs" if cls_name is not None else "*args, **kwargs"  # fallback

        if docs is None:
            return [f"({sig})"], [""]
        docs = docs.split("\n")

        overloads = []  # example: TsVector.percentiles
        overline_lines = []
        re_signature = re.compile(rf"{func_name}\(.*\) -> [\w]*")
        for line in docs:
            if re_signature.match(line):
                if len(overline_lines) > 0:
                    overloads.append(overline_lines)
                overline_lines = []
            overline_lines.append(line)
        overloads.append(overline_lines)

        overload_sigs = []
        overload_docs = []
        for overline_lines in overloads:
            signature_line = overline_lines[0]

            if len(overline_lines) > 1:
                overline_lines[1] = overline_lines[1].lstrip(" ")
            docs = "\n".join(overline_lines[1:])
            overload_docs.append(docs)

            if not signature_line.startswith(func_name):
                overload_sigs.append("(*args, **kwargs)")
                continue

            start, return_type = signature_line.split("->")
            # remove function name and brackets on start
            if start.startswith(func_name):
                start = start[len(func_name):]
                start = start.strip(" ")[1:-1].strip(" ")

            # treat special default value: [not-valid-period>, time(0)
            start = start.replace(_utc_not_valid, "_utc_not_valid")
            start = start.replace(_time_zero, "_time_zero")

            # replace "(int)var_name" -> "varname: int"
            start = re.sub(r"\((\w*)\)(\w*)", r"\2: \1", start)

            # replace square brackets indicating defaults
            start = re.sub(r"[\[\]]", "", start)
            # add space around "=" for defaults
            start = re.sub(r"=", " = ", start)
            # no typing hint for self
            start = re.sub(r"self: \w*", "self", start)
            # and arg1 usually also self, for ct
            # if func_name.startswith('__init__'):
            start = re.sub(r"arg1: \w*", "self", start)

            # default can look like this
            # cfg: DtssCfg = <shyft.time_series._time_series.DtssCfg object at 0x7fa91a0805e0>
            start = re.sub(r"<([\w\.-_]*)\s[^>]*>", r"\1", start)

            start = start.replace("_utc_not_valid", f'"{_utc_not_valid}"')
            start = start.replace("_time_zero", f'"{_time_zero}"')
            start = start.replace("18446744073709551615", "npos")
            if mod_path_replace is not None:
                start = start.replace(mod_path_replace, "")
            start = start.replace(" ,", ",").strip(" ")
            start = start.replace(": list.", ": list")  # tweak for list type of ct.
            start = start.replace('= shyft.energy_market.core._core.', '= ')  # hack for stm that refs to core on default args.
            start = start.replace('= shyft.hydrology._api.', '= ')  # hack for hydrology that refs default args.
            # hack for DoubleVector that is Unit[DoubleVector,list[float]]
            start = start.replace(': DoubleVector', ': Union[DoubleVector,list[float],np.ndarray]')
            start = start.replace(': UtcTimeVector', ': Union[UtcTimeVector,list[time],list[float],np.ndarray]')
            start = start.replace(': StringVector', ': Union[StringVector,list[str]]')
            start = start.replace(': IntVector', ': Union[IntVector,list[int],range]')
            start = start.replace(': XyPointCurveWithZList', ': Union[XyPointCurveWithZList,list[XyPointCurveWithZ]]')
            start = start.replace(': time', ': Union[time,float,int]')
            return_type = return_type.rstrip(": ").lstrip(" ")
            if return_type == "object":
                if cls_name in {"time", "TimeSeries", "TsVector"} and func_name.startswith('__') and func_name in CStubGenerator.math_operators:
                    return_type = cls_name
                else:
                    return_type = "Any"

            overload_sigs.append(f"({start}) -> {return_type}")

        return overload_sigs, overload_docs

    @staticmethod
    def stubs_per_module(o: TextIO, module):
        """ Common/adapted entry for the different modules """
        o.write(f'"""This file is auto-generated with {Path(__file__).name}"""\n')
        o.write("from typing import List,Any,overload,Callable,Union\n")
        o.write("from enum import Enum\n")
        o.write("import numpy as np")
        if module.__name__ != 'shyft.time_series._time_series':  # those needs imports helpers.
            o.write('from shyft.time_series._time_series import *\n')
        if module.__name__ == 'shyft.energy_market.stm._stm':
            o.write(
                'from shyft.energy_market.core._core import StringTimeSeriesDict,GateList,CatchmentList,ModelArea,HydroComponent,HydroComponentList,ConnectionRole,TurbineDescription,'
                'XyPointCurve,XyPointCurveWithZ,XyPointCurveWithZList\n')
            o.write('from shyft.energy_market.core import _core as core\n')
        if module.__name__.startswith('shyft.hydrology.') and module.__name__ != 'shyft.hydrology._api':
            o.write('from shyft.hydrology._api import *\n')  # common for all hydrology modules
        if module.__name__ == 'shyft.energy_market.stm.shop._shop':
            o.write('from shyft.energy_market.stm._stm import StmSystem, LogEntryList\n')
        o.write("# import Boost.Python\n")
        o.write("nan = float('nan')\n")
        sg = BoostModuleInspect(module)
        sg.create_stub(o=o, indent=0)


if __name__ == "__main__":
    """Generate type stubs for c modules. 

    Alternatives:
    - mypy's stubgen: Currently does not include docs and does not analyse signatues 
    """
    file_path = Path(__file__).parent
    shyft_python_folder = file_path.parents[1]
    sys.path.insert(0, str(shyft_python_folder.resolve()))  # explicitly use same shyft version

    packages = ["shyft.time_series", "shyft.energy_market", "shyft.hydrology"]

    _, c_modules = find_module_paths_using_imports(
        [], packages, verbose=False, quiet=False)

    # c modules
    for stub_source in c_modules:
        lib = importlib.import_module(stub_source.module)
        mod_split = stub_source.module.split(".")
        fn = shyft_python_folder.joinpath(*mod_split[:-1])/f"{mod_split[-1]}.pyi"
        fn.parent.mkdir(exist_ok=True, parents=True)
        with fn.open('w') as f:
            logger.info(f"Writing to {fn}")
            CStubGenerator.stubs_per_module(f, lib)
