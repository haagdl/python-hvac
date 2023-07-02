import numpy as np
from hvac import Quantity
from hvac.fluids import HumidAir, Fluid, FluidState, CP_HUMID_AIR
from hvac.heat_transfer.heat_exchanger.fin_tube import core


Q_ = Quantity
HexCore = core.plain_fin_tube.PlainFinTubeHeatExchangerCore


class PlainFinTubeCounterFlowDesuperheatCondenser:
    
    def __init__(
        self,
        L1: Quantity, L3: Quantity,
        S_t: Quantity, S_l: Quantity,
        D_i: Quantity, D_o: Quantity,
        t_f: Quantity, N_f: Quantity,
        k_f: Quantity = Q_(237, 'W / (m * K)')
    ) -> None:
        """Creates a `PlainFinTubeCounterFlowCondensingCondenser` instance by
        defining the known dimensions of the heat exchanger core and its
        geometrical characteristics.

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
        self._hex_core = HexCore(
            L1, L3,
            S_t, S_l,
            D_i, D_o,
            t_f, N_f, k_f
        )
        self.rfg_in: FluidState | None = None
        self.rfg_sat_vap_out: FluidState | None = None
        self.air_in: HumidAir | None = None
        self.air_out: HumidAir | None = None
        self.Q: Quantity | None = None
        self.dT_air: Quantity | None = None
        self.L2_desuperheat: Quantity | None = None
        self.Rfg: Fluid | None = None
        self.P_rfg: Quantity | None = None

    def set_fixed_operating_conditions(
        self,
        m_dot_air: Quantity,
        rfg_in: FluidState,
        m_dot_rfg: Quantity
    ) -> None:
        """Sets the fixed operating conditions on the desuperheating region of
        the condenser.

        Parameters
        ----------
        m_dot_air:
            Mass flow rate of air.
        rfg_in:
            State of refrigerant entering the condenser.
        m_dot_rfg:
            Mass flow rate of the refrigerant.

        Returns
        -------
        None
        """
        self._hex_core.m_dot_ext = m_dot_air
        self.rfg_in = rfg_in
        self._hex_core.m_dot_int = m_dot_rfg
        self.rfg_sat_vap_out = self.rfg_in.fluid(
            P=self.rfg_in.P,
            x=Q_(1.0, 'frac')
        )
        self.Q = self._hex_core.m_dot_int * (self.rfg_in.h - self.rfg_sat_vap_out.h)
        self.dT_air = self.Q / (self._hex_core.m_dot_ext * CP_HUMID_AIR)
        self.Rfg = rfg_in.fluid
        self.P_rfg = rfg_in.P

    def set_air_in(self, air_in: HumidAir) -> None:
        self.air_in = air_in
        T_air_out = self.air_in.Tdb + self.dT_air
        self.air_out = HumidAir(Tdb=T_air_out, W=self.air_in.W)

    def _get_mean_fluid_states(self) -> tuple[FluidState, HumidAir]:
        """Returns the mean states of refrigerant and air across the
        desuperheating region of the condenser.
        """
        C_air = (self.air_in.cp + self.air_out.cp) / 2 * self._hex_core.m_dot_ext
        C_rfg = (self.rfg_in.cp + self.rfg_sat_vap_out.cp) / 2 * self._hex_core.m_dot_int
        C_min = min(C_air, C_rfg)
        C_max = max(C_air, C_rfg)
        C_r = C_min / C_max
        if C_r >= 0.5:
            T_rfg_mean = (self.rfg_in.T.to('K') + self.rfg_sat_vap_out.T.to('K')) / 2
            T_air_mean = (self.air_in.Tdb.to('K') + self.air_out.Tdb.to('K')) / 2
            rfg_mean = self.Rfg(T=T_rfg_mean, P=self.P_rfg)  # we assume constant condenser pressure
            air_mean = HumidAir(Tdb=T_air_mean, W=self.air_in.W)
            return rfg_mean, air_mean
        else:
            if C_max == C_rfg:
                # refrigerant has the smallest temperature change
                T_rfg_mean = (self.rfg_in.T.to('K') + self.rfg_sat_vap_out.T.to('K')) / 2
                DT_max = T_rfg_mean - self.air_in.Tdb.to('K')
                DT_min = T_rfg_mean - self.air_out.Tdb.to('K')
                LMTD = (DT_max - DT_min) / np.log(DT_max / DT_min)
                T_air_mean = T_rfg_mean - LMTD
                rfg_mean = self.Rfg(T=T_rfg_mean, P=self.P_rfg)
                air_mean = HumidAir(Tdb=T_air_mean, W=self.air_in.W)
                return rfg_mean, air_mean
            else:  # C_max == C_ext
                # air has the smallest temperature change
                T_air_mean = (self.air_in.Tdb.to('K') + self.air_out.Tdb.to('K')) / 2
                DT_max = self.rfg_in.T.to('K') - T_air_mean
                DT_min = self.rfg_sat_vap_out.T.to('K') - T_air_mean
                LMTD = (DT_max - DT_min) / np.log(DT_max / DT_min)
                T_rfg_mean = T_air_mean + LMTD
                rfg_mean = self.Rfg(T=T_rfg_mean, P=self.P_rfg)
                air_mean = HumidAir(Tdb=T_air_mean, W=self.air_in.W)
                return rfg_mean, air_mean

    def determine_flow_length(self, L2_ini: Quantity) -> Quantity:
        """Determine the flow length needed to desuperheat the refrigerant from
        the inlet state to the saturated vapor state.
        """
        def _get_new_flow_length(A_int: Quantity) -> Quantity:
            k1 = self._hex_core.int.geo.L3 / self._hex_core.int.geo.S_t
            k2 = A_int / (np.pi * self._hex_core.int.geo.D_i * self._hex_core.int.geo.L1)
            n = 2 * k2 - 1
            d = 2 * k1 - 1
            L2 = (n / d) * self._hex_core.int.geo.S_l
            return L2.to('m')

        L2 = L2_ini.to('m')
        rfg_mean, air_mean = self._get_mean_fluid_states()
        self._hex_core.int.fluid_mean = rfg_mean
        self._hex_core.ext.fluid_mean = air_mean
        i = 0
        i_max = 10
        tol_L2 = Q_(0.001, 'm')
        while i < i_max:
            self._hex_core.L2 = L2
            h_int = self._hex_core.int.h
            T_wall = self._hex_core.T_wall
            R_int = (rfg_mean.T - T_wall) / self.Q
            A_int = 1 / (R_int * h_int)
            L2_new = _get_new_flow_length(A_int.to('m ** 2'))
            dev_L2 = abs(L2_new - L2)
            if dev_L2 <= tol_L2:
                return L2_new
            L2 = L2_new
            i += 1
        else:
            raise ValueError(
                "no acceptable solution found for desuperheating flow length"
            )

    @property
    def eps(self) -> float:
        rfg_mean = self._hex_core.int.fluid_mean
        air_mean = self._hex_core.ext.fluid_mean
        C_rfg = rfg_mean.cp * self._hex_core.m_dot_int
        C_air = air_mean.cp * self._hex_core.m_dot_ext
        C_min = min(C_rfg, C_air)
        Q_max = C_min * (self.rfg_in.T - self.air_in.Tdb)
        eps = self.Q / Q_max
        return eps

    @property
    def dP_air(self) -> Quantity:
        dP_air = self._hex_core.ext.get_pressure_drop(self.air_in, self.air_out)
        return dP_air
