"""
Simple fan models for cooling units.

Author: Daniel Haag
Date: 08.09.2024
"""
import numpy as np
from matplotlib import pyplot as plt


class Fan:

    def __init__(self, V_dot_0Pa: float = 1063.0, dp_max: float = 500.0, P_max: float = 110.0):
        """Initialize a fan object based on nominal values from datasheet

        The fan model assumes that the maximum volume flow rate is reached at 0 Pa pressure loss.
        A pwm signal is used to control the fan power and subsequently the volume flow rate.

        The following is assumed:
        - The fan power consumption is proportional to the signal
        - The fan efficiency is assumed to be constant
        - The fan model is based on the following formula:
            V_dot = V_dot_0Pa * signal^2 * (1 - (dp / dp_max)^2)
            P = P_max * signal


        Parameters
        ----------
        V_dot_0Pa: float
            Volume flow rate at 0 Pa in m^3/h
        dp_max: float
            Maximum pressure difference in Pa (no volume flow rate at this pressure)
        P_max: float
            Maximum electrical power in W (with signal = 1)
        """
        self.V_dot_0Pa = V_dot_0Pa
        self.dp_max = dp_max
        self.P_max = P_max

    def V_dot(self, signal: float, dp: float) -> float:
        """Compute the volume flow rate based on signal and pressure difference

        Parameters
        ----------
        signal: float
            Control signal (0 <= signal <= 1)
        dp: float
            Pressure loss in Pa

        Returns
        -------
        float
            Volume flow rate in m^3/h
        """
        if dp > self.dp_max:
            raise ValueError('Pressure difference is greater than maximum pressure difference')
        if not 0 <= signal <= 1:
            print(f'FanWarning: Signal {round(signal, 2)} is clipped to [0, 1]!')
            print('Real world fan could not cope with this signal!')
            signal = max(0.0, min(1.0, signal))
        return self.V_dot_0Pa * signal ** (1 / 2) * (1 - (dp / self.dp_max) ** 2)

    def P(self, signal: float, dp: float) -> float:
        """Compute the electrical power consumption based on signal and pressure difference

        Parameters
        ----------
        signal: float
            Control signal of the pwm module (0 <= signal <= 1)
        dp: float
            Pressure loss in Pa

        Returns
        -------
        float
            Electrical power consumption in W

        Raises
        ------
        ValueError
            If pressure difference is greater than maximum pressure difference or
            signal is not in range [0, 1]
        """
        _ = dp
        if dp > self.dp_max:
            raise ValueError('Pressure difference is greater than maximum pressure difference')
        if not 0 <= signal <= 1:
            raise ValueError('Signal is not in range [0, 1]')
        return self.P_max * signal

    def signal(self, V_dot: float, dp: float) -> float:
        """Compute the control signal based on the required volume flow rate and pressure loss

        Parameters
        ----------
        V_dot: float
            Volume flow rate in m^3/h
        dp: float
            Pressure loss in Pa

        Returns
        -------
        float
            Power based control signal of the pwm module (0 <= signal <= 1)

        Raises
        ------
        ValueError
            If pressure difference is greater than maximum pressure difference
        """
        if dp > self.dp_max:
            raise ValueError('Pressure difference is greater than maximum pressure difference')
        return V_dot / self.V_dot_0Pa / (1 - (dp / self.dp_max) ** 2) ** 0.5


if __name__ == '__main__':
    fan = Fan(V_dot_0Pa=1000.0, dp_max=500.0, P_max=100.0)
    signals = np.linspace(0, 1, 100)
    dps = np.linspace(0, 400, 100)
    V_dots = []
    Ps = []
    for dp in dps:
        V_dots_ = [fan.V_dot(signal, dp) for signal in signals]
        V_dots.append(V_dots_)
        Ps_ = [fan.P(signal, dp) for signal in signals]
        Ps.append(Ps_)
    # plot different cures for signals over presssure delta for V_dot and P in 2 subplots
    fig, axs = plt.subplots(2, 1)
    for i, dp in enumerate(dps):
        axs[0].plot(signals, V_dots[i], label=f'dp: {dp}')
        axs[1].plot(signals, Ps[i], label=f'dp: {dp}')
    axs[0].set_title('V_dot')
    axs[1].set_title('P')
    plt.show()
