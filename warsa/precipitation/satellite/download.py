import os
import time
import datetime
from datetime import timedelta
import collections
from ftplib import FTP, error_perm
import ConfigParser


class SatelliteBasedPrecipitationDownload(object):

    def __init__(self, local_dir, prefix, suffix, dir_lens, product_subfolder):
        if not prefix:
            prefix = ['']
        elif isinstance(prefix, basestring):
            prefix = [prefix]
        if not suffix:
            suffix = ['']
        elif isinstance(suffix, basestring):
            suffix = [suffix]
        if product_subfolder is None:
            product_subfolder = ''
        product_subfolder = product_subfolder

        local_dir = self.clean_path(local_dir)
        make_dir(local_dir)

        self.local_dir = local_dir.strip()
        self.prefix = prefix
        self.suffix = suffix
        self.dir_lens = dir_lens
        self.product_subfolder = product_subfolder.strip()
        self.verbose = True
        self.begin = datetime.datetime(1, 1, 1, 0, 0)
        self.end = datetime.datetime(9999, 12, 31, 23, 59)
        self.get_full_dir_name = None

        try:
            n = len(dir_lens)
            if n == 1:
                dir_lens = dir_lens[0]
                raise TypeError
            elif n == 2 and dir_lens[0] == 4:
                if dir_lens[1] == 2:
                    self.get_full_dir_name = self.get_full_dir_name_42
                elif dir_lens[1] == 3:
                    self.get_full_dir_name = self.get_full_dir_name_43
                elif dir_lens[1] == 6:
                    self.get_full_dir_name = self.get_full_dir_name_46
            elif n == 3 and dir_lens[0] == 4 and dir_lens[1] == 2 and dir_lens[2] == 2:
                    self.get_full_dir_name = self.get_full_dir_name_422
        except TypeError:
            if dir_lens is None:
                self.get_full_dir_name = self.get_full_dir_name_none
            elif dir_lens == 4:
                self.get_full_dir_name = self.get_full_dir_name_4
            elif dir_lens == 6:
                self.get_full_dir_name = self.get_full_dir_name_6

    @staticmethod
    def clean_path(path):
        # Both local_dir and server_dir should not end with slash or backslash
        path = path.replace('\\', '/')
        while '//' in path:
            path = path.replace('//', '/')
        if path[-1] == '/':
            path = path[:-1]
        return path.strip()

    def get_local_files(self):
        filenames = [['/'.join([root, f]) for f in files] for root, dirs, files in os.walk(self.local_dir) if files]
        return sorted([f for filenames0 in filenames for f in filenames0])

    def startswith_prefix(self, s):
        for pf in self.prefix:
            if s.startswith(pf):
                return True
        return False

    def endswith_prefix(self, s):
        for sf in self.suffix:
            if s.endswith(sf):
                return True
        return False

    def contains_prefix_and_suffix(self, name):
        return self.startswith_prefix(name) and self.endswith_prefix(name)

    @staticmethod
    def get_datetime_from_file_name(filename):
        # Subclass must implement it
        raise NotImplementedError

    def download(self, update=False, verbose=False, begin=None, end=None):
        # Subclass must implement it
        raise NotImplementedError

    def get_full_dir_name_none(self, _):
        return self.local_dir

    def get_full_dir_name_4(self, dt):
        return self.local_dir + '/' + str(dt.year)

    def get_full_dir_name_6(self, dt):
        return '/'.join([self.local_dir, str(dt.year) + str(dt.month).zfill(2)])

    def get_full_dir_name_42(self, dt):
        return '/'.join([self.local_dir, str(dt.year), str(dt.month).zfill(2)])

    def get_full_dir_name_43(self, dt):
        if dt.hour == 0:
            dt -= timedelta(days=1)
        return '/'.join([self.local_dir, str(dt.timetuple().tm_yday).zfill(3)])

    def get_full_dir_name_46(self, dt):
        return '/'.join([self.local_dir, str(dt.year), str(dt.year)+str(dt.month).zfill(2)])

    def get_full_dir_name_422(self, dt):
        return '/'.join([self.local_dir, str(dt.year), str(dt.month).zfill(2), str(dt.day).zfill(2),
                         self.product_subfolder])


