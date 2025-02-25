"""
Simple fan model for volumetric flow rate and power consumption

(C) 2025 Daniel Haag. All rights reserved.
"""

# 3rd party imports
import numpy as np


class Fan:
    def __init__(self, V_dot_0Pa: float = 600.0, dp_max: float = 230.0, P_max: float = 80.0):
        """
        Initialize a fan object based on nominal datasheet values.

        Assumptions for this revised model:
        - The control signal (0 ≤ signal ≤ 1) represents the fraction of maximum speed.
        - At zero pressure drop and full speed (signal = 1), the volumetric flow rate is V_dot_0Pa.
        - The static pressure scales with the square of the speed: dp_max(s) = dp_max * signal^2.
        - The fan performance at a given speed is modeled as:
              dp = dp_max * signal^2 * (1 - (V_dot/(V_dot_0Pa * signal))^2)
          which can be rearranged to compute the volumetric flow rate:
              V_dot = V_dot_0Pa * signal * sqrt(1 - dp/(dp_max * signal^2))
          for dp ≤ dp_max * signal^2.
        - Electrical power consumption scales with the cube of the signal:
              P = P_max * signal^3

        Parameters
        ----------
        V_dot_0Pa : float
            Volume flow rate at 0 Pa (and full speed) in m^3/h.
        dp_max : float
            Maximum static pressure (at full speed) in Pa.
        P_max : float
            Maximum electrical power in W (at full speed).
        """
        self.V_dot_0Pa = V_dot_0Pa
        self.dp_max = dp_max
        self.P_max = P_max

    def V_dot(self, signal: float, dp: float) -> float:
        """
        Compute the volumetric flow rate for a given control signal and pressure loss.

        The flow rate is given by:
            V_dot = V_dot_0Pa * signal * sqrt(1 - dp/(dp_max*signal^2))
        This is valid for dp <= dp_max * signal^2.

        Parameters
        ----------
        signal : float
            Control signal (0 ≤ signal ≤ 1), representing the fraction of maximum speed.
        dp : float
            Pressure loss in Pa.

        Returns
        -------
        float
            Volumetric flow rate in m^3/h.
        """
        if not 0 <= signal <= 1.1: # 10 % tolerance for interoperability
            print(f"FanWarning: Required signal {round(signal, 2)} exceeds 1!")

        available_dp = self.dp_max * signal ** 2
        if 1.10 * dp > available_dp: # 10 % tolerance for interoperability
            print(f"FanWarning: Pressure loss {round(dp, 2)} exceeds available "
                  f"head {round(available_dp, 2)}!")

        return self.V_dot_0Pa * signal * np.sqrt(1 - dp / available_dp)

    def P(self, signal: float, *args, **kwargs) -> float:
        """
        Compute the electrical power consumption for a given control signal.

        The power consumption is modeled as:
            P = P_max * signal^3

        Parameters
        ----------
        signal : float
            Control signal (0 ≤ signal ≤ 1).

        Returns
        -------
        float
            Electrical power consumption in W.
        """
        _ = args, kwargs  # Unused arguments; maintain compatibility with legacy methods
        return self.P_max * signal ** 3

    def signal(self, V_dot: float, dp: float) -> float:
        """
        Compute the required control signal for a given volumetric flow rate and pressure loss.

        The equation:
            V_dot = V_dot_0Pa * signal * sqrt(1 - dp/(dp_max*signal^2))
        can be rearranged to solve for signal. Squaring both sides yields:
            (V_dot/V_dot_0Pa)^2 = signal^2 - dp/dp_max.
        Thus, the required signal is:
            signal = sqrt((V_dot/V_dot_0Pa)^2 + dp/dp_max)

        Note: This inversion is valid as long as dp ≤ dp_max*signal^2.

        Parameters
        ----------
        V_dot : float
            Desired volumetric flow rate in m^3/h.
        dp : float
            Pressure loss in Pa.

        Returns
        -------
        float
            Required control signal (0 ≤ signal ≤ 1).
        """
        required_signal = np.sqrt((V_dot / self.V_dot_0Pa) ** 2 + dp / self.dp_max)
        if required_signal > 1.10:  # 10 % tolerance for interoperability
            print(f"FanWarning: Required signal {round(required_signal, 2)} exceeds 1!")
        return required_signal


if __name__ == '__main__':
    # Example usage:
    fan = Fan(V_dot_0Pa=1000.0, dp_max=500.0, P_max=100.0)