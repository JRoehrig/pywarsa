__author__ = 'roehrig'

import os
import datetime
import ftplib
import zipfile
import ogr, osr


def create_dir(new_dir):
    new_dir += '/'
    d = os.path.dirname(new_dir)
    if not os.path.exists(d):
        os.makedirs(d)
    if not new_dir.endswith('/'):
        new_dir += '/'
    return os.path.normpath(new_dir)


def get_parameters_positions(header, parameters):
    header = [h.strip() for h in header.split(';')]
    assert header[0].upper() == 'STATIONS_ID', header
    assert header[1].upper().startswith('MESS_DATUM'), header
    assert header[-1] == 'eor', header
    if not parameters:
        parameters_positions = range(1, len(header)-1)
    else:
        h_dict = dict()
        for i, h in enumerate(header):
            h_dict[h] = i
        parameters_positions = [h_dict[p] for p in parameters if p in h_dict]
        parameters_positions = [1] + parameters_positions
    return parameters_positions


def get_output_lines(lines, parameters_positions):
    max_pos = max(parameters_positions)
    output_lines = list()
    for i, line in enumerate(lines):
        sp = [v.strip() for v in line.split(';')]
        if len(sp) > max_pos:
            if i > 0:
                d = sp[1]
                sp[1] = d[:4] + '-' + d[4:6] + '-' + d[6:]
            output_line = ';'.join([sp[p] for p in parameters_positions])
            output_lines.append(output_line)
    return output_lines


# =============================================================================
# =============================================================================
# =============================================================================
class CDCstation(object):

    def __init__(self, id, beg, end, filename=None):
        self.id = id
        self.beg = beg
        self.end = end
        self.filename = filename
        self.z = 0.0
        self.lat = 0.0
        self.lon = 0.0
        self.name = ''
        self.state = ''
        self.size = 0

    def __repr__(self):
        return "<CDC-HIST %s, %s, %s, %s, %s, %s, %s, %s>" % (self.id, self.beg, self.end, self.lon, self.lat, self.z, self.name, self.state)

    def __str__(self):
        return "<CDC-HIST %s, %s, %s, %s, %s, %s, %s, %s>" % (self.id, self.beg, self.end, self.lon, self.lat, self.z, self.name, self.state)

    def name_valid_as_filename(self):
        return self.name.replace('/', '_')


