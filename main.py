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
compressor = ReciprocatingCompressor(
    V_dis=Q_(25.00, 'cm^3'),
    C=Q_(0.02, 'frac'),
    speed=Q_(50, '1 / s'),
    n=Q_(1.2, 'dimensionless'),
    refrigerant_type=R134a
)

machine = SingleStageVaporCompressionMachine(
    compressor=compressor,
    condenser=condenser,
    evaporator=evaporator,
    refrigerant=R134a,
    dT_sh=Q_(5.0, 'K'),
    n_cmp_min=Q_(30, '1 / s'),
    n_cmp_max=Q_(50, '1 / s'),
)
evp_air_in = HumidAir(Tdb=Q_(35.0, 'degC'),
                      RH=Q_(50.0, 'pct'))
evp_air_m_dot = Q_(200, 'm^3/h') * evp_air_in.rho
cnd_air_in = HumidAir(Tdb=Q_(35.0, 'degC'),
                      RH=Q_(50.0, 'pct'))
cnd_air_m_dot = Q_(1000.0, 'm^3/h') * cnd_air_in.rho
T_evp_ini = Q_(10.0, 'degC')
T_cnd_ini = Q_(60.0, 'degC')
# output = machine.rate(
#     evp_air_in=evp_air_in,
#     evp_air_m_dot=evp_air_m_dot,
#     cnd_air_in=cnd_air_in,
#     cnd_air_m_dot=cnd_air_m_dot,
#     n_cmp=Q_(25, '1 / s'),
#     T_evp_ini=T_evp_ini,
#     T_cnd_ini=T_cnd_ini,
# )
output = machine.balance_by_speed(
    evp_air_in=evp_air_in,
    evp_air_m_dot=evp_air_m_dot,
    cnd_air_in=cnd_air_in,
    cnd_air_m_dot=cnd_air_m_dot,
    T_evp=T_evp_ini,
    T_cnd=T_cnd_ini,

)




