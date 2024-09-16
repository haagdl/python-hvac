import warnings
from hvac import Quantity
from hvac.fluids import HumidAir, Fluid, CoolPropWarning
import pandas as pd

warnings.filterwarnings('ignore', category=CoolPropWarning)

Q_ = Quantity

from hvac.heat_exchanger.recuperator.fintube.continuous_fin import \
    PlainFinTubeCounterFlowAirCondenser as Condenser, PlainFinTubeCounterFlowAirEvaporator
from hvac.heat_exchanger.recuperator.fintube.continuous_fin.fan import Fan
from hvac.vapor_compression.machine import SingleStageVaporCompressionMachine
from hvac.vapor_compression.reciprocating_compressor import ReciprocatingCompressor

R134a = Fluid('R134a')
condenser = Condenser(
    W_fro=Q_(0.5, 'm'),
    H_fro=Q_(0.334, 'm'),
    N_rows=6,
    S_trv=Q_(25.4, 'mm'),  # vertical distance between tubes
    S_lon=Q_(22.0, 'mm'),  # horizontal distance between tubes
    D_int=Q_(8.422, 'mm'),  # inner tube diameter
    D_ext=Q_(10.2, 'mm'),  # outer tube diameter
    t_fin=Q_(0.3302, 'mm'),  # fin thickness
    N_fin=1 / Q_(3.175, 'mm'),  # fin density
    k_fin=Q_(237, 'W / (m * K)'),  # conductivity of fin material
)
evaporator = PlainFinTubeCounterFlowAirEvaporator(
    W_fro=Q_(1.003, 'm'),
    H_fro=Q_(0.334, 'm'),
    N_rows=2,
    S_trv=Q_(25.4, 'mm'),  # vertical distance between tubes
    S_lon=Q_(22.0, 'mm'),  # horizontal distance between tubes
    D_int=Q_(8.422, 'mm'),  # inner tube diameter
    D_ext=Q_(10.2, 'mm'),  # outer tube diameter
    t_fin=Q_(0.3302, 'mm'),  # fin thickness
    N_fin=1 / Q_(3.175, 'mm'),  # fin density
    k_fin=Q_(237, 'W / (m * K)'),  # conductivity of fin material
)


evp_air_in = HumidAir(Tdb=Q_(30.0, 'degC'),
                      W=Q_(0.0, 'g/kg'))
evp_air_m_dot = Q_(500, 'm^3/h') * evp_air_in.rho


state_in = R134a(T=Quantity(5.0, 'degC'), x=Q_(0.0, 'frac'))


# test evaporator
m_dot_evaporator = evaporator.solve(
    air_in=evp_air_in,
    air_m_dot=evp_air_m_dot,
    rfg_in=state_in,
    dT_sh=Q_(5.0, 'K'),
    rfg_m_dot_ini=Q_(10.0, 'kg/h'),
)
print(evaporator.air_in)
print(evaporator.air_out)
