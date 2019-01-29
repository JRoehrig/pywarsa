import os
import time
import datetime
import calendar
from ftplib import FTP, error_perm
from collections import OrderedDict


class CMorphV0x8km30minFTP(object):
    """
        ftp://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V0.x/RAW/8km-30min/2011/201108/
        CMORPH_V0.x_RAW_8km-30min_2011080100.gz
    """

    def __init__(self, local_folder):

        ftp_dir = '/precip/CMORPH_V0.x/RAW/8km-30min/'
        self.ftp = None
        self.ftp_host = 'ftp.cpc.ncep.noaa.gov'
        self.ftp_dir = ftp_dir
        self.ftp_user = None
        self.ftp_password = None
        self.ftp_timeout = 600

        local_dir = clean_path(local_folder)
        if not os.path.isdir(local_dir):
            os.makedirs(local_dir)

        self.local_dir = local_dir.strip()
        self.verbose = True

        def p(s, same_line=False):
            if same_line:
                print s,
            else:
                print s
            return time.time()
        self.print_verbose = p

    def get_full_dir_name(self, dt):
        return '/'.join([self.local_dir, str(dt.year), str(dt.year)+str(dt.month).zfill(2)])

    @staticmethod
    def get_datetime_from_file_name(filename):
        try:
            return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d%H')
        except ValueError:
            return datetime.datetime.strptime(os.path.splitext(filename)[0].split('_')[-1], '%Y%m%d%H%M')

    @staticmethod
    def valid_filename(filename):
        return filename.startswith('CMORPH_V0.x_RAW_8km-30min_') and filename.endswith('.gz')

    def get_local_files(self):
        filenames = [['/'.join([root, f]) for f in files] for root, dirs, files in os.walk(self.local_dir) if files]
        return sorted([f for filenames0 in filenames for f in filenames0])

    def get_missing_datetime(self, datetime_begin=None, datetime_end=None):
        # Datetime from local files
        datetime_local = [[f.split('_')[-1][:-3] for f in files] for root, dirs, files in os.walk(self.local_dir)]
        datetime_local = [f for filenames0 in datetime_local for f in filenames0]
        # 3B42RT.2000030100.7R2.bin.gz
        # Datetime from files expected to be found on the server
        if not datetime_begin:
            datetime_begin = datetime.datetime(2011, 8, 1, 0, 0)
        if not datetime_end:
            datetime_end = datetime.datetime.now()
        y0, y1 = datetime_begin.year, datetime_end.year
        m0, m1 = datetime_begin.month, datetime_end.month
        d0, d1 = datetime_begin.day, datetime_end.day
        h0, h1 = datetime_begin.hour, datetime_end.hour
        datetime_server = list()
        for y in range(2000, y1 + 1):
            for m in range(1, 13):
                for d in range(1, calendar.monthrange(y, m)[1] + 1):
                    for h in range(0, 24):
                        datetime_server.append('{}{}{}{}'.format(str(y), str(m).zfill(2), str(d).zfill(2), str(h).zfill(2)))
        idx0 = datetime_server.index('{}{}{}{}'.format(str(y0), str(m0).zfill(2), str(d0).zfill(2), str(h0).zfill(2)))
        idx1 = datetime_server.index('{}{}{}{}'.format(str(y1), str(m1).zfill(2), str(d1).zfill(2), str(h1).zfill(2)))
        datetime_server = datetime_server[:idx1 + 1]
        datetime_server = datetime_server[idx0:]
        files = sorted(list(set(datetime_server).difference(set(datetime_local))))
        datetime_missing = OrderedDict()
        for f in files:
            year = f[:4]
            if year not in datetime_missing:
                datetime_missing[year] = OrderedDict()
            month = f[:6]
            if month not in datetime_missing[year]:
                datetime_missing[year][month] = list()
            datetime_missing[year][month].append(f)

        return datetime_missing

    def download(self, update=False, verbose=True, begin=None, end=None):
        """

        :param update: if TRUE, checks for any missing file on the local folder, otherwise starts download at the last
                    saved file
        :param verbose: if TRUE, outputs the current file being downloaded as well the time in seconds took to download
                    each file
        :param begin:
        :param end:
        """
        self.verbose = verbose
        time0 = None
        if self.verbose:
            dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            time0 = self.print_verbose('Downloading from ftp://{} to {} ({})'.format(self.ftp_host, self.local_dir, dt))

        local_files = self.get_missing_datetime(begin, end)

        try:
            self.ftp = None
            self.ftp = FTP(self.ftp_host, timeout=self.ftp_timeout)
            self.ftp.login(self.ftp_user, self.ftp_password)
            self.download_ftp_files(local_files)
        finally:
            if self.ftp:
                self.ftp.close()

        if self.verbose:
            dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            self.print_verbose('Downloading from ftp://{} to {} finished in {:.1f} minutes ({}).'.format(
                self.ftp_host, self.local_dir, (time.time()-time0)/60.0, dt))

    def download_ftp_files(self, missing_datetime):
        missing_ftp_files = self.get_missing_ftp_files(missing_datetime)
        for ftp_filename in missing_ftp_files:
            if self.verbose:
                time0 = self.print_verbose('{};'.format(os.path.basename(ftp_filename)), True)
            local_filename = ftp_filename.replace(self.ftp_dir, self.local_dir)
            if not os.path.isdir(os.path.dirname(local_filename)):
                os.makedirs(os.path.dirname(local_filename))
            with open(local_filename, "wb") as bfile:
                try:
                    resp = self.ftp.retrbinary('RETR ' + ftp_filename, callback=bfile.write)
                    resp = 'OK' if resp == '226 Transfer complete.' else resp
                    if self.verbose:
                        self.print_verbose('{}; {:.2f} seconds'.format(resp, time.time()-time0))
                except Exception, e:
                    print e
                    if os.path.isfile(local_filename):
                        os.remove(local_filename)
                    if self.verbose:
                        self.print_verbose('in {} seconds (failed) '.format(time.time()-time0))

    def get_missing_ftp_files(self, missing_datetimes):
        ftp_files = list()
        for y, m_dict in missing_datetimes.items():
            ftp_dir_y = '{}{}/'.format(self.ftp_dir, y)
            year_records = list()
            for m, records in m_dict.items():
                ftp_dir_m = ftp_dir_y + m
                lines = []
                try:
                    self.ftp.cwd(ftp_dir_m)
                    self.ftp.dir(lines.append)
                except error_perm, e:  # some years do not have month, data is direct under the year folder
                    if self.verbose and '550' not in e.message:
                        self.print_verbose('{}: {}'.format(ftp_dir_m, e.message))
                for f in self.get_ftp_file_names(lines):
                    try:
                        idx = records.index(f.split('_')[-1][:10])
                        del records[idx]
                        f = '/'.join([ftp_dir_m, f])
                        ftp_files.append(f)
                    except ValueError, e:
                        pass
                year_records += records
            if year_records:
                print 'Could not find records {} on server'.format(', '.join(year_records))
        return ftp_files

    def get_ftp_file_names(self, lines):
        file_names = []
        for line in lines:
            if not line.startswith('d'):
                filename = os.path.basename(line.split()[-1])  # basename for link (l)
                if self.valid_filename(filename):
                    file_names.append(filename)
        return file_names


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


def clean_path(path):
    # Both local_dir and server_dir should not end with slash or backslash
    path = path.replace('\\', '/')
    while '//' in path:
        path = path.replace('//', '/')
    path = path.strip()
    if path[-1] != '/':
        path += '/'
    return path


if __name__ == '__main__':
    import sys
    t = CMorphV0x8km30minFTP(sys.argv[1])
    t.download(sys.argv[1])
    # for k, v in t.get_missing_datetime().items():
    #     for k1, v1 in v.items():
    #         print k, k1, v1
