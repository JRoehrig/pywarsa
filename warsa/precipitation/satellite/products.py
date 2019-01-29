# uncompyle6 version 3.2.3
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.14 |Anaconda, Inc.| (default, Dec  7 2017, 17:05:42) 
# [GCC 7.2.0]
# Embedded file name: D:\sciebo\PythonProjects\warsa\warsa\precipitation\satellite\products.py
# Compiled at: 2018-03-30 10:52:30
import os, copy, datetime
from girs.feat.layers import LayersReader
from warsa.config import read_config, decrypt
from warsa.precipitation.satellite import time_series
from warsa.timeseries.timeseries import shift

class SatellitePrecipitationGroups(object):

    def __init__(self, download_dir=None):
        """
        
        :param download_dir: path to local directory where all precipitation products are saved
        """
        self.download_dir = download_dir
        self.product_group = dict()

    def get_download_dir(self):
        return self.download_dir

    def add_product(self, product_group, product, frequency, time_label, depth_intensity, download_class, download_folder, rasterize_class, **kwargs):
        """
        :param product_group:
        :param product:
        :param download_class:
        :param download_folder:
        :param rasterize_class:
        :param kwargs:
        :return:
        """
        if product_group not in self.product_group:
            self.product_group[product_group] = SatellitePrecipitationGroup(self, product_group)
        pf = self.product_group[product_group]
        pf.add_product(product, frequency, time_label, depth_intensity, download_class, download_folder, rasterize_class, **kwargs)

    def group_product(self):
        for gk in sorted(self.product_group.keys()):
            group = self.product_group[gk]
            for pk in sorted(group.product.keys()):
                product = group.product[pk]
                yield (group, product)

    def group_product_names(self):
        for group, product in self.group_product():
            yield (
             group.name, product.name)

    def get_group_product_names(self):
        return [ (g, p) for g, p in self.group_product_names() ]

    def has_product_group(self, product_group):
        return product_group in self.product_group

    def has_product(self, product_group, product):
        return product_group in self.product_group and self.product_group[product_group].has_product(product)

    def get_product_group(self, product_group):
        return self.product_group[product_group]

    def get_product(self, product_group, product):
        product_group = self.get_product_group(product_group=product_group)
        return product_group.get_product(product)

    def get_rasterize_class(self, product_group, product):
        product = self.get_product(product_group, product)
        return product.get_rasterize_class()

    def get_download_class(self, product_group, product):
        product = self.get_product(product_group, product)
        return product.get_download_class()


class SatellitePrecipitationGroup(object):
    """A group of products are satellite precipitation products from the same server
    
    """

    def __init__(self, product_groups, product_group_name, usr=None, pwd=None):
        self.product_groups = product_groups
        self.name = product_group_name
        self.usr = usr
        self.pwd = pwd
        self.product = dict()

    def add_product(self, product, frequency, time_label, depth_intensity, download_class, download_folder, rasterize_class, **kwargs):
        self.usr = kwargs.pop('usr', None)
        self.pwd = kwargs.pop('pwd', None)
        self.product[product] = SatellitePrecipitationProduct(self, product, frequency, time_label, depth_intensity, download_class, download_folder, rasterize_class, **kwargs)
        return

    def has_product(self, product):
        return product in self.product

    def get_name(self):
        return self.name

    def get_product(self, product):
        return self.product[product]

    def get_download_dir(self):
        return self.product_groups.get_download_dir()


class SatellitePrecipitationProduct(object):

    def __init__(self, group, product, frequency, time_label, depth_intensity, download_class, product_dir, rasterize_class, **kwargs):
        self.group = group
        self.name = product
        self.frequency = frequency
        self.time_label = time_label.upper()[0]
        self.depth_intensity = depth_intensity.upper()[0]
        self.download_class = download_class
        self.product_dir = product_dir
        self.rasterize_class = rasterize_class
        try:
            self.start_at = datetime.datetime.strptime(kwargs.pop('start_at', None), '%Y.%d.%m %H:%M')
        except:
            self.start_at = None

        self.options = copy.deepcopy(kwargs)
        assert self.time_label in ('R', 'C')
        assert self.depth_intensity in ('D', 'I')
        return

    def get_download_class(self):
        """Return the class used to download this product
        
        :return: class
        :rtype:
        """
        return self.download_class

    def get_rasterize_class(self):
        return self.rasterize_class

    def get_name(self):
        """Return the product name
        
        :return: product name
        :rtype: str
        """
        return self.name

    def get_download_dir(self):
        """Return the full path of the directory where this product was downloaded.
        
        :return: download dir full path
        :rtype: str
        """
        return os.path.join(self.group.get_download_dir(), self.product_dir)

    def get_product_dir(self):
        """Return the relative path of this product's directory.
        
        The returned path is the same as on the data provider's server
        
        :return:
        :rtype: str
        """
        return self.product_dir

    def get_begin(self):
        return self.start_at


