from bert_schemas import job as job_schema

from oqtant.schemas.interpolation import interpolate_1d_list


class RfSequence(job_schema.RfEvaporation):
    """A class that represents a sequence of radiofrequency powers/frequencies in time"""

    def __init__(
        self,
        times: list = [0],
        powers: list = [0],
        frequencies: list = [0],
        interpolation: str = "LINEAR",
    ):
        super().__init__(
            times_ms=times,
            powers_mw=powers,
            frequencies_mhz=frequencies,
            interpolation=interpolation,
        )

    def evolve(self, duration: float, power: float, frequency: float):
        """Evolves the RfSequence in time by appending time/frequency/powers as necessary.

        Args:
            duration (float): Time (in ms) over which specified evolution takes place.
            power (float): RF power (in mW) to assume at the end of the evolution step.
            frequency (float): RF frequency (in mHz) to assume at the end of the evolution step.
        """
        self.times_ms.append(self.times_ms[-1] + duration)
        self.powers_mw.append(power)
        self.frequencies_mhz.append(frequency)

    def get_frequencies(self, times: list) -> list:
        """Calculates the frequency of the RfSequence object at the specified times.

        Args:
            times (list): Times (in ms) at which the RF frequencies are calculated.
        Returns:
            list: Calculated frequencies (in MHz) at the specified times.
        """
        return interpolate_1d_list(
            self.times_ms,
            self.frequencies_mhz,
            times,
            self.interpolation,
        )

    def get_powers(self, times: list) -> list:
        """Calculates RF evaporation powers at the specified times.
        Args:
            times (list): Times (in ms) at which the RF powers are calculated.
        Returns:
            list: RF powers (in mW) at the specified times.
        """
        return interpolate_1d_list(
            self.times_ms, self.powers_mw, times, self.interpolation
        )


class RfEvap(RfSequence):
    """A class that represents the forced RF evaporation that cools atoms to quantum degeneracy."""

    def __init__(
        self,
        times: list = [0],
        powers: list = [0],
        frequencies: list = [0],
        interpolation: str = "LINEAR",
    ):
        super().__init__(
            times=self.shift_times_negative(times),
            powers=powers,
            frequencies=frequencies,
            interpolation=interpolation,
        )

    @classmethod
    def from_input(cls, rf_evaporation: job_schema.RfEvaporation):
        """
        Creates a new instance of the class using the given `rf_evaporation` object as input.

        Parameters:
            rf_evaporation (job_schema.RfEvaporation): The `RfEvaporation` object containing the data for the instance creation.

        Returns:
            cls: A new instance of the class with the specified properties.
        """
        rf_evap_times = [t for t in rf_evaporation.times_ms if t <= 0.0]
        rf_evap_freqs = [
            f
            for t, f in zip(rf_evaporation.times_ms, rf_evaporation.frequencies_mhz)
            if t <= 0.0
        ]
        rf_evap_pows = [
            p
            for t, p in zip(rf_evaporation.times_ms, rf_evaporation.powers_mw)
            if t <= 0.0
        ]
        return cls(
            times=rf_evap_times,
            powers=rf_evap_pows,
            frequencies=rf_evap_freqs,
            interpolation=rf_evaporation.interpolation,
        )

    def shift_times_negative(self, times: list) -> list:
        """
        Generate a new list of times by shifting each time in the input list
        by the negative value of the maximum time in the list.

        Parameters:
            times (list): A list of times.

        Returns:
            list: A new list of times shifted by the negative value of the maximum time.
        """
        return [t - max(times) for t in times]

    def evolve(self, duration: float, power: float, frequency: float):
        """
        Evolve the object with the given duration, power, and frequency.

        Parameters:
            duration (float): The duration of the evolution.
            power (float): The power of the evolution.
            frequency (float): The frequency of the evolution.

        Returns:
            None
        """
        super().evolve(duration, power, frequency)
        self.times_ms = self.shift_times_negative(self.times_ms)


# A RfShield is a CONSTANT evaporation occuring during the entire experimental phase
# any non-negative time in the rf_evaporation object of a program indicates a
# rf shield is desired for the entire duration of the experiment stage
class RfShield(RfSequence):
    """A class that represents an RF shield (at fixed frequency and power)
    being applied during the 'experiment' phase/stage."""

    def __init__(self, power: float = 0, frequency: float = 0, lifetime: float = 0):
        super().__init__(
            times=[lifetime],  # value(s) not used, just indicates shield is enabled
            powers=[power],
            frequencies=[frequency],
            interpolation="OFF",
        )

    @classmethod
    def from_input(cls, rf_evaporation: job_schema.RfEvaporation):
        """
        Create an instance of the class from the given rf_evaporation input.

        Parameters:
            rf_evaporation (job_schema.RfEvaporation): The input object containing the attributes for the instance creation.

        Returns:
            cls: An instance of the class created from the input.
        """
        if rf_evaporation.times_ms[-1] <= 0:
            return None
        else:
            return cls(
                lifetime=rf_evaporation.times_ms[-1],
                frequency=rf_evaporation.frequencies_mhz[-1],
                power=rf_evaporation.powers_mw[-1],
            )

    @property
    def lifetime(self):
        return self.times_ms[0]

    @property
    def frequency(self):
        return self.frequencies_mhz[0]

    @property
    def frequencies(self, times: list):
        return [self.frequencies_mhz[0]] * len(times)

    @property
    def power(self):
        return self.powers_mw[0]

    @property
    def powers(self, times: list):
        return [self.powers_mw[0]] * len(times)
