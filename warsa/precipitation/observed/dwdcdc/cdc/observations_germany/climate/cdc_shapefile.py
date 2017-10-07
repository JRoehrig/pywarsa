__author__ = 'roehrig'

import os
import tempfile
import time

import ogr
import osr
from precipytation.observed.dwdcdc import \
    CDCObservationsGermanyClimateHourlyCloudinessHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.cdc_climate import create_dir
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.kl_historical import \
    CDCObservationsGermanyClimateDailyKLHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.kl_recent import \
    CDCObservationsGermanyClimateDailyKLRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.more_precip_historical import \
    CDCObservationsGermanyClimateDailyMorePrecipHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.more_precip_recent import \
    CDCObservationsGermanyClimateDailyMorePrecipRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.soil_temperature_recent import \
    CDCObservationsGermanyClimateDailySoilTemperatureRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.daily.solar import \
    CDCObservationsGermanyClimateDailySolar
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.air_temperature_historical import \
    CDCObservationsGermanyClimateHourlyAirTemperatureHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.air_temperature_recent import \
    CDCObservationsGermanyClimateHourlyAirTemperatureRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.cloudiness_recent import \
    CDCObservationsGermanyClimateHourlyCloudinessRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.pressure_historical import \
    CDCObservationsGermanyClimateHourlyPressureHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.pressure_recent import \
    CDCObservationsGermanyClimateHourlyPressureRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.solar import \
    CDCObservationsGermanyClimateHourlySolar
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.sun_historical import \
    CDCObservationsGermanyClimateHourlySunHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.sun_recent import \
    CDCObservationsGermanyClimateHourlySunRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.wind_historical import \
    CDCObservationsGermanyClimateHourlyWindHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.hourly.wind_recent import \
    CDCObservationsGermanyClimateHourlyWindRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.monthly.kl_historical import \
    CDCObservationsGermanyClimateMonthlyKLHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.monthly.kl_recent import \
    CDCObservationsGermanyClimateMonthlyKLRecent
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.monthly.more_precip_historical import \
    CDCObservationsGermanyClimateMonthlyMorePrecipHistorical
from precipytation.observed.dwdcdc.cdc.observations_germany.climate.monthly.more_precip_recent import \
    CDCObservationsGermanyClimateMonthlyMorePrecipRecent
from warsa.gis.features.feature import LayerDefinition, FieldDefinition, delete_shapefile

from warsa.precipitation.observed.dwdcdc.cdc.observations_germany.climate.daily.soil_temperature_historical import \
    CDCObservationsGermanyClimateDailySoilTemperatureHistorical


