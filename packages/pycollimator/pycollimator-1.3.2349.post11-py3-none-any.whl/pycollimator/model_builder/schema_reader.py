import glob
import json
import os


INPUTS = "inputs"
OUTPUTS = "outputs"

_schemas_path = os.path.join(os.path.dirname(__file__), "schemas")
if not os.path.exists(_schemas_path):
    # path used when running from bazel
    _schemas_path = os.path.join("src", "lib", "model-schemas", "schemas")


def _param(p):
    name = p["name"]
    v = p["default_value"]
    t = p["data_type"]
    if t == "float":
        v = float(v)
    elif t == "int":
        v = int(v)
    elif t == "bool":
        v = str(v).lower()
        if v == "true":
            v = True
        elif v == "false":
            v = False
        else:
            raise TypeError(f"unknown bool value {v} for {name}")
    elif t == "stringlist":
        v = eval(v)
    elif t in ("array1df", "array1di", "array2df", "array2di"):
        v = eval(v)
    elif t == "string":
        pass
    elif t == "any":
        pass
    else:
        raise TypeError(f"unknown param type {t} for {name}")
    return (name, v)


def _json_get(json, *keys):
    for k in keys:
        json = json.get(k, {})
    return json


def _param_doc(param_def: dict) -> str:
    allowed_values = None
    default_value = param_def["default_value"]
    data_type = param_def["data_type"]
    if data_type == "string":
        default_value = (
            default_value.replace("`", "\\`").replace("\n", "\\n").replace('"', '\\"')
        )
        default_value = f"'{default_value}'"
        allowed_values = param_def.get("allowed_values", None)
        if allowed_values is None or len(allowed_values) == 0:
            allowed_values = None

    doc = "{"
    doc += data_type
    doc += f", default={default_value}"
    if allowed_values is not None:
        doc += f", allowed_values={allowed_values}"
    doc += f", description='{param_def['description']}'"
    doc += "}"
    return doc


class Schema:
    def __init__(self, json):
        self.json = json
        self.name = json["base"]["name"]
        self.namespace = json["base"]["namespace"]
        self.help_url = json["base"]["help_url"] if "help_url" in json["base"] else None
        self.fullname = f"{self.namespace}.{self.name}"
        param_defs = json.get("parameter_definitions", [])

        self.parameter_definitions = {p["name"]: p for p in param_defs}
        self.default_params = dict(_param(p) for p in param_defs)

        self.default_input_names = None
        self.default_output_names = None

    def __repr__(self) -> str:
        return (
            f"{self.name}: in={self.port_names('inputs')} "
            f"out={self.port_names('outputs')} "
            f"parameters={self.default_params}"
        )

    def doc(self, only_name=False, with_description=True) -> str:
        if only_name:
            return self.fullname

        inputs = list(self.port_names("inputs"))
        outputs = list(self.port_names("outputs"))
        doc = f"{self.fullname}("
        for name, param_def in self.parameter_definitions.items():
            doc += name + "=" + _param_doc(param_def) + ", "
        doc += f"inputs={inputs}, outputs={outputs}"
        if with_description:
            description: str = self.json["base"].get("description", "")
            description = description.replace("\n", " ")
            doc += f', description="{description}"'
        if self.help_url:
            doc += f', help_url="{self.help_url}"'
        doc += ")"
        return doc

    def md_doc(self, show_self_help_url=False) -> str:
        inputs = list(self.port_names("inputs"))
        outputs = list(self.port_names("outputs"))
        params = []

        dyn_in_port = self.has_dynamic_input_ports and self.name not in (
            "Adder",
            "Product",
        )
        dyn_out_port = self.has_dynamic_output_ports and self.name not in (
            "Adder",
            "Product",
        )

        for name, param_def in self.parameter_definitions.items():
            data_type = param_def["data_type"]
            default_value = param_def["default_value"]
            if default_value != "":
                if data_type == "string":
                    default_value = (
                        default_value.replace("`", "\\`")
                        .replace("\n", "\\n")
                        .replace('"', '\\"')
                    )
                    default_value = f"'{default_value}'"
                params.append(f"{name}: {data_type} = {default_value}")
            else:
                params.append(f"{name}: {data_type}")

        if dyn_in_port:
            params.append(f"input_names: list[str] = {inputs}")
        if dyn_out_port:
            params.append(f"output_names: list[str] = {outputs}")
        doc = f"### {self.fullname[5:]}({', '.join(params)})\n\n"
        description: str = self.json["base"].get("description", "")
        description = description.replace("\n", " ")
        doc += f"Description: {description}\n"
        if self.parameter_definitions:
            doc += "\nParameters:\n"
            for name, param_def in self.parameter_definitions.items():
                doc += f"* `{name}`: {_param_doc(param_def)}\n"
        if dyn_in_port:
            doc += f"* `input_names`: list of input port names. Default; {inputs}\n"
        if dyn_out_port:
            doc += f"* `output_names`: list of output port names. Default: {outputs}\n"

        doc += "\n"
        if not dyn_in_port:
            doc += f"Input port names: {inputs}\n"
        if not dyn_out_port:
            doc += f"Output port names: {outputs}\n"

        if self.help_url and show_self_help_url:
            doc += f"Help: {self.help_url}\n"
        return doc

    @property
    def has_dynamic_input_ports(self):
        has_dyn_ports = bool(self.ports("inputs", "dynamic"))
        has_auto_ports = self.json.get("ports").get("has_automatic_ports", False)
        return has_dyn_ports or has_auto_ports

    @property
    def has_dynamic_output_ports(self):
        has_dyn_ports = bool(self.ports("outputs", "dynamic"))
        has_auto_ports = self.json.get("ports").get("has_automatic_ports", False)
        return has_dyn_ports or has_auto_ports

    def port_names(self, inout, *, n_dyn=None):
        return (
            self.port_names_of_kind(inout, "static")
            + self.port_names_of_kind(inout, "conditional")
            + self.port_names_of_kind(inout, "dynamic", n_dyn)
        )

    def port_names_of_kind(self, inout, kind, n_dyn=0):
        ports = self.ports(inout, kind)
        if kind == "dynamic":
            if not ports:
                return ()
            prefix = "in" if inout == "inputs" else "out"
            if n_dyn is None:
                n_dyn = ports.get("default_count", 0)
            return tuple(f"{prefix}_{i}" for i in range(n_dyn))
        else:
            return tuple(p["name"] for p in ports)

    def ports(self, inout, kind):
        if inout not in ("inputs", "outputs"):
            raise KeyError(f"ports must be inputs or outputs; got {inout}")
        return self.json.get("ports", {}).get(inout, {}).get(kind, [])

    def primary_input_port(self):
        ps = self.ports("inputs", "static")
        if len(ps) == 1:
            return ps[0]["name"]
        return None

    def primary_output_port(self):
        ps = self.ports("outputs", "static")
        if len(ps) == 1:
            return ps[0]["name"]
        return None

    def port_kind(self, inout, portname):
        if portname in self.ports(inout, "static"):
            return "static"
        if portname in self.ports(inout, "conditional"):
            return "conditional"
        else:
            return "dynamic"

    def _get(self, *keys):
        return _json_get(self.json, *keys)


