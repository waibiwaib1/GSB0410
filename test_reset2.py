import sys
sys.path.insert(0, r'd:\Code\Multi-SWE-bench\task6\task6_M1')

import xarray as xr
from xarray import Dataset, DataArray
from xarray.core.indexes import PandasMultiIndex, PandasIndex
import pandas as pd
import numpy as np

def create_test_multiindex():
    mindex = pd.MultiIndex.from_product(
        [["a", "b"], [1, 2]], names=("level_1", "level_2")
    )
    return Dataset({}, {"x": mindex})

# 测试 test_reset_index
print("=== Test test_reset_index ===")
ds = create_test_multiindex()
mindex = ds["x"].to_index()
indexes = [mindex.get_level_values(n) for n in mindex.names]
coords = {idx.name: ("x", idx) for idx in indexes}
coords["x"] = ("x", mindex.values)
expected = Dataset({}, coords=coords)

print(f"expected._variables: {list(expected._variables.keys())}")
print(f"expected._coord_names: {expected._coord_names}")
print(f"expected._indexes: {list(expected._indexes.keys())}")

obj = ds.reset_index("x")
print()
print(f"obj._variables: {list(obj._variables.keys())}")
print(f"obj._coord_names: {obj._coord_names}")
print(f"obj._indexes: {list(obj._indexes.keys())}")
print(f"len(obj.xindexes): {len(obj.xindexes)}")

# 检查变量类型
print("Variable types:")
for k, v in obj._variables.items():
    print(f"  {k}: {type(v).__name__}")

# test reset_index with level names
print()
print("=== Test reset_index with level names ===")
ds2 = create_test_multiindex()
obj2 = ds2.reset_index(["level_1", "level_2"])
print(f"obj2._variables: {list(obj2._variables.keys())}")
print(f"obj2._coord_names: {obj2._coord_names}")
print(f"obj2._indexes: {list(obj2._indexes.keys())}")
print(f"len(obj2.xindexes): {len(obj2.xindexes)}")

# test reset_index with x and level_1
print()
print("=== Test reset_index with x and level_1 ===")
ds3 = create_test_multiindex()
obj3 = ds3.reset_index(["x", "level_1"])
print(f"obj3._variables: {list(obj3._variables.keys())}")
print(f"obj3._coord_names: {obj3._coord_names}")
print(f"obj3._indexes: {list(obj3._indexes.keys())}")
print(f"obj3.xindexes: {list(obj3.xindexes)}")

# test reset_index with level_1 only
print()
print("=== Test reset_index with level_1 only ===")
ds4 = create_test_multiindex()
obj4 = ds4.reset_index(["level_1"])
print(f"obj4._variables: {list(obj4._variables.keys())}")
print(f"obj4._coord_names: {obj4._coord_names}")
print(f"obj4._indexes: {list(obj4._indexes.keys())}")
print(f"obj4.xindexes: {list(obj4.xindexes)}")
if "level_2" in obj4.xindexes:
    print(f"type(obj4.xindexes['level_2']): {type(obj4.xindexes['level_2']).__name__}")

# test reset_index with drop=True
print()
print("=== Test reset_index with drop=True ===")
coords_drop = {k: v for k, v in coords.items() if k != "x"}
expected_drop = Dataset({}, coords=coords_drop)
print(f"expected_drop._variables: {list(expected_drop._variables.keys())}")
print(f"expected_drop._coord_names: {expected_drop._coord_names}")

ds5 = create_test_multiindex()
obj5 = ds5.reset_index("x", drop=True)
print()
print(f"obj5._variables: {list(obj5._variables.keys())}")
print(f"obj5._coord_names: {obj5._coord_names}")
print(f"obj5._indexes: {list(obj5._indexes.keys())}")
