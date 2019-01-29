import os
import datetime
from warsa.precipitation.satellite.download import SatelliteBasedPrecipitationDownloadFTP


class TRMMopenFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source:
        ftp://trmmopen.gsfc.nasa.gov
    """
    def __init__(self, local_dir, prefix, suffix, dir_lens, ftp_dir):
        super(TRMMopenFTP, self).__init__(local_dir, prefix, suffix, dir_lens, 'trmmopen.gsfc.nasa.gov', ftp_dir)

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(filename)[0].split('.')[1], '%Y%m%d%H')


class TRMMopen3B40RTv7x3hFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source:
        ftp://trmmopen.gsfc.nasa.gov/pub/merged/combinedMicro/2000/03/
    Format:
        3B40RT.2000030100.7R2.bin.gz
        3B40RT.2016111109.7.bin.gz
    """
    def __init__(self, local_dir):
        super(TRMMopen3B40RTv7x3hFTP, self).__init__(local_dir, '3B40RT.', '.gz', [4, 2],
                                                     'trmmopen.gsfc.nasa.gov', '/pub/merged/combinedMicro/')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(filename)[0].split('.')[1], '%Y%m%d%H')


class TRMMopen3B41RTv7x3hFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source
        ftp://trmmopen.gsfc.nasa.gov/pub/merged/calibratedIR/2000/03/
    Format:
        3B41RT.2000030100.7R2.bin.gz
    """
    def __init__(self, local_dir):
        super(TRMMopen3B41RTv7x3hFTP, self).__init__(local_dir, '3B41RT.', '.gz', [4, 2],
                                                     'trmmopen.gsfc.nasa.gov', '/pub/merged/calibratedIR/')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(filename)[0].split('.')[1], '%Y%m%d%H')


class TRMMopen3B42RTv7x3hFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source
        ftp://trmmopen.gsfc.nasa.gov/pub/merged/mergeIRMicro/2000/03/
    Format:
        3B42RT.2000030100.7R2.bin.gz
    """
    def __init__(self, local_dir):
        super(TRMMopen3B42RTv7x3hFTP, self).__init__(local_dir, '3B42RT.', '.gz', [4, 2],
                                                     'trmmopen.gsfc.nasa.gov', '/pub/merged/mergeIRMicro/')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(filename)[0].split('.')[1], '%Y%m%d%H')


class TRMMopen3B42RTv7x3hGISFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source
        ftp://trmmopen.gsfc.nasa.gov/pub/gis/200003/
    Format:
        3B42RT.2000030200.03hr.tif
        3B42RT.2000030200.03hr.tfw
    """
    def __init__(self, local_dir):
        super(TRMMopen3B42RTv7x3hGISFTP, self).__init__(local_dir, '3B42RT.', ['.tif', '.tfw'], [6],
                                                        'trmmopen.gsfc.nasa.gov', '/pub/gis')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(''.join(os.path.splitext(filename)[0].split('.')[1]), '%Y%m%d%H')


class TRMMopen3B42v7x3hFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source
        ftp://trmmopen.gsfc.nasa.gov/pub/TMPA/TRMMstandard/3B42/1998/01/01/
    Format:
        3B42.19980101.00.7.HDF.gz
    """
    def __init__(self, local_dir):
        super(TRMMopen3B42v7x3hFTP, self).__init__(local_dir, '3B42.', '.HDF.gz', [4, 2, 2],
                                                   'trmmopen.gsfc.nasa.gov', '/pub/trmmdata/ByDate/V07')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(''.join(os.path.splitext(filename)[0].split('.')[1:3]), '%Y%m%d%H')


class TRMMopen3B42v7x3hGISFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source
         ftp://trmmopen.gsfc.nasa.gov/trmmdata/GIS/2014/01/01/
    Format:
        3B42RT.2000030200.03hr.tif
        3B42RT.2000030200.03hr.tfw
    """
    def __init__(self, local_dir):
        super(TRMMopen3B42v7x3hGISFTP, self).__init__(local_dir, '3B42.', ['.tif', 'tfw'], [4, 2, 2],
                                                      'trmmopen.gsfc.nasa.gov', '/trmmdata/GIS')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(''.join(os.path.splitext(filename)[0].split('.')[1:3]), '%Y%m%d%H')


# =============================================================================
# TRMM Nascom
# =============================================================================
class TRMMnascom3B42RTv7x3hFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source
        ftp://disc2.nascom.nasa.gov/data/opendap/TRMM_RT/TRMM_3B42RT.7/2000/060/
    Format:
        3B42RT.2000030100.7R2.nc4
        3B42RT.2000030100.7R2.nc4.xml
        3B42RT.2016111903.7.nc4
        3B42RT.2016111903.7.nc4.xml
    """
    def __init__(self, local_dir):
        super(TRMMnascom3B42RTv7x3hFTP, self).__init__(local_dir, '3B42RT.', '.nc4', [4, 3],
                                                       'disc2.nascom.nasa.gov', '/data/opendap/TRMM_RT/TRMM_3B42RT.7')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(os.path.basename(filename))[0].split('.')[1], '%Y%m%d%H')


class TRMMnascom3B42V7x3hFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source
        ftp://disc2.nascom.nasa.gov/data/opendap/TRMM_L3/TRMM_3B42.7/1997/365/
    Format:
        3B42.19980101.00.7.HDF
        3B42.19980101.00.7.HDF.map.gz
        3B42.19980101.00.7.HDF.xml
    """
    def __init__(self, local_dir):
        super(TRMMnascom3B42V7x3hFTP, self).__init__(local_dir, '3B42.', '.HDF', [4, 3],
                                                     'disc2.nascom.nasa.gov', '/data/opendap/TRMM_L3/TRMM_3B42.7')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(''.join(os.path.splitext(os.path.basename(filename))[0].split('.')[1:3]),
                                          '%Y%m%d%H')


class TRMMnascom3B42V7xDailyFTP(SatelliteBasedPrecipitationDownloadFTP):
    """Source
        ftp://disc2.nascom.nasa.gov/data/opendap/TRMM_L3/TRMM_3B42_Daily.7/1998/01/
    Format:
        3B42_Daily.19980101.7.nc4
        3B42_Daily.19980101.7.nc4.xml
    """
    def __init__(self, local_dir):
        super(TRMMnascom3B42V7xDailyFTP, self).__init__(local_dir, '3B42_Daily.', '.nc4', [4, 2],
                                                     'disc2.nascom.nasa.gov', '/data/opendap/TRMM_L3/TRMM_3B42.7')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(os.path.basename(filename))[0].split('.')[1], '%Y%m%d')


