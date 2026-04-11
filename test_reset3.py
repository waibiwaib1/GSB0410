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

print("=== Test reset_index('x', drop=True) ===")
ds = create_test_multiindex()
print(f"Before: _variables={list(ds._variables.keys())}, _indexes={list(ds._indexes.keys())}")

obj = ds.reset_index("x", drop=True)
print(f"After: _variables={list(obj._variables.keys())}, _coord_names={obj._coord_names}, _indexes={list(obj._indexes.keys())}")

print()
print("=== Test reset_index('x', drop=False) ===")
ds2 = create_test_multiindex()
obj2 = ds2.reset_index("x", drop=False)
print(f"After: _variables={list(obj2._variables.keys())}, _coord_names={obj2._coord_names}, _indexes={list(obj2._indexes.keys())}")
print("Variable types:")
for k, v in obj2._variables.items():
    print(f"  {k}: {type(v).__name__}")

print()
print("=== Test reset_index(['level_1']) ===")
ds3 = create_test_multiindex()
obj3 = ds3.reset_index(["level_1"])
print(f"After: _variables={list(obj3._variables.keys())}, _coord_names={obj3._coord_names}, _indexes={list(obj3._indexes.keys())}")
print(f"xindexes: {list(obj3.xindexes)}")

print()
print("=== Test reset_index(['x', 'level_1']) ===")
ds4 = create_test_multiindex()
obj4 = ds4.reset_index(["x", "level_1"])
print(f"After: _variables={list(obj4._variables.keys())}, _coord_names={obj4._coord_names}, _indexes={list(obj4._indexes.keys())}")
print(f"xindexes: {list(obj4.xindexes)}")
