# __author__ = 'roehrig'
#
# from warsa.precipitation.satellite.satellite_precipitation_products import SatellitePrecipitationFTP, make_dir
#
#
# class Rfe2tif(SatellitePrecipitationFTP):
#     def __init__(self):
#         SatellitePrecipitationFTP.__init__(self)
#         self.ftp_host = 'ftp.cpc.ncep.noaa.gov'
#         self.ftp_dir = '/fews/fewsdata/africa/rfe2/geotiff/'
#         self.dir_lens = None
#         self.prefix = 'africa_rfe.'
#         self.datetime_format = '%Y%m%d'
#
#     def get_ftp_file_names(self, lines):
#         file_names = []
#         for line in lines:
#             if not line.startswith('d'):
#                 filename = line.split()[-1]
#                 if filename.startswith(self.prefix) and filename.endswith('.tif.zip'):
#                     file_names.append(filename)
#         return file_names
#
#     def get_datetime_string_from_file_name(self, filename):
#         return filename.split('.')[1]
#
#     def get_full_dir_name(self, dt):
#         return self.local_dir + '/'
#
#
# def download(target_dir, update=True):
#     make_dir(target_dir)
#     trmm = Rfe2tif()
#     trmm.verbose = True
#     trmm.local_dir = target_dir
#     trmm.download(update)
#
