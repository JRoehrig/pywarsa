import os
import time
import datetime
import calendar
from ftplib import FTP, error_perm
from collections import OrderedDict


class GPMImerg3BHHRearlyFTP(object):
    """
        ftp://ftp.cpc.ncep.noaa.gov/precip/CMORPH_V0.x/RAW/8km-30min/2011/201108/
        CMORPH_V0.x_RAW_8km-30min_2011080100.gz
    """

    def __init__(self, local_folder, ftp_user, ftp_password):

        ftp_dir = '/data/imerg/early/'
        self.ftp = None
        self.ftp_host = 'jsimpson.pps.eosdis.nasa.gov'
        self.ftp_dir = ftp_dir
        self.ftp_user = ftp_user
        self.ftp_password = ftp_password
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
        filename = filename.split('3IMERG.')[1].split('-')
        return datetime.datetime.strptime(filename[0] + filename[1][1:], '%Y%m%d%H%M%S') + datetime.timedelta(minutes=30)

    @staticmethod
    def valid_filename(filename):
        return filename.startswith('3B-HHR-E.') and filename.endswith('.RT-H5')

    @staticmethod
    def filename_to_timestamp(filename):
        f0, f1 = filename.split('.')[4].split('-')[:2]
        return f0 + f1[1:5]

    def get_local_files(self):
        filenames = [['/'.join([root, f]) for f in files] for root, dirs, files in os.walk(self.local_dir) if files]
        return sorted([f for filenames0 in filenames for f in filenames0])

    def get_missing_datetime(self, datetime_begin=None, datetime_end=None):
        # Datetime from local files
        print self.local_dir
        datetime_local = [self.filename_to_timestamp(f) for _, _, fs in os.walk(self.local_dir) if fs for f in fs]

        # 3B42RT.2000030100.7R2.bin.gz
        # Datetime from files expected to be found on the server
        if not datetime_begin:
            datetime_begin = datetime.datetime(2014, 3, 12, 0, 0)
        if not datetime_end:
            datetime_end = datetime.datetime.now()
        y0, y1 = str(datetime_begin.year), str(datetime_end.year)
        m0, m1 = str(datetime_begin.month).zfill(2), str(datetime_end.month).zfill(2)
        d0, d1 = str(datetime_begin.day).zfill(2), str(datetime_end.day).zfill(2)
        h0, h1 = str(datetime_begin.hour).zfill(2), str(datetime_end.hour).zfill(2)
        datetime_server = list()
        for y in range(2000, datetime_end.year + 1):
            ys = str(y)
            for m in range(1, 13):
                ms = str(m).zfill(2)
                for d in range(1, calendar.monthrange(y, m)[1] + 1):
                    ds = str(d).zfill(2)
                    for h in range(0, 24):
                        datetime_server.append('{}{}{}{}00'.format(ys, ms, ds, str(h).zfill(2)))
                        datetime_server.append('{}{}{}{}30'.format(ys, ms, ds, str(h).zfill(2)))
        idx0 = datetime_server.index('{}{}{}{}00'.format(y0, m0, d0, h0))
        idx1 = datetime_server.index('{}{}{}{}00'.format(y1, m1, d1, h1))
        datetime_server = datetime_server[:idx1 + 1]
        datetime_server = datetime_server[idx0:]
        fs = sorted(list(set(datetime_server).difference(set(datetime_local))))
        datetime_missing = OrderedDict()
        for f in fs:
            yearmonth = f[:6]
            if yearmonth not in datetime_missing:
                datetime_missing[yearmonth] = list()
            datetime_missing[yearmonth].append(f)
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
        for ym, records in missing_datetimes.items():
            ftp_dir_ym = '{}{}/'.format(self.ftp_dir, ym)
            lines = []
            try:
                self.ftp.cwd(ftp_dir_ym)
                self.ftp.dir(lines.append)
            except error_perm, e:  # some years do not have month, data is direct under the year folder
                if self.verbose and '550' not in e.message:
                    self.print_verbose('{}: {}'.format(ftp_dir_ym, e.message))
            for f in self.get_ftp_file_names(lines):
                try:
                    idx = records.index(self.filename_to_timestamp(f))
                    del records[idx]
                    f = '/'.join([ftp_dir_ym, f])
                    ftp_files.append(f)
                except ValueError, e:
                    pass
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
    d = sys.argv[1]
    u = sys.argv[2]
    p = sys.argv[3]
    t = GPMImerg3BHHRearlyFTP(d, u, p)
    t.download()
    # for k, v in t.get_missing_datetime().items():
    #     print k, v