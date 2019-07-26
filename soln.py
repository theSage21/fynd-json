import json
import os

# These "classes" are available as JSON
available = [a.rstrip(".json") for a in os.listdir(".")]


def make_function(name, dkt, indent="  "):
    """
    Builds a function object given it's name and dictionary spec.
    """
    # function header
    code = f"def {name}("
    arg_s = []  # argument string
    args, kwargs = dkt.get("args", []), dkt.get("kwargs", [])
    for kind, args in zip(
        ["args", "split", "kwargs"],
        [args, [{"name": "*"}] if len(args) > 0 and len(kwargs) > 0 else [], kwargs],
    ):
        for arg in args:
            assert isinstance(arg["name"], str), f"{arg} has to be of type string"
            s = arg["name"].strip()
            if "annotation" in arg:
                # we could evaluate annotation strings to classes?
                assert isinstance(
                    arg["annotation"], str
                ), f"{arg} annotations can only be strings"
                anno = arg[
                    "annotation"
                ]  # we don't dump this since we want an actual annotation eval
                s += f":{anno}"
            if kind == "kwargs":
                assert (
                    "default" in arg
                    or arg["name"] == "**kwargs"
                    or arg["name"] == "*args"
                    or arg["name"] == "self"
                ), f"{arg['name']} must have a default since it's present in kwargs"
            if "default" in arg:
                default = json.dumps(arg["default"])
                s += f" = {default}"
            arg_s.append(s)
    code += ", ".join(arg_s)
    code += "):\n"
    # fill out the body of the function
    body = indent + dkt["body"].replace("\n", "\n" + indent).strip()
    # Maybe TODO: fix \n within string becoming indents
    code += body
    return code


def read_class(name):
    "Reads a spec with the given name and generates a class object for it"
    assert os.path.exists(
        f"{name}.json"
    ), f"{name}.json is not in the current directory"
    with open(f"{name}.json", "r") as fl:
        klass = json.loads(fl.read())
    # recursively go and get base classes
    bases = klass.get("bases", [])
    assert isinstance(bases, (tuple, list))
    assert all([isinstance(base, str) for base in bases]), "all bases must be strings"
    base_classes = {}
    for base in bases:
        if base in available:
            base_classes[base] = read_class(base)
    bases = tuple([base_classes[base] for base in bases])
    # fill up the variables, methods etc defined
    nsp = klass["namespace"]
    functions = {
        name: make_function(name, dkt)
        for name, dkt in nsp.items()
        if dkt["type"] == "method"
    }
    attributes = {
        name: attr["value"] for name, attr in nsp.items() if attr["type"] == "attribute"
    }
    nsp = {**attributes, **functions, "__doc__": klass.get("docstring", "")}
    # make the class
    # this is required here so that super can work. Class instance is required
    # while generating AST for function body
    klass = type(name, bases, nsp)
    for fn, body in functions.items():
        scope = {name: klass}
        print(body)
        exec(body, scope)
        setattr(klass, fn, scope[fn])
    return klass


if __name__ == "__main__":
    import sys

    name = sys.argv[1].rstrip(".json")
    klass = read_class(name)
    print("Generated class is")
    print(klass)
    print("Attributes are")
    print(klass.__dict__)
    print(klass.sold_units)
    fz = klass(cc=150)
    print("an instance of this class is")
    print(fz)
