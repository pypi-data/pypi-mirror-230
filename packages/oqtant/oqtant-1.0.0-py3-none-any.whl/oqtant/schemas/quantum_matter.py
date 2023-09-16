import warnings
from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
from bert_schemas import job as job_schema
from pydantic import BaseModel, confloat

from oqtant.schemas.interpolation import interpolate_1d, interpolate_1d_list
from oqtant.schemas.job import OqtantJob
from oqtant.schemas.rf import RfEvap, RfShield

DEFAULT_RF_EVAP = RfEvap(
    times=[0, 50, 300, 800, 1100],
    powers=[600, 800, 600, 400, 400],
    frequencies=[21.12, 12.12, 5.12, 0.62, 0.02],
    interpolation="LINEAR",
)

DEFAULT_NAME = "quantum matter"
DEFAULT_LIFETIME = 10  # ms
DEFAULT_TEMPERATURE = 200  # nK
DEFAULT_TOF = 8  # ms
DEFAULT_IMAGE = job_schema.ImageType.TIME_OF_FLIGHT


class LandscapeSnapshot(job_schema.Landscape):
    """A class that represents a painted optical landscape / potential at a single
    point in (experiment stage) time.
    """

    def __init__(
        self,
        time: float = 0,
        positions: list = [-10, 10],
        potentials: list = [0, 0],
        interpolation: job_schema.InterpolationType = "LINEAR",
    ):
        super().__init__(
            time_ms=time,
            positions_um=positions,
            potentials_khz=potentials,
            spatial_interpolation=interpolation,
        )

    def get_potential(self, positions: list) -> list:
        """Samples the potential energy of this snapshot at the specified positions
        Args:
            positions (list): List of positions (in microns).
        Returns:
            list: Value of potential energy (in kHz) at the specified positions.
        """
        potentials = interpolate_1d_list(
            self.positions_um,
            self.potentials_khz,
            positions,
            self.spatial_interpolation,
        )
        return list(np.clip(potentials, 0.0, 100.0))

    def show_potential(self):
        """Plots the potential energy as a function of position for this snapshot"""
        positions = np.arange(-60, 60, 1, dtype=float)
        fig, ax = plt.subplots()
        lns = []
        labs = []
        plt.plot(positions, self.get_potential(positions))
        plt.plot(self.positions_um, self.get_potential(self.positions_um), ".")
        plt.xlabel("position (microns)", labelpad=6)
        plt.ylabel("potential energy (kHz)", labelpad=6)
        plt.title("LandscapeSnapshot potential energy profile")
        plt.xlim([-61, 61])
        plt.ylim([-1, 101])
        ax.legend(lns, labs, loc=0)
        plt.show()


