import numpy as np
# from scipy import optimize
from hvac import Quantity
from hvac.fluids import HumidAir, FluidState, Fluid
# from hvac.fluids import CoolPropError
from hvac.heat_transfer.heat_exchanger.eps_ntu_wet import CounterFlowHeatExchanger
from hvac.heat_transfer.heat_exchanger.fin_tube import core


Q_ = Quantity
HexCore = core.plain_fin_tube.PlainFinTubeHeatExchangerCore


class PlainFinTubeCounterFlowBoilingEvaporator:
    """Model of a single-pass, plain fin tube, counterflow heat exchanger with
    humid air flowing on the external side and with boiling refrigerant on the
    internal side. The state of refrigerant at the evaporator's exit is fixed to
    being saturated vapor (i.e. no superheat and the vapor quality is 100 %).
    """
    def __init__(
        self,
        L1: Quantity,
        L3: Quantity,
        S_t: Quantity,
        S_l: Quantity,
        D_i: Quantity,
        D_o: Quantity,
        t_f: Quantity,
        N_f: Quantity,
        k_f: Quantity = Q_(237, 'W / (m * K)')
    ) -> None:
        """Creates a `PlainFinTubeCounterFlowBoilingEvaporator` instance by
        defining the dimensions of the heat exchanger core and its geometrical
        characteristics.

        Parameters
        ----------
        L1:
            Tube length in the direction of inside flow, i.e. the length of the
            tube available for heat transfer with the outside flow.
        L3:
            Length of the tube bank perpendicular to the direction of external
            flow.
        S_t:
            Lateral or transverse pitch, i.e. distance between tubes of the
            same row.
        S_l:
            Longitudinal pitch, i.e. distance between tubes of two adjacent tube
            rows.
        D_i:
            Inside diameter of the tubes.
        D_o:
            Outside diameter of the tubes.
        t_f:
            Thickness of a circular fin.
        N_f:
            Number of fins per unit length (= fin density)
        k_f:
            Thermal conductivity of the external fin material.
        """
        self.hex_core = HexCore(
            L1, L3,
            S_t, S_l,
            D_i, D_o,
            t_f, N_f, k_f,
            boiling=True
        )
        self.air_in: HumidAir | None = None
        self.rfg_in: FluidState | None = None
        self.rfg_sat_vap_out: FluidState | None = None
        self._Rfg: Fluid | None = None
        self.Q_dot: Quantity | None = None
        self.air_out: HumidAir | None = None
        self.dP_air: Quantity | None = None

    def set_fixed_operating_conditions(
        self,
        m_dot_air: Quantity,
        rfg_in: FluidState
    ) -> None:
        """Sets the known operating conditions of the evaporator with boiling
        refrigerant inside.

        Parameters
        ----------
        m_dot_air:
            Mass flow rate of humid air (referred to mass of dry-air fraction).
        rfg_in:
            State of refrigerant at the evaporator's refrigerant inlet (a
            two-phase, liquid-vapor mixture with a known evaporation temperature
            or pressure and a known vapor quality after the expansion device).

        Notes
        -----
        The state of the refrigerant at the outlet is fixed: it must be
        saturated vapor (in the boiling evaporator the refrigerant's temperature
        and pressure are constant and its vapor quality grows from the initial
        vapor quality at the inlet to 100 % at the outlet).
        """
        self.air_in = None
        self.Q_dot = None
        self.air_out = None
        self.dP_air = None
        self.hex_core.m_dot_ext = m_dot_air
        self.rfg_in = rfg_in
        self._Rfg = rfg_in.fluid
        # The state of the refrigerant at the outlet is already fixed at the
        # start: it must be saturated vapor.
        self.rfg_sat_vap_out = self._Rfg(
            T=self.rfg_in.T,   # boiling refrigerant: constant temperature
            x=Q_(1.0, 'frac')  # at the outlet: saturated vapor
        )

    def set_air_in(self, air_in: HumidAir) -> None:
        """Sets the provisional state of humid air at the air entry to the
        boiling region of the evaporator.
        """
        self.air_in = air_in

    def set_flow_length(self, L2: Quantity) -> None:
        """Sets the provisional flow length of the tube bank's boiling part
        (i.e. in the direction parallel to the external air flow).
        """
        self.hex_core.L2 = L2

    def rate(
        self,
        m_dot_rfg_ini: Quantity,
        i_max: int = 100,
        tol: Quantity = Q_(0.1, 'kg / hr'),
    ) -> tuple[Quantity, HumidAir, Quantity, Quantity]:
        """Determines by iteration the mass flow rate of refrigerant needed to
        get saturated refrigerant vapor at the outlet of the evaporator.

        Parameters
        ----------
        m_dot_rfg_ini:
            Initial guess of the refrigerant mass flow rate.
        i_max:
            Maximum number of iterations to try to find a mass flow rate within
            the given tolerance margin around the previous calculated value.
        tol:
            The tolerated deviation between the last and previous calculated
            mass flow rate at which the iteration will end.

        Raises
        ------
        ValueError when after `i_max` iterations the last calculated value is
        still not within the tolerated margins around the previous calculated
        value.

        Returns
        -------
        m_dot_rfg:
            The mass flow rate of refrigerant that results in saturated
            refrigerant vapor at the outlet under the given operating conditions.
        air_out:
            Resulting state of humid air at the evaporator's outlet.
        Q:
            Resulting heat transfer rate from external humid air stream to
            internal refrigerant stream.
        dP_air:
            Pressure drop on the air-side of the evaporator.
        """
        m_dot_rfg = m_dot_rfg_ini
        Q = m_dot_rfg * (self.rfg_sat_vap_out.h - self.rfg_in.h)
        h_air_out = self.air_in.h - Q / self.hex_core.m_dot_ext
        RH_air_out = Q_(100, 'pct')  # initial guess
        air_out = HumidAir(h=h_air_out, RH=RH_air_out)
        for i in range(i_max):
            # Set initial guess of refrigerant mass flow rate on the heat
            # exchanger core:
            self.hex_core.m_dot_int = m_dot_rfg
            # Calculate mean states of air and refrigerant needed for calculating
            # the heat transfer parameters of the heat exchanger core:
            air_mean = self._get_mean_air(air_out)
            rfg_mean = self._get_mean_refrigerant()
            self.hex_core.ext.fluid_mean = air_mean
            self.hex_core.int.fluid_mean = rfg_mean
            self.hex_core.int.Q = Q  # this is needed for calculating h
            # Calculate new value for the heat transfer rate assuming a
            # wet air-side surface along the boiling region:
            cof_hex = CounterFlowHeatExchanger(
                m_dot_r=self.hex_core.m_dot_int,
                m_dot_a=self.hex_core.m_dot_ext,
                T_r_in=self.rfg_in.T,
                T_r_out=self.rfg_sat_vap_out.T,
                P_r=self.rfg_in.P,
                refrigerant=self._Rfg,
                air_in=self.air_in,
                h_ext=self.hex_core.ext.h,
                h_int=self.hex_core.int.h,
                eta_surf_wet=self.hex_core.ext.eta,
                A_ext_to_A_int=(
                    self.hex_core.ext.geo.alpha /
                    self.hex_core.int.geo.alpha
                ).to('m / m').m,
                A_ext=self.hex_core.ext.geo.A
            )
            # Get new value for the refrigerant mass flow rate:
            m_dot_rfg_new = cof_hex.Q / (self.rfg_sat_vap_out.h - self.rfg_in.h)
            # Determine deviation between new and previous value:
            dev_m_dot_rfg = m_dot_rfg_new - self.hex_core.m_dot_int
            if abs(dev_m_dot_rfg.to('kg / hr')) < tol:
                break
            m_dot_rfg = m_dot_rfg_new
            air_out = cof_hex.air_out
            Q = cof_hex.Q
            i += 1
        else:
            raise ValueError(
                f'No acceptable solution found after {i_max} iterations.'
            )
        self.Q_dot = cof_hex.Q
        self.air_out = cof_hex.air_out
        self.dP_air = self.hex_core.ext.get_pressure_drop(self.air_in, self.air_out)
        return (
            self.hex_core.m_dot_int,
            self.air_out,
            self.Q_dot,
            self.dP_air
        )

    def _get_mean_air(self, air_out: HumidAir) -> HumidAir:
        """Determine the mean or bulk air properties."""
        air_sat_rfg_out = HumidAir(Tdb=self.rfg_sat_vap_out.T, RH=Q_(100, 'pct'))
        air_sat_rfg_in = HumidAir(Tdb=self.rfg_in.T, RH=Q_(100, 'pct'))
        dh_in = self.air_in.h - air_sat_rfg_out.h
        dh_out = max(air_out.h - air_sat_rfg_in.h, Q_(1e-12, 'J / kg'))
        dh_max = max(dh_in, dh_out)
        dh_min = min(dh_in, dh_out)
        LMED = (dh_max - dh_min) / np.log(dh_max / dh_min)
        h_a_sat_rfg_avg = (air_sat_rfg_out.h + air_sat_rfg_in.h) / 2
        h_air_m = h_a_sat_rfg_avg + LMED
        dT_in = self.air_in.Tdb - self.rfg_sat_vap_out.T
        dT_out = max(air_out.Tdb - self.rfg_in.T, Q_(1e-12, 'K'))
        dT_max = max(dT_in, dT_out)
        dT_min = min(dT_in, dT_out)
        LMTD = (dT_max - dT_min) / np.log(dT_max / dT_min)
        T_rfg_avg = (self.rfg_in.T + self.rfg_sat_vap_out.T) / 2
        T_air_m = T_rfg_avg + LMTD
        air_mean = HumidAir(Tdb=T_air_m, h=h_air_m)
        return air_mean

    def _get_mean_refrigerant(self) -> FluidState:
        """Determine the mean or bulk refrigerant properties."""
        # x_rfg_avg = (self.rfg_in.x + self.rfg_sat_vap_out.x) / 2
        # try:
        #     rfg_mean = self._Rfg(T=self.rfg_in.T, x=x_rfg_avg)
        # except CoolPropError:
        #     # if `self._Rfg` is a pseudo-pure fluid, `x` cannot be an input
        #     # variable
        #     x_target = x_rfg_avg.to('frac').m
        #
        #     def _eq(h: float) -> float:
        #         state = self._Rfg(
        #             P=self.rfg_sat_vap_out.P,
        #             h=Q_(h, 'kJ / kg')
        #         )
        #         x = state.x.to('frac').m
        #         return x - x_target
        #
        #     h_ini = self.rfg_in.h.to('kJ / kg').m
        #     h_fin = self.rfg_sat_vap_out.h.to('kJ / kg').m
        #     sol = optimize.root_scalar(_eq, bracket=[h_ini, h_fin])
        #     h = Q_(sol.root, 'kJ / kg')
        #     rfg_mean = self._Rfg(
        #         P=self.rfg_sat_vap_out.P,
        #         h=h
        #     )
        h_rfg_avg = (self.rfg_in.h + self.rfg_sat_vap_out.h) / 2
        rfg_mean = self._Rfg(
            P=self.rfg_sat_vap_out.P,
            h=h_rfg_avg
        )
        return rfg_mean
