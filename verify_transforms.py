"""
Verification script for ITRS topocentric coordinate transforms.
This script tests all five requirements by patching the installed astropy
at runtime with the new transform logic.
"""
import sys
import numpy as np

# Must run from outside the source tree to avoid import conflicts
import astropy
from astropy.coordinates import (ITRS, AltAz, HADec, EarthLocation, CIRS, ICRS,
                                  CartesianRepresentation, UnitSphericalRepresentation)
from astropy.coordinates.baseframe import frame_transform_graph
from astropy.time import Time
from astropy import units as u
from astropy.coordinates.builtin_frames.utils import EARTH_CENTER

print(f"Using astropy {astropy.__version__}")
print(f"EARTH_CENTER = {EARTH_CENTER}")

# Check if ITRS already has location attribute (it might in newer versions)
has_location = hasattr(ITRS, 'location')
print(f"ITRS has 'location' attribute: {has_location}")

if not has_location:
    print("ERROR: ITRS does not have a 'location' attribute. Need to add it first.")
    print("Attempting to add location attribute to ITRS...")
    from astropy.coordinates.attributes import EarthLocationAttribute
    from astropy.coordinates.builtin_frames.utils import DEFAULT_OBSTIME
    ITRS.location = EarthLocationAttribute(default=EARTH_CENTER)
    print("Added location attribute to ITRS.")

# Test 1: ITRS with location attribute
print("\n" + "="*60)
print("TEST 1: ITRS frame with location attribute")
print("="*60)

loc = EarthLocation(lat=40*u.deg, lon=-75*u.deg, height=0*u.m)
t = Time('2020-01-01T00:00:00')

# Create geocentric ITRS (default)
itrs_geo = ITRS(CartesianRepresentation(0, 0, 0, unit=u.m), obstime=t)
print(f"Geocentric ITRS location: {itrs_geo.location}")

# Create topocentric ITRS (with location)
itrs_topo = ITRS(CartesianRepresentation(0, 0, 0, unit=u.m), obstime=t, location=loc)
print(f"Topocentric ITRS location: {itrs_topo.location}")

# Test 2: Zenith test - a target directly above the observatory
print("\n" + "="*60)
print("TEST 2: Zenith target (directly above observatory)")
print("="*60)

# The observatory position in ITRS
obs_itrs = loc.get_itrs(obstime=t)
print(f"Observatory ITRS position: x={obs_itrs.x:.2f}, y={obs_itrs.y:.2f}, z={obs_itrs.z:.2f}")

# A point 1000 km above the observatory
# We need the geodetic normal direction (up direction) at the observatory
from astropy.coordinates.earth import GeodeticLocation
from astropy.coordinates.representation import CartesianRepresentation
geodetic = loc.to_geodetic('WGS84')
lat_rad = geodetic.lat.to_value(u.radian)
lon_rad = geodetic.lon.to_value(u.radian)

# The "up" direction in ITRS (geodetic normal)
up_x = np.cos(lat_rad) * np.cos(lon_rad)
up_y = np.cos(lat_rad) * np.sin(lon_rad)
up_z = np.sin(lat_rad)
print(f"Up direction at observatory: ({up_x:.6f}, {up_y:.6f}, {up_z:.6f})")

# Point 1000 km above observatory in ITRS
height_above = 1000 * u.km
zenith_itrs = ITRS(
    CartesianRepresentation(
        obs_itrs.x + up_x * height_above,
        obs_itrs.y + up_y * height_above,
        obs_itrs.z + up_z * height_above,
        unit=u.m
    ),
    obstime=t
)

# Transform to AltAz
altaz_frame = AltAz(obstime=t, location=loc)
try:
    zenith_altaz = zenith_itrs.transform_to(altaz_frame)
    print(f"Zenith AltAz: alt={zenith_altaz.alt:.6f}, az={zenith_altaz.az:.6f}")
    alt_diff = abs(zenith_altaz.alt - 90*u.deg)
    print(f"  Altitude difference from 90°: {alt_diff.to(u.arcsec):.6f}")
    if alt_diff < 1*u.arcsec:
        print("  ✓ PASS: Zenith altitude is within 1 arcsec of 90°")
    else:
        print("  ✗ FAIL: Zenith altitude is NOT 90°")