# (potentially) dynamic landscape made up of snapshots
class Landscape(job_schema.OpticalLandscape):
    """Class that represents a dynamic painted-potential optical landscape constructed
    from individual (instantaneous time) LandscapeSnapshots
    """

    def __init__(
        self,
        snapshots: list = [LandscapeSnapshot(time=0), LandscapeSnapshot(time=2)],
    ):
        print("initializing Landscape...")
        optical_landscapes = []
        for snapshot in snapshots:
            print("copying to optical landscape")
            optical_landscapes.append(  # kludge!
                job_schema.Landscape(
                    time_ms=snapshot.time_ms,
                    positions_um=snapshot.positions_um,
                    potentials_khz=snapshot.potentials_khz,
                    spatial_interpolation=snapshot.spatial_interpolation,
                )
            )
        print("optical landscapes length:", len(optical_landscapes))
        super().__init__(landscapes=optical_landscapes)

    @classmethod
    def from_input(cls, optical_landscape: job_schema.OpticalLandscape):
        """
        Creates an instance of the class using the provided optical_landscape.

        Args:
            optical_landscape (job_schema.OpticalLandscape): The optical landscape object.

        Returns:
            cls: An instance of the class.
        """
        snapshots = cls._landscapes_to_snapshots(optical_landscape.landscapes)
        return cls(snapshots=snapshots)

    # extract LandscapeSnapshot abstract objects from backend data structure
    @property
    def snapshots(self) -> list[LandscapeSnapshot]:
        """
        Returns a list of landscape snapshots.

        Returns: A list of LandscapeSnapshot objects.
        """
        return self._landscapes_to_snapshots(self.landscapes)

    @staticmethod
    def _landscapes_to_snapshots(
        landscapes: list[job_schema.Landscape],
    ) -> list[LandscapeSnapshot]:
        """
        Convert a list of `job_schema.Landscape` objects to a list of `LandscapeSnapshot` objects.

        Args:
            landscapes (list[job_schema.Landscape]): A list of landscape objects.

        Returns:
            list[LandscapeSnapshot]: A list of snapshot objects representing the landscapes.
        """
        snapshots = []
        for landscape in landscapes:
            snapshot = LandscapeSnapshot()
            snapshot.__dict__.update(landscape.model_dump())
            snapshots.append(snapshot)
        return snapshots

    def get_potential(
        self, time: float, positions: list = list(np.linspace(-50, 50, 101))
    ) -> list:
        """Calculates potential energy at the specified time and positions.
        Args:
            time (float):
                Time (in ms) at which the potential energy is calculated.
            positions (list, optional):
                Positions at which the potential energy is calculated.
                Defaults to np.linspace(-100, 100, 201).
        Returns:
            list: Potential energies (in kHz) at specified time and positions.
        """
        potentials = [0] * len(positions)
        snaps = self.snapshots
        if len(snaps) < 2:
            return potentials
        snap_times = [snap.time_ms for snap in snaps]
        if time >= min(snap_times) and time <= max(snap_times):
            pre = next(snap for snap in snaps if snap.time_ms <= time)
            nex = next(snap for snap in snaps if snap.time_ms >= time)
            ts = [pre.time_ms, nex.time_ms]
            pots = [
                interpolate_1d(ts, [p1, p2], time, self.interpolation)
                for p1, p2 in zip(
                    pre.get_potential(positions), nex.get_potential(positions)
                )
            ]
            current = LandscapeSnapshot(
                time=time, positions=list(positions), potentials=pots
            )
            potentials = current.get_potential(positions)
            np.clip(potentials, 0.0, 100.0)
        return potentials

    def show_potential(self, times: list):
        """Plots the potential energy as a function of position at the specified times.

        Args:
            times (list): times (in ms) at which to evaluate the potential energy landscape.
        """
        positions = np.arange(-60, 60, 1, dtype=float)
        fig, ax = plt.subplots()
        lns = []
        labs = []
        for time in times:
            potentials = self.get_potential(time, positions)
            np.clip(potentials, 0, 100)
            color = next(ax._get_lines.prop_cycler)["color"]
            (ln,) = plt.plot(positions, potentials, color=color)
            # plt.plot(positions, potentials, ".", color=color)
            lns.append(ln)
            labs.append("t=" + str(time))
        plt.xlabel("position (microns)", labelpad=6)
        plt.ylabel("potential energy (kHz)", labelpad=6)
        plt.title("Landscape potential energy profile")
        plt.xlim([-61, 61])
        plt.ylim([-1, 101])
        ax.legend(lns, labs, loc=0)
        plt.show()


