import os
import datetime
from warsa.precipitation.satellite.download import FTPDownload


class GPMImergFTP(FTPDownload):
    def __init__(self, local_dir, prefix, suffix, dir_lens, ftp_host, ftp_dir, ftp_user, ftp_password,
                 ftp_timeout, product_subfolder):
        super(GPMImergFTP, self).__init__(local_dir, prefix, suffix, dir_lens, ftp_host, ftp_dir, ftp_user,
                                          ftp_password, ftp_timeout, product_subfolder)

    @staticmethod
    def get_datetime_from_file_name(filename):
        s = os.path.basename(filename).split('.')[4].split('-')
        return datetime.datetime.strptime(''.join([s[0], s[1][1:]]), '%Y%m%d%H%M%S')


class GPMImergProductionHHFTP(GPMImergFTP):
    """Source:
        ftp://arthurhou.pps.eosdis.nasa.gov/gpmdata/2014/03/01/imerg
        ftp://arthurhou.pps.eosdis.nasa.gov/gpmdata/2014/11/07/imerg
    Format:
        3B-MO.MS.MRG.3IMERG.20140312-S000000-E235959.03.V03D.HDF5
        3B-HHR.MS.MRG.3IMERG.20141107-S000000-E002959.0000.V03D.HDF5
    """

    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergProductionHHFTP, self).__init__(local_dir, '3B-HHR.', '.HDF5', [4, 2, 2],
                                                    'arthurhou.pps.eosdis.nasa.gov', '/gpmdata', ftp_user, ftp_password,
                                                    600, 'imerg')


class GPMImergProductionMOFTP(GPMImergFTP):
    """Source:
        ftp://arthurhou.pps.eosdis.nasa.gov/gpmdata/2014/03/01/imerg
        ftp://arthurhou.pps.eosdis.nasa.gov/gpmdata/2014/11/07/imerg
    Format:
        3B-MO.MS.MRG.3IMERG.20140312-S000000-E235959.03.V03D.HDF5
        3B-HHR.MS.MRG.3IMERG.20141107-S000000-E002959.0000.V03D.HDF5
    """

    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergProductionMOFTP, self).__init__(local_dir, '3B-MO.', '.HDF5', [4, 2, 2],
                                                      'arthurhou.pps.eosdis.nasa.gov', '/gpmdata', ftp_user,
                                                      ftp_password, 600, 'imerg')


class GPMImergVersionFTP(GPMImergFTP):
    """Source:
        ftp://arthurhou.pps.eosdis.nasa.gov/gpmdata/2014/03/01/imerg
        ftp://arthurhou.pps.eosdis.nasa.gov/gpmdata/2014/11/07/imerg
    Format:
        3B-MO.MS.MRG.3IMERG.20140312-S000000-E235959.03.V03D.HDF5
        3B-HHR.MS.MRG.3IMERG.20141107-S000000-E002959.0000.V03D.HDF5
    """

    def __init__(self, local_dir, version, prefix, suffix, ftp_user, ftp_password, ftp_timeout, product_subfolder):
        super(GPMImergVersionFTP, self).__init__(local_dir, prefix, suffix, [4, 2, 2],
                                                    'arthurhou.pps.eosdis.nasa.gov', '/gpmallversions/' + version, ftp_user, ftp_password,
                                                    ftp_timeout, product_subfolder)


class GPMImerg3BHHRv03FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImerg3BHHRv03FTP, self).__init__(local_dir, 'V03', '3B-HHR.', '.HDF5', ftp_user, ftp_password, 600,
                                                  'imerg')


class GPMImerg3BMOv03FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImerg3BMOv03FTP, self).__init__(local_dir, 'V03', '3B-MO.', '.HDF5', ftp_user, ftp_password, 600,
                                                 'imerg')


class GPMImergGIS3BHHRv03FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergGIS3BHHRv03FTP, self).__init__(local_dir, 'V03', '3B-HHR-GIS.', ['.tfw', '.tif'], ftp_user,
                                                     ftp_password, 600, 'gis')


class GPMImergGIS3BDailyV03FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergGIS3BDailyV03FTP, self).__init__(local_dir, 'V03', '3B-DAY-GIS.', ['.tfw', '.tif'], ftp_user,
                                                       ftp_password, 600, 'gis')


