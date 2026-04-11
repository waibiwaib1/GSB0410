import sys
sys.path.insert(0, r'd:\Code\Multi-SWE-bench\task6\task6_M1')

import xarray as xr
from xarray import Dataset, DataArray
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

obj = ds.reset_index("x")
print(f"obj._variables: {list(obj._variables.keys())}")
print(f"obj._coord_names: {obj._coord_names}")
print(f"obj._indexes: {list(obj._indexes.keys())}")
print(f"len(obj.xindexes): {len(obj.xindexes)}")

# 检查变量类型
print("Variable types:")
for k, v in obj._variables.items():
    print(f"  {k}: {type(v).__name__}")

print()
print("=== Test reset_index with drop=True ===")
ds2 = create_test_multiindex()
# 预期：drop=True 时只删除 'x'，保留 level_1 和 level_2
obj_drop = ds2.reset_index("x", drop=True)
print(f"obj_drop._variables: {list(obj_drop._variables.keys())}")
print(f"obj_drop._coord_names: {obj_drop._coord_names}")
print(f"obj_drop._indexes: {list(obj_drop._indexes.keys())}")

print()
print("=== Test reset_index with level name ===")
ds3 = create_test_multiindex()
obj_level = ds3.reset_index("level_1")
print(f"obj_level._variables: {list(obj_level._variables.keys())}")
print(f"obj_level._coord_names: {obj_level._coord_names}")
print(f"obj_level._indexes: {list(obj_level._indexes.keys())}")