def get_groups(**kwargs):
    """
    
    :param kwargs:
        :key root_dir:
        :key sarp_list
    :return:
    """
    from warsa.precipitation.satellite.arc2.download import ARC2AfricaBinFTP, ARC2AfricaTifFTP
    from warsa.precipitation.satellite.rfe.download import RFE2AfricaBinFTP, RFE2AfricaTifFTP, RFE2AsiaBinFTP
    from warsa.precipitation.satellite.chirps.download import Chirps20GlobalDaily05TifFTP, Chirps20GlobalDaily25TifFTP, Chirps20GlobalMonthly05TifFTP
    from warsa.precipitation.satellite.cmorph.download import CMorphV0x025deg3hlyFTP, CMorphV0x025degDailyFTP, CMorphV1x8km30minFTP, CMorphV1x025deg3hlyFTP, CMorphV1x025degDailyFTP
    from warsa.precipitation.satellite.cmorph.download_v0x_8km_30min import CMorphV0x8km30minFTP
    from warsa.precipitation.satellite.gpm.download import GPMImerg3BHHRlateFTP, GPMImergGIS3BHHRv05FTP, GPMImerg3BMOv05FTP, GPMImergGIS3BDailyV05FTP, GPMImergGIS3BMOv05FTP, GPMImergGIS3BHHRv04FTP, GPMImergGIS3BDailyV04FTP
    from warsa.precipitation.satellite.gpm.download_gpm_imerg_3BHHR_early import GPMImerg3BHHRearlyFTP
    from warsa.precipitation.satellite.gpm.download_gpm_imerg_3BHHR_v05 import GPMImerg3BHHRv05FTP
    from warsa.precipitation.satellite.trmm.download import TRMMopen3B40RTv7x3hFTP, TRMMopen3B41RTv7x3hFTP, TRMMopen3B42RTv7x3hGISFTP, TRMMopen3B42v7x3hFTP, TRMMopen3B42v7x3hGISFTP, TRMMnascom3B42RTv7x3hFTP, TRMMnascom3B42V7x3hFTP, TRMMnascom3B42V7xDailyFTP
    from warsa.precipitation.satellite.trmm.download_trmm_3B42RT_v7_3h_trmmopen import TRMMopen3B42RTv7x3hFTP
    from warsa.precipitation.satellite.arc2.rasterize import ARC2AfricaBinRasterize, ARC2AfricaTifRasterize
    from warsa.precipitation.satellite.rfe.rasterize import RFE2AfricaBinRasterize, RFE2AfricaTifRasterize, RFE2AsiaBinRasterize
    from warsa.precipitation.satellite.chirps.rasterize import Chirps20GlobalDaily05TifRasterize, Chirps20GlobalDaily25TifRasterize, Chirps20GlobalMonthly05TifRasterize
    from warsa.precipitation.satellite.cmorph.rasterize import CMorphV0x8km30minRasterize, CMorphV0x025deg3hlyRasterize, CMorphV0x025degDailyRasterize, CMorphV1x8km30minRasterize, CMorphV1x025deg3hlyRasterize, CMorphV1x025degDailyRasterize
    from warsa.precipitation.satellite.gpm.rasterize import GPMImerg3BHHRearlyRasterize, GPMImerg3BHHRlateRasterize, GPMImerg3BMOv05Rasterize, GPMImerg3BHHRv05Rasterize, GPMImergGIS3BHHRv05Rasterize, GPMImergGIS3BHHRv04Rasterize, GPMImergGIS3BDailyV05Rasterize, GPMImergGIS3BMOv05Rasterize, GPMImergGIS3BDailyV04Rasterize
    from warsa.precipitation.satellite.trmm.rasterize import TRMMnascom3B42RTv7x3hRasterize, TRMMnascom3B42V7x3hRasterize, TRMMnascom3B42V7xDailyRasterize, TRMMopen3B40RTv7x3hRasterize, TRMMopen3B41RTv7x3hRasterize, TRMMopen3B42RTv7x3hGISRasterize, TRMMopen3B42RTv7x3hRasterize, TRMMopen3B42v7x3hGISRasterize, TRMMopen3B42v7x3hRasterize
    root_dir = kwargs.pop('root_dir', read_config().get('grp', 'dir'))
    sarp_list = kwargs.pop('sarp_list', None)
    groups = None
    if sarp_list:
        from collections import OrderedDict
        sarp_list = OrderedDict(sarp_list)
        groups = sarp_list.keys()
    spm = SatellitePrecipitationGroups(root_dir)
    if not groups or 'arc2' in groups:
        spm.add_product('arc2', 'bin', '1440min', 'R', 'D', ARC2AfricaBinFTP, 'ARC2Africa/bin', ARC2AfricaBinRasterize)
        spm.add_product('arc2', 'tif', '1440min', 'R', 'D', ARC2AfricaTifFTP, 'ARC2Africa/geotiff', ARC2AfricaTifRasterize)
    spm.add_product('rfe2', 'africa_bin', '1440min', 'R', 'D', RFE2AfricaBinFTP, 'rfe2Africa/bin', RFE2AfricaBinRasterize)
    spm.add_product('rfe2', 'africa_tif', '1440min', 'R', 'D', RFE2AfricaTifFTP, 'rfe2Africa/geotiff', RFE2AfricaTifRasterize)
    spm.add_product('rfe2', 'asia_bin', '1440min', 'R', 'D', RFE2AsiaBinFTP, 'rfe2Asia/bin', RFE2AsiaBinRasterize)
    spm.add_product('chirps20', 'global_daily_05_tif', '1440min', 'R', 'D', Chirps20GlobalDaily05TifFTP, 'CHIRPS-2.0/global_daily/tifs/p05/', Chirps20GlobalDaily05TifRasterize)
    spm.add_product('chirps20', 'global_daily_25_tif', '1440min', 'R', 'D', Chirps20GlobalDaily25TifFTP, 'CHIRPS-2.0/global_daily/tifs/p25/', Chirps20GlobalDaily25TifRasterize)
    spm.add_product('chirps20', 'global_monthly_05_tif', '1m', 'R', 'D', Chirps20GlobalMonthly05TifFTP, 'CHIRPS-2.0/global_monthly/tifs/', Chirps20GlobalMonthly05TifRasterize)
    spm.add_product('cmorph', 'v0x_8km_30min', '30min', 'C', 'I', CMorphV0x8km30minFTP, 'CMORPH/cmorph_v0_8km_30min/', CMorphV0x8km30minRasterize)
    spm.add_product('cmorph', 'v0x_025deg_3hly', '180min', 'R', 'D', CMorphV0x025deg3hlyFTP, 'CMORPH/cmorph_v0_025deg_3hly', CMorphV0x025deg3hlyRasterize)
    spm.add_product('cmorph', 'v0x_025deg_daily', '1440min', 'R', 'D', CMorphV0x025degDailyFTP, 'CMORPH/cmorph_v0_025deg_daily', CMorphV0x025degDailyRasterize)
    spm.add_product('cmorph', 'v1x_8km_30min', '30min', 'C', 'I', CMorphV1x8km30minFTP, 'CMORPH/cmorph_v1_8km_30min', CMorphV1x8km30minRasterize)
    spm.add_product('cmorph', 'v1x_025deg_3hly', '180min', 'R', 'D', CMorphV1x025deg3hlyFTP, 'CMORPH/cmorph_v1_025deg_3hly', CMorphV1x025deg3hlyRasterize)
    spm.add_product('cmorph', 'v1x_025deg_daily', '1440min', 'R', 'D', CMorphV1x025degDailyFTP, 'CMORPH/cmorph_v1_025deg_daily', CMorphV1x025degDailyRasterize)
    spm.add_product('gpm', '3b_hhr_early', '30min', 'C', 'I', GPMImerg3BHHRearlyFTP, 'GPM/imerg_3B_HHR_Early', GPMImerg3BHHRearlyRasterize)
    spm.add_product('gpm', '3b_hhr_late', '30min', 'C', 'I', GPMImerg3BHHRlateFTP, 'GPM/imerg_3B_HHR_Late', GPMImerg3BHHRlateRasterize)
    spm.add_product('gpm', '3b_hhr_v05', '30min', 'C', 'I', GPMImerg3BHHRv05FTP, 'GPM/imerg_3B_HHR_v05', GPMImerg3BHHRv05Rasterize)
    spm.add_product('gpm', '3b_mo_v05', '1M', 'R', 'D', GPMImerg3BMOv05FTP, 'GPM/imerg_3B_MO_v05', GPMImerg3BMOv05Rasterize)
    spm.add_product('gpm', 'gis_3b_hhr_v04', '30min', 'C', 'I', GPMImergGIS3BHHRv04FTP, 'GPM/imerg_3B_HHR_v04_GIS', GPMImergGIS3BHHRv04Rasterize)
    spm.add_product('gpm', 'gis_3b_hhr_v05', '30min', 'C', 'I', GPMImergGIS3BHHRv05FTP, 'GPM/imerg_3B_HHR_v05_GIS', GPMImergGIS3BHHRv05Rasterize)
    spm.add_product('gpm', 'gis_3b_daily_v04', '1440min', 'R', 'D', GPMImergGIS3BDailyV04FTP, 'GPM/imerg_3B_Daily_v04_GIS', GPMImergGIS3BDailyV04Rasterize)
    spm.add_product('gpm', 'gis_3b_daily_v05', '1440min', 'R', 'D', GPMImergGIS3BDailyV05FTP, 'GPM/imerg_3B_Daily_v05_GIS', GPMImergGIS3BDailyV05Rasterize)
    spm.add_product('gpm', 'gis_3b_mo_v05', '1M', 'R', 'D', GPMImergGIS3BMOv05FTP, 'GPM/imerg_3B_MO_v05_GIS', GPMImergGIS3BMOv05Rasterize)
    spm.add_product('trmmnascom', '3b42rt_v7x_3h_nc4', '180min', 'C', 'I', TRMMnascom3B42RTv7x3hFTP, 'TMPA/Nascom/3B42RT_v7x_3hours_nc4_Nascom', TRMMnascom3B42RTv7x3hRasterize)
    spm.add_product('trmmnascom', '3b42rt_v7x_3h_bin', '180min', 'C', 'I', None, 'TMPA/Nascom/3B42RT_v7x_3hours_bin_Nascom', None)
    spm.add_product('trmmnascom', '3b42_v7x_3h_hd5', '180min', 'C', 'I', TRMMnascom3B42V7x3hFTP, 'TMPA/Nascom/3B42_v7x_3hours_hd5_Nascom', TRMMnascom3B42V7x3hRasterize)
    spm.add_product('trmmnascom', '3b42_v7x_3h_hd5z', '180min', 'C', 'I', None, 'TMPA/Nascom/3B42_v7x_3hours_hd5Z_Nascom', None)
    spm.add_product('trmmnascom', '3b42_v7x_daily_nc4', '1440min', 'R', 'D', TRMMnascom3B42V7xDailyFTP, 'TMPA/Nascom/3B42_daily_nc4_Nascom', TRMMnascom3B42V7xDailyRasterize)
    spm.add_product('trmmnascom', '3b42_v7x_daily_bin', '1440min', 'R', 'D', None, 'TMPA/Nascom/3B42_daily_bin_Nascom', None)
    spm.add_product('trmmopen', '3b40rt_v7x_3h', '180min', 'C', 'I', TRMMopen3B40RTv7x3hFTP, 'TMPA/TRMMOpen/3B40RT_v7x_3hour_TrmmOpen', TRMMopen3B40RTv7x3hRasterize)
    spm.add_product('trmmopen', '3b41rt_v7x_3h', '180min', 'C', 'I', TRMMopen3B41RTv7x3hFTP, 'TMPA/TRMMOpen/3B41RT_v7x_3hours_Trmmopen', TRMMopen3B41RTv7x3hRasterize)
    spm.add_product('trmmopen', '3b42rt_v7x_3h', '180min', 'C', 'I', TRMMopen3B42RTv7x3hFTP, 'TMPA/TRMMOpen/3B42RT_v7x_3hours_Trmmopen', TRMMopen3B42RTv7x3hRasterize)
    spm.add_product('trmmopen', '3b42rt_v7x_3h_gis', '180min', 'C', 'I', TRMMopen3B42RTv7x3hGISFTP, 'TMPA/TRMMOpen/3B42RT_v7x_3hours_Gis_Trmmopen', TRMMopen3B42RTv7x3hGISRasterize)
    spm.add_product('trmmopen', '3b42_v7x_3h', '180min', 'C', 'I', TRMMopen3B42v7x3hFTP, 'TMPA/TRMMOpen/3B42_v7x_3hours_Trmmopen', TRMMopen3B42v7x3hRasterize, start_at='1999.01.01 00:00')
    spm.add_product('trmmopen', '3b42_v7x_3h_gis', '180min', 'C', 'I', TRMMopen3B42v7x3hGISFTP, 'TMPA/TRMMOpen/3B42_v7x_3hours_Gis_Trmmopen', TRMMopen3B42v7x3hGISRasterize)
    return spm


