# -*- coding: utf-8 -*-

"""The Selventa knowledge repository."""

import os

from pybel.repository import BELMetadata, BELRepository

__all__ = [
    "repository",
    "metadata",
    "get_graph",
    "get_graphs",
    "get_summary_df",
    "main",
]

HERE = os.path.dirname(__file__)
VERSION = "20150611"

# All metadata is grouped here
metadata = BELMetadata(
    name="Selventa Corpora",
    version=VERSION,
    authors="Selventa",
    contact="support@belframework.org",
    description="Selventa Large and Small Corpora.",
    license="Creative Commons Attribution-Non-Commercial-ShareAlike 3.0 Unported License",
    copyright="Copyright (c) 2011-2015, Selventa. All Rights Reserved.",
)

repository = BELRepository(
    HERE,
    metadata=metadata,
    from_path_kwargs=dict(
        citation_clearing=False,
    ),
    formats=("pickle", "nodelink.json.gz")
)

get_graph = repository.get_graph
get_graphs = repository.get_graphs
get_summary_df = repository.get_summary_df

main = repository.build_cli()
