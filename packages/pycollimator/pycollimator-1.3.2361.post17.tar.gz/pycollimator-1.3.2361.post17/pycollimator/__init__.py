"""Main package to import to use collimator for notebook execution"""
import sys

if sys.platform != "emscripten":
    from pycollimator.api import Api
    from pycollimator.global_variables import get_project_url, set_auth_token
    from pycollimator.log import Log
    from pycollimator.models import Model, load_model, list_models
    from pycollimator.projects import get_project
    from pycollimator.simulations import run_simulation, linearize

    __all__ = [
        "Api",
        "Log",
        "Model",
        "load_model",
        "list_models",
        "get_project",
        "get_project_url",
        "linearize",
        "run_simulation",
        "set_auth_token",
    ]

    try:
        from pycollimator.widgets import parameter_sweep_widget  # noqa: F401

        __all__.append("parameter_sweep_widget")
    except Exception:
        # Log.error(
        #     "There was an error importing widgets in pycollimator. "
        #     "Widgets will not be available. Try "
        #     "`pip install pycollimator[notebook]`"
        # )
        pass
