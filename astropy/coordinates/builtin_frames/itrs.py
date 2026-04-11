# Licensed under a 3-clause BSD style license - see LICENSE.rst

from astropy.utils.decorators import format_doc
from astropy.coordinates.representation import CartesianRepresentation, CartesianDifferential
from astropy.coordinates.baseframe import BaseCoordinateFrame, base_doc
from astropy.coordinates.attributes import TimeAttribute, EarthLocationAttribute
from .utils import DEFAULT_OBSTIME, EARTH_CENTER

__all__ = ['ITRS']


@format_doc(base_doc, components="", footer="")
class ITRS(BaseCoordinateFrame):
    """
    A coordinate or frame in the International Terrestrial Reference System
    (ITRS).  This is approximately a geocentric system, although strictly it is
    defined by a series of reference locations near the surface of the Earth.
    For more background on the ITRS, see the references provided in the
    :ref:`astropy:astropy-coordinates-seealso` section of the documentation.

    If the ``location`` frame attribute is set to an `~astropy.coordinates.EarthLocation`
    other than the geocenter, the ITRS frame is "topocentric" - i.e., positions
    are expressed relative to that surface location. This is useful for nearby
    targets (satellites, aircraft, etc.) where the standard geocentric ITRS
    representation would place the observer at the center of the Earth. For such
    cases, the topocentric ITRS can be directly transformed to/from `AltAz` and
    `HADec` without leaving the ITRS system, avoiding the complications of
    aberration corrections that arise when going through CIRS/ICRS.

    For distant targets (stars, etc.), the standard geocentric ITRS path through
    CIRS is more appropriate, as it properly accounts for stellar aberration.
    """

    default_representation = CartesianRepresentation
    default_differential = CartesianDifferential

    obstime = TimeAttribute(default=DEFAULT_OBSTIME)
    location = EarthLocationAttribute(default=EARTH_CENTER)

    @property
    def earth_location(self):
        """
        The data in this frame as an `~astropy.coordinates.EarthLocation` class.
        """
        from astropy.coordinates.earth import EarthLocation

        cart = self.represent_as(CartesianRepresentation)
        return EarthLocation(x=cart.x, y=cart.y, z=cart.z)

# Self-transform is in intermediate_rotation_transforms.py with all the other
# ITRS transforms
