import xarray as xr
import pandas as pd

lines = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    msg = f"  {name}: {status}"
    if detail:
        msg += f" - {detail}"
    lines.append(msg)

# Issue 1 tests
mindex = pd.MultiIndex.from_arrays(
    [["a", "b", "c"], [1, 2, 3]], names=["level_1", "level_2"]
)

# Test 1: reset_index(dim)
ds = xr.Dataset({}, coords={"x": xr.Variable("x", mindex)})
result = ds.reset_index("x")
check("reset_index(x)", result._coord_names == {"x", "level_1", "level_2"} and len(result._indexes) == 0)

# Test 2: reset_index(dim, drop=True)
result = ds.reset_index("x", drop=True)
check("reset_index(x, drop=True)", len(result._variables) == 0 and len(result._indexes) == 0)

# Test 3: reset_index(level)
result = ds.reset_index("level_1")
check("reset_index(level_1)", "x" in result._indexes and "level_1" not in result._indexes)

# Test 4: reset_index(level, drop=True)
result = ds.reset_index("level_1", drop=True)
check("reset_index(level_1, drop=True)", "x" in result._indexes and "level_1" not in result._coord_names)

# Test 5: reset_index([level_1, level_2])
result = ds.reset_index(["level_1", "level_2"])
check("reset_index([level_1, level_2])", len(result._indexes) == 0 and result._coord_names == {"x", "level_1", "level_2"})

# Test 6: reset_index([level_1, level_2], drop=True)
result = ds.reset_index(["level_1", "level_2"], drop=True)
check("reset_index([level_1, level_2], drop=True)", result._coord_names == {"x"} and len(result._indexes) == 0)

# Test 7: MVCE - original bug
ds2 = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ["a", "b", "c"])})
result = ds2.set_index(z=["a", "b"]).reset_index("z", drop=True)
check("MVCE", result._coord_names.issubset(result._variables.keys()) and len(result.data_vars) >= 0)

# Issue 3 tests
# Test 8: multi-index to single-index - name should be dim name
result = ds.reset_index("level_1")
idx = result._indexes.get("x")
check("Issue3: index on 'x'", idx is not None)
if idx is not None:
    check("Issue3: index.name == dim", idx.index.name == "x", f"got {idx.index.name}")

# Test 9: keep_levels returns PandasIndex with dim name
from xarray.core.indexes import PandasMultiIndex, PandasIndex
orig_idx = ds._indexes["x"]
new_idx = orig_idx.keep_levels({"level_2": ds._variables["level_2"]})
check("keep_levels returns PandasIndex", isinstance(new_idx, PandasIndex))
if isinstance(new_idx, PandasIndex):
    check("keep_levels index.name == dim", new_idx.index.name == "x", f"got {new_idx.index.name}")

# Test 10: sel after reset_index level
ds3 = xr.Dataset({"var": ("x", [10, 20, 30])}, coords={"x": xr.Variable("x", mindex)})
ds4 = ds3.reset_index("level_1")
try:
    result = ds4.sel(x=1)
    check("sel after reset_index(level)", True)
except Exception as e:
    check("sel after reset_index(level)", False, str(e))

# Test 11: sel on multi-index still works
try:
    result = ds3.sel(level_1="a")
    check("sel(level_1='a') on multi-index", True)
except Exception as e:
    check("sel(level_1='a') on multi-index", False, str(e))

# Test 12: Simple index reset_index
ds5 = xr.Dataset(coords={"x": [1, 2, 3]})
result = ds5.reset_index("x")
check("simple reset_index", "x" in result._coord_names and len(result._indexes) == 0)

result = ds5.reset_index("x", drop=True)
check("simple reset_index drop=True", len(result._variables) == 0)

all_pass = all("PASS" in line for line in lines)
summary = f"\n{'All tests passed!' if all_pass else 'Some tests FAILED!'}"
lines.append(summary)

with open("comprehensive_test_results.txt", "w") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
