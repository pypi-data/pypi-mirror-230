import os.path

from digitalarztools.io.vector.gpd_vector import GPDVector
from test.test_config import BASE_DIR

if __name__ == "__main__":
    # shp_path = os.path.join(BASE_DIR, '../../DHATreeCount/media/shp/AOI.shp')
    # gdf_io = GPDVector.from_shp(shp_path)
    # crs = gdf_io.get_crs()
    # print(crs.to_wkt())
    fp = os.path.join(BASE_DIR, "test_data/flood_analysis_rp.xlsx")
    gdv = GPDVector.from_excel(fp, geom_col="Location")
    print(gdv.to_goejson())
    print(gdv.head())