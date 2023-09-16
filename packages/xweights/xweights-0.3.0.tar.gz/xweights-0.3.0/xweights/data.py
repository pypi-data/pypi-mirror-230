from pathlib import Path

data_path = Path(__file__).parent

nclist = list((data_path / "data/netcdf").glob("*"))
netcdf = [nc.as_posix() for nc in nclist]

shplist = list((data_path / "data/shp").glob("*.shp"))
shp = [sh.as_posix() for sh in shplist]
