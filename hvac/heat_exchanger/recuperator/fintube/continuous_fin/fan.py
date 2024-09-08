"""
Simple fan models for cooling units.

Author: Daniel Haag
Date: 08.09.2024
"""


class Fan:
    def __init__(self, V_dot_n: float = 865.0, V_dot: float = 865, pressure_loss: float = 0.0,
                 rpm_n: float = 4800.0, P_el_n: float = 110.0, eta_fan: float = 0.7):
        """Initialize a fan object based on nominal values from datasheet

        Pressure loss dependency is not considered in this model. Simple assumptions:
        - Volume flow rate scales with speed
        - (Electric) Power scales with volume flow rate

        Parameters
        ----------
        V_dot_n: float
            Nominal volume flow rate in m^3/h
        V_dot: float
            Current volume flow rate in m^3/h
        pressure_loss: float
            Current Pressure loss in Pa
        rpm_n: float
            Nominal speed in rpm
        P_el_n: float
            Nominal electrical power in W
        eta_fan: float
            Assumed fan efficiency (default: 0.7)


        Raises
        ------
        ValueError
            If volume flow rate is less than 10% of nominal value
        """
        if V_dot < 0.1 * V_dot_n:
            raise ValueError('Volume flow rate is below 10% of nominal value')
        self.V_dot_n = V_dot_n
        self.V_dot = V_dot
        self.pressure_loss = pressure_loss
        self.rpm_n = rpm_n
        self.P_el_n = P_el_n
        self.eta_fan = eta_fan

    @property
    def power(self) -> float:
        """Compute the electrical power consumption of the fan based on current volume flow rate

        Returns
        -------
        float
            Electrical power consumption in W
        """
        return (self.P_el_n * (self.V_dot / self.V_dot_n) +
                (self.V_dot / 3600.0) * self.pressure_loss / self.eta_fan)

    @property
    def speed(self) -> float:
        """Compute the speed of the fan based on current volume flow rate

        Returns
        -------
        float
            Speed in rpm
        """
        return self.rpm_n * (self.V_dot / self.V_dot_n)


if __name__ == '__main__':
    fan = Fan(pressure_loss=10.0)
    print(f'Power: {fan.power} W')
    print(f'Speed: {fan.speed} rpm')