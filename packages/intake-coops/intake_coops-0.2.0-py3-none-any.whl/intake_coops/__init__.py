"""
intake-axds: Intake approach for Axiom assets.
"""

# from .axds_cat import AXDSCatalog
# from .utils import (  # noqa: F401
#     _get_version,
#     available_names,
#     match_key_to_parameter,
#     return_parameter_options,
# )


# __version__ = _get_version()

from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("intake-coops")
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"
