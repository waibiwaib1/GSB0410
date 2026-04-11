import sys
sys.path.insert(0, r'd:\Code\Multi-SWE-bench\task6\task6_M1')

import xarray as xr
import pandas as pd
import numpy as np

print("Python version:", sys.version)
print("xarray version:", xr.__version__)
print()

# 创建一个简单的数据集
ds = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ['a', 'b', 'c'])})
print("Original dataset:")
print("  _variables:", list(ds._variables.keys()))
print("  _coord_names:", ds._coord_names)
print("  _indexes:", list(ds._indexes.keys()))
print()

# set_index
ds_set = ds.set_index(z=['a', 'b'])
print("After set_index(z=['a', 'b']):")
print("  _variables:", list(ds_set._variables.keys()))
print("  _coord_names:", ds_set._coord_names)
print("  _indexes:", list(ds_set._indexes.keys()))
print()

# 检查变量类型
print("Variable types:")
for k, v in ds_set._variables.items():
    print(f"  {k}: {type(v).__name__}")
print()

# 检查 DataVariables 长度
try:
    dv_len = len(ds_set.data_vars)
    print(f"DataVariables length: {dv_len}")
except Exception as e:
    print(f"DataVariables length error: {e}")
    import traceback
    traceback.print_exc()
print()

# reset_index with drop=True
try:
    ds_reset = ds_set.reset_index("z", drop=True)
    print("After reset_index('z', drop=True):")
    print("  _variables:", list(ds_reset._variables.keys()))
    print("  _coord_names:", ds_reset._coord_names)
    print("  _indexes:", list(ds_reset._indexes.keys()))
    print()
    try:
        dv_len = len(ds_reset.data_vars)
        print(f"DataVariables length: {dv_len}")
    except Exception as e:
        print(f"DataVariables length error: {e}")
        import traceback
        traceback.print_exc()
except Exception as e:
    print(f"reset_index error: {e}")
    import traceback
    traceback.print_exc()
