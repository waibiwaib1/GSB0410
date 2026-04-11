import xarray as xr
import pandas as pd
import numpy as np

lines = []
def log(msg):
    lines.append(msg)

def assert_identical(a, b):
    if a.equals(b):
        return True
    return False

# Test set_index: test_set_index case 1
mindex = pd.MultiIndex.from_arrays(
    [["a", "b", "c"], [1, 2, 3]], names=["level_1", "level_2"]
)
expected = xr.Dataset({}, coords={"x": xr.Variable("x", mindex)})
indexes = [mindex.get_level_values(n) for n in mindex.names]
coords = {idx.name: ("x", idx) for idx in indexes}
ds = xr.Dataset({}, coords=coords)
obj = ds.set_index(x=mindex.names)

try:
    xr.testing.assert_identical(obj, expected)
    log("test_set_index case 1 (multi-index names): PASS")
except Exception as e:
    log(f"test_set_index case 1 (multi-index names): FAIL - {e}")

# Test set_index: case 2 - pre-existing indexes removed
ds2 = xr.Dataset({}, coords={"x": xr.Variable("x", mindex)})
coords2 = {"x": coords["level_1"], "level_2": coords["level_2"]}
expected2 = xr.Dataset({}, coords=coords2)
obj2 = ds2.set_index(x="level_1")

try:
    xr.testing.assert_identical(obj2, expected2)
    log("test_set_index case 2 (pre-existing indexes): PASS")
except Exception as e:
    log(f"test_set_index case 2 (pre-existing indexes): FAIL - {e}")

# Test set_index: case 3 - single data var
ds3 = xr.Dataset(data_vars={"x_var": ("x", [0, 1, 2])})
expected3 = xr.Dataset(coords={"x": [0, 1, 2]})
obj3 = ds3.set_index(x="x_var")

try:
    xr.testing.assert_identical(obj3, expected3)
    log("test_set_index case 3 (single data var): PASS")
except Exception as e:
    log(f"test_set_index case 3 (single data var): FAIL - {e}")

# Test reset_index
ds4 = xr.Dataset({}, coords={"x": xr.Variable("x", mindex)})
obj4 = ds4.reset_index("x")
expected_vars = set(["x", "level_1", "level_2"])
if set(obj4._variables.keys()) == expected_vars and len(obj4._indexes) == 0:
    log("test_reset_index case 1 (full reset): PASS")
else:
    log(f"test_reset_index case 1 (full reset): FAIL - vars={set(obj4._variables.keys())}, indexes={list(obj4._indexes.keys())}")

obj5 = ds4.reset_index("x", drop=True)
if len(obj5._variables) == 0 and len(obj5._indexes) == 0:
    log("test_reset_index case 2 (full reset drop): PASS")
else:
    log(f"test_reset_index case 2 (full reset drop): FAIL - vars={list(obj5._variables.keys())}")

# Test sel on multi-index
ds5 = xr.Dataset({"var": ("x", [10, 20, 30])}, coords={"x": xr.Variable("x", mindex)})
try:
    result = ds5.sel(x="a")
    log(f"test_sel on multi-index: PASS (result={result['var'].values})")
except Exception as e:
    log(f"test_sel on multi-index: FAIL - {e}")

try:
    result2 = ds5.sel(level_1="a")
    log(f"test_sel on level: PASS (result={result2['var'].values})")
except Exception as e:
    log(f"test_sel on level: FAIL - {e}")

# Test reset_index level then sel
ds6 = ds4.reset_index("level_1")
try:
    result3 = ds6.sel(x=1)
    log(f"test_sel after reset_index level (on dim): PASS")
except Exception as e:
    log(f"test_sel after reset_index level (on dim): FAIL - {e}")

with open("test_results.txt", "w") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
