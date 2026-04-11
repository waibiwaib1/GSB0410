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
print(f"mda._variables: {list(mda._variables.keys())}")
print(f"mda._coord_names: {mda._coord_names}")
print(f"mda._indexes: {list(mda._indexes.keys())}")
print(f"mda.xindexes: {list(mda.xindexes)}")

# expected
indexes = [mindex.get_level_values(n) for n in mindex.names]
coords = {idx.name: ("x", idx) for idx in indexes}  # level_1, level_2
coords["x"] = ("x", mindex.values)  # x
expected = DataArray(mda.values, coords=coords, dims=["x", "y"])

print()
print("=== expected ===")
print(f"expected._variables: {list(expected._variables.keys())}")
print(f"expected._coord_names: {expected._coord_names}")
print(f"expected._indexes: {list(expected._indexes.keys())}")
print(f"expected.xindexes: {list(expected.xindexes)}")

# test 1: reset_index("x")
print()
print("=== reset_index('x') ===")
obj = mda.reset_index("x")
print(f"obj._variables: {list(obj._variables.keys())}")
print(f"obj._coord_names: {obj._coord_names}")
print(f"obj._indexes: {list(obj._indexes.keys())}")
print(f"obj.xindexes: {list(obj.xindexes)}")
print(f"len(obj.xindexes): {len(obj.xindexes)} (expected: 0)")

# test 2: reset_index(mindex.names)
print()
print("=== reset_index(mindex.names) ===")
obj2 = mda.reset_index(mindex.names)
print(f"obj2._variables: {list(obj2._variables.keys())}")
print(f"obj2._coord_names: {obj2._coord_names}")
print(f"obj2._indexes: {list(obj2._indexes.keys())}")
print(f"obj2.xindexes: {list(obj2.xindexes)}")
print(f"len(obj2.xindexes): {len(obj2.xindexes)} (expected: 0)")

# test 3: reset_index(["x", "level_1"])
print()
print("=== reset_index(['x', 'level_1']) ===")
obj3 = mda.reset_index(["x", "level_1"])
print(f"obj3._variables: {list(obj3._variables.keys())}")
print(f"obj3._coord_names: {obj3._coord_names}")
print(f"obj3._indexes: {list(obj3._indexes.keys())}")
print(f"obj3.xindexes: {list(obj3.xindexes)}")
print(f"obj3.xindexes (expected: ['level_2'])")

# test 4: reset_index(["level_1"])
print()
print("=== reset_index(['level_1']) ===")
obj4 = mda.reset_index(["level_1"])
print(f"obj4._variables: {list(obj4._variables.keys())}")
print(f"obj4._coord_names: {obj4._coord_names}")
print(f"obj4._indexes: {list(obj4._indexes.keys())}")
print(f"obj4.xindexes: {list(obj4.xindexes)}")
print(f"obj4.xindexes (expected: ['level_2'])")
if "level_2" in obj4.xindexes:
    print(f"type(obj4.xindexes['level_2']): {type(obj4.xindexes['level_2']).__name__}")

# test 5: reset_index("x", drop=True)
print()
print("=== reset_index('x', drop=True) ===")
coords_drop = {k: v for k, v in coords.items() if k != "x"}
expected_drop = DataArray(mda.values, coords=coords_drop, dims=["x", "y"])
print(f"expected_drop._variables: {list(expected_drop._variables.keys())}")
print(f"expected_drop._coord_names: {expected_drop._coord_names}")

obj5 = mda.reset_index("x", drop=True)
print(f"obj5._variables: {list(obj5._variables.keys())}")
print(f"obj5._coord_names: {obj5._coord_names}")
print(f"obj5._indexes: {list(obj5._indexes.keys())}")
