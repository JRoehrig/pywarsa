import os
import datetime
from warsa.precipitation.satellite.download import SatelliteBasedPrecipitationDownloadFTP


class CMorphFTP(SatelliteBasedPrecipitationDownloadFTP):
    """
    ftp://ftp.cpc.ncep.noaa.gov
    """
    def __init__(self, local_folder, prefix, suffix, dir_lens, ftp_dir):
        super(CMorphFTP, self).__init__(local_folder, prefix, suffix, dir_lens, 'ftp.cpc.ncep.noaa.gov', ftp_dir)


    @staticmethod
    def get_datetime_from_file_name(filename):
        # Subclass must implement it
        raise NotImplementedError


# class CMorphV0x8km30minFTP(CMorphFTP):
#     """
#         ftp://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V0.x/RAW/8km-30min/2011/201108/
#         CMORPH_V0.x_RAW_8km-30min_2011080100.gz
#     """
#
#     def __init__(self, local_folder):
#         super(CMorphV0x8km30minFTP, self).__init__(local_folder, 'CMORPH_V0.x_RAW_8km-30min_', '.gz', [4, 6],
#                                                    '/precip/CMORPH_V0.x/RAW/8km-30min/')
#
#     @staticmethod
#     def get_datetime_from_file_name(filename):
#         try:
#             return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d%H')
#         except ValueError:
#             return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d%H%M')


class CMorphV0x025deg3hlyFTP(CMorphFTP):
    """Source:
        ftp://ftp.cpc.ncep.noaa.gov//precip/CMORPH_V0.x/RAW/
    File format:
        CMORPH_V0.x_RAW_8km-30min_2011080100.gz
    """

    def __init__(self, local_folder):
        super(CMorphV0x025deg3hlyFTP, self).__init__(local_folder, 'CMORPH_V0.x_RAW_0.25deg-3HLY_', '.gz', [4, 6],
                                                     '/precip/CMORPH_V0.x/RAW/0.25deg-3HLY/')

    @staticmethod
    def get_datetime_from_file_name(filename):
        try:
            # As downloaded
            return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d')
        except ValueError:
            # rasterized
            return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d%H')


class CMorphV0x025degDailyFTP(CMorphFTP):
    """Source:
        ftp://ftp.cpc.ncep.noaa.gov//precip/CMORPH_V0.x/RAW/8km-30min
    Format:
        CMORPH_V0.x_RAW_0.25deg-DLY_00Z_20140601.bz2
        CMORPH_V0.x_RAW_0.25deg-DLY_00Z_20161111.gz
    """
    def __init__(self, local_folder):
        super(CMorphV0x025degDailyFTP, self).__init__(local_folder, 'CMORPH_V0.x_RAW_0.25deg-DLY_00Z_', ['.bz2','gz'],
                                                      [4, 6], '/precip/CMORPH_V0.x/RAW/0.25deg-DLY_00Z/')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d')


class CMorphV1x8km30minFTP(CMorphFTP):
    """Source
        ftp://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/RAW/8km-30min
    Format
        CMORPH_V1.0_8km-30min_199801.tar
    """
    def __init__(self, local_folder):
        super(CMorphV1x8km30minFTP, self).__init__(local_folder, 'CMORPH_V1.0_8km-30min_', '.tar', [4],
                                                   '/precip/CMORPH_V1.0/RAW/8km-30min')

    @staticmethod
    def get_datetime_from_file_name(filename):
        try:
            return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m')
        except ValueError:
            return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d%H%M')


class CMorphV1x025deg3hlyFTP(CMorphFTP):
    """Source:
        ftp://ftp.cpc.ncep.noaa.gov//precip/CMORPH_V1.0/RAW/0.25deg-3HLY/1998/199801/
    Format
        CMORPH_V1.0_RAW_0.25deg-3HLY_19980101.gz
    """
    def __init__(self, local_folder):
        super(CMorphV1x025deg3hlyFTP, self).__init__(local_folder, 'CMORPH_V1.0_RAW_0.25deg-3HLY_', ['.gz', '.bz2'],
                                                        [4, 6], '/precip/CMORPH_V1.0/RAW/0.25deg-3HLY')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d')


class CMorphV1x025degDailyFTP(CMorphFTP):
    """Source:
        ftp://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V1.0/RAW/0.25deg-DLY_00Z/1998/199801/
    Format:
        CMORPH_V1.0_RAW_0.25deg-DLY_00Z_19980101.gz
        CMORPH_V1.0_RAW_0.25deg-DLY_00Z_20160101.bz2
    """
    def __init__(self, local_folder):
        super(CMorphV1x025degDailyFTP, self).__init__(local_folder, 'CMORPH_V1.0_RAW_0.25deg-DLY_00Z_', ['.gz', '.bz2'],
                                                      [4, 6], '/precip/CMORPH_V1.0/RAW/0.25deg-DLY_00Z')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d')