# =============================================================================
# =============================================================================
# =============================================================================
class CDC(object):

    def __init__(self, local_root_dir, local_dir, station_filename, sid_idx, beg_idx, end_idx):
        # local_dir = ftp_dir
        self.local_root_dir = os.path.normpath(local_root_dir)
        self.local_dir = os.path.normpath(create_dir(os.path.join(local_root_dir, local_dir)))
        self.ftp_host = 'ftp-cdc.dwd.de'
        self.ftp_dir = os.path.join('/pub/CDC/', local_dir)
        self.stations_filename = station_filename
        self.ftp_timeout = 600
        self.ftp_user = None
        self.ftp_password = None
        self.ftp_stations = []
        self.verbose = True
        self.sid_idx = sid_idx
        self.beg_idx = beg_idx
        self.end_idx = end_idx

    def get_station_from_filename(self, filename):
        """Extract all station information from the given file name.
        Args:
            :param filename: the full path file name (string)
        Returns:
            a CDC object
        """
        if not filename.endswith('.zip'):
            return None
        basename = os.path.basename(filename)[:-4]
        fields = basename.split('_')
        sid = fields[self.sid_idx]
        beg = datetime.datetime.strptime(fields[self.beg_idx], '%Y%m%d') if self.beg_idx else None
        end = datetime.datetime.strptime(fields[self.end_idx], '%Y%m%d') if self.end_idx else None
        return CDCstation(sid, beg, end, filename)

    def get_stations(self, station_ids=None, check_consistency=False):
        stations_filename = os.path.join(self.local_dir, self.stations_filename)
        with open(stations_filename, 'r') as f:
            f.readline()
            f.readline()
            line = f.readline()
            try:
                int(line[:5])
                s_type = 1
            except ValueError:
                s_type = 2
        if s_type == 1:
            return self._get_stations1(station_ids, check_consistency)
        elif s_type == 2:
            return self._get_stations2(station_ids, check_consistency)
        else:
            return None

    def _get_stations1(self, station_ids, check_consistency):
        stations_filename = os.path.join(self.local_dir, self.stations_filename)
        stations = dict()
        for s in [self.get_station_from_filename(os.path.join(self.local_dir, f)) for f in os.listdir(self.local_dir) if f.endswith('.zip')]:
            if station_ids is None or int(s.id) in station_ids:
                stations[int(s.id)] = s
        with open(stations_filename, 'r') as f:
            for line in f.readlines()[2:]:
                sid = int(line[:5])
                if sid in stations:
                    s = stations[sid]
                    if check_consistency:
                        beg = datetime.datetime.strptime(line[5:14].strip(), '%Y%m%d')
                        end = datetime.datetime.strptime(line[14:23].strip(), '%Y%m%d')
                        if s.beg != beg or s.end != end:
                            print 'Inconsistent station', s, beg, end
                    s.z = float(line[23:38].strip())
                    s.lat = float(line[38:50].strip())
                    s.lon = float(line[50:60].strip())
                    s.name = line[60:101].strip()
                    s.state = line[101:].strip()
                elif check_consistency:
                    print 'Station', sid, 'does not exist as zip-file'

        return stations

    def _get_stations2(self, station_ids, check_consistency):
        stations_filename = os.path.join(self.local_dir, self.stations_filename)
        stations = dict()
        for s in [self.get_station_from_filename(os.path.join(self.local_dir, f)) for f in os.listdir(self.local_dir) if f.endswith('.zip')]:
            if station_ids is None or int(s.id) in station_ids:
                stations[int(s.id)] = s
        with open(stations_filename, 'r') as f:
            for line in f.readlines()[2:]:
                sid = int(line[0:12])
                if sid in stations:
                    s = stations[sid]
                    if check_consistency:
                        beg = datetime.datetime.strptime(line[12:21].strip(), '%Y%m%d')
                        end = datetime.datetime.strptime(line[21:30].strip(), '%Y%m%d')
                        if s.beg != beg or s.end != end:
                            print 'Inconsistent station', s, beg, end
                    s.z = float(line[30:45].strip())
                    s.lat = float(line[45:56].strip())
                    s.lon = float(line[56:67].strip())
                    s.name = line[67:108].strip()
                    s.state = line[108:].strip()
                elif check_consistency:
                    print 'Station', sid, 'does not exist as zip-file'

        return stations

    def download(self):
        ftp = None
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.ftp_host, timeout=self.ftp_timeout)
            ftp.login(self.ftp_user, self.ftp_password)
            ftp.cwd(self.ftp_dir)
            self.ftp_stations = []
            ftp.retrlines('MLSD', self._stations_callback)
            ftp_filenames = self._files_to_download()
            n = len(ftp_filenames)
            for i, ftp_filename in enumerate(ftp_filenames):
                with open(os.path.join(self.local_dir, ftp_filename), "wb") as bfile:
                    try:
                        ftp.retrbinary('RETR ' + self.ftp_dir + ftp_filename, callback=bfile.write)
                        print (i+1), 'of', n, self.ftp_dir + ftp_filename, ' downloaded'
                    except Exception, e:
                        print e

        finally:
            if ftp:
                ftp.close()

    def _stations_callback(self, line):
        sp = line.split(';')
        sp[-1] = 'name=' + sp[-1].strip()
        parameters = {}
        for p in sp:
            sp1 = p.split('=')
            parameters[sp1[0]] = sp1[1]
        if 'type' in parameters and parameters['type'] == 'file' and 'size' in parameters:
            station = self.get_station_from_filename(parameters['name'])
            if station:
                station.size = int(parameters['size'])
                self.ftp_stations.append(station)

    def _files_to_download(self):
        local_stations_dict = dict()
        local_stations = [self.get_station_from_filename(f) for f in os.listdir(self.local_dir) if f.endswith('.zip')]
        for s in local_stations:
            f_stat = os.stat(os.path.join(self.local_dir, s.filename))
            s.size = f_stat.st_size
            local_stations_dict[s.id] = s
        local_files_to_remove = list()
        ftp_files_to_download = [self.stations_filename]
        for s_ftp in self.ftp_stations:
            if s_ftp.id in local_stations_dict:
                s_local = local_stations_dict[s_ftp.id]
                if s_local.beg != s_ftp.beg or s_local.end != s_ftp.end or s_local.size != s_ftp.size:
                    local_files_to_remove.append(s_local.filename)
                    ftp_files_to_download.append(s_ftp.filename)
            else:
                ftp_files_to_download.append(s_ftp.filename)
        for f in local_files_to_remove:
            ff = os.path.join(self.local_dir, f)
            if os.path.isfile(ff):
                os.remove(ff)
            else:
                print ff, 'does not exist and could not be removed'
        return ftp_files_to_download

    def read(self, output_dir='all_csv', parameters=None, station_ids=None):
        stations = self.get_stations(station_ids)
        if len(stations) == 0:
            return
        if isinstance(parameters, basestring):
            parameters = [parameters]
        output_dir = os.path.normpath(output_dir)
        suffix = '_' + output_dir.split(os.sep)[-1] + '.csv'
        output_dir0 = create_dir(os.path.join(self.local_dir, output_dir))
        parameter_type = '_' + parameters[0].lower() if parameters and len(parameters) == 1 else ''
        i = 0
        n = len(stations)
        for k, s in stations.items():
            i += 1
            print 'Extracting csv %d of %d: %s, %s' % (i, n, s.name, s.id)
            try:
                with zipfile.ZipFile(s.filename, 'r', zipfile.ZIP_DEFLATED) as zf:
                    try:
                        zip_filename = [sn for sn in zf.namelist() if sn.startswith('produkt_')][0]
                        ts = zf.read(zip_filename)
                        lines = ts.split('\n')
                        parameters_positions = get_parameters_positions(lines[0], parameters)
                        output_lines = get_output_lines(lines, parameters_positions)
                        s_name = s.name.replace('/', '-')
                        output_filename = os.path.join(output_dir0, s.id + '_' + s_name + parameter_type + suffix)
                        with open(output_filename, 'w') as f:
                            for output_line in output_lines:
                                f.write(output_line + '\n')
                    except KeyError:
                        print 'ERROR: Did not find the product in zip file %s' % s.filename
            except zipfile.BadZipfile, e:
                print e, s.filename


    def get_shapefile(self):
        f0 = create_dir('_'.join(reversed(self.local_dir[len(self.local_root_dir):].split(os.sep)[1:])))
        return os.path.join(create_dir(os.path.join(self.local_dir, 'gis')), 'station_' + f0 + '_wgs84.shp')

    def create_shapefile(self):
        sr = osr.SpatialReference()
        sr.ImportFromEPSG(4326)
        shp = self.get_shapefile()
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.isfile(shp) and os.stat(shp):
            driver.DeleteDataSource(shp)
        print 'Creating shapefile', shp
        ds = driver.CreateDataSource(shp)
        layer = ds.CreateLayer('', sr, ogr.wkbPoint)

        layer.CreateField(ogr.FieldDefn("Id", ogr.OFTInteger))

        field_sid = ogr.FieldDefn("Ids", ogr.OFTString)
        field_sid.SetWidth(8)
        layer.CreateField(field_sid)

        stations = self.get_stations()

        name_length = 20
        for s in stations.values():
            n = len(s.name_valid_as_filename())
            if n > name_length:
                name_length = n + 5
        field_name = ogr.FieldDefn("Name", ogr.OFTString)
        field_name.SetWidth(name_length)
        layer.CreateField(field_name)

        field_state = ogr.FieldDefn("Bundesland", ogr.OFTString)
        field_state.SetWidth(25)
        layer.CreateField(field_state)

        layer.CreateField(ogr.FieldDefn('Latitude', ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn('Longitude', ogr.OFTReal))
        layer.CreateField(ogr.FieldDefn('Elevation', ogr.OFTReal))

        ld = layer.GetLayerDefn()
        for s in stations.values():
            feat = ogr.Feature(ld)
            try:
                sid = int(s.id)
            except ValueError:
                sid = 0
            feat.SetField('Id', sid)
            feat.SetField('Ids', s.id)
            feat.SetField('Name', s.name)
            feat.SetField('Bundesland', s.state)
            feat.SetField('Latitude', s.lat)
            feat.SetField('Longitude', s.lon)
            feat.SetField('Elevation', s.z)
            point = ogr.Geometry(ogr.wkbPoint)
            point.AddPoint(s.lon, s.lat)
            feat.SetGeometry(point)
            layer.CreateFeature(feat)
        ds = layer = feat = point = None

# =============================================================================
# =============================================================================
# =============================================================================
class CDCHistorical(CDC):
    def __init__(self, local_root_dir, local_dir, station_filename, sid_idx=2, beg_idx=3, end_idx=4):
        super(CDCHistorical, self).__init__(local_root_dir, local_dir, station_filename, sid_idx, beg_idx, end_idx)

# =============================================================================
# =============================================================================
# =============================================================================
class CDCRecent(CDC):
    def __init__(self, local_root_dir, local_dir, station_filename, sid_idx=2):
        super(CDCRecent, self).__init__(local_root_dir, local_dir, station_filename, sid_idx, None, None)










    # def get_station(self, filename):
    #     if not filename.endswith('.zip'):
    #         return None
    #     else:
    #         basename = os.path.basename(filename)
    #         fields = basename.split('_')
    #         sid = fields[2]
    #         beg = datetime.datetime.strptime(fields[3], '%Y%m%d')
    #         end = datetime.datetime.strptime(fields[4], '%Y%m%d')
    #         return CDCstation(sid, beg, end, filename)

    # def read(self, output_dir='all_csv', parameters=None, station_ids=None):
    #     if isinstance(parameters, basestring):
    #         parameters = [parameters]
    #     output_dir = create_dir(os.path.join(self.local_dir, output_dir))
    #     stations = self.get_stations(station_ids)
    #     parameter_type = '_' + parameters[0].lower() if parameters and len(parameters) == 1 else ''
    #     i = 0
    #     n = len(stations)
    #     for k, s in stations.items():
    #         i += 1
    #         print 'Extracting csv %d of %d: %s, %s' % (i, n, s.name, s.id)
    #         with zipfile.ZipFile(s.filename, 'r', zipfile.ZIP_DEFLATED) as zf:
    #             try:
    #                 zip_filename = get_zip_filename(zf.namelist())
    #                 ts = zf.read(zip_filename)
    #                 lines = ts.split('\n')
    #                 parameters_positions = get_parameters_positions(lines[0], parameters)
    #                 output_lines = get_output_lines(lines, parameters_positions)
    #                 s_name = s.name.replace('/', '-')
    #                 output_filename = output_dir + s.id + '_' + s_name + parameter_type + '.csv'
    #                 with open(output_filename, 'w') as f:
    #                     for output_line in output_lines:
    #                         f.write(output_line + '\n')
    #             except KeyError:
    #                 print 'ERROR: Did not find %s in zip file' % zip_filename

    # def get_station(self, filename):
    #     if not filename.endswith('.zip'):
    #         return None
    #     else:
    #         basename = os.path.basename(filename)
    #         basename = basename[:-4]
    #         fields = basename.split('_')
    #         name = fields[2]
    #         return CDCstation(name, None, None, filename)
    #
    # def read(self, output_dir='all_csv', parameters=None, station_ids=None):
    #     if isinstance(parameters, basestring):
    #         parameters = [parameters]
    #     output_dir = create_dir(os.path.join(self.local_dir, output_dir))
    #     stations = self.get_stations(station_ids)
    #     parameter_type = '_' + parameters[0].lower() if parameters and len(parameters) == 1 else ''
    #     i = 0
    #     n = len(stations)
    #     for k, s in stations.items():
    #         i += 1
    #         print 'Extracting csv %d of %d: %s, %s' % (i, n, s.name, s.id)
    #         with zipfile.ZipFile(s.filename, 'r', zipfile.ZIP_DEFLATED) as zf:
    #             try:
    #                 zip_filename = get_zip_filename(zf.namelist())
    #                 ts = zf.read(zip_filename)
    #                 lines = ts.split('\n')
    #                 parameters_positions = get_parameters_positions(lines[0], parameters)
    #                 output_lines = get_output_lines(lines, parameters_positions)
    #                 s_name = s.name.replace('/', '-')
    #                 output_filename = output_dir + s.id + '_' + s_name + parameter_type + '.csv'
    #                 with open(output_filename, 'w') as f:
    #                     for output_line in output_lines:
    #                         f.write(output_line + '\n')
    #             except KeyError:
    #                 print 'ERROR: Did not find %s in zip file' % zip_filename


