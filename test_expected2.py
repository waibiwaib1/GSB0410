import sys
sys.path.insert(0, r'd:\Code\Multi-SWE-bench\task6\task6_M1')

import xarray as xr
from xarray import Dataset, DataArray
from xarray.core.indexes import PandasMultiIndex, PandasIndex
import pandas as pd
import numpy as np

# 模拟 TestDataArrayCoords.test_reset_index 的设置
mindex = pd.MultiIndex.from_product(
    [["a", "b"], [1, 2]], names=("level_1", "level_2")
)
mda = DataArray(np.arange(4).reshape(4, 1), coords={"x": mindex}, dims=["x", "y"])

print("=== Original mda ===")
print(f"mda.coords: {list(mda.coords.keys())}")
print(f"mda.xindexes: {list(mda.xindexes)}")

# expected
indexes = [mindex.get_level_values(n) for n in mindex.names]
coords = {idx.name: ("x", idx) for idx in indexes}  # level_1, level_2
coords["x"] = ("x", mindex.values)  # x
expected = DataArray(mda.values, coords=coords, dims=["x", "y"])

print()
print("=== expected ===")
print(f"expected.coords: {list(expected.coords.keys())}")
print(f"expected.xindexes: {list(expected.xindexes)}")

# test 1: reset_index("x")
print()
print("=== reset_index('x') ===")
obj = mda.reset_index("x")
print(f"obj.coords: {list(obj.coords.keys())}")
print(f"obj.xindexes: {list(obj.xindexes)}")
print(f"len(obj.xindexes): {len(obj.xindexes)} (expected: 0)")

# test 2: reset_index(mindex.names)
print()
print("=== reset_index(mindex.names) ===")
obj2 = mda.reset_index(mindex.names)
print(f"obj2.coords: {list(obj2.coords.keys())}")
print(f"obj2.xindexes: {list(obj2.xindexes)}")
print(f"len(obj2.xindexes): {len(obj2.xindexes)} (expected: 0)")

# test 3: reset_index(["x", "level_1"])
print()
print("=== reset_index(['x', 'level_1']) ===")
obj3 = mda.reset_index(["x", "level_1"])
print(f"obj3.coords: {list(obj3.coords.keys())}")
print(f"obj3.xindexes: {list(obj3.xindexes)}")
print(f"obj3.xindexes (expected: ['level_2'])")

# test 4: reset_index(["level_1"])
print()
print("=== reset_index(['level_1']) ===")
obj4 = mda.reset_index(["level_1"])
print(f"obj4.coords: {list(obj4.coords.keys())}")
print(f"obj4.xindexes: {list(obj4.xindexes)}")
print(f"obj4.xindexes (expected: ['level_2'])")
if "level_2" in obj4.xindexes:
    print(f"type(obj4.xindexes['level_2']): {type(obj4.xindexes['level_2']).__name__}")

# test 5: reset_index("x", drop=True)
print()
print("=== reset_index('x', drop=True) ===")
coords_drop = {k: v for k, v in coords.items() if k != "x"}
expected_drop = DataArray(mda.values, coords=coords_drop, dims=["x", "y"])
print(f"expected_drop.coords: {list(expected_drop.coords.keys())}")

obj5 = mda.reset_index("x", drop=True)
print(f"obj5.coords: {list(obj5.coords.keys())}")
print(f"obj5.xindexes: {list(obj5.xindexes)}")
