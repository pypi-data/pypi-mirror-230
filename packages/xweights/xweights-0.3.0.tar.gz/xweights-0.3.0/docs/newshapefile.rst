.. highlight:: shell

==============================
How to add your own shape file
==============================

Instructions how to add a new shape file of a new region to xweights.

Here it is explained on the example of the IPCC_ Reference Regions: IPCC-WGI Reference Regions version 4:


 * Fork https://github.com/ludwiglierhammer/test_data to your own github account.

 * Make a new branch (git checkout -b your-branch-name).

 * Add your zipped sape file to the directory shp.

 * push

 * make pull request


xweights:
.........

Same procedure now for xweight, fork github/xweights to your github account, pull and make a new branch.


Edit:
.....
=======
Hier eine Anleitung, wie du weitere Regionen hinzufügen kannst (am Beispiel SREX):
..................................................................................

Erstelle in meinen repository test_data einen neuen branch.
Füge im Verzeichnis shp deinen gezippten shape file hinzu und pushe das Ganze.
Nun kannst du einen pull request stellen.
Erstelle einen neuen branch in weights.

Editiere die Datei

.. code-block:: console

		xweights/_regions.py:

L.51: Add your new region to the list (e.g. ipcc):

.. code-block:: console

		self.regions = ["counties", "counties_merged", "states", "prudence", "ipcc"]

Add at the end __init__ -Funktion

.. code-block:: console

		self.ipcc=IPCC()

copy the class counties_merged and add it again with your new name e.g. ipcc and add the name of your zipped shape file:

.. code-block:: console

		class IPCC:
		      def __init__(self):
		      self.description = (
		      "IPCC regions"
		      )
		      self.geodataframe = self._ipcc()
		      self.selection = "name"

		def _ipcc(self):

=======
L.51: Erweiter die Liste um den Namen deiner neuen Region.

.. code-block:: console

		self.regions = ["counties", "counties_merged", "states", "prudence", "srex"]

Füge am Ende der

.. code-block:: console

		__init__-Funktion self.srex=SREX()

Kopiere die Klasse Counties_merged und füge sie als neue Klasse unter dem Namen SREX hinzu:

.. code-block:: console

		class SREX:
		      def __init__(self):
		      self.description = (
		      "S-REX regions"
		      )
		      self.geodataframe = self._srex()
		      self.selection = "name"

		def _srex(self):
		    url_base = (
		    "https://github.com/ludwiglierhammer/test_data/raw/main/shp"  # noqa
		    )
		    url = os.path.join(
		          url_base, "<name_deiner_zip_datei>",
			  )
		    shape_zip = _pooch_retrieve(
                    url,
                    known_hash="2ca82af334aee2afdcce4799d5cc1ce50ce7bd0710c9ec39e6378519df60ad7a",  # noqa
                     )
<<<<<<< HEAD
                    return _get_geodataframe(shape_zip, name="IPCCv4")



You can replace the known_hash with the HASH of your zipped file. This will be displayed when you run the following:


.. code-block:: console

		xweights -which_regions



.. _ipcc: https://github.com/IPCC-WG1/Atlas/tree/main/reference-regions
=======
                    return _get_geodataframe(shape_zip, name="SREX_Region")


Den known_hash kannst du mit dem HASH deiner gezippten Datei ersetzen. Dieser wird dir angezeigt, wenn du folgendes ausführst:

.. code-block:: console

		xweights which_regions
