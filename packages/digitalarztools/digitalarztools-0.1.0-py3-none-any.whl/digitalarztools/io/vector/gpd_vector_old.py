import json
import math
import os.path
import traceback

import fiona
import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from pyproj import CRS
from rasterio.features import rasterize
from shapely import wkt
from shapely.geometry import GeometryCollection
from sqlalchemy import Engine, create_engine, text

from digitalarztools.adapters.manager import DBString, DBManager, GeoDBManager
from digitalarztools.operations.transformation import TransformationOperations


class GPDVector():
    gdf: gpd.GeoDataFrame
    orig_crs: CRS

    def __init__(self, gdf: gpd.GeoDataFrame):
        self.gdf = gdf
        self.orig_crs = self.gdf.crs

    @classmethod
    def from_kml(cls, fp):
        fiona.drvsupport.supported_drivers['KML'] = 'rw'
        gdf = gpd.read_file(fp, driver='KML')
        return cls(gdf)

    @property
    def extent(self):
        return self.gdf.total_bounds

    @classmethod
    def from_xy(cls, src, sheet_name='Sheet1', x_col='X', y_col='Y', crs='epsg:4326') -> 'GPDVector':
        """
        Create GeoDataFrame from xy value in an excel file
        :param src:
        :param sheet_name:
        :param x_col:
        :param y_col:
        :param crs:
        :return:
        """
        if os.path.exists(src):
            df = pd.read_excel(src, sheet_name=sheet_name)
            geom = gpd.points_from_xy(df[x_col], df[y_col])
            gdf = gpd.GeoDataFrame(df, geometry=geom, crs=crs)
            return cls(gdf)
        else:
            raise Exception(f"Excel file doesn't exist at {src}")

    @classmethod
    def from_excel(cls, src, sheet_name='Sheet1', crs='epsg:4326', geom_col='geometry') -> 'GPDVector':
        if os.path.exists(src):
            df = pd.read_excel(src, sheet_name=sheet_name)
            gdf = gpd.GeoDataFrame(df)

            def load_wkt(x):
                try:
                    if pd.notnull(x):
                        return shapely.wkt.loads(x)
                    else:
                        return GeometryCollection()
                except:
                    return GeometryCollection()

            # gdf[geom_col] = gdf[geom_col].apply(wkt.loads)
            gdf["geometry"] = gdf[geom_col].apply(load_wkt)
            gdf.drop([geom_col], axis=1)
            gdf.geometry = gdf["geometry"]
            gdf.crs = crs
            # for index, row in df.iterrows():
            #     value = row[geom_col]
            #     try:
            #         if pd.notnull(value):
            #             # df[index][geom_col] = wkt.loads(value)
            #             df.xs(geom_col)[index] = wkt.loads(value)
            #     except Exception as e:
            #         traceback.print_exc()
            #         print(f'{index} [{len(value)}] {value!r}')
            # gdf = gpd.GeoDataFrame(df, geometry=df[geom_col], crs=crs)
            return cls(gdf)
        else:
            raise Exception(f"Excel file doesn't exist at {src}")

    @classmethod
    def from_shp(cls, src, srid: int = None) -> 'GPDVector':
        gdf = gpd.read_file(src)
        if srid is not None:
            gdf.crs = srid
        return cls(gdf)

    @classmethod
    def from_df(cls, df, geom_col='geometry', crs='epsg:4326') -> 'GPDVector':
        gdf = gpd.GeoDataFrame(df, geometry=df[geom_col], crs=crs)
        return cls(gdf)

    @classmethod
    def from_gpkg(cls, src, layer) -> 'GPDVector':
        gdf = gpd.read_file(src, layer=layer)
        return cls(gdf)

    @classmethod
    def from_postgis(cls, query: str, db_str: DBString, srid, geom_col='geom'):
        engine = DBManager.create_postgres_engine(db_str)
        manager = GeoDBManager(engine)
        gdf = manager.execute_query_as_gdf(query, srid, geom_col)
        return cls(gdf)

    def to_postgis(self, table_name, db_str: DBString, schema=None, if_exists="fail", index=False, index_label=None,
                   chunksize=None, dtype=None):
        """

        :param table_name:
        :param db_str: DBString
        if_exists : {'fail', 'replace', 'append'}, default 'fail'
            How to behave if the table already exists:

            - fail: Raise a ValueError.
            - replace: Drop the table before inserting new values.
            - append: Insert new values to the existing table.
        schema : string, optional
            Specify the schema. If None, use default schema: 'public'.
        index : bool, default False
            Write DataFrame index as a column.
            Uses *index_label* as the column name in the table.
        index_label : string or sequence, default None
            Column label for index column(s).
            If None is given (default) and index is True,
            then the index names are used.
        chunksize : int, optional
            Rows will be written in batches of this size at a time.
            By default, all rows will be written at once.
        dtype : dict of column name to SQL type, default None
            Specifying the datatype for columns.
            The keys should be the column names and the values
            should be the SQLAlchemy types.

        Examples
        --------

        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("postgresql://myusername:mypassword@myhost:5432\/mydatabase")  # doctest: +SKIP
        >>> gdf.to_postgis("my_table", engine)  # doctest: +SKIP

        :return:
        """
        engine = DBManager.create_postgres_engine(db_str)
        self.gdf.to_postgis(table_name, engine, schema,
                            if_exists, index,
                            index_label,
                            chunksize,
                            dtype)

    def to_gpkg(self, des, layer):
        self.gdf.to_file(des, layer=layer, driver="GPKG")

    def to_excel(self, des, sheet_name="Sheet1", mode='a'):
        """
        :param des: destination file
        :param sheet_name:
        :param mode: either w (write) or a (append) default w
        :return:
        """
        cols = self.gdf.select_dtypes(include=['datetime64[ns, UTC]']).columns
        for col in cols:
            self.gdf[col] = self.gdf[col].dt.tz_localize(None)

        mode = mode if os.path.exists(des) else 'w'
        sheet_exists = 'replace' if os.path.exists(des) else None
        with pd.ExcelWriter(des, engine="openpyxl", mode=mode, if_sheet_exists=sheet_exists) as writer:
            self.gdf.to_excel(writer, sheet_name=sheet_name, index_label="index")

    def to_file(self, des):
        self.gdf.to_file(des)

    def get_srs(self) -> str:
        return self.gdf.crs.srs

    def get_crs(self):
        return self.gdf.crs

    def to_crs(self, crs=None, epsg=None):
        """
        :param crs:
        :param epsg:
        :return:
        """
        if crs is not None:
            self.gdf = self.gdf.to_crs(crs)
        if epsg is not None:
            self.gdf = self.gdf.to_crs(epsg=epsg)

    def to_raster(self, res, value_col='id') -> 'RioRaster':
        # out_arr = np.zeros((rows,cols))
        # shapes = ((geom, value) for geom, value in zip(self.gdf.geometry, self.gdf[value_col]))
        # rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
        extent = tuple(self.get_extent())
        out_shape = (math.ceil((extent[2] - extent[0]) / res), math.ceil((extent[3] - extent[1]) / res))
        transform = TransformationOperations.get_affine_matrix(extent, out_shape)
        shapes = self.get_geometry_list(value_col)
        data = rasterize(shapes, out_shape=out_shape, transform=transform)
        from digitalarztools.raster.rio_raster import RioRaster
        raster = RioRaster.raster_from_array(data, crs=self.gdf.crs, g_transform=transform,
                                             nodata_value=0)
        return raster

    def to_crs_original(self):
        if str(self.gdf.crs) != str(self.orig_crs):
            self.gdf = self.gdf.to_crs(crs=self.orig_crs)

    def get_extent(self):
        return tuple(self.gdf.geometry.total_bounds)

    def inplace_result(self, gdf, inplace) -> 'GPDVector':
        if inplace:
            self.gdf = gdf
            return self
        else:
            return GPDVector(gdf)

    def extract_sub_data(self, col_name: str, col_vals: list, inplace=False) -> 'GPDVector':
        """
        :param col_name: column name
        :param col_vals: column value as a list
        :param inplace: 
        :return: 
        """
        if isinstance(col_vals, list):
            res = []
            for v in col_vals:
                res.append(self.gdf[self.gdf[col_name] == v])

            gdf = gpd.GeoDataFrame(pd.concat(res, ignore_index=True), crs=self.get_crs())
        else:
            gdf = self.gdf[self.gdf[col_name] == col_vals]
        return self.inplace_result(gdf, inplace)

    def select_columns(self, cols, inplace=True):
        gdf = self.gdf[cols]
        return self.inplace_result(gdf, inplace)

    def add_id_col(self):
        """
        add id column in the dataframe
        """
        self.gdf["id"] = self.gdf.index + 1

    def add_class_id(self, class_id, value=None):
        # if value is not none:
        #     self.g
        self.gdf['cls_id'] = class_id

    def add_area_col(self, unit='sq.km'):
        """
        :param unit: values sq.km, sq.m
        :return:
        """
        gdf = self.gdf.to_crs(epsg='3857') if self.gdf.crs.is_geographic else self.gdf
        if unit == "sq.km":
            self.gdf['area'] = round(gdf.geometry.area / (1000 * 1000), 4)
        else:
            self.gdf['area'] = round(gdf.geometry.area, 4)

    def head(self, n=5):
        print(self.gdf.head(n=n))

    def tail(self, n=5):
        print(self.gdf.tail(n=n))

    def get_geometry(self, col_name, col_val):
        res = self.gdf[self.gdf[col_name] == col_val]['geometry']
        if not res.empty:
            return res.values[0]

    def get_gdf(self):
        return self.gdf

    def get_geometry_list(self, attr_name=None) -> list:
        if attr_name:
            # return [(row['geometry'], row[attr_name]) for index, row in self.gdf.iterrows()]
            return list(zip(self.gdf['geometry'], self.gdf[attr_name]))
        else:
            return self.gdf.geometry.tolist()

    def spatial_join(self, input_gdf: gpd.GeoDataFrame, predicate='intersects', how="inner") -> 'GPDVector':
        # inp, res = self.gdf.geometry.sindex.query_bulk(input_gdf.geometry, predicate=predicate)
        # res_df = pd.DataFrame({
        #     'self_index': res,
        #     'inp_index': inp
        # })
        # return res_df
        if str(input_gdf.crs) != str(self.get_crs()):
            input_gdf = input_gdf.to_crs(self.get_crs())
        join_result = self.gdf.sjoin(input_gdf, how="inner", predicate=predicate)
        return GPDVector(join_result)

    def to_goejson(self):
        gdf = self.gdf.dropna()
        geojson = json.loads(gdf.to_json())
        return geojson

    def apply_buffer(self, distance_in_meter: int, inplace=False) -> 'GPDVector':
        """
        :param distance_in_meter: buffer distance in radiuse
        :param inplace:
        :return: GPDVector
        """
        gdf = self.gdf.to_crs(epsg=3857)
        gdf = gdf.buffer(distance_in_meter)
        gdf = gdf.to_crs(epsg=4326)
        return self.inplace_result(gdf, inplace)

    def get_unary_union(self):
        """
        combine all geometry as a single geometry
        :return: shapely geometry
        """
        if self.get_rows_count() > 1:
            return self.gdf.geometry.unary_union
        else:
            return self.gdf.geometry.values[0]

    def get_rows_count(self) -> int:
        """
        :return: rows count
        """
        return self.gdf.shape[0]

    def get_cols_count(self) -> int:
        """
        :return: no of columns
        """
        return self.gdf.shape[1]

    def get_cols_list(self) -> list:
        """
        :return: column name list
        """
        return self.gdf.columns.tolist()

    def get_col_values(self, col_name) -> list:
        return self.gdf[col_name].values.tolist()

    def drop_duplicate_geometry(self):
        """
        :return:
        """
        self.gdf = self.gdf.drop_duplicates()

    def calculate_total_area(self):
        gdf = self.gdf.to_crs(epsg=3857)
        return gdf.area.sum()

    def remove_duplicates(self, col_name=None):
        if col_name is None:
            self.gdf = self.gdf.drop_duplicates(keep='first')
        else:
            self.gdf = self.gdf[~self.gdf.set_index(col_name).index.duplicated()]

    def is_empty(self):
        return self.gdf.empty

    def check_dates_available(self, col_name, start_date, end_date):
        res = self.gdf[self.gdf[col_name].between(start_date, end_date)]
        return res

    @classmethod
    def extent_2_envelop(cls, min_x, min_y, max_x, max_y, crs) -> 'GPDVector':
        wkt = f"Polygon(({min_x} {max_y}, {max_x} {max_y}, {max_x} {min_y}, {min_x} {min_y}, {min_x} {max_y} ))"
        env = shapely.wkt.loads(wkt)

        return cls(gpd.GeoDataFrame({'geometry': env}, index=[0], crs=crs))

    def clip_data(self, gdf: gpd.GeoDataFrame):
        if str(gdf.crs) != str(self.gdf.crs):
            gdf.to_crs(self.gdf.crs, inplace=True)
        self.gdf = self.gdf.clip(gdf, True)
        return self.gdf