class FTPDownload(SatelliteBasedPrecipitationDownload):

    def __init__(self, local_dir, prefix, suffix, dir_lens, ftp_host, ftp_dir, ftp_user=None, ftp_password=None,
                 ftp_timeout=600, product_subfolder=''):
        super(FTPDownload, self).__init__(local_dir, prefix, suffix, dir_lens, product_subfolder)

        ftp_dir = self.clean_path(ftp_dir)
        # always absolute path
        if not ftp_dir.startswith('/'):
            ftp_dir = '/' + ftp_dir

        self.ftp = None
        self.ftp_host = ftp_host
        self.ftp_dir = ftp_dir
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password
        self.ftp_timeout = ftp_timeout

    def describe(self):
        print 'Local dir: {}'.format(self.local_dir)
        print 'FTP host: {}'.format(self.ftp_host)
        print 'FTP username: {}'.format(self.ftp_user)
        print 'FTP password: {}'.format(self.ftp_password)
        print 'FTP dir: {}'.format(self.ftp_dir)
        print 'FTP timeout: {}'.format(self.ftp_timeout)
        print 'Directory length: {}'.format(self.dir_lens)
        print 'Prefix: {}'.format(self.prefix)
        print 'Suffix{}'.format(self.suffix)
        print 'Verbose {}'.format(self.verbose)

    def download(self, update=False, verbose=False, begin=None, end=None):
        """

        :param update: if TRUE, checks for any missing file on the local folder, otherwise starts download at the last
                    saved file
        :param verbose: if TRUE, outputs the current file being downloaded as well the time in seconds took to download
                    each file
        """
        run_time = print_verbose('Downloading from ftp://{} to {} ({})'.format(
            self.ftp_host, self.local_dir, datetime.datetime.now()))

        local_files = self.get_local_files()

        self.verbose = verbose
        self.begin = begin
        if not self.begin:
            if local_files and update:
                self.begin = self.__class__.get_datetime_from_file_name(os.path.basename(local_files[-1]))
            else:
                self.begin = datetime.datetime(1, 1, 1, 0, 0)
        if end:
            self.end = end
        try:
            self.ftp = None
            self.ftp = FTP(self.ftp_host, timeout=self.ftp_timeout)
            self.ftp.login(self.ftp_user, self.ftp_password)
            self.download_ftp_files(local_files)
        finally:
            if self.ftp:
                self.ftp.close()

        print_verbose('Downloading from ftp://{} to {} finished in {} minutes ({}).'.format(
            self.ftp_host, self.local_dir, (time.time()-run_time)/60.0, datetime.datetime.now()))

    def download_ftp_files(self, local_files):
        local_files = collections.deque(sorted(set([f.replace(self.local_dir, self.ftp_dir).replace(os.sep, '/')
                                                    for f in local_files])))
        local_file = local_files.pop() if local_files else None
        ftp_dir_len = len(self.ftp_dir)
        for ftp_filename in self.ftp_files():
            # Reduce the local files size to improve further searches
            while local_file and local_file < ftp_filename:
                local_file = local_files.pop() if local_files else None
            if ftp_filename not in local_files:
                dt0 = print_verbose('{};'.format(ftp_filename[ftp_dir_len+1:]), True)
                local_filename = ftp_filename.replace(self.ftp_dir, self.local_dir)
                if not os.path.isdir(os.path.dirname(local_filename)):
                    os.makedirs(os.path.dirname(local_filename))
                downloaded = True
                with open(local_filename, "wb") as bfile:
                    try:
                        resp = self.ftp.retrbinary('RETR ' + ftp_filename, callback=bfile.write)
                        resp = 'OK' if resp == '226 Transfer complete.' else resp
                        print_verbose('{}; {:.2f} seconds'.format(resp, time.time()-dt0))
                    except Exception, e:
                        print e
                        downloaded = False
                if not downloaded:
                    if os.path.isfile(local_filename):
                        os.remove(local_filename)
                    print_verbose('in {} seconds (failed) '.format(time.time()-dt0))

    def ftp_files(self):
        """Guarantees that the full path has no double slashes '//'
        :param begin:
        :return: file name with full path lead by '/'
        """
        full_dir_name = self.get_full_dir_name(self.begin).replace(self.local_dir, self.ftp_dir) if self.begin else ''
        for ftp_dir in self.ftp_folders(self.ftp_dir, self.dir_lens, full_dir_name):

            ftp_dir = '/'.join([ftp_dir, self.product_subfolder])
            lines = []
            try:
                self.ftp.cwd(ftp_dir)
                self.ftp.dir(lines.append)
            except error_perm, _:
                print_verbose('Folder {} not found'.format(ftp_dir))
            ftp_files = ['/'.join([ftp_dir, f]) for f in self.get_ftp_file_names(lines)]
            ftp_files = [f for f in ftp_files if self.__class__.get_datetime_from_file_name(f) >= self.begin]
            ftp_files = [f for f in ftp_files if self.__class__.get_datetime_from_file_name(f) <= self.end]
            # if not ftp_files:
            #     raise StopIteration
            for ftp_file in ftp_files:
                yield '/' + '/'.join([f for f in ftp_file.split('/') if f])

    def ftp_folders(self, ftp_dir, folder_lengths, dir_beg=None):
        if not folder_lengths:
            yield ftp_dir
            return
        folder_length = folder_lengths[0]  # current directory level
        lines = []
        self.ftp.cwd(ftp_dir)
        self.ftp.dir(lines.append)
        ftp_dirs = ['/'.join([ftp_dir, d]) for d in parse_ftp_dirs(folder_length, lines)]
        if ftp_dirs:
            dir_beg0 = dir_beg[:len(ftp_dirs[0])]
            ftp_dirs = [ftp_dir for ftp_dir in ftp_dirs if ftp_dir >= dir_beg0]
        folder_lengths = folder_lengths[1:] if len(folder_lengths) > 1 else None  # next levels
        if folder_lengths:
            for dir0 in ftp_dirs:
                for d in self.ftp_folders(dir0, folder_lengths, dir_beg):
                    yield d
        else:
            for d in ftp_dirs:
                yield d

    def get_ftp_file_names(self, lines):
        file_names = []
        for line in lines:
            if not line.startswith('d'):
                filename = os.path.basename(line.split()[-1])  # basename for link (l)
                if self.contains_prefix_and_suffix(filename):
                    file_names.append(filename)
        return file_names


