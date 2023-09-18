# This module dynamically creates classes from the schemas which pylint
# doesn't understand.
#
# pylint: skip-file

from . import model
from . import schema_reader

SCHEMAS = {}
CLASSES = {}

for s in schema_reader.load_schemas("core"):
    klass = model._node_class_from_schema(s)
    SCHEMAS[s.name] = s
    CLASSES[s.name] = klass

# Assign top-level names to the classes. We could just do
# `globals()[s.name] = klass` in the loop above, but pylint
# doesn't like that.

Abs = CLASSES["Abs"]
Adder = CLASSES["Adder"]
BatteryCell = CLASSES["BatteryCell"]
BusCreator = CLASSES["BusCreator"]
BusSelector = CLASSES["BusSelector"]
CFunction = CLASSES["CFunction"]
Chirp = CLASSES["Chirp"]
Clock = CLASSES["Clock"]
CodeBlockDev = CLASSES["CodeBlockDev"]
Comparator = CLASSES["Comparator"]
Conditional = CLASSES["Conditional"]
Constant = CLASSES["Constant"]
CoordinateRotation = CLASSES["CoordinateRotation"]
CoordinateRotationConversion = CLASSES["CoordinateRotationConversion"]
CosineWave = CLASSES["CosineWave"]
CppFunction = CLASSES["CppFunction"]
CrossProduct = CLASSES["CrossProduct"]
DataSource = CLASSES["DataSource"]
DeadZone = CLASSES["DeadZone"]
Delay = CLASSES["Delay"]
Demux = CLASSES["Demux"]
Derivative = CLASSES["Derivative"]
DerivativeDiscrete = CLASSES["DerivativeDiscrete"]
DiscreteInitializer = CLASSES["DiscreteInitializer"]
DotProduct = CLASSES["DotProduct"]
DriveCycle = CLASSES["DriveCycle"]
EdgeDetection = CLASSES["EdgeDetection"]
ExperimentIterator = CLASSES["ExperimentIterator"]
ExperimentModel = CLASSES["ExperimentModel"]
Exponent = CLASSES["Exponent"]
FilterDiscrete = CLASSES["FilterDiscrete"]
Gain = CLASSES["Gain"]
Generic = CLASSES["Generic"]
Group = CLASSES["Group"]
IfThenElse = CLASSES["IfThenElse"]
ImageSegmentation = CLASSES["ImageSegmentation"]
ImageSource = CLASSES["ImageSource"]
Inport = CLASSES["Inport"]
Integrator = CLASSES["Integrator"]
IntegratorDiscrete = CLASSES["IntegratorDiscrete"]
Iterator = CLASSES["Iterator"]
Log = CLASSES["Log"]
LogicalOperator = CLASSES["LogicalOperator"]
LookupTable1d = CLASSES["LookupTable1d"]
LookupTable2d = CLASSES["LookupTable2d"]
LoopBreak = CLASSES["LoopBreak"]
LoopCounter = CLASSES["LoopCounter"]
LoopMemory = CLASSES["LoopMemory"]
MatrixConcatenation = CLASSES["MatrixConcatenation"]
MatrixInversion = CLASSES["MatrixInversion"]
MatrixMultiplication = CLASSES["MatrixMultiplication"]
MatrixOperator = CLASSES["MatrixOperator"]
MatrixTransposition = CLASSES["MatrixTransposition"]
MinMax = CLASSES["MinMax"]
ModelicaFMU = CLASSES["ModelicaFMU"]
Mux = CLASSES["Mux"]
ObjectDetection = CLASSES["ObjectDetection"]
Offset = CLASSES["Offset"]
Outport = CLASSES["Outport"]
PID = CLASSES["PID"]
PID_Discrete = CLASSES["PID_Discrete"]
Power = CLASSES["Power"]
Predictor = CLASSES["Predictor"]
Product = CLASSES["Product"]
ProductOfElements = CLASSES["ProductOfElements"]
Pulse = CLASSES["Pulse"]
PythonScript = CLASSES["PythonScript"]
Quantizer = CLASSES["Quantizer"]
Ramp = CLASSES["Ramp"]
RateLimiter = CLASSES["RateLimiter"]
Reciprocal = CLASSES["Reciprocal"]
ReferenceSubmodel = CLASSES["ReferenceSubmodel"]
Relay = CLASSES["Relay"]
Replicator = CLASSES["Replicator"]
RigidBody = CLASSES["RigidBody"]
Saturate = CLASSES["Saturate"]
Sawtooth = CLASSES["Sawtooth"]
ScalarBroadcast = CLASSES["ScalarBroadcast"]
SignalDatatypeConversion = CLASSES["SignalDatatypeConversion"]
SineWave = CLASSES["SineWave"]
Slice = CLASSES["Slice"]
SquareRoot = CLASSES["SquareRoot"]
Stack = CLASSES["Stack"]
StateMachine = CLASSES["StateMachine"]
StateSpace = CLASSES["StateSpace"]
Step = CLASSES["Step"]
Stop = CLASSES["Stop"]
Submodel = CLASSES["Submodel"]
SumOfElements = CLASSES["SumOfElements"]
TransferFunction = CLASSES["TransferFunction"]
TransferFunctionDiscrete = CLASSES["TransferFunctionDiscrete"]
Trigonometric = CLASSES["Trigonometric"]
UnitDelay = CLASSES["UnitDelay"]
VideoSink = CLASSES["VideoSink"]
VideoSource = CLASSES["VideoSource"]
ZeroOrderHold = CLASSES["ZeroOrderHold"]


