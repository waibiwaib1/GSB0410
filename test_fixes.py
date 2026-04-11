import xarray as xr
import pandas as pd

lines = []
def log(msg):
    lines.append(msg)

log("=== MVCE ===")
ds = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ["a", "b", "c"])})
result = ds.set_index(z=["a", "b"]).reset_index("z", drop=True)
log(f"len(data_vars) = {len(result.data_vars)}")
log(f"coord_names = {result._coord_names}")
log(f"variables = {list(result._variables.keys())}")
log(f"coord_names subset of variables: {result._coord_names.issubset(result._variables.keys())}")
try:
    repr(result)
    log("repr: OK")
except Exception as e:
    log(f"repr: FAIL - {e}")

log("\n=== Issue 2: set_index then reset_index preserves coords ===")
ds2 = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ["a", "b", "c"])})
ds3 = ds2.set_index(z=["a", "b"])
ds4 = ds3.reset_index("z", drop=False)
log(f"reset_index(z, drop=False): coords={list(ds4.coords)}, indexes={list(ds4._indexes.keys())}")
ds5 = ds3.reset_index("z", drop=True)
log(f"reset_index(z, drop=True): coords={list(ds5.coords)}, indexes={list(ds5._indexes.keys())}")

log("\n=== Issue 3: multi-index to single-index name ===")
mindex = pd.MultiIndex.from_arrays(
    [["a", "b", "c"], [1, 2, 3]], names=["level_1", "level_2"]
)
ds6 = xr.Dataset({}, coords={"x": xr.Variable("x", mindex)})
ds7 = ds6.reset_index("level_1")
log(f"reset_index('level_1'): indexes={list(ds7._indexes.keys())}")
has_x_index = "x" in ds7._indexes
log(f"  Has index on 'x': {has_x_index}")
if has_x_index:
    idx = ds7._indexes["x"]
    log(f"  Index type: {type(idx).__name__}, dim={idx.dim}")
    log(f"  index.name: {idx.index.name}")
try:
    repr(ds7)
    log("  repr: OK")
except Exception as e:
    log(f"  repr: FAIL - {e}")

log("\n=== Issue 1: reset_index duplicate processing ===")
ds8 = ds6.reset_index(["level_1", "level_2"])
log(f"reset_index(['level_1', 'level_2']): coord_names={ds8._coord_names}")
log(f"  coord_names subset of variables: {ds8._coord_names.issubset(ds8._variables.keys())}")

ds9 = ds6.reset_index(["level_1", "level_2"], drop=True)
log(f"reset_index(['level_1', 'level_2'], drop=True): coord_names={ds9._coord_names}")
log(f"  coord_names subset of variables: {ds9._coord_names.issubset(ds9._variables.keys())}")

log("\n=== Issue 2: set_index with dim name different from variable dims ===")
ds10 = xr.Dataset({"data": ("x", [10, 20, 30])}, coords={"a": ("x", [1, 2, 3]), "b": ("x", ["a", "b", "c"])})
ds11 = ds10.set_index(z=["a", "b"])
log(f"After set_index(z=['a','b']):")
log(f"  dims: {dict(ds11.dims)}")
log(f"  coords: {list(ds11.coords)}")
log(f"  indexes: {list(ds11._indexes.keys())}")
try:
    result = ds11.sel(a=1)
    log(f"  sel(a=1): OK, data={result['data'].values}")
except Exception as e:
    log(f"  sel(a=1): FAIL - {e}")

with open("final_test_results.txt", "w") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