# =============================================================================
# Auxiliary functions
# =============================================================================
def print_verbose(msg, same_line=False):
    if same_line:
        print msg,
    else:
        print msg
    return time.time()


def make_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)
    return d


def parse_ftp_dirs(folder_length, lines):
    dirs = []
    for line in lines:
        if line.startswith('d'):
            s = line.split()[-1]
            if len(s) == folder_length:
                try:
                    int(s)
                    dirs.append(s)
                except ValueError:
                    pass
    return dirs


def get_config_dict():
    from warsa.precipitation.satellite.arc2.download import ARC2AfricaBinFTP, ARC2AfricaTifFTP
    from warsa.precipitation.satellite.rfe.download import RFE2AfricaBinFTP, RFE2AfricaTifFTP, RFE2AsiaBinFTP
    from warsa.precipitation.satellite.chirps.download import Chirps20GlobalDaily05TifFTP, Chirps20GlobalDaily25TifFTP
    from warsa.precipitation.satellite.cmorph.download import CMorphV0x8km30minFTP, CMorphV0x025deg3hlyFTP, \
        CMorphV0x025degDailyFTP, CMorphV1x8km30minFTP, CMorphV1x025deg3hlyFTP, CMorphV1x025degDailyFTP
    from warsa.precipitation.satellite.gpm.download import GPMImerg3BHHRearlyFTP, GPMImerg3BHHRlateFTP, \
        GPMImerg3BHHRv03FTP, GPMImerg3BHHRv04FTP, GPMImerg3BHHRv05FTP, GPMImerg3BMOv03FTP, GPMImerg3BMOv04FTP, \
        GPMImerg3BMOv05FTP, GPMImergGIS3BDailyV03FTP, GPMImergGIS3BDailyV04FTP, GPMImergGIS3BDailyV05FTP, \
        GPMImergGIS3BHHRv03FTP, GPMImergGIS3BHHRv04FTP, GPMImergGIS3BHHRv05FTP, GPMImergGIS3BMOv03FTP, \
        GPMImergGIS3BMOv04FTP, GPMImergGIS3BMOv05FTP
    from warsa.precipitation.satellite.trmm.download import TRMMopen3B40RTv7x3hFTP, TRMMopen3B41RTv7x3hFTP, \
        TRMMopen3B42RTv7x3hFTP, TRMMopen3B42RTv7x3hGISFTP, TRMMopen3B42v7x3hFTP, TRMMopen3B42v7x3hGISFTP, \
        TRMMnascom3B42RTv7x3hFTP, TRMMnascom3B42V7x3hFTP, TRMMnascom3B42V7xDailyFTP

    config_dict = {
        'ARC2': {
            'BIN': [ARC2AfricaBinFTP, 'arc2Africa/bin'],
            'TIF': [ARC2AfricaTifFTP, 'arc2Africa/geotiff']
        },
        'RFE2': {
            'AFRICA_BIN': [RFE2AfricaBinFTP, 'rfe2Africa/bin'],
            'AFRICA_TIF': [RFE2AfricaTifFTP, 'rfe2Africa/geotiff'],
            'ASIA_BIN': [RFE2AsiaBinFTP, 'rfe2Asia/bin']
        },
        'Chirps20': {
            'GLOBAL_DAILY_05_TIF': [Chirps20GlobalDaily05TifFTP, 'CHIRPS-2.0/global_daily/tifs/p05/'],
            'GLOBAL_DAILY_25_TIF': [Chirps20GlobalDaily25TifFTP, 'CHIRPS-2.0/global_daily/tifs/p25/']
        },
        'CMorph': {
            'V0X_8KM_30MIN': [CMorphV0x8km30minFTP, 'cmorph/cmorph_v0_8km_30min/'],
            'V0X_025DEG_3HLY': [CMorphV0x025deg3hlyFTP, 'cmorph/cmorph_v0_025deg_3hly'],
            'V0X_025DEG_DAILY': [CMorphV0x025degDailyFTP, 'cmorph/cmorph_v0_025deg_daily'],
            'V1X_8KM_30MIN': [CMorphV1x8km30minFTP, 'cmorph/cmorph_v1_8km_30min'],
            'V1X_025DEG_3HLY': [CMorphV1x025deg3hlyFTP, 'cmorph/cmorph_v1_025deg_3hly'],
            'V1X_025DEG_DAILY': [CMorphV1x025degDailyFTP, 'cmorph/cmorph_v1_025deg_daily']
        },
        'GPMImerg': {
            '3B_HHR_V03': [GPMImerg3BHHRv03FTP, 'gpm/imerg_3B_HHR_v03'],
            '3B_MO_V03': [GPMImerg3BMOv03FTP, 'gpm/imerg_3B_MO_v03'],
            'GIS_3B_HHR_V03': [GPMImergGIS3BHHRv03FTP, 'gpm/imerg_3B_HHR_v03_GIS'],
            'GIS_3B_DAILY_V03': [GPMImergGIS3BDailyV03FTP, 'gpm/imerg_3B_Daily_v03_GIS'],
            'GIS_3B_MO_V03': [GPMImergGIS3BMOv03FTP, 'gpm/imerg_3B_MO_v03_GIS'],
            '3B_HHR_V04': [GPMImerg3BHHRv04FTP, 'gpm/imerg_3B_HHR_v04'],
            '3B_MO_V04': [GPMImerg3BMOv04FTP, 'gpm/imerg_3B_MO_v04'],
            'GIS_3B_HHR_V04': [GPMImergGIS3BHHRv04FTP, 'gpm/imerg_3B_HHR_v04_GIS'],
            'GIS_3B_DAILY_V04': [GPMImergGIS3BDailyV04FTP, 'gpm/imerg_3B_Daily_v04_GIS'],
            'GIS_3B_MO_V04': [GPMImergGIS3BMOv04FTP, 'gpm/imerg_3B_MO_v04_GIS'],
            '3B_HHR_V05': [GPMImerg3BHHRv05FTP, 'gpm/imerg_3B_HHR_v05'],
            '3B_MO_V05': [GPMImerg3BMOv05FTP, 'gpm/imerg_3B_MO_v05'],
            'GIS_3B_HHR_V05': [GPMImergGIS3BHHRv05FTP, 'gpm/imerg_3B_HHR_v05_GIS'],
            'GIS_3B_DAILY_V05': [GPMImergGIS3BDailyV05FTP, 'gpm/imerg_3B_Daily_v05_GIS'],
            'GIS_3B_MO_V05': [GPMImergGIS3BMOv05FTP, 'gpm/imerg_3B_MO_v05_GIS'],
            '3B_HHR_EARLY': [GPMImerg3BHHRearlyFTP, 'gpm/imerg_3B_HHR_Early'],
            '3B_HHR_LATE': [GPMImerg3BHHRlateFTP, 'gpm/imerg_3B_HHR_Late'],
        },
        'TRMMnascom': {
            '3B42RT_V7X_3H_NC4': [TRMMnascom3B42RTv7x3hFTP, 'tmpa/Nascom/3B42RT_v7x_3hours_nc4_Nascom'],
            '3B42RT_V7X_3H_BIN': [None, 'tmpa/Nascom/3B42RT_v7x_3hours_bin_Nascom'],
            '3B42_V7X_3H_HD5': [TRMMnascom3B42V7x3hFTP, 'tmpa/Nascom/3B42_v7x_3hours_hd5_Nascom'],
            '3B42_V7X_3H_HD5Z': [None, 'tmpa/Nascom/3B42_v7x_3hours_hd5Z_Nascom'],
            '3B42_V7X_DAILY_NC4': [TRMMnascom3B42V7xDailyFTP, 'tmpa/Nascom/3B42_daily_nc4_Nascom'],
            '3B42_V7X_DAILY_BIN': [None, 'tmpa/Nascom/3B42_daily_bin_Nascom']
        },
        'TRMMopen': {
            '3B40RT_V7X_3H': [TRMMopen3B40RTv7x3hFTP, 'tmpa/TRMMOpen/3B40RT_v7x_3hour_TrmmOpen'],
            '3B41RT_V7X_3H': [TRMMopen3B41RTv7x3hFTP, 'tmpa/TRMMOpen/3B41RT_v7x_3hours_Trmmopen'],
            '3B42RT_V7X_3H': [TRMMopen3B42RTv7x3hFTP, 'tmpa/TRMMOpen/3B42RT_v7x_3hours_Trmmopen'],
            '3B42RT_V7X_3H_GIS': [TRMMopen3B42RTv7x3hGISFTP, 'tmpa/TRMMOpen/3B42RT_v7x_3hours_Gis_Trmmopen'],
            '3B42_V7X_3H': [TRMMopen3B42v7x3hFTP, 'tmpa/TRMMOpen/3B42_v7x_3hours_Trmmopen, 1999.01.01 00:00'],
            '3B42_V7X_3H_GIS': [TRMMopen3B42v7x3hGISFTP, 'tmpa/TRMMOpen/3B42_v7x_3hours_Gis_Trmmopen']
        }
    }
    return config_dict


