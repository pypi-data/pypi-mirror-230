Selventa Knowledge
==================
Updated versions of the Selventa Small and Large Corpus

Licenses
--------
- Code in this repository is licensed under the MIT License
- Both the Selvanta Small Corpus and Selventa Large Corpus are distributed under
  the Creative Commons Attribution-Non-Commercial-ShareAlike 3.0 Unported
  License.

Installation
------------
``selventa_knowledge`` can be installed from `PyPI <https://pypi.org/project/selventa-knowledge>`_ with:

.. code-block:: sh

   $ pip install selventa-knowledge

``selventa_knowledge`` can be installed from `GitHub <https://github.com/cthoyt/selventa-knowledge>`_ with:

.. code-block:: sh

   $ pip install git+https://github.com/cthoyt/selventa-knowledge.git

Usage
-----
The combine graph can be loaded with:

.. code-block:: python

    >>> import selventa_knowledge
    >>> graph = selventa_knowledge.get_graph()

If you need granularity, you can load each graph in a dictionary where
all of the names of the files creating each graph are the keys and the
values are also BEL graphs with:

.. code-block:: python

    >>> import selventa_knowledge
    >>> graphs = selventa_knowledge.get_graphs()

The functions from each of the previous examples are simply
exposing the bound functions from the BELRepository object,
which can be accessed with:

.. code-block:: python

    >>> import selventa_knowledge
    >>> repository = selventa_knowledge.repository

If you want to use this knowledge with INDRA, there's a method:

.. code-block:: python

    >>> import selventa_knowledge
    >>> statements = selventa_knowledge.repository.get_indra_statements()

More BEL Content
----------------
See `A Listing of Publicly Available Content in the Biological Expression Language (BEL)
<https://cthoyt.com/2020/04/30/public-bel-content.html>`_ on Charles Tapley Hoyt's blog
for more BEL content.
