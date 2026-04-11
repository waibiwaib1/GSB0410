import numpy as np
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import (
    EarthLocation, ITRS, AltAz, HADec, CIRS
)

def test_itrs_altaz():
    """Test ITRS <-> AltAz transformation"""
    t = Time('J2010')
    obj = EarthLocation(-1*u.deg, 52*u.deg, height=10.*u.km)
    home = EarthLocation(-1*u.deg, 52*u.deg, height=0.*u.km)

    obj_itrs = obj.get_itrs(t)
    altaz_frame = AltAz(obstime=t, location=home)
    
    aa = obj_itrs.transform_to(altaz_frame)
    print('Test ITRS -> AltAz')
    print(f'  Alt: {aa.alt}')
    print(f'  Az: {aa.az}')
    
    itrs_back = aa.transform_to(ITRS())
    diff = np.max(np.abs(itrs_back.cartesian.xyz - obj_itrs.cartesian.xyz))
    print(f'  Round trip diff: {diff}')
    assert diff < 1e-6 * u.m, f"Round trip failed with diff {diff}"
    print('  OK!')

def test_itrs_hadec():
    """Test ITRS <-> HADec transformation"""
    t = Time('J2010')
    obj = EarthLocation(-1*u.deg, 52*u.deg, height=10.*u.km)
    home = EarthLocation(-1*u.deg, 52*u.deg, height=0.*u.km)

    obj_itrs = obj.get_itrs(t)
    hadec_frame = HADec(obstime=t, location=home)
    
    hd = obj_itrs.transform_to(hadec_frame)
    print('\nTest ITRS -> HADec')
    print(f'  HA: {hd.ha}')
    print(f'  Dec: {hd.dec}')
    
    itrs_back = hd.transform_to(ITRS())
    diff = np.max(np.abs(itrs_back.cartesian.xyz - obj_itrs.cartesian.xyz))
    print(f'  Round trip diff: {diff}')
    assert diff < 1e-6 * u.m, f"Round trip failed with diff {diff}"
    print('  OK!')

if __name__ == '__main__':
    test_itrs_altaz()
    test_itrs_hadec()
    print('\nAll tests passed!')