def create_shapefile_historical(local_dir):
    CDCObservationsGermanyClimateDailyKLHistorical(local_dir).create_shapefile()
    CDCObservationsGermanyClimateDailyMorePrecipHistorical(local_dir).create_shapefile()
    CDCObservationsGermanyClimateDailySoilTemperatureHistorical(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlyAirTemperatureHistorical(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlyCloudinessHistorical(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlyPressureHistorical(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlySunHistorical(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlyWindHistorical(local_dir).create_shapefile()
    CDCObservationsGermanyClimateMonthlyKLHistorical(local_dir).create_shapefile()
    CDCObservationsGermanyClimateMonthlyMorePrecipHistorical(local_dir).create_shapefile()


def create_shapefile_recent(local_dir):
    CDCObservationsGermanyClimateDailyKLRecent(local_dir).create_shapefile()
    CDCObservationsGermanyClimateDailyMorePrecipRecent(local_dir).create_shapefile()
    CDCObservationsGermanyClimateDailySoilTemperatureRecent(local_dir).create_shapefile()
    CDCObservationsGermanyClimateDailySolar(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlyAirTemperatureRecent(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlyCloudinessRecent(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlyPressureRecent(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlySolar(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlySunRecent(local_dir).create_shapefile()
    CDCObservationsGermanyClimateHourlyWindRecent(local_dir).create_shapefile()
    CDCObservationsGermanyClimateMonthlyKLRecent(local_dir).create_shapefile()
    CDCObservationsGermanyClimateMonthlyMorePrecipRecent(local_dir).create_shapefile()


def create_shapefile_all(local_dir):
    create_shapefile_historical(local_dir)
    create_shapefile_recent(local_dir)


def get_shapefiles(local_dir):
    return [
        CDCObservationsGermanyClimateDailyKLHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateDailyMorePrecipHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateDailySoilTemperatureHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlyAirTemperatureHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlyCloudinessHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlyPressureHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlySunHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlyWindHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateMonthlyKLHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateMonthlyMorePrecipHistorical(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateDailyKLRecent(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateDailyMorePrecipRecent(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateDailySoilTemperatureRecent(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateDailySolar(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlyAirTemperatureRecent(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlyCloudinessRecent(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlyPressureRecent(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlySolar(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlySunRecent(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateHourlyWindRecent(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateMonthlyKLRecent(local_dir).get_shapefile(),
        CDCObservationsGermanyClimateMonthlyMorePrecipRecent(local_dir).get_shapefile()
        ]


def get_merged_fields(local_dir):
    shapefiles = get_shapefiles(local_dir)
    dataset = ogr.Open(shapefiles[0], 0)
    layer_definition = LayerDefinition(dataset.GetLayer(0))
    del dataset
    records = list()
    for shapefile in shapefiles:
        shp = '-'.join(os.path.basename(shapefile)[:-4].split('_')[1:])
        dataset = ogr.Open(shapefile, 0)
        ly = dataset.GetLayer(0)
        ly.ResetReading()
        for feat in ly:
            fds = layer_definition.field_definitions
            record = tuple([feat.GetGeometryRef().ExportToWkb()]) + \
                     tuple([feat.GetField(fd.name) for fd in fds]) + \
                     tuple([shp])
            records.append(record)
        del dataset
    fd_shp = FieldDefinition('Source', ogr.OFTString, 'String', 50, 0)
    layer_definition.field_definitions.append(fd_shp)
    return layer_definition, records


def merge_shapefiles(local_dir, shp):
    layer_definition, records = get_merged_fields(local_dir)
    rd = {}
    for record in records:
        r0 = record[:-1]
        if r0 not in rd:
            rd[r0] = record
    records = sorted(rd.values())

    sr = osr.SpatialReference()
    sr.ImportFromWkt(layer_definition.spatial_ref)

    driver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.isfile(shp) and os.stat(shp):
        driver.DeleteDataSource(shp)
    ds = driver.CreateDataSource(shp)

    layer = ds.CreateLayer('', sr, layer_definition.geom_type)

    for fd in layer_definition.field_definitions:
        fd_def = ogr.FieldDefn(fd.name, fd.type_code)
        fd_def.SetWidth(fd.width)
        fd_def.SetPrecision(fd.precision)
        layer.CreateField(fd_def)

    ld = layer.GetLayerDefn()
    for r in records:
        feat = ogr.Feature(ld)
        feat.SetGeometry(ogr.CreateGeometryFromWkb(r[0]))
        n = ld.GetFieldCount()
        for i in range(n):
            name = ld.GetFieldDefn(i).GetName()
            value = r[i+1]
            feat.SetField(name, value)
        layer.CreateFeature(feat)
    ds = layer = feat = point = None


def get_stations_in_region(shp_region, shp_input_stations, shp_output_stations, overwrite=False):

    if os.path.isfile(shp_output_stations):
        if not overwrite:
            print 'File %s already exists and was not overwritten.' % shp_output_stations
            return
        else:
            delete_shapefile(shp_output_stations)

    create_dir(os.path.basename(shp_output_stations))

    region_dataset = ogr.Open(shp_region, 0)
    region_layer = region_dataset.GetLayer(0)
    region_geom = None
    region_layer.ResetReading()
    for r_feat in region_layer:
        geom = r_feat.GetGeometryRef().ExportToWkb()
        if geom:
            region_geom = ogr.CreateGeometryFromWkb(geom) if not region_geom else region_geom.Union(ogr.CreateGeometryFromWkb(geom))

    tmp_dir = None
    if not shp_input_stations:
        tmp_dir = tempfile.gettempdir()
        shp_input_stations = os.path.join(tmp_dir, 'tmp' + str(sum(time.time().as_integer_ratio())) + '.shp')

    stations_dataset = ogr.Open(shp_input_stations, 0)
    stations_layer = stations_dataset.GetLayer(0)
    stations_layer_definition = stations_layer.GetLayerDefn()
    field_definitions = [stations_layer_definition.GetFieldDefn(ifd) for ifd in range(stations_layer_definition.GetFieldCount())]

    driver = ogr.GetDriverByName('ESRI Shapefile')
    output_dataset = driver.CreateDataSource(shp_output_stations)
    if output_dataset is None:
        if os.path.exists(shp_output_stations):
            raise ValueError("Data source {} already exists".format(str(shp_output_stations)))
        else:
            raise ValueError("Data source {} could not be created".format(str(shp_output_stations)))
    output_layer = output_dataset.CreateLayer('stations', stations_layer.GetSpatialRef(), stations_layer.GetGeomType())
    for fd in field_definitions:
        output_layer.CreateField(fd)

    stations_layer.ResetReading()
    for s_feat in stations_layer:
        s_geom = s_feat.GetGeometryRef()
        if s_geom.Within(region_geom):
            output_layer.CreateFeature(s_feat)

    output_dataset = output_layer = None

    if tmp_dir:
        os.remove(shp_input_stations)


def get_stations_ids(shp):
    dataset = ogr.Open(shp, 0)
    layer = dataset.GetLayer(0)
    layer.ResetReading()
    ids = [feat.GetField('Id') for feat in layer]
    del dataset, layer
    return ids


