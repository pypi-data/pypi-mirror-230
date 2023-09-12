from cyclone_track_database import CycloneTrackDatabase

tdb = CycloneTrackDatabase("ibtracs", file_name=r"d:\old_d\delftdashboard\data\toolboxes\TropicalCyclone\IBTrACS.ALL.v04r00.nc")

#index = tdb.filter(basin="NA", year_min=1960, year_max=2023, name='hugo')
#trk   = tdb.get_track(index[0])

#index = tdb.filter(lon=-70.0, lat=30.0, distance=100.0)
index = tdb.filter(lon=[-70.0, -60.0], lat=[30.0, 40.0])

gdf = tdb.to_gdf(index=index)
gdf = tdb.to_gdf()

pass