def download(sarp_list=None, update=False, verbose=True):
    """Download satellite precipitation products
    
    :param sarp_list: list with tuple (section, option) from config file. section is the product group and option the
                      product. If empty or None (default), all products from all groups in the config file will be
                      downloaded
    :type sarp_list: list
    :param update:
    :param verbose:
    :return:
    """
    spm = get_groups()
    if not sarp_list:
        sarp_list = spm.get_group_product_names()
    config = read_config()
    for group_name, product_name in sarp_list:
        product = spm.get_product(group_name, product_name)
        product_download_class = product.get_download_class()
        product_dir = product.get_download_dir()
        begin = product.get_begin()
        if config.has_option(group_name, 'usr') and config.has_option(group_name, 'pwd'):
            usr, pwd = decrypt(config.get(group_name, 'usr'), config.get(group_name, 'pwd'))
            download_obj = product_download_class(product_dir, ftp_user=usr, ftp_password=pwd)
        else:
            download_obj = product_download_class(product_dir)
        download_obj.download(verbose=verbose, begin=begin, update=update)


def rasterize(output_dir, sarp_list, **kwargs):
    """
    
    :param output_dir:
    :param sarp_list:
    :param kwargs: see Rasterizer()
    :return:
    """
    spm = get_groups()
    if not sarp_list:
        sarp_list = spm.get_group_product_names()
    for group_name, product_name in sarp_list:
        product = spm.get_product(group_name, product_name)
        product_dir = product.get_download_dir()
        raster_dir = os.path.join(output_dir, product.get_product_dir())
        product_rasterize_class = product.get_rasterize_class()
        rc = product_rasterize_class(product_dir=product_dir, output_raster_dir=raster_dir, **kwargs)
        rc.rasterize_folder(verbose=True)