def create_config(root_dir=None, gpm_usr=None, gpm_pwd=None):
    home = os.path.expanduser("~")
    if not root_dir:
        root_dir = os.path.join(home, 'SARP')

    conf = ConfigParser.RawConfigParser()
    conf.optionxform = str
    conf.add_section('SatellitePrecipitationDownload')
    conf.set('SatellitePrecipitationDownload', 'root_dir', root_dir)

    for section, v0 in get_config_dict().items():
        if section == 'GPMImerg':
            if not conf.has_section(section):
                conf.add_section(section)
            conf.set(section, 'usr', gpm_usr)
            conf.set(section, 'pwd', gpm_pwd)
        for product_key, v1 in v0.items():
            if not conf.has_section(section):
                conf.add_section(section)
            conf.set(section, product_key, v1[1])
    with open(os.path.join(home, '.WARSASARP.cfg'), 'wb') as configfile:
        conf.write(configfile)


def read_config(filename=None):
    if not filename:
        home = os.path.expanduser("~")
        filename = os.path.join(home, '.WARSASARP.cfg')
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config.read(filename)
    return config


def get_download_folder(sarp_list, conf=None):
    if not conf:
        conf = read_config()
    for section, option in sarp_list:
        sarp_folder = conf.get(section, option) if conf.has_section(section) and conf.has_option(section, option) else None
        if sarp_folder:
            yield section, option, sarp_folder


