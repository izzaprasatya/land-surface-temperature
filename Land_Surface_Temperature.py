"""
Model exported as python.
Name : Land Surface Temperature
Group : 
With QGIS : 34007
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsExpression
import processing


class LandSurfaceTemperature(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterNumber('k1', 'K1', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('k2', 'K2 ', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('ml_factor', 'Ml factor', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('nir_band', 'NIR Band', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('red_band', 'Red Band', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('tir_band', 'TIR Band', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('ToaSpectralRadiance', 'TOA Spectral Radiance', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('BrightnessTemperature', 'Brightness Temperature', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Ndvi', 'NDVI', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('ProportionOfVegetation', 'Proportion of Vegetation', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('LandSurfaceEmissivity', 'Land Surface Emissivity', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('LandSurfaceTemperature', 'Land Surface Temperature', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Utfvi', 'UTFVI', createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(9, model_feedback)
        results = {}
        outputs = {}

        # Raster calculator NDVI
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': None,
            'FORMULA': '((A / 10000.0) - (B / 10000.0)) / ((A / 10000.0) + (B / 10000.0))',
            'INPUT_A': parameters['nir_band'],
            'INPUT_B': parameters['red_band'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': -9999,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': parameters['Ndvi']
        }
        outputs['RasterCalculatorNdvi'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Ndvi'] = outputs['RasterCalculatorNdvi']['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # NDVI Statistics
        alg_params = {
            'BAND': 1,
            'INPUT': outputs['RasterCalculatorNdvi']['OUTPUT']
        }
        outputs['NdviStatistics'] = processing.run('native:rasterlayerstatistics', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Raster calculator TOA
        alg_params = {
            'BAND_A': 1,
            'BAND_B': None,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': None,
            'FORMULA': QgsExpression("'(A * ' || @ml_factor || ') + 0.1 - 0.29'\n").evaluate(),
            'INPUT_A': parameters['tir_band'],
            'INPUT_B': None,
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': parameters['ToaSpectralRadiance']
        }
        outputs['RasterCalculatorToa'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['ToaSpectralRadiance'] = outputs['RasterCalculatorToa']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Raster calculator PV
        alg_params = {
            'BAND_A': 1,
            'BAND_B': None,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': None,
            'FORMULA': QgsExpression("'pow((A - ' || @NDVI_Statistics_MIN || ') / (' || @NDVI_Statistics_MAX || ' - ' || @NDVI_Statistics_MIN || '), 2)'\n").evaluate(),
            'INPUT_A': outputs['RasterCalculatorNdvi']['OUTPUT'],
            'INPUT_B': None,
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': parameters['ProportionOfVegetation']
        }
        outputs['RasterCalculatorPv'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['ProportionOfVegetation'] = outputs['RasterCalculatorPv']['OUTPUT']

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Raster calculator E
        alg_params = {
            'BAND_A': 1,
            'BAND_B': None,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': None,
            'FORMULA': '0.004 * A + 0.986',
            'INPUT_A': outputs['RasterCalculatorPv']['OUTPUT'],
            'INPUT_B': None,
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': parameters['LandSurfaceEmissivity']
        }
        outputs['RasterCalculatorE'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['LandSurfaceEmissivity'] = outputs['RasterCalculatorE']['OUTPUT']

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Raster calculator BT
        alg_params = {
            'BAND_A': 1,
            'BAND_B': None,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': None,
            'FORMULA': QgsExpression("'(' || @k2 || ' / log((' || @k1 || ' / A) + 1)) - 273.15'\n").evaluate(),
            'INPUT_A': outputs['RasterCalculatorToa']['OUTPUT'],
            'INPUT_B': None,
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': parameters['BrightnessTemperature']
        }
        outputs['RasterCalculatorBt'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['BrightnessTemperature'] = outputs['RasterCalculatorBt']['OUTPUT']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Raster calculator LST
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': None,
            'FORMULA': '( A / ( 1 + ( 0.00115 * A / 1.4388 ) * log(B)))',
            'INPUT_A': outputs['RasterCalculatorBt']['OUTPUT'],
            'INPUT_B': outputs['RasterCalculatorE']['OUTPUT'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': parameters['LandSurfaceTemperature']
        }
        outputs['RasterCalculatorLst'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['LandSurfaceTemperature'] = outputs['RasterCalculatorLst']['OUTPUT']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # LST Statistics
        alg_params = {
            'BAND': 1,
            'INPUT': outputs['RasterCalculatorLst']['OUTPUT']
        }
        outputs['LstStatistics'] = processing.run('native:rasterlayerstatistics', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Raster calculator UTFVI
        alg_params = {
            'BAND_A': 1,
            'BAND_B': None,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTENT_OPT': 0,  # Ignore
            'EXTRA': None,
            'FORMULA': QgsExpression("'(A - ' || @LST_Statistics_MEAN || ') / A'\n").evaluate(),
            'INPUT_A': outputs['RasterCalculatorLst']['OUTPUT'],
            'INPUT_B': None,
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': None,
            'PROJWIN': None,
            'RTYPE': 5,  # Float32
            'OUTPUT': parameters['Utfvi']
        }
        outputs['RasterCalculatorUtfvi'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Utfvi'] = outputs['RasterCalculatorUtfvi']['OUTPUT']
        return results

    def name(self):
        return 'Land Surface Temperature'

    def displayName(self):
        return 'Land Surface Temperature'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">This algorithm generates a Land Surface Temperature (LST) map and other parameters that are used to generate LST such as Top of Atmospheric (TOA) Spectral Radiance, Brightness Temperature, Normalized Difference Vegetation Index (NDVI), Proportion of Vegetation and Land Surface Emissivity from Landsat 8/9 imagery. This algorithm also creates an Urban Thermal Field Variance Index (UTFVI) which is useful to assess ecological index in a specific area.</p></body></html></p>
<h2>Input parameters</h2>
<h3>K1</h3>
<p>Thermal constant</p>
<h3>K2 </h3>
<p>Thermal constant</p>
<h3>Ml factor</h3>
<p>Band-specific multiplicative rescaling factor</p>
<h3>NIR Band</h3>
<p>Near-infrared band imagery</p>
<h3>Red Band</h3>
<p>Red band imagery</p>
<h3>TIR Band</h3>
<p>Thermal infrared band imagery</p>
<h2>Outputs</h2>
<h3>TOA Spectral Radiance</h3>
<p>The amount of solar energy (radiation) recorded by a satellite sensor at the top of the Earth’s atmosphere, before any correction for atmospheric effects (like scattering or absorption). It's expressed in units like watts per square meter per steradian per micrometer (W/m².sr.µm).</p>
<h3>Brightness Temperature</h3>
<p>The apparent temperature of an object calculated from the thermal infrared radiation (usually from Landsat Band 10 or Band 11). It assumes the object is a perfect blackbody.
</p>
<h3>NDVI</h3>
<p>A widely used vegetation index calculated from red and near-infrared bands. It ranges from -1 to +1. Higher values indicate more vegetation.</p>
<h3>Proportion of Vegetation</h3>
<p>Represents the fractional vegetation cover in a pixel and is derived from NDVI. It helps estimate how much of the land surface is covered by vegetation.</p>
<h3>Land Surface Emissivity</h3>
<p>The efficiency of the Earth's surface in emitting thermal radiation, often influenced by vegetation, soil, and moisture. It’s crucial for accurately estimating Land Surface Temperature from satellite thermal data.</p>
<h3>Land Surface Temperature</h3>
<p>The actual temperature of the Earth's surface corrected from brightness temperature using emissivity and atmospheric effects. A key parameter in studying Urban Heat Island (UHI) effects and environmental health.</p>
<h3>UTFVI</h3>
<p>An index to assess thermal stress and ecological conditions in urban environments. Higher values indicate higher thermal stress and worse environmental conditions</p>
<h2>Examples</h2>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br></body></html>"""

    def createInstance(self):
        return LandSurfaceTemperature()
