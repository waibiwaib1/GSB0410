import sys
sys.path.insert(0, r'd:\Code\Multi-SWE-bench\task6\task6_M1')

import xarray as xr
from xarray import Dataset, DataArray
from xarray.core.indexes import PandasMultiIndex, PandasIndex
import pandas as pd
import numpy as np

print("=" * 80)
print("问题 1: reset_index 对多级索引的处理不完整")
print("=" * 80)

mindex = pd.MultiIndex.from_product(
    [["a", "b"], [1, 2]], names=("level_1", "level_2")
)
ds = Dataset({}, {"x": mindex})

print(f"\n原始数据集:")
print(f"  _variables: {list(ds._variables.keys())}")
print(f"  _coord_names: {ds._coord_names}")
print(f"  _indexes: {list(ds._indexes.keys())}")

print("\n测试 1a: reset_index('x', drop=True) 只删除 x，保留 level_1, level_2")
ds1 = ds.reset_index("x", drop=True)
print(f"  _variables: {list(ds1._variables.keys())} (预期: ['level_1', 'level_2'])")
print(f"  _coord_names: {ds1._coord_names} (预期: {{'level_1', 'level_2'}})")
print(f"  _indexes: {list(ds1._indexes.keys())} (预期: [])")
assert 'level_1' in ds1._variables, "level_1 应该保留"
assert 'level_2' in ds1._variables, "level_2 应该保留"
assert 'x' not in ds1._variables, "x 应该被删除"
print("  测试通过!")

print("\n测试 1b: reset_index('x', drop=False) 保留所有坐标，转为普通坐标")
ds2 = ds.reset_index("x", drop=False)
print(f"  _variables: {list(ds2._variables.keys())} (预期: ['x', 'level_1', 'level_2'])")
print(f"  _indexes: {list(ds2._indexes.keys())} (预期: [])")
print("  Variable types:")
for k, v in ds2._variables.items():
    print(f"    {k}: {type(v).__name__} (预期: Variable, 非 IndexVariable)")
    assert type(v).__name__ == 'Variable', f"{k} 应该是 Variable"
print("  测试通过!")

print("\n测试 1c: reset_index(['level_1']) 只重置 level_1，level_2 保留为索引")
ds3 = ds.reset_index(["level_1"])
print(f"  _indexes: {list(ds3._indexes.keys())} (预期: ['level_2'])")
print(f"  xindexes: {list(ds3.xindexes)} (预期: ['level_2'])")
assert 'level_2' in ds3.xindexes, "level_2 应该是索引"
print("  测试通过!")

print("\n测试 1d: reset_index(['x', 'level_1']) 重置 x 和 level_1，level_2 保留为索引")
ds4 = ds.reset_index(["x", "level_1"])
print(f"  _indexes: {list(ds4._indexes.keys())} (预期: ['level_2'])")
print(f"  xindexes: {list(ds4.xindexes)} (预期: ['level_2'])")
assert 'level_2' in ds4.xindexes, "level_2 应该是索引"
print("  测试通过!")

print("\n" + "=" * 80)
print("问题 2: set_index 操作后旧坐标丢失")
print("=" * 80)

ds5 = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ['a', 'b', 'c'])})
print(f"\n原始数据集:")
print(f"  _variables: {list(ds5._variables.keys())} (预期: ['a', 'b'])")

ds5_set = ds5.set_index(z=['a', 'b'])
print(f"\nAfter set_index(z=['a', 'b']):")
print(f"  _variables: {list(ds5_set._variables.keys())} (预期: ['z', 'a', 'b'])")
assert 'a' in ds5_set._variables, "a 应该保留"
assert 'b' in ds5_set._variables, "b 应该保留"
assert 'z' in ds5_set._variables, "z 应该添加"
print("  测试通过!")

print("\n" + "=" * 80)
print("问题 3: 多级索引降为单级索引时名称不一致")
print("=" * 80)

ds6 = Dataset({}, {"x": mindex})
print(f"\n原始多级索引:")
print(f"  xindexes: {list(ds6.xindexes)}")
print(f"  多级索引层级名: {list(ds6['x'].to_index().names)}")

ds6_reset = ds6.reset_index(["level_1"])
print(f"\nAfter reset_index(['level_1']):")
print(f"  xindexes: {list(ds6_reset.xindexes)} (预期: ['level_2'])")
assert 'level_2' in ds6_reset.xindexes, "索引名应该是 level_2 (原始层级名)"
if 'level_2' in ds6_reset.xindexes:
    idx = ds6_reset.xindexes['level_2']
    print(f"  索引名: {idx.index.name} (预期: level_2)")
    print(f"  维度名: {idx.dim} (预期: x)")
    assert idx.index.name == 'level_2', "索引名应该是 level_2"
    assert idx.dim == 'x', "维度名应该是 x"
print("  测试通过!")

print("\n" + "=" * 80)
print("原始问题: ValueError: __len__() should return >= 0")
print("=" * 80)

ds_original = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ['a', 'b', 'c'])})
result = ds_original.set_index(z=['a', 'b']).reset_index("z", drop=True)

print(f"\nResult after set_index(z=['a', 'b']).reset_index('z', drop=True):")
print(f"  repr: {repr(result)}")
print(f"  len(result.data_vars): {len(result.data_vars)} (预期: 0)")
print(f"  _variables: {list(result._variables.keys())}")
print(f"  _coord_names: {result._coord_names}")

assert len(result.data_vars) == 0, "DataVariables 长度应该为 0"
print("  测试通过!")

print("\n" + "=" * 80)
print("所有测试通过!")
print("=" * 80)