def get_download_class(section, option):
    d0 = get_config_dict()
    if section in d0:
        d1 = d0[section]
        if option in d1:
            return d1[option][0]
    return None


def run(sarp_list=None, update=False, verbose=True):

    # To get the download class.
    config_dict = get_config_dict()

    download_config = read_config()
    download_config.optionxform = str
    download_root_dir = download_config.get('SatellitePrecipitationDownload', 'root_dir')
    download_sections = download_config.sections()
    if not sarp_list:
        sarp_list = []
        for section in download_sections:
            sarp_list += [[section, option] for option in download_config.options(section)]
    for section, product_key in sarp_list:
        if download_config.has_section(section) and download_config.has_option(section, product_key) and section in config_dict:
            download_class = config_dict[section][product_key][0]
            splt = download_config.get(section, product_key).split(',')
            full_path_local_dir = os.path.join(download_root_dir, splt[0].strip())
            try:
                begin = datetime.datetime.strptime(splt[1].strip(), '%Y.%d.%m %H:%M')
            except IndexError:
                begin = None
            if download_config.has_option(section, 'usr') and download_config.has_option(section, 'pwd'):
                usr = download_config.get(section, 'usr')
                pwd = download_config.get(section, 'pwd')
                download_obj = download_class(full_path_local_dir, ftp_user=usr, ftp_password=pwd)
            else:
                download_obj = download_class(full_path_local_dir)
            download_obj.download(verbose=verbose, begin=begin, update=update)

