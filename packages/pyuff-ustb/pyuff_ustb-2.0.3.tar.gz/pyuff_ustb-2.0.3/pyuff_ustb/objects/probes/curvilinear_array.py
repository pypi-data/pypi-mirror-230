import numpy as np

from pyuff_ustb.objects.probes.probe import Probe
from pyuff_ustb.objects.uff import (
    compulsory_property,
    dependent_property,
    optional_property,
)
from pyuff_ustb.readers import LazyScalar


class CurvilinearArray(Probe):
    """:class:`Uff` class to define a curvilinear array probe geometry.

    :class:`CurvilinearArray` defines a array of regularly space elements on an arc in 
    the azimuth dimensions. Optionally it can hold each element width and height, 
    assuming the elements are rectangular.
        
    Original authors:
        Alfonso Rodriguez-Molares (alfonsom@ntnu.no)
    """

    # Compulsory properties
    @compulsory_property
    def N(self) -> int:
        "Number of elements"
        return LazyScalar(self._reader["N"])

    @compulsory_property
    def pitch(self) -> float:
        "Distance between the elements in the azimuth direction [m]"
        return LazyScalar(self._reader["pitch"])

    @compulsory_property
    def radius(self) -> float:
        "Radius of the curvilinear array [m]"
        return LazyScalar(self._reader["radius"])

    # Optional properties
    @optional_property
    def element_width(self) -> float:
        "Width of the elements in the azimuth direction [m]"
        return LazyScalar(self._reader["element_width"])

    @optional_property
    def element_height(self) -> float:
        "Height of the elements in the elevation direction [m]"
        return LazyScalar(self._reader["element_height"])

    # Dependent properties
    @dependent_property
    def maximum_angle(self) -> float:
        "Angle of the outermost elements in the array"
        return np.max(np.abs(self.theta))
