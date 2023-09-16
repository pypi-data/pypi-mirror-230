=======
History
=======

0.1.0 (2022-03-04)
------------------

* First release on PyPI.

0.1.1 (2022-07-01)
------------------

* adjusted to pre-commit
* use functions from pyhomogenize

0.1.2 (2022-07-08)
------------------

* change pyhomogenize version requirements

0.2.0 (2022-07-11)
------------------

* rename spatial_averager
* keep geometry attributes

0.2.1 (2022-07-11)
------------------

* read and write column name to attributes

0.2.2 (2022-07-12)
------------------

* add data and tables via pip install

0.2.3 (2023-01-26)
------------------

* remove cartopy from requirements.txt

0.2.4 (2023-03-13)
------------------

* using pycordex >= 0.5.1

0.2.5 (2023-08-23)
------------------

* adding new region: counties_merged (merge counties less than 400m2)

0.2.6 (2023-08-30)
------------------

* optionally: wite variable attributes to dataframe

0.3.0 (2023-09-15)
------------------

* added new regions: IPCC WG1 Reference Regions v4 from Atlas
* xweights/_io.py is no longer available
* xweights/_domains.py is no longer available
* function `spatial_averager` -> `spatial_averaging`
* function `compute_weighted_means`:

  * optionally: set `averager_ds` to calculate a general xesmf.SpatialAverager
  * parameter `shp` -> `gdf`
  * parameter `input` -> `dataset_dict`
  * parameter `dataset_dict` has to be a dictionary
  * parameter `outdir` -> `output`

* function `compute_weighted_means_ds`: parameters are now similar to `compute_weighted_means`
* command-line interface is no longer available