def create_time_series(output_dir, raster_root_dir, sarp_list, layers, **kwargs):
    """Create from a precipitation raster product a time series as precipitation DEPTH in (mm) with timestamp right
    labeled . Default is no time zone shifting, i.e. as given in the product (generally UTC)
    
    :param output_dir:
    :param raster_root_dir:
    :param sarp_list:
    :param layers:
    :param kwargs:
        :key prefix: default is 'precipitation'
        :key utc: time zone in hours (negative for West)
        further keys for time_series.create_time_series
    :return:
    """
    prefix = kwargs.pop('prefix', 'precipitation')
    utc = int(kwargs.pop('utc', 0))
    try:
        layers = LayersReader(layers)
    except:
        pass

    spm = get_groups()
    if not sarp_list:
        sarp_list = spm.get_group_product_names()
    for group_name, product_name in sarp_list:
        product = spm.get_product(group_name, product_name)
        raster_dir = os.path.join(raster_root_dir, product.get_product_dir())
        download_class = spm.get_download_class(product_group=group_name, product=product_name)
        lrs_name = os.path.splitext(os.path.basename(layers.get_source()))[0]
        time_label = product.time_label
        depth_intensity = product.depth_intensity
        ts_filename = '{}_{}_{}_{}_UTC+00_{}{}.csv'.format(prefix, lrs_name, group_name, product_name, time_label,
                                                           depth_intensity)
        ts_filename = os.path.join(output_dir, ts_filename)
        df = time_series.create_time_series(time_series_filename=ts_filename, raster_dir=raster_dir, layers=layers,
                                            get_datetime_from_raster_file=download_class.get_datetime_from_file_name,
                                            float_format='%.3f', **kwargs)
        if utc == 0 and product.time_label == 'R' and product.depth_intensity == 'D':
            return
        if utc:
            df = shift(df, product.frequency, utc * 60)
        if time_label == 'C':
            df = (df.shift(freq=product.frequency) + df) * 0.5
            time_label = 'R'
        assert time_label == 'R'
        if depth_intensity == 'I':
            depth_intensity = 'D'
            if not product.frequency.endswith('H'):
                if product.frequency.endswith(('min', 'T')):
                    frequency = float(''.join([ c for c in product.frequency if c.isdigit()]))
                    df = df * (frequency / 60.0)
                else:
                    raise NotImplementedError('Intensity to depth for {} not implemented'.format(product.frequency))
        assert time_label == 'R' and depth_intensity == 'D'
        ts_filename = '{}_{}_{}_{}_UTC{}{:02d}_{}{}.csv'.format(prefix, lrs_name, group_name, product_name,
                                                                '+' if utc >= 0 else '-', abs(utc), time_label,
                                                                depth_intensity)
        df.index.name = 'Date'
        df.to_csv(os.path.join(output_dir, ts_filename), sep=';', float_format='%.2f')