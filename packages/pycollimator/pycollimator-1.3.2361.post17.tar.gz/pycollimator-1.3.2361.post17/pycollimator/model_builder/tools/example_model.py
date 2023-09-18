from model_builder import core
from model_builder.model import ModelBuilder


def create_model():
    model_builder = ModelBuilder("model_builder")
    model_builder.add_parameter("length", "1.0")  # length of the pendulum
    model_builder.add_parameter("gravity", "-9.81")  # gravitational constant

    # Initial angle (in radians), velocity and acceleration are set to zero
    Angle = core.Integrator(
        model_builder,
        name="Angle",
        initial_states="0.0",
        enable_reset="false",
        enable_external_reset="true",
        enable_hold="false",
        enable_limits="false",
    )
    AngularVelocity = core.Integrator(
        model_builder,
        name="AngularVelocity",
        initial_states="0.0",
        enable_reset="false",
        enable_external_reset="true",
        enable_hold="false",
        enable_limits="false",
    )

    # Compute acceleration based on angle and physical constants
    Acceleration = core.Product(
        model_builder,
        name="Acceleration",
        operators="*/*",
        divide_by_zero_behavior="inf",
        denominator_limit="1e-12",
        input_names=("in_0", "in_1", "in_2"),
    )

    Gravity = core.Constant(model_builder, name="Gravity", value="gravity")
    Length = core.Constant(model_builder, name="Length", value="length")
    Sin = core.Trigonometric(model_builder, name="Sin", function="sin")

    # Connect the elements
    model_builder.add_link(AngularVelocity.out_0, Angle.in_0)
    model_builder.add_link(Acceleration.out_0, AngularVelocity.in_0)
    model_builder.add_link(Angle.out_0, Sin.in_0)
    model_builder.add_link(Sin.out_0, Acceleration.in_0)
    model_builder.add_link(Gravity.out_0, Acceleration.in_1)
    model_builder.add_link(Length.out_0, Acceleration.in_2)
    return model_builder
