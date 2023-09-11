from ._pt_st_hbv import *
from ...time_series import ByteVector
# Fix up types that we need attached to the model
PTSTHBVStateVector.push_back = lambda self, x: self.append(x)
PTSTHBVStateVector.size = lambda self: len(self)

PTSTHBVModel.cell_t = PTSTHBVCellAll
PTSTHBVParameter.map_t = PTSTHBVParameterMap
PTSTHBVModel.parameter_t = PTSTHBVParameter
PTSTHBVModel.state_t = PTSTHBVState
PTSTHBVModel.state_with_id_t = PTSTHBVStateWithId
PTSTHBVModel.state = property(lambda self:PTSTHBVCellAllStateHandler(self.get_cells()))
PTSTHBVModel.statistics = property(lambda self: PTSTHBVCellAllStatistics(self.get_cells()))

PTSTHBVModel.snow_tiles_state = property(lambda self: PTSTHBVCellSnowTilesStateStatistics(self.get_cells()))
PTSTHBVModel.snow_tiles_response = property(lambda self: PTSTHBVCellSnowTilesResponseStatistics(self.get_cells()))
PTSTHBVModel.priestley_taylor_response = property(lambda self: PTSTHBVCellPriestleyTaylorResponseStatistics(self.get_cells()))
PTSTHBVModel.soil_state = property(lambda self: PTSTHBVCellHBVSoilStateStatistics(self.get_cells()))
PTSTHBVModel.soil_response = property(lambda self: PTSTHBVCellHBVSoilResponseStatistics(self.get_cells()))
PTSTHBVModel.tank_state = property(lambda self: PTSTHBVCellHBVTankStateStatistics(self.get_cells()))
PTSTHBVModel.tank_response = property(lambda self: PTSTHBVCellHBVTankResponseStatistics(self.get_cells()))

PTSTHBVOptModel.cell_t = PTSTHBVCellOpt
PTSTHBVOptModel.parameter_t = PTSTHBVParameter
PTSTHBVOptModel.state_t = PTSTHBVState
PTSTHBVOptModel.state_with_id_t = PTSTHBVStateWithId
PTSTHBVOptModel.state = property(lambda self:PTSTHBVCellOptStateHandler(self.get_cells()))
PTSTHBVOptModel.statistics = property(lambda self:PTSTHBVCellOptStatistics(self.get_cells()))

PTSTHBVOptModel.optimizer_t = PTSTHBVOptimizer

PTSTHBVOptModel.full_model_t =PTSTHBVModel
PTSTHBVModel.opt_model_t =PTSTHBVOptModel
PTSTHBVModel.create_opt_model_clone = lambda self: create_opt_model_clone(self)
#PTSTHBVModel.create_opt_model_clone.__doc__ = create_opt_model_clone.__doc__
PTSTHBVOptModel.create_full_model_clone = lambda self: create_full_model_clone(self)
#PTSTHBVOptModel.create_full_model_clone.__doc__ = create_full_model_clone.__doc__

PTSTHBVCellAll.vector_t = PTSTHBVCellAllVector
PTSTHBVCellOpt.vector_t = PTSTHBVCellOptVector
PTSTHBVState.vector_t = PTSTHBVStateVector
#PTSTHBVState.serializer_t= PTSTHBVStateIo

#decorate StateWithId for serialization support
def serialize_to_bytes(state_with_id_vector:PTSTHBVStateWithIdVector)->ByteVector:
    if not isinstance(state_with_id_vector,PTSTHBVStateWithIdVector):
        raise RuntimeError("supplied argument must be of type PTSTHBVStateWithIdVector")
    return serialize(state_with_id_vector)

def __serialize_to_str(state_with_id_vector:PTSTHBVStateWithIdVector)->str:
    return str(serialize_to_bytes(state_with_id_vector))  # returns hex-string formatted vector

def __deserialize_from_str(s:str)->PTSTHBVStateWithIdVector:
    return deserialize_from_bytes(ByteVector.from_str(s))

PTSTHBVStateWithIdVector.serialize_to_bytes = lambda self: serialize_to_bytes(self)
PTSTHBVStateWithIdVector.serialize_to_str = lambda self: __serialize_to_str(self)
PTSTHBVStateWithIdVector.deserialize_from_str = __deserialize_from_str
PTSTHBVStateWithIdVector.state_vector = property(lambda self: extract_state_vector(self),doc="extract_state_vector.__doc__")
PTSTHBVStateWithId.vector_t = PTSTHBVStateWithIdVector

def deserialize_from_bytes(byts: ByteVector)->PTSTHBVStateWithIdVector:
    if not isinstance(byts,ByteVector):
        raise RuntimeError("Supplied type must be a ByteVector, as created from serialize_to_bytes")
    states=PTSTHBVStateWithIdVector()
    deserialize(byts,states)
    return states
__all__=[
    'PTSTHBVStateVector',
    'PTSTHBVStateWithId',
    'PTSTHBVStateWithIdVector',
    'PTSTHBVCellAll',
    'PTSTHBVCellOpt',
    'PTSTHBVState',
    'PTSTHBVModel',
    'PTSTHBVOptModel',
    'PTSTHBVParameter'
]