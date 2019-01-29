from warsa.precipitation.satellite.arc2.rasterize import ARC2AfricaBinRasterize, ARC2AfricaTifRasterize, ARC2RFE2BinRasterize


class RFE2AfricaBinRasterize(ARC2AfricaBinRasterize):
    pass


class RFE2AfricaTifRasterize(ARC2AfricaTifRasterize):
    pass


class RFE2AsiaBinRasterize(ARC2RFE2BinRasterize):
    def __init__(self, product_dir, output_raster_dir, **kwargs):
        super(RFE2AsiaBinRasterize, self).__init__(401, 301, 70.05, 35.05, product_dir, output_raster_dir, **kwargs)


