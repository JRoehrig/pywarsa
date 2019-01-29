import os
import time
import datetime
import calendar
from collections import OrderedDict
from ftplib import FTP, error_perm


class TRMMopen3B42RTv7x3hFTP(object):
    """Source
        ftp://trmmopen.gsfc.nasa.gov/pub/merged/mergeIRMicro
    Format:
        3B42RT.2000030100.7R2.bin.gz
        3B42RT.2018010409.7.bin.gz
    Folder structure:
        year/month/data
        year/data
    """
    def __init__(self, local_dir):

        self.ftp = None
        self.ftp_host = 'trmmopen.gsfc.nasa.gov'
        self.ftp_dir = '/pub/merged/mergeIRMicro/'
        self.ftp_user = None
        self.ftp_password = None
        self.ftp_timeout = 600
        self.local_dir = clean_path(local_dir)
        if not os.path.isdir(self.local_dir):
            os.makedirs(self.local_dir)
        self.verbose = True

        def p(s, same_line=False):
            if same_line:
                print s,
            else:
                print s
            return time.time()
        self.print_verbose = p

    @staticmethod
    def valid_filename(filename):
        return filename.startswith('3B42RT.') and filename.endswith('.gz')

    @staticmethod
    def get_datetime_from_file_name(filename):
        return datetime.datetime.strptime(os.path.splitext(filename)[0].split('.')[1], '%Y%m%d%H')

    def get_local_files(self):
        filenames = [['/'.join([root, f]) for f in files] for root, dirs, files in os.walk(self.local_dir) if files]
        return sorted([f for filenames0 in filenames for f in filenames0])

    def get_missing_datetime(self, datetime_begin=None, datetime_end=None):
        # Datetime from local files
        datetime_local = [[f[7:17] for f in files] for root, dirs, files in os.walk(self.local_dir)]
        datetime_local = [f for filenames0 in datetime_local for f in filenames0]

        # 3B42RT.2000030100.7R2.bin.gz
        # Datetime from files expected to be found on the server
        if not datetime_begin:
            datetime_begin = datetime.datetime(2000, 3, 1, 0, 0)
        if not datetime_end:
            datetime_end = datetime.datetime.now()
        y0, y1 = datetime_begin.year, datetime_end.year
        m0, m1 = datetime_begin.month, datetime_end.month
        d0, d1 = datetime_begin.day, datetime_end.day
        h0, h1 = 3 * (datetime_begin.hour // 3), 3 * (datetime_end.hour // 3)
        datetime_server = list()
        for y in range(2000, y1 + 1):
            for m in range(1, 13):
                for d in range(1, calendar.monthrange(y, m)[1] + 1):
                    for h in range(0, 24, 3):
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
            month = f[4:6]
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
        for ftp_filename in self.get_missing_ftp_files(missing_datetime):
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
                    idx = records.index(f[7:17])
                    if idx != -1:
                        del records[idx]
                        yield '/'.join([ftp_dir_m, f])
                year_records += records

            if year_records:
                lines = []
                try:
                    self.ftp.cwd(ftp_dir_y)
                    self.ftp.dir(lines.append)
                except error_perm, e:
                    if self.verbose:
                        self.print_verbose('{}: {}'.format(ftp_dir_y, e.message))
                for f in self.get_ftp_file_names(lines):
                    try:
                        idx = year_records.index(f[7:17])
                        del year_records[idx]
                        yield '/'.join([ftp_dir_y, f])
                    except ValueError, e:
                        pass
            if year_records:
                print 'Could not find records {} on server'.format(', '.join(year_records))

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
    t = TRMMopen3B42RTv7x3hFTP(sys.argv[1])
    t.download()