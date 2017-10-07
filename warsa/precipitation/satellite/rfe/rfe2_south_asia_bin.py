__author__ = 'roehrig'
"""
From ftp://ftp.cpc.ncep.noaa.gov/fews/S.Asia/SOUTH_ASIA_README.txt

This is the readme file for archived southern Asia area NOAA/Climate Prediction Center RFE2.0 daily rainfall estimates.  This file
describes all archived rainfall estimates for the region, though the data located on the NOAA/CPC anonymous ftp server:
ftp://ftpprd.ncep.noaa.gov/pub/cpc/fews/S.Asia/data/ .

CONTENTS:

  Southern Asia area daily rainfall estimates

    --data for May 01, 2001 - present:  'cpc_rfe_v2.0_sa_dly.bin.YYYYMMDD.gz'  where YYYY is year, MM is month, DD is day.

    --Spatial domain:  70.0-110.0E; 5.0-35.0N
    --Temporal domain:  00Z-00Z

    --Resolution:  0.1 ir 0.1 degree

    --File structure:  binary, 4-byte floating point,
                       big_endian for daily files contained in
                       ftp://ftpprd.ncep.noaa.gov/pub/cpc/fews/S.Asia/data/

                       little_endian for climatology files contained in
                       ftp://ftpprd.ncep.noaa.gov/pub/cpc/fews/S.Asia/clim/

                       undefined = -999.0

                       file contains one record with (401 pixels in ir direction) * (301 pixels in ic direction) = 120701 points

                       uncompressed file size = 120701 points * 4 bytes per point = 482804 bytes

                       file starting pixel = (5.0N;70.0E)
                       pixel #2 = (5.0N;70.1E)
                       pixel #402 = (5.1N;70.0E)
                       pixel #120701 = (35.0N;110.0E)

    --Monthly accumulations for 2003 are available as created with similar format to daily estimates


These products were created by the NOAA/Climate Prediction Center's FEWS-NET group sponsored by USAID.  For details regarding
the algorithm, see http://www.cpc.ncep.noaa.gov/products/fews.  For usage or other information, contact Nicholas.Novella@noaa.gov or
Pingping.Xie@noaa.gov.


Modified November, 2010
"""
import os

from warsa.precipitation import SARP, make_dir


class Rfe2bin(SARP):
    def __init__(self):
        SARP.__init__(self)
        self.ftp_host = 'ftp://ftp.cpc.ncep.noaa.gov'
        self.ftp_dir = '/fews/S.Asia/data/'
        self.dir_lens = None
        self.prefix = 'cpc_rfe_v2.0_sa_dly.bin.'
        self.datetime_format = '%Y%m%d'

    def get_ftp_file_names(self, lines):
        file_names = []
        for line in lines:
            if not line.startswith('d'):
                filename = line.split()[-1]
                if filename.startswith(self.prefix) and filename.endswith('.gz'):
                    file_names.append(filename)
        return file_names

    def get_datetime_string_from_file_name(self, filename):
        return os.path.splitext(filename)[0].split('.')[-1]

    def get_full_dir_name(self, dt):
        return self.local_dir + '/'


def download(target_dir):
    make_dir(target_dir)
    trmm = Rfe2bin()
    trmm.verbose = True
    trmm.local_dir = target_dir
    trmm.download_ftp(False)