def _bool_param(params: dict, name: str, default=False) -> bool:
    if name in params:
        return str(params[name]).lower() == "true"
    return default


def init_integrator(**params):
    if "input_names" not in params:
        ins = ("in_0",)
        if _bool_param(params, "enable_reset"):
            if "reset" not in ins:
                ins += ("reset",)
            if _bool_param(params, "enable_external_reset"):
                if "reset_value" not in ins:
                    ins += ("reset_value",)
        elif "enable_reset" in params:
            del params["enable_reset"]
            if "enable_external_reset" in params:
                del params["enable_external_reset"]

        if _bool_param(params, "enable_hold"):
            if "hold" not in ins:
                ins += ("hold",)
        elif "enable_hold" in params:
            del params["enable_hold"]

        if _bool_param(params, "enable_limits"):
            if "upper_limit" not in ins:
                ins += ("upper_limit", "lower_limit")
        elif "enable_limits" in params:
            del params["enable_limits"]

        params["input_names"] = ins

    if "lower_limit" in params:
        del params["lower_limit"]
    if "upper_limit" in params:
        del params["upper_limit"]
    if "reset_trigger_method" in params:
        del params["reset_trigger_method"]
    if "hold_trigger_method" in params:
        del params["hold_trigger_method"]

    return params


class Trigonometric(Trigonometric):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = ("x",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class Integrator(Integrator):
    def __init__(self, *args, **params):
        super().__init__(*args, **init_integrator(**params))


class IntegratorDiscrete(IntegratorDiscrete):
    def __init__(self, *args, **params):
        super().__init__(*args, **init_integrator(**params))


class PID(PID):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = ("in_0",)
            if _bool_param(params, "enable_external_initial_state"):
                if "initial_state" not in ins:
                    ins += ("initial_state",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class PID_Discrete(PID_Discrete):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = ("in_0",)
            if _bool_param(params, "enable_external_initial_state"):
                if "initial_state" not in ins:
                    ins += ("initial_state",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class LogicalOperator(LogicalOperator):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = (
                "in_0",
                "in_1",
            )
            if params.get("function") == "not":
                ins = ("in_0",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class RateLimiter(RateLimiter):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = ("in_0",)
            if _bool_param(params, "enable_dynamic_upper_limit"):
                if "upper_limit" not in ins:
                    ins += ("upper_limit",)
            if _bool_param(params, "enable_dynamic_lower_limit"):
                if "lower_limit" not in ins:
                    ins += ("lower_limit",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class Saturate(Saturate):
    def __init__(self, *args, **params):
        if "input_names" not in params:
            ins = ("in_0",)
            if _bool_param(params, "enable_dynamic_upper_limit"):
                if "upper_limit" not in ins:
                    ins += ("upper_limit",)
            if _bool_param(params, "enable_dynamic_lower_limit"):
                if "lower_limit" not in ins:
                    ins += ("lower_limit",)
            params["input_names"] = ins
        super().__init__(*args, **params)


class Adder(Adder):
    def __init__(self, *args, **params):
        if "operators" not in params:
            raise ValueError("Adder requires 'operators' parameter " "(list or string with one operation per input)")
        if "input_names" not in params:
            ins = [f"in_{k}" for k in range(len(params["operators"]))]
            params["input_names"] = tuple(ins)
        if type(params["operators"]) is list:
            params["operators"] = "".join(params["operators"])
        if len(params["input_names"]) != len(params["operators"]):
            raise ValueError("Number of inputs and operators must be equal.")
        if len(params["operators"]) < 2:
            raise ValueError("Adder requires at least two inputs.")
        super().__init__(*args, **params)

    def update_parameters(self, **kwargs):
        if "operators" in kwargs:
            ins = [f"in_{k}" for k in range(len(kwargs["operators"]))]
            self.input_names = tuple(ins)

            if type(kwargs["operators"]) is list:
                kwargs["operators"] = "".join(kwargs["operators"])
        super().update_parameters(**kwargs)


class Product(Product):
    def __init__(self, *args, **params):
        if "operators" not in params:
            raise ValueError("Product requires 'operators' parameter " "(list or string with one operation per input)")
        if "input_names" not in params:
            ins = [f"in_{k}" for k in range(len(params["operators"]))]
            params["input_names"] = tuple(ins)
        if type(params["operators"]) is list:
            params["operators"] = "".join(params["operators"])
        if len(params["input_names"]) != len(params["operators"]):
            raise ValueError("Number of inputs and operators must be equal.")
        if len(params["operators"]) < 2:
            raise ValueError("Product requires at least two inputs.")
        super().__init__(*args, **params)

    def update_parameters(self, **kwargs):
        if "operators" in kwargs:
            ins = [f"in_{k}" for k in range(len(kwargs["operators"]))]
            self.input_names = tuple(ins)

            if type(kwargs["operators"]) is list:
                kwargs["operators"] = "".join(kwargs["operators"])
        super().update_parameters(**kwargs)
