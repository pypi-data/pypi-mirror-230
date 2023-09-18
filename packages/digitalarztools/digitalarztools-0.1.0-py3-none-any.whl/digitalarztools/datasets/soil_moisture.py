from digitalarztools.pipelines.gee.core.image import GEEImage
from digitalarztools.pipelines.gee.core.image_collection import GEEImageCollection
from digitalarztools.utils.logger import da_logger


class SoilMoisture:

    @staticmethod
    def smap_data_using_gee(gee_auth, region, start_date, end_date,  how='mean', band="sm_surface") -> GEEImage:
        """
        https://developers.google.com/earth-engine/datasets/catalog/NASA_SMAP_SPL4SMGP_007#bands
         :param gdv: for define AOI
        :param start_date:
        :param end_date:
          :param how: choices are 'median', 'max', 'mean', 'first', 'cloud_cover',
        :param band: choices are sm_surface, sm_rootzone,sm_profile etc. see detail in above url
        :return: GEEImage
        """
        if gee_auth.is_initialized:
            date_range = (start_date, end_date)
            img_collection = GEEImageCollection(region, "NASA/SMAP/SPL4SMGP/007", date_range)
            img_collection.select_dataset(band)
            return GEEImage(img_collection.get_image(how))
        else:
            da_logger.error("Please initialized GEE before further processing")