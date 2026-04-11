import xarray as xr
import pandas as pd

lines = []

def log(msg):
    lines.append(msg)

log("=== Issue 2 Analysis: set_index loses old coordinates ===")
ds = xr.Dataset(coords={"a": ("x", [1, 2, 3]), "b": ("x", ["a", "b", "c"])})
log(f"Original: coord_names={ds._coord_names}, variables={list(ds._variables.keys())}")
log(f"  a: dims={ds._variables['a'].dims}")
log(f"  b: dims={ds._variables['b'].dims}")

ds2 = ds.set_index(z=["a", "b"])
log(f"\nAfter set_index(z=['a','b']):")
log(f"  coord_names={ds2._coord_names}, variables={list(ds2._variables.keys())}")
log(f"  indexes={list(ds2._indexes.keys())}")
for k in ds2._variables:
    log(f"  {k}: dims={ds2._variables[k].dims}")

ds3 = ds2.reset_index("z", drop=False)
log(f"\nAfter reset_index('z', drop=False):")
log(f"  coord_names={ds3._coord_names}, variables={list(ds3._variables.keys())}")
log(f"  indexes={list(ds3._indexes.keys())}")
for k in ds3._variables:
    log(f"  {k}: dims={ds3._variables[k].dims}")

ds4 = ds2.reset_index("z", drop=True)
log(f"\nAfter reset_index('z', drop=True):")
log(f"  coord_names={ds4._coord_names}, variables={list(ds4._variables.keys())}")
log(f"  indexes={list(ds4._indexes.keys())}")
for k in ds4._variables:
    log(f"  {k}: dims={ds4._variables[k].dims}")

log("\n=== Issue 3 Analysis: multi-index to single-index name inconsistency ===")
mindex = pd.MultiIndex.from_arrays(
    [["a", "b", "c"], [1, 2, 3]], names=["level_1", "level_2"]
)
ds5 = xr.Dataset({}, coords={"x": xr.Variable("x", mindex)})
log(f"\nMulti-index dataset:")
log(f"  coord_names={ds5._coord_names}, variables={list(ds5._variables.keys())}")
log(f"  indexes={list(ds5._indexes.keys())}")

ds6 = ds5.reset_index("level_1")
log(f"\nAfter reset_index('level_1'):")
log(f"  coord_names={ds6._coord_names}, variables={list(ds6._variables.keys())}")
log(f"  indexes={list(ds6._indexes.keys())}")
for k in ds6._variables:
    log(f"  {k}: dims={ds6._variables[k].dims}, type={type(ds6._variables[k]).__name__}")
for k in ds6._indexes:
    log(f"  index[{k}]: type={type(ds6._indexes[k]).__name__}, dim={ds6._indexes[k].dim}")
    if hasattr(ds6._indexes[k], 'index'):
        log(f"    index.name={ds6._indexes[k].index.name}")

ds7 = ds5.reset_index(["level_1", "level_2"])
log(f"\nAfter reset_index(['level_1', 'level_2']) - all levels dropped:")
log(f"  coord_names={ds7._coord_names}, variables={list(ds7._variables.keys())}")
log(f"  indexes={list(ds7._indexes.keys())}")
for k in ds7._variables:
    log(f"  {k}: dims={ds7._variables[k].dims}")

log("\n=== Issue 3 Detail: check keep_levels behavior ===")
from xarray.core.indexes import PandasMultiIndex, PandasIndex
idx = ds5._indexes["x"]
log(f"Original index type: {type(idx).__name__}")
log(f"  index.names={idx.index.names}")
log(f"  dim={idx.dim}")

kept_vars = {"level_2": ds5._variables["level_2"]}
new_idx = idx.keep_levels(kept_vars)
log(f"\nAfter keep_levels(level_2):")
log(f"  new index type: {type(new_idx).__name__}")
log(f"  dim={new_idx.dim}")
if isinstance(new_idx, PandasIndex):
    log(f"  index.name={new_idx.index.name}")
new_vars = new_idx.create_variables(kept_vars)
log(f"  create_variables keys: {list(new_vars.keys())}")
for k, v in new_vars.items():
    log(f"    {k}: dims={v.dims}")

with open("analysis_output.txt", "w") as f:
    f.write("\n".join(lines))
print("Done. See analysis_output.txt")