class Barrier(job_schema.Barrier):
    """Class that represents a painted optical barrier."""

    def __init__(
        self,
        position: float = 0,
        height: float = 0,
        width: float = 1,
        birth: float = 0,
        lifetime: float = 0,
        shape: job_schema.ShapeType = "GAUSSIAN",
        interpolation: job_schema.InterpolationType = "LINEAR",
    ):
        super().__init__(
            **{
                "times_ms": [birth],
                "positions_um": [position],
                "heights_khz": [height],
                "widths_um": [width],
                "shape": shape,
                "interpolation": interpolation,
            }
            if lifetime == 0
            else {
                "times_ms": [birth, birth + lifetime],
                "positions_um": [position] * 2,
                "heights_khz": [height] * 2,
                "widths_um": [width] * 2,
                "shape": shape,
                "interpolation": interpolation,
            }
        )

    @classmethod
    def from_input(cls, barrier: job_schema.Barrier):
        return cls(
            position=barrier.positions_um[0],
            height=barrier.heights_khz[0],
            width=barrier.widths_um[0],
            birth=barrier.times_ms[0],
            shape=barrier.shape,
            interpolation=barrier.interpolation,
        )

    @property
    def lifetime(self) -> float:
        """Extract the Barrier lifetime.

        Returns:
            float: Amount of time (in ms) that Barrier object will exist.
        """
        return self.death - self.birth

    @property
    def birth(self) -> float:
        """Extract the (experiment stage) time that the Barrier will be created.

        Returns:
            float: Time (in ms) at which the Barrier will start being projected.
        """
        return min(self.times_ms)

    @property
    def death(self) -> float:
        """Extract the (experiment stage) time that the Barrier will cease to exist.

        Returns:
            float: Time (in ms) at which the Barrier will stop being projected.
        """
        return max(self.times_ms)

    def evolve(self, duration: float, position=None, height=None, width=None):
        """Evolve the position, height, and/or width of a Barrier over a duration.
        Used to script a Barrier's behavior.

        Args:
            duration (float): Time (in ms) over which evolution should take place.
            position (float, optional): Position, in microns, to evolve to.
                                        Defaults to None (position remains unchanged).
            height (float, optional): Height, in kHz, to evolve to.
                                        Defaults to None (height remains unchanged).
            width (float, optional): Width, in microns, to evolve to.
                                        Defaults to None (width remains unchanged).
        """
        if position is None:
            position = self.positions_um[-1]
        if height is None:
            height = self.heights_khz[-1]
        if width is None:
            width = self.widths_um[-1]
        self.positions_um.append(position)
        self.heights_khz.append(height)
        self.widths_um.append(width)
        self.times_ms.append(self.times_ms[-1] + duration)

    def is_active(self, time: float) -> bool:
        """Queries if the barrier is active (exists) at the specified time
        Args:
            time (float): Time (in ms) at which the query is evaluated.
        Returns:
            bool: True if the barrier exists at the specified time.
        """
        return time >= self.times_ms[0] and time <= self.times_ms[-1]

    def get_positions(self, times: list, corrected: bool = False) -> list:
        """Calculate barrier position at the specified (experiment stage) times.

        Args:
            times (float): Times (in ms) at which positions are calculated.
        Returns:
            list: Barrier positions (in microns) at desired times.
        """
        if corrected:
            times = list(np.round(np.asarray(times), 1))
        return interpolate_1d_list(
            self.times_ms, self.positions_um, times, self.interpolation
        )

    def get_heights(self, times: list, corrected: bool = False) -> list:
        """Get barrier heights at the specified list of times

        Args:
            times (float): Times (ms) at which the heights are calculated.
        Returns:
            list: Barrier heights (kHz) at desired times.
        """
        if corrected:
            times = list(np.round(np.asarray(times), 1))
        return interpolate_1d_list(
            self.times_ms, self.heights_khz, times, self.interpolation
        )

    def get_widths(self, times: list, corrected: bool = False) -> list:
        """Get barrier widths at the specified list of times

        Args:
            times (float): Times (ms) at which the widths are calculated.
        Returns:
            list: Barrier widths (in microns) at desired times.
        """
        if corrected:
            times = list(np.round(np.asarray(times), 1))
        return interpolate_1d_list(
            self.times_ms, self.widths_um, times, self.interpolation
        )

    def get_potential(
        self, time: float, positions: list = range(-50, 51, 1), corrected: bool = False
    ) -> list:
        """Barrier potential energy at given positions at the specified time

        Args:
            time_ms (float): Time (in ms) at which the potential is calculated
            positions_um (list, optional):
                Positions (um) at which the potential energies are evaluated.
                Defaults to range(-50, 51, 1).

        Returns:
            list: Potential energies (in kHz) at the input positions
        """
        h = self.get_heights([time], corrected)[0]
        p = self.get_positions([time], corrected)[0]
        w = self.get_widths([time], corrected)[0]
        pots = [0] * len(positions)
        if h <= 0 or w <= 0 or not self.is_active(time):
            return pots
        if self.shape == "SQUARE":  # width = half width
            pots = [0 if (x < p - w or x > p + w) else h for x in positions]
        elif self.shape == "LORENTZIAN":  # width == HWHM (half-width half-max)
            pots = [h / (1 + ((x - p) / w) ** 2) for x in positions]
        elif self.shape == "GAUSSIAN":  # width = sigma (Gaussian width)
            pots = [h * np.exp(-((x - p) ** 2) / (2 * w**2)) for x in positions]
        return pots

    def show_dynamics(self, corrected: bool = False):
        """Plots the position, width, and height of the barrier over time."""
        tstart = min(self.times_ms)
        tstop = max(self.times_ms)
        times = np.linspace(
            tstart, tstop, num=int((tstop - tstart) / 0.1), endpoint=True
        )
        tstart = min(self.times_ms)
        tstop = max(self.times_ms)
        times = np.linspace(
            tstart, tstop, num=int((tstop - tstart) / 0.1), endpoint=True
        )
        fig, ax1 = plt.subplots()
        # plot position and width vs time
        style = "steps-pre" if corrected else "default"
        color = next(ax1._get_lines.prop_cycler)["color"]
        ax1.set_xlabel("time (ms)")
        ax1.set_ylabel("position or width (microns)")
        ax1.set_xlim([-1, self.times_ms[-1] + 1])
        ax1.set_ylim([-50, 50])
        (ln1,) = plt.plot(
            times, self.get_positions(times, corrected), color=color, drawstyle=style
        )
        plt.plot(
            self.times_ms,
            self.get_positions(self.times_ms, corrected),
            ".",
            color=color,
        )
        color = next(ax1._get_lines.prop_cycler)["color"]
        (ln2,) = plt.plot(
            times, self.get_widths(times, corrected), color=color, drawstyle=style
        )
        plt.plot(
            self.times_ms, self.get_widths(self.times_ms, corrected), ".", color=color
        )
        # plot height on the same time axis
        ax2 = ax1.twinx()
        ax2.set_ylabel("height (kHz)")
        ax2.set_ylim([0, 100])
        color = next(ax1._get_lines.prop_cycler)["color"]
        (ln3,) = plt.plot(
            times, self.get_heights(times, corrected), color=color, drawstyle=style
        )
        plt.plot(
            self.times_ms, self.get_heights(self.times_ms, corrected), ".", color=color
        )
        # shared setup
        color = next(ax1._get_lines.prop_cycler)["color"]
        ax1.legend([ln1, ln2, ln3], ["position", "width", "height"], loc="upper left")
        plt.title("Barrier dynamics")
        fig.tight_layout()
        plt.show()

    def show_potential(self, times: list = [0], corrected: bool = False):
        """Plot the potential energy vs. position at the given times.
        Args:
            times (list): times (in ms) at which the potential is calculated.
        """
        x_limits = [-61, 61]
        y_limits = [-1, max(self.heights_khz) + 1]
        positions = np.arange(min(x_limits), max(x_limits) + 1, 1)

        fig, ax1 = plt.subplots()
        ax = plt.gca()
        lns = []
        labs = []
        for time in times:
            color = next(ax._get_lines.prop_cycler)["color"]
            (ln,) = plt.plot(
                positions, self.get_potential(time, positions, corrected), color=color
            )
            plt.plot(
                positions,
                self.get_potential(time, positions, corrected),
                ".",
                color=color,
            )
            lns.append(ln)
            labs.append("t=" + str(time))

        plt.xlabel("position (microns)", labelpad=6)
        plt.ylabel("potential energy (kHz)", labelpad=6)
        plt.title("Barrier temporal snapshots")
        plt.xlim(x_limits)
        plt.ylim(y_limits)
        ax1.legend(lns, labs, loc=0)
        plt.show()


