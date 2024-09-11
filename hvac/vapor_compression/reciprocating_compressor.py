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
        refrigerant_type: Fluid,
        eta_is: Quantity = Q_(0.8, 'frac'),
        eta_mech: Quantity = Q_(0.9, 'frac'),
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
        refrigerant_type: Type[Refrigerant]
            Type of refrigerant.
    eta_is: Quantity
        Isentropic efficiency: The ratio of the actual work required for compression to the ideal
        isentropic work (i.e., the work required if the compression process were isentropic).
        This efficiency accounts for deviations from ideal behavior due to irreversibilities
        such as heat transfer, friction, and other real-world losses during the compression process.
        It reflects how close the actual compression process is to an ideal isentropic process.
        (default is 0.8)
    eta_mech: Quantity
        Mechanical efficiency: The ratio of the actual work delivered by the compressor to the
        total input work provided to the compressor. This accounts for mechanical losses such as
        friction in the moving parts (e.g., pistons, bearings, valves) and energy dissipation due to
        imperfect mechanical transmission. Mechanical efficiency represents how effectively the
        compressor converts the input work into useful work for compressing the refrigerant.
        (default is 0.9)
        """
        self.V_dis = V_dis
        self.C = C
        self.speed = speed
        self.n = n
        self.Refrigerant = refrigerant_type

        self.eta_is = eta_is
        self.eta_mech = eta_mech

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
        eta_vol = 1 + self.C - self.C * (self.P_cnd / self.P_evp) ** (1 / self.n)
        return eta_vol

    @property
    def m_dot(self) -> Quantity:
        """Get mass flow rate of refrigerant at given working conditions."""
        m_dot = self.eta_vol * self.speed * self.V_dis / self.v_suc
        return m_dot

    @property
    def W_dot(self) -> Quantity:
        """Get compressor power at given working conditions."""
        e = self.n / (self.n - 1)
        a = self.eta_vol * self.speed * self.V_dis * self.P_evp * e
        b = (self.P_cnd / self.P_evp) ** (1 / e) - 1
        W_dot = a * b
        return W_dot / (self.eta_is * self.eta_mech)

    @property
    def suction_gas(self) -> FluidState:
        """Get state of suction gas at compressor inlet."""
        return self.Refrigerant(P=self.P_evp, rho=1 / self.v_suc)

    @suction_gas.setter
    def suction_gas(self, refrigerant: FluidState) -> None:
        """Set state of suction gas at compressor inlet."""
        self.P_evp = refrigerant.P
        self.v_suc = 1 / refrigerant.rho

    @property
    def v_dis(self) -> Quantity:
        """Get specific volume of discharge gas at compressor outlet."""
        v_dis = (self.P_evp * (self.v_suc ** self.n) / self.P_cnd) ** (1 / self.n)
        return v_dis

    @property
    def discharge_gas(self) -> FluidState:
        """Get state of discharge gas at compressor outlet."""
        return self.Refrigerant(P=self.P_cnd, rho=1 / self.v_dis)

    @property
    def Q_dot(self) -> Quantity:
        """Get cooling capacity of compressor at given working conditions."""
        condenser_out = self.Refrigerant(P=self.P_cnd, x=Q_(0, 'frac'))
        evaporator_in = self.Refrigerant(P=self.P_evp, h=condenser_out.h)
        evaporator_out = self.Refrigerant(P=self.P_evp, rho=1 / self.v_suc)
        Q_dot = self.m_dot * (evaporator_out.h - evaporator_in.h)
        return Q_dot

    @property
    def COP(self) -> Quantity:
        """Get COP of compressor under given working conditions."""
        return self.Q_dot / self.W_dot
