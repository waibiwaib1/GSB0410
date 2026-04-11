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

print("=== 测试 1: reset_index(['level_1']) ===")
print("预期: xindexes = ['level_2'] (测试用例期望)")
obj4 = mda.reset_index(["level_1"])
print(f"实际: xindexes = {list(obj4.xindexes)}")
for key in obj4.xindexes:
    idx = obj4.xindexes[key]
    print(f"  {key}: type={type(idx).__name__}, dim={idx.dim}, index.name={idx.index.name}")
print(f"  coords: {list(obj4.coords)}")

print()
print("=== 问题描述 3: 多级索引降为单级索引时名称不一致 ===")
print("问题描述说: 生成的单级索引名称应自动改为对应的维度名 (x)")
print("但测试用例期望: level_2")

print()
print("=== 让我分析一下 ===")
print("测试用例中的 expected 是:")
indexes = [mindex.get_level_values(n) for n in mindex.names]
coords = {idx.name: ("x", idx) for idx in indexes}
coords["x"] = ("x", mindex.values)
expected = DataArray(mda.values, coords=coords, dims=["x", "y"])
print(f"expected.coords: {list(expected.coords)}")
print(f"expected.xindexes: {list(expected.xindexes)}")

print()
print("=== 让我看一下 xindexes.get_all_coords ===")
# 这是理解行为的关键
from xarray.core.indexes import Indexes

idx = mda.xindexes["x"]
print(f"type(mda.xindexes['x']): {type(idx).__name__}")
print(f"mda.xindexes['x'].dim: {idx.dim}")
print(f"mda.xindexes['x'].index.names: {idx.index.names}")

all_coords_x = list(mda.xindexes.get_all_coords("x"))
all_coords_level1 = list(mda.xindexes.get_all_coords("level_1"))
all_coords_level2 = list(mda.xindexes.get_all_coords("level_2"))

print(f"get_all_coords('x'): {all_coords_x}")
print(f"get_all_coords('level_1'): {all_coords_level1}")
print(f"get_all_coords('level_2'): {all_coords_level2}")