class QuantumMatter(BaseModel):
    """A class that represents user inputs to create and control quantum matter."""

    name: str = DEFAULT_NAME
    temperature: confloat(ge=0, le=1000) | None = DEFAULT_TEMPERATURE
    lifetime: confloat(ge=0, le=80) = DEFAULT_LIFETIME
    image: job_schema.ImageType = DEFAULT_IMAGE
    time_of_flight: float = DEFAULT_TOF
    rf_evap: RfEvap = DEFAULT_RF_EVAP
    rf_shield: RfShield | None = None
    barriers: list[Barrier] | None = None
    landscape: Landscape | None = None
    lasers: list[job_schema.Laser] | None = None
    note: str | None = None

    def __init__(self, *args, **kwargs):

        if kwargs.get("temperature") and kwargs.get("rf_evap"):
            warnings.warn(
                "Both 'temperature' and 'rf_evap' inputs provided, last rf_evap frequency will be altered by desired temperature."
            )

        # warn if object lifetime is not suitable for any optical potentials specified
        matter_lifetime = kwargs.get("lifetime", DEFAULT_LIFETIME)
        end_time = 0.0
        if kwargs.get("barriers"):
            for barrier in kwargs.get("barriers"):
                end_time = max(end_time, barrier.death)
        if kwargs.get("landscape"):
            for snapshot in kwargs.get("landscape").snapshots:
                end_time = max(end_time, snapshot.time_ms)
        if end_time > matter_lifetime:
            warnings.warn(
                "Specified 'lifetime' not sufficient for included barriers and/or landscapes."
            )

        super().__init__(*args, **kwargs)

    @classmethod
    def from_input(
        cls,
        name: str,
        input: job_schema.InputValues,
    ):

        evap = RfEvap.from_input(input.rf_evaporation)
        shield = RfShield.from_input(input.rf_evaporation)

        barriers = []
        if input.optical_barriers:
            for barrier in input.optical_barriers:
                barriers.append(Barrier.from_input(barrier))

        landscape = None
        if input.optical_landscape:
            landscape = Landscape.from_input(input.optical_landscape)

        return cls(
            name=name,
            lifetime=input.end_time_ms,
            time_of_flight=input.time_of_flight_ms,
            rf_evap=evap,
            rf_shield=shield,
            barriers=barriers,
            landscape=landscape,
            lasers=input.lasers,
        )

    @classmethod
    def from_oqtant_job(cls, job: OqtantJob, run: int = 1):
        """Convenience method for creating a QuantumMatter object from an existing OqtantJob."""
        return QuantumMatter.from_input(name=job.name, input=job.inputs[run - 1].values)

    @property
    def input(self) -> job_schema.InputValues:
        """Extracts InputValues needed to construct a job from this object."""
        return job_schema.InputValues(
            end_time_ms=self.lifetime,
            time_of_flight_ms=self.time_of_flight,
            image_type=self.image,
            rf_evaporation=self.rf_evaporation,
            optical_barriers=self.barriers,
            optical_landscape=self.landscape,
            lasers=self.lasers,
        )

    @property
    def rf_evaporation(self) -> job_schema.RfEvaporation:
        """Extracts RfEvaporation object from this object."""
        rf_evap_derived = deepcopy(self.rf_evap)
        rf_evap_derived.frequencies_mhz[-1] = (0.02 / 200) * self.temperature
        rf_evaporation = job_schema.RfEvaporation(
            times_ms=rf_evap_derived.times_ms,
            frequencies_mhz=rf_evap_derived.frequencies_mhz,
            powers_mw=rf_evap_derived.powers_mw,
            interpolation=rf_evap_derived.interpolation,
        )
        if self.rf_shield is not None:
            rf_evaporation.times_ms.append(self.lifetime)
            rf_evaporation.powers_mw.append(self.rf_shield.power)
            rf_evaporation.frequencies_mhz.append(self.rf_shield.frequency)

        return rf_evaporation

    def corrected_rf_power(self, frequency_mhz, power_mw):
        """
        Calculate the corrected RF power based on the given frequency and power.

        Args:
            frequency_mhz (float): The frequency in MHz.
            power_mw (float): The power in mW.

        Returns:
            float: The corrected RF power in mW.
        """
        # based on data taken from smallbert for power measured in dbm by a nearby pickup rf loop
        # as a function of the frequency (in MHz) and RF attenuator voltage (in volts)
        # the 'composer' turns payload powers of 0-1000 mW into voltages using a linear
        # relationship that maps 0-1000 mW to 0-5 V on the RF attenuator (5V = max power)
        voltage = power_mw * 5.0 / 1000.0  # payload power to attenuator voltage
        power_dbm = (
            -26.2 - 42 * np.exp(-0.142 * frequency_mhz) - 32.76 * np.exp(-1.2 * voltage)
        )
        return (1000.0 / 2.0e-3) * 10 ** (
            power_dbm / 10.0
        )  # dbm to mW with overall scaling

    def corrected_rf_powers(self, frequencies, powers):
        """Calculates corrected rf powers for the given equal-length lists of
        frequencies and powers.

        Args:
            frequencies (list): input frequencies (in MHz)
            powers (list): input powers (in mW)

        Returns:
            list: Corrected rf powers corresponding to the input lists as ordered pairs.
        """
        return [
            self.corrected_rf_power(freq, pow) for freq, pow in zip(frequencies, powers)
        ]

    def show_rf_dynamics(self, corrected: bool = False):
        """Plots the dynamics of a QuantumMatter object's RF output."""
        evap = RfEvap.from_input(self.rf_evaporation)
        shield = RfShield.from_input(self.rf_evaporation)
        tstart = min(evap.times_ms)
        evap_times = np.linspace(tstart, 0, num=int(abs(tstart) / 10), endpoint=True)
        fig, ax1 = plt.subplots()
        lns = []
        labs = []

        # plot of rf frequency vs time
        color = next(ax1._get_lines.prop_cycler)["color"]
        ax1.set_xlabel("time (ms)")
        ax1.set_ylabel("frequency (MHz)")
        ax1.set_ylim([0, 25])
        (ln1,) = plt.plot(evap_times, evap.get_frequencies(evap_times), color=color)
        lns.append(ln1)
        labs.append("frequency")
        plt.plot(evap.times_ms, evap.get_frequencies(evap.times_ms), ".", color=color)
        if shield is not None:
            plt.plot(
                [0, shield.lifetime],
                [shield.frequency] * 2,
                marker=".",
                color=color,
            )

        # plot of rf power vs time, on the same time axis as ax1
        ax2 = ax1.twinx()
        ax2.set_ylim([0, 1000])
        ax2.set_ylabel("power (mW)")
        color = next(ax1._get_lines.prop_cycler)["color"]
        (ln2,) = plt.plot(evap_times, evap.get_powers(evap_times), color=color)
        lns.append(ln2)
        labs.append("power")
        plt.plot(evap.times_ms, evap.get_powers(evap.times_ms), ".", color=color)
        if shield is not None:
            plt.plot([0, shield.lifetime], [shield.power] * 2, marker=".", color=color)
        if corrected:
            (ln3,) = plt.plot(
                evap_times,
                self.corrected_rf_powers(
                    evap.get_frequencies(evap_times), evap.get_powers(evap_times)
                ),
                "--",
                color=color,
            )
            if shield is not None:
                plt.plot(
                    [0, shield.lifetime],
                    self.corrected_rf_powers(
                        [shield.frequency] * 2,
                        [shield.power] * 2,
                    ),
                    "--",
                    color=color,
                )
            lns.append(ln3)
            labs.append("corrected power")
        # shared setup
        ax1.legend(lns, labs, loc="upper center")
        color = next(ax1._get_lines.prop_cycler)["color"]
        plt.axvline(x=0, linestyle="dashed", color=color)
        plt.title("RF dynamic behavior")
        fig.tight_layout()  # avoid clipping right y-axis label
        plt.show()

    def get_magnetic_potential(self, positions: list) -> list:
        """
        Calculate the magnetic potentials for a given set of positions.

        # U = mf * g * ub * |B| with B = B0 + 0.5 * m * w^2 * x^2
        # for this purpose, we will set B0 = 0
        # (magnetic potential referenced to trap bottom as rf frequencies are)
        # our measured trap frequency is ~ 50 Hz

        Args:
            positions (list): A list of positions at which to calculate the potentials.

        Returns:
            list: A list of magnetic potentials in kHz corresponding to the given positions.
        """
        w = 2 * np.pi * 50  # weak axis trap frequency
        m = 87 * 1.66054e-27
        h = 6.626e-34
        potentials = 0.5 * m * w**2 * np.square(1e-6 * np.asarray(positions))  # in J
        potentials_khz = potentials / h / 1000.0  # in kHz
        return list(potentials_khz)

    def get_barrier_potential(
        self, time: float, positions: list, corrected: bool = False
    ) -> list:
        """Extracts the potential energy due to all a QuantumMatter object's barriers.

        Args:
            time (float): Experiment time at which to evaluate barrier(s) parameters.
            positions (list): List of positions where potential energies are evaluated.

        Returns:
            list: Potential energies (in kHz) at specified time and positions.
        """
        potentials = np.zeros_like(positions)
        if self.barriers is not None:
            for barr in self.barriers:
                potentials += np.asarray(barr.get_potential(time, positions, corrected))
        np.clip(potentials, 0, 100)
        return list(potentials)

    def get_landscape_potential(
        self, time: float, positions: list, corrected: bool = False
    ) -> list:
        potentials = np.zeros_like(positions)
        if self.landscape is not None:
            potentials = self.landscape.get_potential(time, positions)
        return potentials

    def get_potential(self, time: float, positions: list) -> list:
        potentials = np.asarray(self.get_barrier_potential(time, positions))
        potentials += np.asarray(self.get_landscape_potential(time, positions))
        np.clip(potentials, 0, 100)  # total optical potential clipped at 100 kHz
        potentials += np.asarray(self.get_magnetic_potential(positions))
        return list(potentials)

    def show_potential(self, times: list = [0]):
        """Plots the (optical) potential energy surface at the specified times."""
        positions = np.arange(-60, 60, 1, dtype=float)
        fig, ax = plt.subplots()
        lns = []
        labs = []
        for time in times:
            potentials = self.get_potential(time, positions)
            color = next(ax._get_lines.prop_cycler)["color"]
            (ln,) = plt.plot(positions, potentials, color=color)
            plt.plot(positions, potentials, color=color)
            lns.append(ln)
            labs.append("t=" + str(time))
        plt.xlabel("position (microns)", labelpad=6)
        plt.ylabel("potential energy (kHz)", labelpad=6)
        plt.xlim([-61, 61])
        plt.ylim([-1, 101])
        ax.legend(lns, labs, loc=0)
        plt.show()

    def show_barrier_dynamics(self, corrected: bool = False):
        """
        Plots the time dynamics of all of a QuantumMatter object's Barrier objects.

        Args:
            corrected (bool, optional): Determines whether the corrected barrier dynamics
                should be shown. Defaults to False.

        Returns:
            None
        """
        fig, (ax1, ax2, ax3) = plt.subplots(
            nrows=3, ncols=1, sharex=True, figsize=(6, 6)
        )
        fig.suptitle("Barrier dynamics")
        ax1.set_xlim([-1, self.input.end_time_ms])
        ax1.set_ylabel("position (microns)")
        ax2.set_ylabel("height (kHz)")
        ax3.set_ylabel("width (microns)")
        ax3.set_xlabel("time (ms)")
        lns = []
        labs = []

        style = "steps-pre" if corrected else "default"
        for indx, barrier in enumerate(self.barriers):
            color = next(ax1._get_lines.prop_cycler)["color"]
            tstart = min(barrier.times_ms)
            tstop = max(barrier.times_ms)
            times = np.linspace(
                tstart, tstop, num=int((tstop - tstart) / 0.1), endpoint=True
            )
            (ln,) = ax1.plot(
                times, barrier.get_positions(times), color=color, drawstyle=style
            )
            ax1.plot(
                barrier.times_ms,
                barrier.get_positions(barrier.times_ms),
                ".",
                color=color,
            )
            ax2.plot(times, barrier.get_heights(times), color=color, drawstyle=style)
            ax2.plot(
                barrier.times_ms,
                barrier.get_heights(barrier.times_ms),
                ".",
                color=color,
            )
            ax3.plot(times, barrier.get_widths(times), color=color, drawstyle=style)
            ax3.plot(
                barrier.times_ms, barrier.get_widths(barrier.times_ms), ".", color=color
            )
            lns.append(ln)
            labs.append("barrier " + str(indx + 1))
        fig.legend(lns, labs)
        plt.show()

    class Config:
        validate_assignment = True
