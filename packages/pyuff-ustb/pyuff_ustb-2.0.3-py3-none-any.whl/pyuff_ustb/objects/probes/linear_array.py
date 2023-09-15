from pyuff_ustb.objects.probes.probe import Probe
from pyuff_ustb.objects.uff import compulsory_property, optional_property
from pyuff_ustb.readers import LazyScalar


class LinearArray(Probe):
    """:class:`Uff` class to define a linear array probe geometry.
    
    :class:`LinearArray` defines an array of elements regularly place along a line. 
    Optionally :class:`LinearArray` specifies element width and heightassuming the they 
    are rectangular.

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

    # Optional properties
    @optional_property
    def element_width(self) -> float:
        "Width of the elements in the azimuth direction [m]"
        return LazyScalar(self._reader["element_width"])

    @optional_property
    def element_height(self) -> float:
        "Height of the elements in the elevation direction [m]"
        return LazyScalar(self._reader["element_height"])
