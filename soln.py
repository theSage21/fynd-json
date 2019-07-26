import json
import os

# These "classes" are available as JSON
available = [a.rstrip(".json") for a in os.listdir(".")]


def make_annotation(arg):
    # we could evaluate annotation strings to classes?
    assert isinstance(arg["annotation"], str), f"{arg} annotations can only be strings"
    anno = arg["annotation"]
    # we don't dump this since we want an actual annotation eval for now
    # maybe later we can have complex types
    return anno


def check_arg(arg, kind):
    assert isinstance(arg["name"], str), f"{arg} has to be of type string"
    if kind == "kwargs":
        assert (
            "default" in arg
            or arg["name"] == "**kwargs"
            or arg["name"] == "*args"
            or arg["name"] == "self"
        ), f"{arg['name']} must have a default since it's present in kwargs"


def make_function(name, dkt, indent="  "):
    """
    Builds a function object given it's name and dictionary spec.
    """
    # function header
    # ============================================
    code = f"def {name}("
    arg_s = []  # argument string
    args, kwargs = dkt.get("args", []), dkt.get("kwargs", [])
    for kind, args in zip(
        ["args", "split", "kwargs"],
        [args, [{"name": "*"}] if len(args) > 0 and len(kwargs) > 0 else [], kwargs],
    ):
        for arg in args:
            check_arg(arg, kind)
            s = arg["name"].strip()
            if "annotation" in arg:
                s += f":{make_annotation(arg)}"
            if "default" in arg:
                default = json.dumps(arg["default"])
                s += f" = {default}"
            arg_s.append(s)
    code += ", ".join(arg_s)
    code += f") -> {dkt.get('return', None)}:\n"
    # ============================================
    body = indent + dkt["body"].replace("\n", "\n" + indent).strip()
    # Maybe TODO: fix \n within string becoming indents
    code += body
    return code


def ensure_bases(bases):
    assert isinstance(bases, (tuple, list))
    assert all([isinstance(base, str) for base in bases]), "all bases must be strings"
    base_classes = {}
    for base in bases:
        if base in available:
            base_classes[base] = read_class(base)
    bases = tuple([base_classes[base] for base in bases])
    return bases


def read_class(name):
    "Reads a spec with the given name and generates a class object for it"
    assert os.path.exists(
        f"{name}.json"
    ), f"{name}.json is not in the current directory"
    with open(f"{name}.json", "r") as fl:
        klass = json.loads(fl.read())
    bases = ensure_bases(klass.get("bases", []))
    nsp = klass["namespace"]
    functions = {
        name: make_function(name, dkt)  # str
        for name, dkt in nsp.items()
        if dkt["type"] == "method"
    }
    attributes = {
        name: attr["value"] for name, attr in nsp.items() if attr["type"] == "attribute"
    }
    nsp = {
        **attributes,
        **functions,
        "__doc__": klass.get("docstring", ""),
        "__annotations__": {
            name: eval(make_annotation(attr))
            for name, attr in nsp.items()
            if (attr["type"] == "attribute") and ("annotation" in attr)
        },
    }
    # make the class
    # this is required here so that super can work. Class instance is required
    # while generating AST for function body
    klass = type(name, bases, nsp)
    for fn, body in functions.items():
        scope = {name: klass}
        exec(body, scope)
        setattr(klass, fn, scope[fn])
    return klass


if __name__ == "__main__":
    import sys

    # mini test suite
    name = sys.argv[1].rstrip(".json")
    klass = read_class(name)
    print(klass)
    print(klass.__dict__)
    print(klass.__annotations__)
    print(klass.sold_units)
    fz = klass(cc=150)
    print(fz)
