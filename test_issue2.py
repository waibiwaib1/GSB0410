import xarray as xr
import pandas as pd

lines = []
def log(msg):
    lines.append(msg)

# Test: set_index(z=['a','b']) then reset_index('z', drop=True)
ds = xr.Dataset({"data": ("x", [10, 20, 30])}, coords={"a": ("x", [1, 2, 3]), "b": ("x", ["a", "b", "c"])})
log("Original:")
log(f"  dims: {dict(ds.dims)}, coords: {list(ds.coords)}, data_vars: {list(ds.data_vars)}")

ds2 = ds.set_index(z=["a", "b"])
log("\nAfter set_index(z=['a','b']):")
log(f"  dims: {dict(ds2.dims)}, coords: {list(ds2.coords)}, data_vars: {list(ds2.data_vars)}")
log(f"  coord_names: {ds2._coord_names}")
log(f"  variables: {list(ds2._variables.keys())}")

ds3 = ds2.reset_index("z", drop=False)
log("\nAfter reset_index('z', drop=False):")
log(f"  dims: {dict(ds3.dims)}, coords: {list(ds3.coords)}, data_vars: {list(ds3.data_vars)}")
log(f"  coord_names: {ds3._coord_names}")
log(f"  variables: {list(ds3._variables.keys())}")
log(f"  indexes: {list(ds3._indexes.keys())}")

ds4 = ds2.reset_index("z", drop=True)
log("\nAfter reset_index('z', drop=True):")
log(f"  dims: {dict(ds4.dims)}, coords: {list(ds4.coords)}, data_vars: {list(ds4.data_vars)}")
log(f"  coord_names: {ds4._coord_names}")
log(f"  variables: {list(ds4._variables.keys())}")
log(f"  coord_names subset of variables: {ds4._coord_names.issubset(ds4._variables.keys())}")

# Test: set_index(x=['a','b']) then reset_index('x', drop=True)
ds5 = xr.Dataset({"data": ("x", [10, 20, 30])}, coords={"a": ("x", [1, 2, 3]), "b": ("x", ["a", "b", "c"])})
ds6 = ds5.set_index(x=["a", "b"])
log("\nAfter set_index(x=['a','b']):")
log(f"  dims: {dict(ds6.dims)}, coords: {list(ds6.coords)}, data_vars: {list(ds6.data_vars)}")

ds7 = ds6.reset_index("x", drop=True)
log("\nAfter reset_index('x', drop=True):")
log(f"  dims: {dict(ds7.dims)}, coords: {list(ds7.coords)}, data_vars: {list(ds7.data_vars)}")
log(f"  coord_names: {ds7._coord_names}")
log(f"  variables: {list(ds7._variables.keys())}")
log(f"  coord_names subset of variables: {ds7._coord_names.issubset(ds7._variables.keys())}")

# Test: standard multi-index operations
mindex = pd.MultiIndex.from_arrays(
    [["a", "b", "c"], [1, 2, 3]], names=["level_1", "level_2"]
)
ds8 = xr.Dataset({"data": ("x", [10, 20, 30])}, coords={"x": xr.Variable("x", mindex)})
log("\n=== Standard multi-index ===")
log(f"Original: dims={dict(ds8.dims)}, coords={list(ds8.coords)}")

ds9 = ds8.reset_index("level_1", drop=True)
log(f"reset_index('level_1', drop=True): dims={dict(ds9.dims)}, coords={list(ds9.coords)}, indexes={list(ds9._indexes.keys())}")

ds10 = ds8.reset_index(["level_1", "level_2"], drop=True)
log(f"reset_index(['level_1', 'level_2'], drop=True): dims={dict(ds10.dims)}, coords={list(ds10.coords)}, indexes={list(ds10._indexes.keys())}")
log(f"  coord_names subset of variables: {ds10._coord_names.issubset(ds10._variables.keys())}")

with open("issue2_test_results.txt", "w") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
