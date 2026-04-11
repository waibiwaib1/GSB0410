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

# 根据测试用例理解预期行为
print("=== Understanding expected behavior ===")
ds = create_test_multiindex()
mindex = ds["x"].to_index()

# expected in test:
indexes = [mindex.get_level_values(n) for n in mindex.names]
coords = {idx.name: ("x", idx) for idx in indexes}  # level_1, level_2
coords["x"] = ("x", mindex.values)  # x
expected = Dataset({}, coords=coords)

print(f"expected._variables: {list(expected._variables.keys())}")
print(f"expected._coord_names: {expected._coord_names}")
print(f"expected._indexes: {list(expected._indexes.keys())}")

# 测试 reset_index("x") - 应该移除所有索引
print()
print("=== reset_index('x') ===")
ds1 = create_test_multiindex()
obj1 = ds1.reset_index("x")
print(f"obj1._variables: {list(obj1._variables.keys())}")
print(f"obj1._coord_names: {obj1._coord_names}")
print(f"obj1._indexes: {list(obj1._indexes.keys())}")
print(f"obj1.xindexes: {list(obj1.xindexes)}")

# 测试 reset_index(["x", "level_1"]) - 测试用例说应该只有 level_2 作为索引
print()
print("=== reset_index(['x', 'level_1']) ===")
ds2 = create_test_multiindex()
obj2 = ds2.reset_index(["x", "level_1"])
print(f"obj2._variables: {list(obj2._variables.keys())}")
print(f"obj2._coord_names: {obj2._coord_names}")
print(f"obj2._indexes: {list(obj2._indexes.keys())}")
print(f"obj2.xindexes: {list(obj2.xindexes)}")

# 测试 reset_index(["level_1"]) - 应该只有 level_2 作为索引
print()
print("=== reset_index(['level_1']) ===")
ds3 = create_test_multiindex()
obj3 = ds3.reset_index(["level_1"])
print(f"obj3._variables: {list(obj3._variables.keys())}")
print(f"obj3._coord_names: {obj3._coord_names}")
print(f"obj3._indexes: {list(obj3._indexes.keys())}")
print(f"obj3.xindexes: {list(obj3.xindexes)}")
if "level_2" in obj3.xindexes:
    print(f"type(obj3.xindexes['level_2']): {type(obj3.xindexes['level_2']).__name__}")
