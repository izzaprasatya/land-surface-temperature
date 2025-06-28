# land-surface-temperature
A QGIS Model Builder to generate a Land Surface Temperature (LST) map and other parameters related to Urban Heat Island analysis.

Outputs:
- TOA Spectral Radiance
The amount of solar energy (radiation) recorded by a satellite sensor at the top of the Earth’s atmosphere, before any correction for atmospheric effects (like scattering or absorption). It's expressed in units like watts per square meter per steradian per micrometer (W/m².sr.µm).
- Brightness Temperature
The apparent temperature of an object calculated from the thermal infrared radiation (usually from Landsat Band 10 or Band 11). It assumes the object is a perfect blackbody.
- NDVI
A widely used vegetation index calculated from red and near-infrared bands. It ranges from -1 to +1. Higher values indicate more vegetation.
- Proportion of Vegetation
Represents the fractional vegetation cover in a pixel and is derived from NDVI. It helps estimate how much of the land surface is covered by vegetation.
- Land Surface Emissivity
The efficiency of the Earth's surface in emitting thermal radiation, often influenced by vegetation, soil, and moisture. It’s crucial for accurately estimating Land Surface Temperature from satellite thermal data.
- Land Surface Temperature
The actual temperature of the Earth's surface corrected from brightness temperature using emissivity and atmospheric effects. A key parameter in studying Urban Heat Island (UHI) effects and environmental health.
- UTFVI
An index to assess thermal stress and ecological conditions in urban environments. Higher values indicate higher thermal stress and worse environmental conditions.
