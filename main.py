import warnings
from hvac import Quantity
from hvac.fluids import HumidAir, Fluid, CoolPropWarning

warnings.filterwarnings('ignore', category=CoolPropWarning)

from hvac.heat_exchanger.recuperator.fintube.continuous_fin import PlainFinTubeCounterFlowAirEvaporator as Evaporator
from hvac.charts import PsychrometricChart
from hvac.air_conditioning import AirConditioningProcess

import numpy as np

Q_ = Quantity

R134a = Fluid('R134a')

evp = Evaporator(
    W_fro=Q_(0.731, 'm'),         # width of frontal area
    H_fro=Q_(0.244, 'm'),         # height of frontal area
    N_rows=3,                     # number of rows
    S_trv=Q_(25.4, 'mm'),         # vertical distance between tubes
    S_lon=Q_(22.0, 'mm'),         # horizontal distance between tubes
    D_int=Q_(8.422, 'mm'),        # inner tube diameter
    D_ext=Q_(10.2, 'mm'),         # outer tube diameter
    t_fin=Q_(0.3302, 'mm'),       # fin thickness
    N_fin=1 / Q_(3.175, 'mm'),    # fin density
    k_fin=Q_(237, 'W / (m * K)')  # conductivity of fin material
)

cnd_rfg_sat_liq = R134a(T=Q_(50, 'degC'), x=Q_(0, 'frac'))
P_cnd = cnd_rfg_sat_liq.P

dT_sc = Q_(5, 'K')

cnd_rfg_out = R134a(T=cnd_rfg_sat_liq.T.to('K') - dT_sc, P=P_cnd)

evp_rfg_sat_vap = R134a(T=Q_(5, 'degC'), x=Q_(1, 'frac'))
P_evp = evp_rfg_sat_vap.P

evp_rfg_in = R134a(P=P_evp, h=cnd_rfg_out.h)

for rh in np.linspace(30.0, 80.0, 7):
    air_in = HumidAir(Tdb=Q_(24.0, 'degC'), RH=Q_(rh, 'pct'))

    rfg_m_dot = evp.solve(
        air_in=air_in,
        air_m_dot=Q_(1500, 'kg / hr'),
        rfg_in=evp_rfg_in,
        dT_sh=Q_(10, 'K'),
        rfg_m_dot_ini=Q_(138.854, 'kg / hr'),
    )

    water_in = (air_in.W.to('kg / kg') *  Q_(1500, 'kg / hr')).to('g / h')
    water_out = (evp.air_out.W.to('kg / kg') * Q_(1500, 'kg / hr')).to('g / h')
    condensate = (water_in - water_out).to('g / hr')

    print(
        f"m_dot_rfg = {rfg_m_dot.to('kg / hr'):~P.3f}\n"
        f"air_out: {evp.air_out.Tdb.to('degC'):~P.1f} DB, "
        f"{evp.air_out.RH.to('pct'):~P.0f} RH\n"
        f"Q = {evp.Q_dot.to('kW'):~P.3f}\n"
        f"dP_air = {evp.air_dP.to('Pa'):~P.0f}\n"
        f"superheating flow length = {evp.superheating_region.L_flow.to('mm'):~P.0f}\n"
        f"condensate = {condensate:~P.3f}\n"
    )