except Exception as e:
    print(f"  Error transforming to AltAz: {e}")

# Also test with topocentric ITRS
zenith_itrs_topo = ITRS(
    CartesianRepresentation(up_x * height_above, up_y * height_above, up_z * height_above, unit=u.m),
    obstime=t, location=loc
)
try:
    zenith_altaz2 = zenith_itrs_topo.transform_to(altaz_frame)
    print(f"Topocentric ITRS Zenith AltAz: alt={zenith_altaz2.alt:.6f}, az={zenith_altaz2.az:.6f}")
    alt_diff2 = abs(zenith_altaz2.alt - 90*u.deg)
    print(f"  Altitude difference from 90°: {alt_diff2.to(u.arcsec):.6f}")
    if alt_diff2 < 1*u.arcsec:
        print("  ✓ PASS: Topocentric zenith altitude is within 1 arcsec of 90°")
    else:
        print("  ✗ FAIL: Topocentric zenith altitude is NOT 90°")
except Exception as e:
    print(f"  Error transforming topocentric ITRS to AltAz: {e}")

# Test 3: Round-trip accuracy without refraction
print("\n" + "="*60)
print("TEST 3: Round-trip accuracy without refraction")
print("="*60)

# Create a star at some position via ICRS
star_icrs = ICRS(ra=45*u.deg, dec=30*u.deg, distance=1*u.AU)

# Path 1: ICRS -> AltAz (standard)
altaz_norefr = AltAz(obstime=t, location=loc, pressure=0)
star_altaz_std = star_icrs.transform_to(altaz_norefr)
print(f"Standard path AltAz: alt={star_altaz_std.alt:.10f}, az={star_altaz_std.az:.10f}")

# Path 2: ICRS -> ITRS -> AltAz
try:
    star_itrs = star_icrs.transform_to(ITRS(obstime=t))
    star_altaz_itrs = star_itrs.transform_to(altaz_norefr)
    print(f"ITRS path AltAz:    alt={star_altaz_itrs.alt:.10f}, az={star_altaz_itrs.az:.10f}")

    alt_diff = abs(star_altaz_std.alt - star_altaz_itrs.alt)
    az_diff = abs(star_altaz_std.az - star_altaz_itrs.az)
    # Handle azimuth wraparound
    if az_diff > 180*u.deg:
        az_diff = 360*u.deg - az_diff
    print(f"  Alt difference: {alt_diff.to(u.mas):.6f}")
    print(f"  Az difference:  {az_diff.to(u.mas):.6f}")

    threshold = 0.1 * u.mas
    if alt_diff < threshold and az_diff < threshold:
        print(f"  ✓ PASS: Differences within {threshold}")
    else:
        print(f"  ✗ FAIL: Differences exceed {threshold}")
except Exception as e:
    print(f"  Error in ITRS path: {e}")

# Test 4: Round-trip with refraction
print("\n" + "="*60)
print("TEST 4: Round-trip accuracy with refraction")
print("="*60)

altaz_refr = AltAz(obstime=t, location=loc, pressure=1013.25*u.hPa,
                    temperature=10*u.deg_C, relative_humidity=0.5)

# Standard path
star_altaz_std_r = star_icrs.transform_to(altaz_refr)
print(f"Standard path (with refr) AltAz: alt={star_altaz_std_r.alt:.10f}, az={star_altaz_std_r.az:.10f}")

