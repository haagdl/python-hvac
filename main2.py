import warnings
from hvac import Quantity
from hvac.fluids import HumidAir, Fluid, CoolPropWarning
import numpy as np
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore', category=CoolPropWarning)

Q_ = Quantity

from hvac.heat_exchanger.recuperator.fintube.continuous_fin import \
    PlainFinTubeCounterFlowAirCondenser as Condenser, PlainFinTubeCounterFlowAirEvaporator
from hvac.heat_exchanger.recuperator.fintube.continuous_fin.fan import Fan
from hvac.vapor_compression.machine import SingleStageVaporCompressionMachine
from hvac.vapor_compression.reciprocating_compressor import ReciprocatingCompressor

refrigerant = Fluid('R134a')

compressor = ReciprocatingCompressor(
    V_dis=Q_(25.00, 'cm^3'),
    C=Q_(0.02, 'frac'),
    speed=Q_(50, '1 / s'),
    n=Q_(1.2, 'dimensionless'),
    refrigerant=refrigerant,
    eta_is=Q_(1.0, 'frac'),
    eta_mech=Q_(1.0, 'frac'),
    eta_el=Q_(1.0, 'frac'),
)

p_evap = Q_(3.961, 'bar')
P_cnd = Q_(20.502, 'bar')
dT_sup = Q_(5.0, 'K')
state_in = refrigerant(P=p_evap, T=Q_(13.641, 'degC').to('K'))
v_suc = 1 / state_in.rho
state_out = refrigerant(P=P_cnd, T=Q_(127.454, 'degC').to('K'))

compressor.P_evp = p_evap
compressor.P_cnd = P_cnd
compressor.v_suc = v_suc

# state_in = compressor.suction_gas
# state_out = compressor.discharge_gas
P_cmp = (state_out.h - state_in.h) * compressor.m_dot
eta_vol = compressor.volumetric_efficiency
P_cpm_model = compressor.W_dot
print(f'Compressor power: {P_cmp.to("kW")}')
print(f'Compressor power model: {P_cpm_model.to("kW")}')
print(F'Mass flow rate: {compressor.m_dot.to("kg/h")}')
print(f'Volumetric efficiency: {eta_vol}')

m_dots = []
W_dots = []
speeds = np.linspace(10, 100, 10)
for speed in speeds:
    compressor.speed = Q_(speed, '1 / s')
    m_dot = compressor.m_dot.to('kg/h').magnitude
    m_dots.append(m_dot)
    W_dot = compressor.W_dot.to('kW').magnitude
    W_dots.append(W_dot)

plt.plot(speeds, W_dots)
plt.xlabel('Speed [1/s]')
plt.ylabel('Compressor power [kW]')
# plt.show()
