import sys
sys.path.insert(0, r'd:\Code\Multi-SWE-bench\task6\task6_M1')

import xarray as xr
import pandas as pd
import numpy as np

# 创建一个简单的数据集
ds = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ['a', 'b', 'c'])})

# set_index
ds_set = ds.set_index(z=['a', 'b'])
print("After set_index(z=['a', 'b']):")
print("  _variables:", list(ds_set._variables.keys()))
print("  _coord_names:", ds_set._coord_names)
print("  _indexes:", list(ds_set._indexes.keys()))
print()

# reset_index with drop=False
ds_reset = ds_set.reset_index("z", drop=False)
print("After reset_index('z', drop=False):")
print("  _variables:", list(ds_reset._variables.keys()))
print("  _coord_names:", ds_reset._coord_names)
print("  _indexes:", list(ds_reset._indexes.keys()))
print("  Variable types:")
for k, v in ds_reset._variables.items():
    print(f"    {k}: {type(v).__name__}")
print()

# 测试 MultiIndex 情况
mindex = pd.MultiIndex.from_product(
    [["a", "b"], [1, 2]], names=("level_1", "level_2")
)
ds_midx = xr.Dataset({}, {"x": mindex})
print("MultiIndex dataset:")
print("  _variables:", list(ds_midx._variables.keys()))
print("  _coord_names:", ds_midx._coord_names)
print("  _indexes:", list(ds_midx._indexes.keys()))
print()

# reset_index 单个层级
ds_reset1 = ds_midx.reset_index("level_1")
print("After reset_index('level_1'):")
print("  _variables:", list(ds_reset1._variables.keys()))
print("  _coord_names:", ds_reset1._coord_names)
print("  _indexes:", list(ds_reset1._indexes.keys()))
print()

# reset_index 多个层级
ds_reset2 = ds_midx.reset_index(["level_1", "level_2"])
print("After reset_index(['level_1', 'level_2']):")
print("  _variables:", list(ds_reset2._variables.keys()))
print("  _coord_names:", ds_reset2._coord_names)
print("  _indexes:", list(ds_reset2._indexes.keys()))
print()

# reset_index 维度名
ds_reset3 = ds_midx.reset_index("x")
print("After reset_index('x'):")
print("  _variables:", list(ds_reset3._variables.keys()))
print("  _coord_names:", ds_reset3._coord_names)
print("  _indexes:", list(ds_reset3._indexes.keys()))
print()

# reset_index with drop=True for MultiIndex
ds_reset4 = ds_midx.reset_index("x", drop=True)
print("After reset_index('x', drop=True):")
print("  _variables:", list(ds_reset4._variables.keys()))
print("  _coord_names:", ds_reset4._coord_names)
print("  _indexes:", list(ds_reset4._indexes.keys()))