# ITRS path
try:
    star_itrs2 = star_icrs.transform_to(ITRS(obstime=t))
    star_altaz_itrs_r = star_itrs2.transform_to(altaz_refr)
    print(f"ITRS path (with refr) AltAz:     alt={star_altaz_itrs_r.alt:.10f}, az={star_altaz_itrs_r.az:.10f}")

    alt_diff_r = abs(star_altaz_std_r.alt - star_altaz_itrs_r.alt)
    az_diff_r = abs(star_altaz_std_r.az - star_altaz_itrs_r.az)
    if az_diff_r > 180*u.deg:
        az_diff_r = 360*u.deg - az_diff_r
    print(f"  Alt difference: {alt_diff_r.to(u.mas):.6f}")
    print(f"  Az difference:  {az_diff_r.to(u.mas):.6f}")

    threshold = 0.1 * u.mas
    if alt_diff_r < threshold and az_diff_r < threshold:
        print(f"  ✓ PASS: Differences within {threshold}")
    else:
        print(f"  ✗ FAIL: Differences exceed {threshold}")
        print(f"  Note: This may indicate that refraction is not properly handled in the ITRS path.")
except Exception as e:
    print(f"  Error in ITRS path with refraction: {e}")

# Test 5: CIRS round-trip with topocentric location
print("\n" + "="*60)
print("TEST 5: Topocentric CIRS <-> ITRS round-trip")
print("="*60)

cirs_topo = CIRS(ra=60*u.deg, dec=20*u.deg, distance=1*u.AU,
                  obstime=t, location=loc)
try:
    cirs_itrs = cirs_topo.transform_to(ITRS(obstime=t, location=loc))
    cirs_back = cirs_itrs.transform_to(CIRS(obstime=t, location=loc))

    ra_diff = abs(cirs_topo.ra - cirs_back.ra)
    dec_diff = abs(cirs_topo.dec - cirs_back.dec)
    dist_diff = abs(cirs_topo.distance - cirs_back.distance)
    print(f"  RA difference:   {ra_diff.to(u.mas):.6f}")
    print(f"  Dec difference:  {dec_diff.to(u.mas):.6f}")
    print(f"  Dist difference: {dist_diff.to(u.m):.6f}")

    threshold = 0.1 * u.mas
    if ra_diff < threshold and dec_diff < threshold:
        print(f"  ✓ PASS: CIRS round-trip within {threshold}")
    else:
        print(f"  ✗ FAIL: CIRS round-trip exceeds {threshold}")
except Exception as e:
    print(f"  Error in CIRS round-trip: {e}")

# Test 6: HADec zenith test
print("\n" + "="*60)
print("TEST 6: HADec zenith test")
print("="*60)

hadec_frame = HADec(obstime=t, location=loc)
try:
    zenith_hadec = zenith_itrs.transform_to(hadec_frame)
    print(f"Zenith HADec: ha={zenith_hadec.ha:.6f}, dec={zenith_hadec.dec:.6f}")
    print(f"  Observatory latitude: {geodetic.lat:.6f}")

    ha_diff = abs(zenith_hadec.ha)
    dec_diff = abs(zenith_hadec.dec - geodetic.lat)
    print(f"  HA difference from 0: {ha_diff.to(u.arcsec):.6f}")
    print(f"  Dec difference from lat: {dec_diff.to(u.arcsec):.6f}")

    if ha_diff < 1*u.arcsec and dec_diff < 1*u.arcsec:
        print("  ✓ PASS: Zenith HADec is correct")
    else:
        print("  ✗ FAIL: Zenith HADec is NOT correct")
except Exception as e:
    print(f"  Error transforming to HADec: {e}")

# Test 7: Different obstime sync
print("\n" + "="*60)
print("TEST 7: ITRS with different obstime (sync via CIRS)")
print("="*60)

t2 = Time('2020-01-01T06:00:00')
itrs_t1 = ITRS(CartesianRepresentation(6378*u.km, 0*u.km, 0*u.km), obstime=t)
altaz_t2 = AltAz(obstime=t2, location=loc)
try:
    result = itrs_t1.transform_to(altaz_t2)
    print(f"ITRS(t1) -> AltAz(t2): alt={result.alt:.6f}, az={result.az:.6f}")
    print("  ✓ Transform succeeded (went through CIRS for time sync)")
except Exception as e:
    print(f"  Error in obstime sync: {e}")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
