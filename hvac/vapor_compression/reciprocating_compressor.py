from scipy.optimize import root_scalar, fsolve
from hvac import Quantity
from hvac.fluids import Fluid, FluidState
from matplotlib import pyplot as plt
import numpy as np


class ReciprocatingCompressor:
    def __init__(
            self,
            volume_displacement: Quantity,
            clearance_fraction: Quantity,
            isentropic_efficiency: Quantity,
            refrigerant: Fluid
    ):
        """
        Parameters
        ----------
        volume_displacement: Quantity
            Displacement volume
        clearance_fraction: Quantity
            Volume fraction that remains in the cylinder after the exhaust stroke
        isentropic_efficiency: Quantity
            Isentropic efficiency
        polytropic_exponent: float
            Polytropic exponent
        refrigerant: Fluid
            Refrigerant
        """
        self.volume_displacement = volume_displacement
        self.clearance_fraction = clearance_fraction
        self.isentropic_efficiency = isentropic_efficiency
        self.refrigerant = refrigerant

        self.__speed = None
        self.__pressure_evaporation = None
        self.__pressure_condensation = None
        self.__specific_volume_suction = None
        self.__polytropic_exponent = None

    @property
    def speed(self) -> Quantity:
        """Get compressor speed."""
        return self.__speed

    @speed.setter
    def speed(self, value: Quantity):
        """Set compressor speed."""
        self.__speed = value

    @property
    def pressure_evaporation(self) -> Quantity:
        """Get evaporation pressure."""
        return self.__pressure_evaporation

    @pressure_evaporation.setter
    def pressure_evaporation(self, value: Quantity):
        """Set evaporation pressure."""
        self.__pressure_evaporation = value

    @property
    def pressure_condensation(self) -> Quantity:
        """Get condensation pressure."""
        return self.__pressure_condensation

    @pressure_condensation.setter
    def pressure_condensation(self, value: Quantity):
        """Set condensation pressure."""
        self.__pressure_condensation = value

    @property
    def specific_volume_suction(self) -> Quantity:
        """Get specific volume of suction gas at compressor inlet."""
        return self.__specific_volume_suction

    @specific_volume_suction.setter
    def specific_volume_suction(self, value: Quantity):
        """Set specific volume of suction gas at compressor inlet."""
        self.__specific_volume_suction = value

    @property
    def polytropic_exponent(self) -> float:
        """Get polytropic exponent."""
        return self.__polytropic_exponent

    @polytropic_exponent.setter
    def polytropic_exponent(self, value: float):
        """Set polytropic exponent."""
        self.__polytropic_exponent = value


    def __call__(self,
                 speed: Quantity,
                 temperature_evaporation: Quantity,
                 temperature_condensation: Quantity,
                 superheating: Quantity):
        self.pressure_evaporation = self.refrigerant(T=temperature_evaporation,
                                                     x=Quantity(1, 'frac')).P.to('bar')
        self.pressure_condensation = self.refrigerant(T=temperature_condensation,
                                                      x=Quantity(1, 'frac')).P.to('bar')
        state_evaporation_superheated = self.refrigerant(T=temperature_evaporation.to('K') +
                                                           superheating,
                                                         P=self.pressure_evaporation)
        self.specific_volume_suction = 1 / state_evaporation_superheated.rho
        self.speed = speed.to('1/s')

        # find polytropic exponent that matches isentropic efficiency
        def entropy_deviation(polytropic_exponent):
            self.polytropic_exponent = polytropic_exponent
            entropy_deviation = (self.state_refrigerant_out.s - self.state_refrigerant_in.s).to(
                'J / kg / K').magnitude
            return entropy_deviation

        isentropic_exponent = root_scalar(entropy_deviation, bracket=[1.12, 1.22]).root
        self.polytropic_exponent = isentropic_exponent
        W_dot_isentropic = self.W_dot.to('W')

        def isentropic_efficiency_deviation(polytropic_exponent):
            self.polytropic_exponent = polytropic_exponent
            W_dot = self.W_dot.to('W')
            isentropic_efficiency = (W_dot_isentropic / W_dot).magnitude
            isentropic_efficiency_deviation = isentropic_efficiency - self.isentropic_efficiency.magnitude
            return isentropic_efficiency_deviation

        self.polytropic_exponent = fsolve(isentropic_efficiency_deviation, isentropic_exponent)[0]

        return self.m_dot_refrigerant, self.W_dot

    @property
    def volumetric_efficiency(self) -> Quantity:
        volumetric_efficiency = (1.0 - self.clearance_fraction *
                                 ((self.pressure_condensation / self.pressure_evaporation) **
                                  (1 / self.polytropic_exponent) - 1.0))
        return volumetric_efficiency

    @property
    def m_dot_refrigerant(self) -> Quantity:
        m_dot_refrigerant = (self.volumetric_efficiency * self.speed * self.volume_displacement /
                             self.specific_volume_suction)
        return m_dot_refrigerant

    @property
    def W_dot(self) -> Quantity:
        W_dot = self.m_dot_refrigerant * (self.state_refrigerant_out.h -
                                          self.state_refrigerant_in.h)
        return W_dot

    @property
    def state_refrigerant_in(self) -> FluidState:
        state_refrigerant_in = self.refrigerant(P=self.pressure_evaporation,
                                                rho=1 / self.specific_volume_suction)
        return state_refrigerant_in

    @property
    def state_refrigerant_out(self) -> FluidState:
        state_refrigerant_out = self.refrigerant(T=self.temperature_out,
                                                 P=self.pressure_condensation)
        return state_refrigerant_out

    @property
    def temperature_in(self) -> Quantity:
        return self.state_refrigerant_in.T

    @property
    def temperature_out(self) -> Quantity:
        return self.temperature_in * (self.pressure_condensation / self.pressure_evaporation) ** (
                (self.polytropic_exponent - 1) / self.polytropic_exponent)

if __name__ == '__main__':
    refrigerant = Fluid('R134a')
    isentropic_efficiencies = np.linspace(0.1, 1.0, 11)
    powers = []
    for isentropic_efficiency in isentropic_efficiencies:
        compressor = ReciprocatingCompressor(
            volume_displacement=Quantity(6.00, 'cm^3'),
            clearance_fraction=Quantity(0.06, 'frac'),
            isentropic_efficiency=Quantity(isentropic_efficiency, 'frac'),
            refrigerant=refrigerant
        )
        compressor(speed=Quantity(50.0, '1/s'),
                    temperature_evaporation=Quantity(0.0, 'degC'),
                    temperature_condensation=Quantity(60.0, 'degC'),
                    superheating=Quantity(5.0, 'K'))
        powers.append(compressor.W_dot.to('W').magnitude)
    plt.plot(isentropic_efficiencies, powers)
    plt.xlabel('Isentropic efficiency')
    plt.ylabel('Power [W]')
    plt.show()