def load_schema(path):
    with open(path) as f:
        return Schema(json.load(f))


def load_schemas(namespace):
    root_dir = f"{_schemas_path}/blocks/{namespace}"
    for name in sorted(glob.glob(f"{root_dir}/*.json")):
        yield load_schema(f"{name}")


DOCS_WHITELIST = [
    "Abs",
    "Adder",
    # "BatteryCell",
    # "CFunction",
    "Chirp",
    "Clock",
    "Comparator",
    "Constant",
    # "CoordinateRotation",
    # "CoordinateRotationConversion",
    # "CosineWave",
    # "CppFunction",
    "CrossProduct",
    # "DataSource",
    "DeadZone",
    "Delay",
    "Demux",
    "Derivative",
    "DerivativeDiscrete",
    "DiscreteInitializer",
    "DotProduct",
    "DriveCycle",
    "EdgeDetection",
    "Exponent",
    "FilterDiscrete",
    "Gain",
    "IfThenElse",
    # "ImageSegmentation",
    # "ImageSource",
    "Integrator",
    "IntegratorDiscrete",
    "Log",
    "LogicalOperator",
    "LookupTable1d",
    "LookupTable2d",
    "MatrixInversion",
    "MatrixMultiplication",
    "MatrixOperator",
    "MatrixTransposition",
    "MinMax",
    # "ModelicaFMU",
    "Mux",
    # "ObjectDetection",
    "Offset",
    "PID",
    "PID_Discrete",
    "Power",
    # "Predictor",
    "Product",
    "ProductOfElements",
    "Pulse",
    "PythonScript",
    "Quantizer",
    "Ramp",
    "RateLimiter",
    "Reciprocal",
    "Relay",
    "RigidBody",
    "Saturate",
    "Sawtooth",
    "ScalarBroadcast",
    # "SineWave",
    "Slice",
    "SquareRoot",
    "Stack",
    "StateSpace",
    "Step",
    "Stop",
    "SumOfElements",
    "TransferFunction",
    "TransferFunctionDiscrete",
    "Trigonometric",
    "UnitDelay",
    # "VideoSink",
    # "VideoSource",
    "ZeroOrderHold",
]


def ts_docs(only_names=False):
    print("const MODEL_BUILDER_BLOCK_DOCS = [")
    for schema in load_schemas("core"):
        if schema.name not in DOCS_WHITELIST:
            continue
        feature_level = schema._get("base", "feature_level")
        if feature_level in ["disabled", "dev"]:
            continue
        if schema._get("base", "hidden"):
            continue
        if schema._get("base", "supports_models") is False:
            continue
        print(f"  `{schema.doc(only_name=only_names)}`,")
    print("];")


def name_to_md_doc_dict():
    name_to_doc = {}
    for schema in load_schemas("core"):
        if schema.name not in DOCS_WHITELIST:
            continue
        feature_level = schema._get("base", "feature_level")
        if feature_level in ["disabled", "dev"]:
            continue
        if schema._get("base", "hidden"):
            continue
        if schema._get("base", "supports_models") is False:
            continue
        name_to_doc[schema.name] = schema.md_doc()
    return name_to_doc


if __name__ == "__main__":
    print(json.dumps(name_to_md_doc_dict(), indent=2))
    # for schema in load_schemas("core"):
    #     print(schema)
