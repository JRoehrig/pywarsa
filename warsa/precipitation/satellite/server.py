import os
import time
from ftplib import FTP


class Server(object):

    def __init__(self, satellite_precipitation_product):
        self.spp = satellite_precipitation_product

    def local_dir(self):
        return self.spp.local_dir

    def get_local_files(self):
        return self.spp.get_local_files()

    def get_datetime_from_file_name(self, filename):
        return self.get_datetime_from_file_name(filename)

    def dir_lens(self):
        return self.spp.dir_lens

    def replace_server_by_local_dir(self):
        return os.path.normpath(self.local_dir()), os.path.normpath(self.ftp_dir)


class FTPServer(Server):

    def __init__(self, satellite_precipitation_product, host, directory, user=None, password=None, timeout=600):
        super(FTPServer, self).__init__(satellite_precipitation_product)
        self.ftp = None
        self.ftp_host = host
        self.ftp_dir = directory
        self.ftp_timeout = timeout
        self.ftp_user = user
        self.ftp_password = password

    def describe(self):
        print 'FTP host: {}'.format(self.ftp_host)
        print 'FTP username: {}'.format(self.ftp_user)
        print 'FTP password: {}'.format(self.ftp_password)
        print 'FTP dir: {}'.format(self.ftp_dir)
        print 'FTP timeout: {}'.format(self.ftp_timeout)

    def download(self, update=True):
        dt00 = print_verbose('Downloading from ftp://{} to {}'.format(self.ftp_host, self.local_dir()))
        try:
            local_files = self.get_local_files()
            # Get the date of the last local file. If there is no local file, dt0 = None
            if update:
                dt0 = self.spp.get_datetime_from_file_name(os.path.basename(local_files[-1])) if local_files else None
            else:
                dt0 = None
            self.ftp = FTP(self.ftp_host, timeout=self.ftp_timeout)
            self.ftp.login(self.ftp_user, self.ftp_password)
            self.download_ftp_files(local_files, dt0)
        finally:
            if self.ftp:
                self.ftp.close()
        print_verbose('Downloading from ftp://{} to {} finished in {} minutes.'.format(self.ftp_host, self.local_dir, (time.time()-dt00)/60.0))

    def download_ftp_files(self, local_files, dt):
        local_files = set([f.replace(os.path.normpath(self.local_dir()), os.path.normpath(self.ftp_dir)) for f in local_files])
        # local_files = deque(sorted(local_files))
        # local_files.reverse()
        # local_file = local_files.pop() if local_files else None
        remaining_filenames = []
        for ftp_filename in self.ftp_files(dt):
            # while local_file and local_file < ftp_filename:
            #     local_file = local_files.pop() if local_files else None
            # if ftp_filename != local_file:
            if ftp_filename not in local_files:
                local_filename = ftp_filename.replace(self.ftp_dir, self.local_dir)
                dt0 = print_verbose('Downloading {} to {}'.format(ftp_filename, local_filename), True)
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

    def ftp_files(self, dt=None):
        n = self.spp.get_full_dir_name(dt)
        for ftp_dir in self.ftp_folders(self.ftp_dir, self.dir_lens(),
                                        self.spp.get_full_dir_name(dt).replace(self.local_dir, self.ftp_dir) if dt else ''):
            lines = []
            self.ftp.cwd(ftp_dir)
            self.ftp.dir(lines.append)
            ftp_files = [ftp_dir + '/' + f for f in self.spp.get_ftp_file_names(lines)]
            for ftp_file in ftp_files:
                yield ftp_file

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


def print_verbose(msg, same_line=False):
    if same_line:
        print msg,
    else:
        print msg
    return time.time()


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


