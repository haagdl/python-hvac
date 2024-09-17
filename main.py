import warnings
from hvac import Quantity
from hvac.fluids import HumidAir, Fluid, CoolPropWarning

warnings.filterwarnings('ignore', category=CoolPropWarning)

from hvac.heat_exchanger.recuperator.fintube.continuous_fin.air_evaporator_dry import PlainFinTubeCounterFlowAirEvaporator as Evaporator
from hvac.charts import PsychrometricChart
from hvac.air_conditioning import AirConditioningProcess

import numpy as np

Q_ = Quantity

R134a = Fluid('R134a')

evp = Evaporator(
    W_fro=Q_(0.5, 'm'),         # width of frontal area
    H_fro=Q_(0.5, 'm'),         # height of frontal area
    N_rows=5,                     # number of rows
    S_trv=Q_(25.4, 'mm'),         # vertical distance between tubes
    S_lon=Q_(50.0, 'mm'),         # horizontal distance between tubes
    D_int=Q_(8.422, 'mm'),        # inner tube diameter
    D_ext=Q_(10.2, 'mm'),         # outer tube diameter
    t_fin=Q_(0.3302, 'mm'),       # fin thickness
    N_fin=1 / Q_(3.175, 'mm'),    # fin density
    k_fin=Q_(237, 'W / (m * K)')  # conductivity of fin material
)

cnd_rfg_sat_liq = R134a(T=Q_(60, 'degC'), x=Q_(0.0, 'frac'))


evp_rfg_in = R134a(T=Q_(10, 'degC'), x=Q_(0.1, 'frac'))

for rh in np.linspace(50., 50., 1):
    air_in = HumidAir(Tdb=Q_(50.0, 'degC'), RH=Q_(rh, 'pct'))

    m_dot = Q_(1000.0, 'kg / hr')
    rfg_m_dot = evp.solve(
        air_in=air_in,
        air_m_dot=m_dot,
        rfg_in=evp_rfg_in,
        dT_sh=Q_(5.0, 'K'),
        rfg_m_dot_ini=Q_(8.0, 'kg / hr'),
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

    evp_process = AirConditioningProcess(
        air_in=air_in,
        air_out=evp.air_out,
        m_da=m_dot,
    )
    print(
        f"- ADP: {evp_process.ADP}",
        f"- contact factor = {evp_process.beta.to('pct'):~P.1f}",
        f"- sensible cooling capacity = {evp_process.Q_sen.to('kW'):~P.3f}",
        f"- latent cooling capacity = {evp_process.Q_lat.to('kW'):~P.3f}",
        f"- SHR = {evp_process.SHR.to('pct'):~P.1f}",
        sep='\n'
    )
