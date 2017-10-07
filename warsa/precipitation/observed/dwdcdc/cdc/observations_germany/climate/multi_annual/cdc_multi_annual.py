__author__ = 'roehrig'

import os
import ftplib


def create_dir(new_dir):
    d = os.path.dirname(new_dir)
    if not os.path.exists(d):
        os.makedirs(d)
    if not new_dir.endswith('/'):
        new_dir += '/'
    return new_dir


# =============================================================================
# =============================================================================
# =============================================================================
class CDCMultiAnnual(object):

    def __init__(self, local_root_dir, local_dir):
        # local_dir = ftp_dir
        if not local_dir.endswith('/'):
            local_dir += '/'
        self.local_dir = create_dir(os.path.join(local_root_dir, local_dir))
        self.ftp_host = 'ftp-cdc.dwd.de'
        self.ftp_dir = '/pub/CDC/' + local_dir
        self.ftp_timeout = 600
        self.ftp_user = None
        self.ftp_password = None
        self.ftp_files = []
        self.verbose = True

    def download(self):
        ftp = None
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.ftp_host, timeout=self.ftp_timeout)
            ftp.login(self.ftp_user, self.ftp_password)
            ftp.cwd(self.ftp_dir)
            self.ftp_files = []
            ftp.retrlines('MLSD', self.files_callback)
            n = len(self.ftp_files)
            for i, ftp_filename in enumerate(self.ftp_files):
                with open(self.local_dir + ftp_filename, "wb") as bfile:
                    try:
                        ftp.retrbinary('RETR ' + self.ftp_dir + ftp_filename, callback=bfile.write)
                        print (i+1), 'of', n, self.ftp_dir + ftp_filename, ' downloaded'
                    except Exception, e:
                        print e
        finally:
            if ftp:
                ftp.close()

    def files_callback(self, line):
        sp = line.split(';')
        sp[-1] = 'name=' + sp[-1].strip()
        parameters = {}
        for p in sp:
            sp1 = p.split('=')
            parameters[sp1[0]] = sp1[1]
        if 'type' in parameters and parameters['type'] == 'file' and 'name' in parameters:
            filename =  parameters['name']
            if filename.endswith('.txt'):
                self.ftp_files.append(filename)


# =============================================================================
# =============================================================================
# =============================================================================
class CDCObservationsGermanyClimateMultiAnnual19611990(CDCMultiAnnual):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateMultiAnnual19611990, self).__init__(
            local_root_dir,
            'observations_germany/climate/multi_annual/mean_61-90/')


# =============================================================================
# =============================================================================
# =============================================================================
class CDCObservationsGermanyClimateMultiAnnual19712000(CDCMultiAnnual):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateMultiAnnual19712000, self).__init__(
            local_root_dir,
            'observations_germany/climate/multi_annual/mean_71-00/')


# =============================================================================
# =============================================================================
# =============================================================================
class CDCObservationsGermanyClimateMultiAnnual19812010(CDCMultiAnnual):

    def __init__(self, local_root_dir):
        super(CDCObservationsGermanyClimateMultiAnnual19812010, self).__init__(
            local_root_dir,
            'observations_germany/climate/multi_annual/mean_81-10/')





