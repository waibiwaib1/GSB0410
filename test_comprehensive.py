import xarray as xr
import pandas as pd

lines = []
errors = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    msg = f"  {name}: {status}"
    if detail:
        msg += f" - {detail}"
    lines.append(msg)
    if not condition:
        errors.append(name)

mindex = pd.MultiIndex.from_arrays(
    [["a", "b", "c"], [1, 2, 3]], names=["level_1", "level_2"]
)

# ============================================================
# 1. MVCE - original bug
# ============================================================
ds = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ["a", "b", "c"])})
result = ds.set_index(z=["a", "b"]).reset_index("z", drop=True)
check("MVCE: no ValueError", result._coord_names.issubset(result._variables.keys()))

# ============================================================
# 2. Issue 1: reset_index multi-level handling
# ============================================================
ds_midx = xr.Dataset({}, coords={"x": xr.Variable("x", mindex)})

r1 = ds_midx.reset_index("x")
check("reset_index(dim)", r1._coord_names == {"x", "level_1", "level_2"} and len(r1._indexes) == 0)

r2 = ds_midx.reset_index("x", drop=True)
check("reset_index(dim, drop=True)", len(r2._variables) == 0)

r3 = ds_midx.reset_index("level_1")
check("reset_index(level)", "x" in r3._indexes and "level_1" not in r3._indexes)

r4 = ds_midx.reset_index("level_1", drop=True)
check("reset_index(level, drop=True)", "x" in r4._indexes and "level_1" not in r4._coord_names)

r5 = ds_midx.reset_index(["level_1", "level_2"])
check("reset_index([l1,l2])", len(r5._indexes) == 0 and r5._coord_names == {"x", "level_1", "level_2"})
check("reset_index([l1,l2]) coord subset", r5._coord_names.issubset(r5._variables.keys()))

r6 = ds_midx.reset_index(["level_1", "level_2"], drop=True)
check("reset_index([l1,l2],drop)", r6._coord_names == {"x"} and len(r6._indexes) == 0)

# ============================================================
# 3. Issue 2: set_index preserves dimension alignment
# ============================================================
ds2 = xr.Dataset({"data": ("x", [10, 20, 30])}, coords={"a": ("x", [1, 2, 3]), "b": ("x", ["a", "b", "c"])})

s1 = ds2.set_index(z=["a", "b"])
check("set_index(z=[a,b]): single dim", "z" in s1.dims and "x" not in s1.dims)
check("set_index(z=[a,b]): data dim", s1._variables["data"].dims == ("z",))

s2 = s1.reset_index("z", drop=False)
check("reset_index(z,drop=F): coords preserved", "a" in s2.coords and "b" in s2.coords and "z" in s2.coords)
check("reset_index(z,drop=F): no indexes", len(s2._indexes) == 0)

s3 = s1.reset_index("z", drop=True)
check("reset_index(z,drop=T): coords removed", "a" not in s3.coords and "b" not in s3.coords and "z" not in s3.coords)
check("reset_index(z,drop=T): data preserved", "data" in s3.data_vars)

# ============================================================
# 4. Issue 3: multi-index to single-index name
# ============================================================
r7 = ds_midx.reset_index("level_1")
idx = r7._indexes.get("x")
check("Issue3: index exists on 'x'", idx is not None)
if idx:
    check("Issue3: name == 'x'", idx.index.name == "x")

from xarray.core.indexes import PandasIndex
orig_idx = ds_midx._indexes["x"]
new_idx = orig_idx.keep_levels({"level_2": ds_midx._variables["level_2"]})
check("keep_levels returns PandasIndex", isinstance(new_idx, PandasIndex))
if isinstance(new_idx, PandasIndex):
    check("keep_levels name == dim", new_idx.index.name == "x")

# ============================================================
# 5. sel operations
# ============================================================
ds_sel = xr.Dataset({"var": ("x", [10, 20, 30])}, coords={"x": xr.Variable("x", mindex)})
try:
    r = ds_sel.sel(level_1="a")
    check("sel(level_1='a')", True)
except Exception as e:
    check("sel(level_1='a')", False, str(e))

ds_after_reset = ds_sel.reset_index("level_1")
try:
    r = ds_after_reset.sel(x=1)
    check("sel after reset_index(level)", True)
except Exception as e:
    check("sel after reset_index(level)", False, str(e))

# ============================================================
# 6. Simple index
# ============================================================
ds_simple = xr.Dataset(coords={"x": [1, 2, 3]})
rs = ds_simple.reset_index("x")
check("simple reset_index", "x" in rs._coord_names and len(rs._indexes) == 0)

rs_drop = ds_simple.reset_index("x", drop=True)
check("simple reset_index(drop=True)", len(rs_drop._variables) == 0)

# ============================================================
# Summary
# ============================================================
all_pass = len(errors) == 0
summary = f"\n{'All tests passed!' if all_pass else f'{len(errors)} tests FAILED:'}\n"
for e in errors:
    summary += f"  - {e}\n"
lines.append(summary)

with open("comprehensive_test_results.txt", "w") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
