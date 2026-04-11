import xarray as xr
import pandas as pd
import numpy as np
import sys

print("Python version:", sys.version)
print()

# 创建一个简单的数据集
ds = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ['a', 'b', 'c'])})
print("Original dataset:")
print(repr(ds))
print()
print("Original _variables:", list(ds._variables.keys()))
print("Original _coord_names:", ds._coord_names)
print("Original _indexes:", list(ds._indexes.keys()))
print()

# set_index
ds_set = ds.set_index(z=['a', 'b'])
print("After set_index(z=['a', 'b']):")
try:
    print(repr(ds_set))
except Exception as e:
    print(f"repr error: {e}")
    import traceback
    traceback.print_exc()
print()
print("set_index _variables:", list(ds_set._variables.keys()))
print("set_index _coord_names:", ds_set._coord_names)
print("set_index _indexes:", list(ds_set._indexes.keys()))
print()

# 检查变量类型
print("Variable types:")
for k, v in ds_set._variables.items():
    print(f"  {k}: {type(v).__name__}")
print()

# 检查 a 和 b 是否存在
print(f"'a' in variables: {'a' in ds_set._variables}")
print(f"'b' in variables: {'b' in ds_set._variables}")
print()

# 检查 DataVariables 长度
print("DataVariables length:", len(ds_set.data_vars))
print()

# reset_index with drop=True
try:
    ds_reset = ds_set.reset_index("z", drop=True)
    print("After reset_index('z', drop=True):")
    try:
        print(repr(ds_reset))
    except Exception as e:
        print(f"repr error: {e}")
        import traceback
        traceback.print_exc()
    print()
    print("reset_index _variables:", list(ds_reset._variables.keys()))
    print("reset_index _coord_names:", ds_reset._coord_names)
    print("reset_index _indexes:", list(ds_reset._indexes.keys()))
    print()
    print("DataVariables length after reset:", len(ds_reset.data_vars))
except Exception as e:
    print(f"reset_index error: {e}")
    import traceback
    traceback.print_exc()
