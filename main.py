import warnings
from hvac import Quantity
from hvac.fluids import HumidAir, Fluid, CoolPropWarning

warnings.filterwarnings('ignore', category=CoolPropWarning)

Q_ = Quantity

from hvac.heat_exchanger.recuperator.fintube.continuous_fin import PlainFinTubeCounterFlowAirCondenser as Condenser

R134a = Fluid('R134a')

condenser = Condenser(
    W_fro=Q_(1.003, 'm'),
    H_fro=Q_(0.334, 'm'),
    N_rows=5,
    S_trv=Q_(25.4, 'mm'),         # vertical distance between tubes
    S_lon=Q_(22.0, 'mm'),         # horizontal distance between tubes
    D_int=Q_(8.422, 'mm'),        # inner tube diameter
    D_ext=Q_(10.2, 'mm'),         # outer tube diameter
    t_fin=Q_(0.3302, 'mm'),       # fin thickness
    N_fin=1 / Q_(3.175, 'mm'),    # fin density
    k_fin=Q_(237, 'W / (m * K)')  # conductivity of fin material
)

# Refrigerant state at condenser inlet:
rfg_in = R134a(T=Q_(81.7, 'degC'), P=Q_(13.179, 'bar'))

# Selected condensing temperature:
T_cnd = Q_(50, 'degC')

rfg_sat = R134a(T=T_cnd, x=Q_(0, 'frac'))
P_cnd = rfg_sat.P

# Selected degree of subcooling:
dT_sc = Q_(5, 'K')

# Refrigerant state at condenser outlet:
T_rfg_out = rfg_sat.T - dT_sc
rfg_out = R134a(T=T_rfg_out, P=P_cnd)

# Selected mass flow rate of refrigerant
# (which follows from the evaporator rating)
rfg_m_dot = Q_(168.745, 'kg / hr')

# Heat rejection rate of refrigerant in the condenser:
cnd_Q_dot = rfg_m_dot * (rfg_in.h - rfg_out.h)
print(cnd_Q_dot.to('kW'))

# Air state at condenser inlet:
air_in = HumidAir(Tdb=Q_(35.0, 'degC'), RH=Q_(30, 'pct'))

# Selected air temperature rise across condenser
# (this choice depends also on the selected condensing temperature):
air_dT = Q_(10, 'K')

# Air state at condenser outlet:
air_out = HumidAir(Tdb=air_in.Tdb + air_dT, W=air_in.W)

# Mass flow rate of air through the condenser:
air_m_dot = cnd_Q_dot / (air_out.h - air_in.h)
print(air_m_dot.to('kg/hr'))

air_out, rfg_out = condenser.solve(
    air_in=air_in,
    air_m_dot=air_m_dot,
    rfg_in=rfg_in,
    rfg_m_dot=rfg_m_dot
)

print(
    f"air out = {air_out.Tdb.to('degC'):~P.1f} DB, "
    f"{air_out.RH.to('pct'):~P.0f} RH\n"
    f"refrigerant out = {rfg_out.T.to('degC'):~P.1f}\n"
    f"degree of subcooling = {condenser.dT_sc.to('K'):~P.2f}\n"
    f"heat rejection rate = {condenser.Q_dot.to('kW'):~P.3f}\n"
    f"L2 desuperheating = {condenser.desuperheating_region.L_flow.to('mm'):~P.0f}\n"
    f"L2 condensing = {condenser.condensing_region.L_flow.to('mm'):~P.0f}\n"
    f"L2 subcooling = {condenser.subcooling_region.L_flow.to('mm'):~P.0f}\n"
    f"air-side pressure drop = {condenser.air_dP.to('Pa'):~P.3f}\n",
    f"Electric power consumption of the condenser fan = {condenser.P_fan.to('W'):~P.2f}"
)