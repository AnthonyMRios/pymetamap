pymetamap
=========

Python wrapper around `MetaMap <http://metamap.nlm.nih.gov/>`_.
This will take a list of sentences and extract concepts using MetaMap
then return them in the form of a list of Concept objects.

**Note:** This code does **not** work with Windows because of my use of NamedTemporaryFile in SubprocessBackend.py.

How to Install
--------------

First, install MetaMap by using the following instructions: https://metamap.nlm.nih.gov/Installation.shtml

Next, pymetamap can be installed using the following command:

>>> python setup.py install

Example Usage
-------------

To start you must create a MetaMap instance from the pymetamap package.

::

    >>> from pymetamap import MetaMap
    >>> mm = MetaMap.get_instance('/opt/public_mm/bin/metamap12')

You must supply the metamap binary to ``get_instance()`` in order to
extract concepts. Depending on where you installed MetaMap and depending on the version you are using, you will need to change the ``/opt/public_mm/bin/metamap12`` to the correct location.
For example, if you installed the 2016 version of MetaMap, then the binary will be called ``metamap16``.

We now support MetaMapLite. To use MetaMapLite, rather than MetaMap, create a MetaMapLite instance:

::

    >>> from pymetamap import MetaMapLite
    >>> mm = MetaMapLite.get_instance('/opt/public_mm_lite_3.6.2rc3/')

**Note:** The MetaMap binary path and MetaMapLite home directory should be absolute.

To extract concepts from a sentence with MetaMapLite and MetaMap use the ``extract_concepts()``
method. This method takes a list of sentences as input and will return
a list of Concept objects.

::

    >>> sents = ['Heart Attack', 'John had a huge heart attack']
    >>> concepts,error = mm.extract_concepts(sents,[1,2])
    >>> for concept in concepts:
    ...     print concept
    Concept(index='1', mm='MM', score='14.64', preferred_name='Myocardial Infarction', cui='C0027051', semtypes='[dsyn]', trigger='["Heart attack"-tx-1-"Heart Attack"]', location='TX', pos_info='1:12', tree_codes='C14.280.647.500;C14.907.585.500')
    Concept(index='2', mm='MM', score='13.22', preferred_name='Myocardial Infarction', cui='C0027051', semtypes='[dsyn]', trigger='["Heart attack"-tx-1-"heart attack"]', location='TX', pos_info='17:12', tree_codes='C14.280.647.500;C14.907.585.500')

This example shows two separate concepts extracted via MetaMap from two
different sentences (sentence 1 and sentence 2).

More Information
----------------

Licensed under `Apache 2.0 <http://www.apache.org/licenses/LICENSE-2.0>`_.

Written by Anthony Rios

Special thanks to `joaopalotti <https://github.com/joaopalotti>`_ and others for their contributions.
