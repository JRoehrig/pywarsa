import os
import time
import collections
import datetime
from datetime import timedelta
from ftplib import FTP, error_perm


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


class SatelliteBasedPrecipitationDownloadFTP(SatelliteBasedPrecipitationDownload):

    def __init__(self, local_dir, prefix, suffix, dir_lens, ftp_host, ftp_dir, ftp_user=None, ftp_password=None,
                 ftp_timeout=600, product_subfolder=''):
        super(SatelliteBasedPrecipitationDownloadFTP, self).__init__(local_dir, prefix, suffix, dir_lens,
                                                                     product_subfolder)

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
            time0 = print_verbose('Downloading from ftp://{} to {} ({})'.format(self.ftp_host, self.local_dir, dt))

        local_files = self.get_local_files()

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

        if self.verbose:
            dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            print_verbose('Downloading from ftp://{} to {} finished in {:.1f} minutes ({}).'.format(
                self.ftp_host, self.local_dir, (time.time()-time0)/60.0, dt))

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
                if self.verbose:
                    time0 = print_verbose('{};'.format(ftp_filename[ftp_dir_len+1:]), True)
                local_filename = ftp_filename.replace(self.ftp_dir, self.local_dir)
                if not os.path.isdir(os.path.dirname(local_filename)):
                    os.makedirs(os.path.dirname(local_filename))
                downloaded = True
                with open(local_filename, "wb") as bfile:
                    try:
                        resp = self.ftp.retrbinary('RETR ' + ftp_filename, callback=bfile.write)
                        resp = 'OK' if resp == '226 Transfer complete.' else resp
                        if self.verbose:
                            print_verbose('{}; {:.2f} seconds'.format(resp, time.time()-time0))
                    except Exception, e:
                        print e
                        downloaded = False
                if not downloaded:
                    if os.path.isfile(local_filename):
                        os.remove(local_filename)
                    if self.verbose:
                        print_verbose('in {} seconds (failed) '.format(time.time()-time0))
            else:
                print_verbose('{} already downloaded'.format(ftp_filename))

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
                if self.verbose:
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
