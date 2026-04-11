# Licensed under a 3-clause BSD style license - see LICENSE.rst

from astropy.utils.decorators import format_doc
from astropy.coordinates.representation import CartesianRepresentation, CartesianDifferential
from astropy.coordinates.baseframe import BaseCoordinateFrame, base_doc
from astropy.coordinates.attributes import TimeAttribute, EarthLocationAttribute
from .utils import DEFAULT_OBSTIME, EARTH_CENTER

__all__ = ['ITRS']

doc_footer = """
    Other parameters
    ----------------
    obstime : `~astropy.time.Time`
        The time at which the observation is taken.  Used for determining the
        position of the Earth and its precession.
    location : `~astropy.coordinates.EarthLocation`
        The location on the Earth. This can be specified either as an
        `~astropy.coordinates.EarthLocation` object or as anything that can be
        transformed to an `~astropy.coordinates.ITRS` frame. The default is the
        centre of the Earth.

        .. note::

            ITRS frames can be either **geocentric** (default, location=None) or
            **topocentric** (with a specific location).

            - **Geocentric ITRS**: Coordinates are relative to the Earth's center.
              This is the standard ITRS frame used for satellite orbits, Earth
              orientation, etc.

            - **Topocentric ITRS**: Coordinates are relative to a specific observer
              location on the Earth's surface. This is useful for expressing nearby
              targets (e.g., aircraft, mountains, adjacent buildings) in a frame that
              is "attached" to both the Earth and the observer.

            When transforming between ITRS and observed frames (AltAz, HADec),
            using a topocentric ITRS provides a more direct transformation path
            that avoids unnecessary complications with aberration and parallax for
            nearby targets.
"""


@format_doc(base_doc, components="", footer=doc_footer)
class ITRS(BaseCoordinateFrame):
    """
    A coordinate or frame in the International Terrestrial Reference System
    (ITRS).  This is approximately a geocentric system, although strictly it is
    defined by a series of reference locations near the surface of the Earth.
    For more background on the ITRS, see the references provided in the
    :ref:`astropy:astropy-coordinates-seealso` section of the documentation.

    ITRS coordinates are fixed relative to the Earth's surface. The frame can
    be either geocentric (relative to Earth's center) or topocentric (relative
    to a specific observer location on Earth).
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
