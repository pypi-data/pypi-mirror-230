"""
File: primitive.py
Project: gain
Created Date: 21/10/2022
Author: Shun Suzuki
-----
Last Modified: 28/05/2023
Modified By: Shun Suzuki (suzuki@hapis.k.u-tokyo.ac.jp)
-----
Copyright (c) 2022-2023 Shun Suzuki. All rights reserved.

"""

from abc import ABCMeta, abstractmethod
from datetime import timedelta
import numpy as np
from functools import reduce
from ctypes import c_double
from typing import Optional

from pyautd3.native_methods.autd3capi import NativeMethods as Base
from pyautd3.native_methods.autd3capi_def import ModulationPtr, FPGA_SUB_CLK_FREQ
from pyautd3.internal.modulation import IModulation


class Static(IModulation):
    _amp: Optional[float]

    def __init__(self):
        super().__init__()
        self._amp = None

    def with_amp(self, amp: float) -> "Static":
        self._amp = amp
        return self

    def modulation_ptr(self) -> ModulationPtr:
        ptr = Base().modulation_static()
        if self._amp is not None:
            ptr = Base().modulation_static_with_amp(ptr, self._amp)
        return ptr


class Sine(IModulation):
    _freq: int
    _amp: Optional[float]
    _offset: Optional[float]
    _phase: Optional[float]
    _freq_div: Optional[int]

    def __init__(self, freq: int):
        super().__init__()
        self._freq = freq
        self._amp = None
        self._offset = None
        self._phase = None
        self._freq_div = None

    def with_amp(self, amp: float) -> "Sine":
        self._amp = amp
        return self

    def with_offset(self, offset: float) -> "Sine":
        self._offset = offset
        return self

    def with_phase(self, phase: float) -> "Sine":
        self._phase = phase
        return self

    def with_sampling_frequency_division(self, div: int) -> "Sine":
        self._freq_div = div
        return self

    def with_sampling_frequency(self, freq: float) -> "Sine":
        div = int(FPGA_SUB_CLK_FREQ / freq)
        return self.with_sampling_frequency_division(div)

    def with_sampling_period(self, period: timedelta) -> "Sine":
        return self.with_sampling_frequency_division(int(FPGA_SUB_CLK_FREQ / 1000000000. * (period.total_seconds() * 1000. * 1000. * 1000.)))

    def modulation_ptr(self) -> ModulationPtr:
        ptr = Base().modulation_sine(self._freq)
        if self._amp is not None:
            ptr = Base().modulation_sine_with_amp(ptr, self._amp)
        if self._offset is not None:
            ptr = Base().modulation_sine_with_offset(ptr, self._offset)
        if self._phase is not None:
            ptr = Base().modulation_sine_with_phase(ptr, self._phase)
        if self._freq_div is not None:
            ptr = Base().modulation_sine_with_sampling_frequency_division(
                ptr, self._freq_div
            )
        return ptr


class Fourier(IModulation):
    _components: list[Sine]

    def __init__(self):
        super().__init__()
        self._components = []

    def add_component(self, component: Sine) -> "Fourier":
        self._components.append(component)
        return self

    def modulation_ptr(self) -> ModulationPtr:
        return reduce(
            lambda acc, s: Base().modulation_fourier_add_component(
                acc, s.modulation_ptr()
            ),
            self._components,
            Base().modulation_fourier(),
        )


class SineLegacy(IModulation):
    _freq: float
    _amp: Optional[float]
    _offset: Optional[float]
    _freq_div: Optional[int]

    def __init__(self, freq: float):
        super().__init__()
        self._freq = freq
        self._amp = None
        self._offset = None
        self._freq_div = None

    def with_amp(self, amp: float) -> "SineLegacy":
        self._amp = amp
        return self

    def with_offset(self, offset: float) -> "SineLegacy":
        self._offset = offset
        return self

    def with_sampling_frequency_division(self, div: int) -> "SineLegacy":
        self._freq_div = div
        return self

    def with_sampling_frequency(self, freq: float) -> "SineLegacy":
        div = int(FPGA_SUB_CLK_FREQ / freq)
        return self.with_sampling_frequency_division(div)

    def with_sampling_period(self, period: timedelta) -> "SineLegacy":
        return self.with_sampling_frequency_division(int(FPGA_SUB_CLK_FREQ / 1000000000. * (period.total_seconds() * 1000. * 1000. * 1000.)))

    def modulation_ptr(self) -> ModulationPtr:
        ptr = Base().modulation_sine_legacy(self._freq)
        if self._amp is not None:
            ptr = Base().modulation_sine_legacy_with_amp(ptr, self._amp)
        if self._offset is not None:
            ptr = Base().modulation_sine_legacy_with_offset(ptr, self._offset)
        if self._freq_div is not None:
            ptr = Base().modulation_sine_legacy_with_sampling_frequency_division(
                ptr, self._freq_div
            )
        return ptr


class Square(IModulation):
    _freq: int
    _low: Optional[float]
    _high: Optional[float]
    _duty: Optional[float]
    _freq_div: Optional[int]

    def __init__(self, freq: int):
        super().__init__()
        self._freq = freq
        self._low = None
        self._high = None
        self._duty = None
        self._freq_div = None

    def with_low(self, low: float) -> "Square":
        self._low = low
        return self

    def with_high(self, high: float) -> "Square":
        self._high = high
        return self

    def with_duty(self, duty: float) -> "Square":
        self._duty = duty
        return self

    def with_sampling_frequency_division(self, div: int) -> "Square":
        self._freq_div = div
        return self

    def with_sampling_frequency(self, freq: float) -> "Square":
        div = int(FPGA_SUB_CLK_FREQ / freq)
        return self.with_sampling_frequency_division(div)

    def with_sampling_period(self, period: timedelta) -> "Square":
        return self.with_sampling_frequency_division(int(FPGA_SUB_CLK_FREQ / 1000000000. * (period.total_seconds() * 1000. * 1000. * 1000.)))

    def modulation_ptr(self) -> ModulationPtr:
        ptr = Base().modulation_square(self._freq)
        if self._low is not None:
            ptr = Base().modulation_square_with_low(ptr, self._low)
        if self._high is not None:
            ptr = Base().modulation_square_with_high(ptr, self._high)
        if self._duty is not None:
            ptr = Base().modulation_square_with_duty(ptr, self._duty)
        if self._freq_div is not None:
            ptr = Base().modulation_square_with_sampling_frequency_division(
                ptr, self._freq_div
            )
        return ptr


class Modulation(IModulation, metaclass=ABCMeta):
    _freq_div: int

    def __init__(self, freq_div: int):
        super().__init__()
        self._freq_div = freq_div

    @abstractmethod
    def calc(self) -> np.ndarray:
        pass

    def modulation_ptr(self) -> ModulationPtr:
        data = self.calc()
        size = len(data)
        return Base().modulation_custom(
            self._freq_div, np.ctypeslib.as_ctypes(data.astype(c_double)), size
        )
