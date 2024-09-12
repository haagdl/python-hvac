from typing import Type
from .. import Quantity
from ..fluids import Fluid, FluidState

Q_ = Quantity


class ReciprocatingCompressor:
    """
    Model of an ideal reciprocating compressor.
    The clearance volume efficiency and polytropic work relations assume that
    there are no pressure drops across the valves and that the compression and
    expansion processes are ideal and polytropic. These relations give an
    upper limit for the performance.
    """

    def __init__(
            self,
            V_dis: Quantity,
            C: Quantity,
            speed: Quantity,
            n: float,
            refrigerant: Fluid,
    ) -> None:
        """
        Parameters
        ----------
        V_dis: Quantity
            Displacement volume.
        C: Quantity
            Clearance volume fraction.
        speed: Quantity
            Compressor speed.
        n: float
            Polytropic exponent.
        refrigerant: Fluid
            Type of refrigerant.
        """
        self.V_dis = V_dis
        self.C = C
        self.speed = speed
        self.n = n
        self.refrigerant = refrigerant

        self._P_cnd: Quantity = None
        self._P_evp: Quantity = None
        self._v_suc: Quantity = None

    @property
    def P_cnd(self) -> Quantity:
        """Get condenser pressure."""
        return self._P_cnd

    @P_cnd.setter
    def P_cnd(self, v: Quantity) -> None:
        """Set condenser pressure."""
        self._P_cnd = v

    @property
    def P_evp(self) -> Quantity:
        """Get evaporator pressure."""
        return self._P_evp

    @P_evp.setter
    def P_evp(self, v: Quantity) -> None:
        """Set evaporator pressure."""
        self._P_evp = v

    @property
    def v_suc(self) -> Quantity:
        """Get specific volume of suction gas at compressor inlet."""
        return self._v_suc

    @v_suc.setter
    def v_suc(self, v: Quantity) -> None:
        """Set specific volume of suction gas at compressor inlet."""
        self._v_suc = v

    @property
    def eta_vol(self) -> Quantity:
        """Get clearance volumetric efficiency at given working conditions."""
        eta_vol = 1.0 - self.C * ((self.P_cnd / self.P_evp) ** (1 / self.n) - 1.0)
        return eta_vol

    @property
    def m_dot(self) -> Quantity:
        """Get mass flow rate of refrigerant at given working conditions."""
        m_dot = self.eta_vol * self.speed * self.V_dis / self.v_suc
        return m_dot

    @property
    def W_dot(self) -> Quantity:
        """Get compressor power at given working conditions."""
        W_dot = self.m_dot * (self.discharge_gas.h - self.suction_gas.h)
        return W_dot

    @property
    def suction_gas(self) -> FluidState:
        """Get state of suction gas at compressor inlet."""
        return self.refrigerant(P=self.P_evp, rho=1 / self.v_suc)

    @property
    def T_suc(self) -> Quantity:
        """Get temperature of suction gas at compressor inlet."""
        return self.suction_gas.T

    @property
    def T_dis(self) -> Quantity:
        """Get temperature of discharge gas at compressor outlet."""
        return self.T_suc * (self.P_cnd / self.P_evp) ** ((self.n - 1) / self.n)

    @property
    def discharge_gas(self) -> FluidState:
        """Get state of discharge gas at compressor outlet."""
        return self.refrigerant(P=self.P_cnd, T=self.T_dis)

    @property
    def Q_dot(self) -> Quantity:
        """Get cooling capacity of compressor at given working conditions."""
        condenser_out = self.refrigerant(P=self.P_cnd, x=Q_(0, 'frac'))
        evaporator_in = self.refrigerant(P=self.P_evp, h=condenser_out.h)
        evaporator_out = self.refrigerant(P=self.P_evp, rho=1 / self.v_suc)
        Q_dot = self.m_dot * (evaporator_out.h - evaporator_in.h)
        return Q_dot

    @property
    def COP(self) -> Quantity:
        """Get COP of compressor under given working conditions."""
        return self.Q_dot / self.W_dot
