import sys
sys.path.insert(0, r'd:\Code\Multi-SWE-bench\task6\task6_M1')

import xarray as xr
from xarray import Dataset, DataArray
from xarray.core.indexes import PandasMultiIndex, PandasIndex
import pandas as pd
import numpy as np

# 模拟 set_index 的场景
ds = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ['a', 'b', 'c'])})

print("=== Original dataset ===")
print(f"_variables: {list(ds._variables.keys())}")
print(f"_coord_names: {ds._coord_names}")
print(f"_indexes: {list(ds._indexes.keys())}")

# set_index
ds2 = ds.set_index(z=['a', 'b'])

print()
print("=== After set_index(z=['a', 'b']) ===")
print(f"_variables: {list(ds2._variables.keys())}")
print(f"_coord_names: {ds2._coord_names}")
print(f"_indexes: {list(ds2._indexes.keys())}")
print()
print("Variable types:")
for k, v in ds2._variables.items():
    print(f"  {k}: {type(v).__name__}")

# 问题描述说："那些'被替换掉'的原有坐标会从变量列表中消失"
# 但从输出看，a 和 b 还在变量列表中。
# 让我检查一下是否有其他场景...

print()
print("=== 让我检查另一个场景：用不同变量创建单级索引 ===")
ds3 = xr.Dataset(coords={"x": [1, 2, 3], "a": ("x", [10, 20, 30])})
print(f"Original _variables: {list(ds3._variables.keys())}")
print(f"Original _indexes: {list(ds3._indexes.keys())}")

ds4 = ds3.set_index(x="a")
print()
print(f"After set_index(x='a'):")
print(f"_variables: {list(ds4._variables.keys())}")
print(f"_coord_names: {ds4._coord_names}")
print(f"_indexes: {list(ds4._indexes.keys())}")
print()
print("Variable types:")
for k, v in ds4._variables.items():
    print(f"  {k}: {type(v).__name__}")

# 原始 x 坐标是否丢失了？
print()
print("=== 检查原始 x 坐标 ===")
ds5 = xr.Dataset(coords={"x": [1, 2, 3], "a": ("x", [10, 20, 30])})
print(f"Original:")
print(f"  x values: {ds5['x'].values}")
print(f"  a values: {ds5['a'].values}")

ds6 = ds5.set_index(x="a")
print()
print(f"After set_index(x='a'):")
print(f"  x values: {ds6['x'].values}")  # 这应该是 a 的值 [10, 20, 30]
# 原始的 [1, 2, 3] 是否丢失了？