class GPMImergGIS3BMOv03FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergGIS3BMOv03FTP, self).__init__(local_dir, 'V03', '3B-MO-GIS.', ['.tfw', '.tif'], ftp_user,
                                                    ftp_password, 600, 'gis')


class GPMImerg3BHHRv04FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImerg3BHHRv04FTP, self).__init__(local_dir, 'V04', '3B-HHR.', '.HDF5', ftp_user, ftp_password, 600,
                                                  'imerg')


class GPMImerg3BMOv04FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImerg3BMOv04FTP, self).__init__(local_dir, 'V04', '3B-MO.', '.HDF5', ftp_user, ftp_password, 600,
                                                 'imerg')


class GPMImergGIS3BHHRv04FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergGIS3BHHRv04FTP, self).__init__(local_dir, 'V04', '3B-HHR-GIS.', ['.tfw', '.tif'], ftp_user,
                                                     ftp_password, 600, 'gis')


class GPMImergGIS3BDailyV04FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergGIS3BDailyV04FTP, self).__init__(local_dir, 'V04', '3B-DAY-GIS.', ['.tfw', '.tif'], ftp_user,
                                                       ftp_password, 600, 'gis')


class GPMImergGIS3BMOv04FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergGIS3BMOv04FTP, self).__init__(local_dir, 'V04', '3B-MO-GIS.', ['.tfw', '.tif'], ftp_user,
                                                    ftp_password, 600, 'gis')


class GPMImerg3BHHRv05FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImerg3BHHRv05FTP, self).__init__(local_dir, 'V05', '3B-HHR.', '.HDF5', ftp_user, ftp_password, 600,
                                                  'imerg')


class GPMImerg3BMOv05FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImerg3BMOv05FTP, self).__init__(local_dir, 'V05', '3B-MO.', '.HDF5', ftp_user, ftp_password, 600,
                                                 'imerg')


class GPMImergGIS3BHHRv05FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergGIS3BHHRv05FTP, self).__init__(local_dir, 'V05', '3B-HHR-GIS.', ['.tfw', '.tif'], ftp_user,
                                                     ftp_password, 600, 'gis')


class GPMImergGIS3BDailyV05FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergGIS3BDailyV05FTP, self).__init__(local_dir, 'V05', '3B-DAY-GIS.', ['.tfw', '.tif'], ftp_user,
                                                       ftp_password, 600, 'gis')


class GPMImergGIS3BMOv05FTP(GPMImergVersionFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImergGIS3BMOv05FTP, self).__init__(local_dir, 'V05', '3B-MO-GIS.', ['.tfw', '.tif'], ftp_user,
                                                    ftp_password, 600, 'gis')


class GPMImergRealTimeFTP(GPMImergFTP):
    """Source:
        ftp://jsimpson.pps.eosdis.nasa.gov/data/imerg/early/201503/
    Format:
        3B-HHR-E.MS.MRG.3IMERG.20150331-S190000-E192959.1140.V03E.RT-H5
        3B-HHR-L.MS.MRG.3IMERG.20150307-S000000-E002959.0000.V03E.RT-H5
    """
    def __init__(self, local_dir, prefix, suffix, ftp_dir, ftp_user, ftp_password):
        """
        :param local_dir:
        :param ftp_user:
        :param ftp_password:
        :return:
        """
        super(GPMImergRealTimeFTP, self).__init__(local_dir, prefix, suffix, [6], 'jsimpson.pps.eosdis.nasa.gov',
                                                  ftp_dir, ftp_user, ftp_password, 600, product_subfolder='')


class GPMImerg3BHHRearlyFTP(GPMImergRealTimeFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImerg3BHHRearlyFTP, self).__init__(local_dir, '3B-HHR-E.', '.RT-H5', '/data/imerg/early',
                                                      ftp_user, ftp_password)


class GPMImerg3BHHRlateFTP(GPMImergRealTimeFTP):
    def __init__(self, local_dir, ftp_user, ftp_password):
        super(GPMImerg3BHHRlateFTP, self).__init__(local_dir, '3B-HHR-L.', '.RT-H5', '/data/imerg/late',
                                                   ftp_user, ftp_password)


