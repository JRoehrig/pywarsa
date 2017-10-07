import os
import time
import datetime
import collections
from ftplib import FTP


class SatellitePrecipitationFTP(object):

    def __init__(self, local_dir, prefix, suffix, dir_lens, ftp_host, ftp_dir, ftp_user=None, ftp_password=None, ftp_timeout=600):
        if not prefix:
            prefix = ['']
        elif isinstance(prefix, basestring):
            prefix = [prefix]
        if not suffix:
            suffix = ['']
        elif isinstance(suffix, basestring):
            suffix = [suffix]
        # Both local_dir and ftp_dir do not end with slash or backslash
        while ftp_dir[-1] == '/':
            ftp_dir = ftp_dir[:-1]
        make_dir(local_dir)
        self.local_dir = os.path.normpath(local_dir)
        self.prefix = prefix
        self.suffix = suffix
        self.dir_lens = dir_lens
        self.verbose = True
        # DON'T CHANGE IT:
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

    def replace_local_by_ftp_path(self, local_filename):
        return local_filename.replace(self.local_dir, self.ftp_dir).replace(os.sep, '/')

    def replace_ftp_by_local_path(self, ftp_filename):
        return os.path.normpath(ftp_filename.replace(self.ftp_dir, self.local_dir))

    def download(self, update=True, verbose=True):
        verbose_old = self.verbose
        self.verbose = verbose
        run_time = print_verbose('Downloading from ftp://{} to {} ({})'.format(
            self.ftp_host, self.local_dir, datetime.datetime.now()))
        try:
            local_files = self.get_local_files()
            # Get the date of the last local file (on the hard disk). If there is no local file, beg_dt = None
            if local_files and update:
                last_filename = os.path.basename(local_files[-1])
                beg_dt = self.get_datetime_from_file_name(last_filename) if local_files else None
            else:
                beg_dt = None
            self.ftp = None
            self.ftp = FTP(self.ftp_host, timeout=self.ftp_timeout)
            self.ftp.login(self.ftp_user, self.ftp_password)
            self.download_ftp_files(local_files, beg_dt)
        finally:
            if self.ftp:
                self.ftp.close()
            self.verbose = verbose_old

        print_verbose('Downloading from ftp://{} to {} finished in {} minutes ({}).'.format(
            self.ftp_host, self.local_dir, (time.time()-run_time)/60.0, datetime.datetime.now()))

    def download_ftp_files(self, local_files, beg_dt):
        local_files = collections.deque(sorted(set([self.replace_local_by_ftp_path(f) for f in local_files])))
        local_file = local_files.pop() if local_files else None
        remaining_filenames = []
        for ftp_filename in self.ftp_files(beg_dt):
            # Reduce the local files size to improve further searches
            while local_file and local_file < ftp_filename:
                local_file = local_files.pop() if local_files else None
            if ftp_filename not in local_files:
                local_filename = self.replace_ftp_by_local_path(ftp_filename)
                dt0 = print_verbose('Downloading from {} to {}'.format(self.ftp_dir, local_filename), True)
                if not os.path.isdir(os.path.dirname(local_filename)):
                    os.makedirs(os.path.dirname(local_filename))
                downloaded = True
                with open(local_filename, "wb") as bfile:
                    try:
                        resp = self.ftp.retrbinary('RETR ' + ftp_filename, callback=bfile.write)
                        print_verbose('({}) in {} seconds'.format(resp, time.time()-dt0))
                    except Exception, e:
                        print e
                        downloaded = False
                if not downloaded:
                    if os.path.isfile(local_filename):
                        os.remove(local_filename)
                    print_verbose('in {} seconds (failed) '.format(time.time()-dt0))
                    remaining_filenames.append([ftp_filename, local_filename])
        return remaining_filenames

    def get_local_files(self):
        filenames = [[os.path.join(root, f) for f in files] for root, dirs, files in os.walk(self.local_dir) if files]
        return sorted([f for filenames0 in filenames for f in filenames0])

    def get_datetime_from_file_name(self, filename):
        # Subclass must implement it
        raise NotImplementedError

    def get_full_dir_name(self, dt):
        # Subclass must implement it
        raise NotImplementedError

    def ftp_folders(self, ftp_dir, folder_lengths, dir_beg=None):
        if not folder_lengths:
            yield ftp_dir
            return
        folder_length = folder_lengths[0]  # current directory level
        lines = []
        self.ftp.cwd(ftp_dir)
        self.ftp.dir(lines.append)
        ftp_dirs = [ftp_dir + '/' + d for d in parse_ftp_dirs(folder_length, lines)]
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

    def ftp_files(self, dt=None):
        for ftp_dir in self.ftp_folders(self.ftp_dir, self.dir_lens, self.get_full_dir_name(dt).replace(self.local_dir, self.ftp_dir) if dt else ''):
            lines = []
            self.ftp.cwd(ftp_dir)
            self.ftp.dir(lines.append)
            ftp_files = [ftp_dir + '/' + f for f in self.get_ftp_file_names(lines)]
            for ftp_file in ftp_files:
                yield ftp_file

    def get_ftp_file_names(self, lines):
        file_names = []
        for line in lines:
            if not line.startswith('d'):
                filename = line.split()[-1]
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





