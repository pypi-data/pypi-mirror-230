from ...utilities import environ_util
from typing import Union
from ...time_series import lib_path
from ..core import ModelInfo, run_state
from ..core import _core  # need to pull in dependent base-types
from ._stm import *

__doc__ = _stm.__doc__
__version__ = _stm.__version__

# backward compatible names after renaming
if shyft_with_stm:
    Aggregate=Unit
    AggregateList=UnitList
    WaterRoute=Waterway
    PowerStation=PowerPlant
    HydroPowerSystem.create_aggregate=HydroPowerSystem.create_unit
    HydroPowerSystem.create_power_station=HydroPowerSystem.create_power_plant
    HydroPowerSystem.create_water_route=HydroPowerSystem.create_waterway
# end backward compat section

# Optional Shop integration
# Set Shop API specific environment variable ICC_COMMAND_PATH,
# value pointing to the shared library path where the solver libraries
# and license file should be located.
# Note: Needed by DStmServer.do_optimize, as well as subpackage shop.
environ_util.set_environment('ICC_COMMAND_PATH', lib_path)


__all__ = [
    "shyft_with_stm",
    "HydroPowerSystem","HydroPowerSystemList",
    "StmSystem","StmSystemList","StmPatchOperation",
    "MarketArea",
    "ModelState",
    "ModelState",
    "Unit", "UnitList",
    "Reservoir",
    "PowerPlant",
    "Gate",
    "Waterway",
    "UnitGroupType",
    "UnitGroup",
    "t_xy","t_turbine_description","MessageList", "t_xyz_list","t_xyz",
    "_t_xy_", "_turbine_description", "_ts","_time_axis", "_t_xy_z_list","_string","_double",
    "_i64","_bool","_u16",
    "DStmClient", "DStmServer",
    "HpsClient", "HpsServer",
    "StmClient", "StmServer",
    "StmTaskServer", "StmTaskClient",
    "StmCase", "ModelRefList", "StmModelRef", "StmTask",
    "Contract","ContractList",
    "ContractPortfolio","ContractPortfolioList",
    "PowerModule","Busbar","Network","TransmissionLine",
    "compute_effective_price"
]
