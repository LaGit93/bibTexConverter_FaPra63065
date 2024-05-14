# -*- coding: utf-8 -*-
"""
Lade Beispieldaten von semantic schooler
"""

import config as cfg
import logging
import requests as rq
import json
from typing import List, Set
import random

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

# initialize logging
cfg.initialize_global_config()

fields = [  # see https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/post_graph_get_papers
    "paperId",  # unique identifier
    "url",  # url on semantic schoolary
    "isOpenAccess",
    "openAccessPdf",  # link to the pdf if publicly available
    "publicationTypes",  # Journal Article, Conference, Review, etc
    "citations",
    "references",
]


def collect_documents(
    document_id_pool: List[str],
    visited_document_ids: Set[str] = None,
    n_documents: int = 20,
    fields: List[str] = fields,
):
    """
    Wähle zufällig eine document_id aus dem pool und lade das Dokument herunter
    (falls verfügbar), füge die Ids der Dokumente ein, die das heruntergeladene
    Dokument referenzieren.

    Parameters
    ----------
    document_id_pool : List[str]
        Dokumente, die noch nicht abgearbeitet wurden.

    visited_document_ids : Set[str]
        Dokumente, die bereits verarbeitet wurden und nich noch einmal
        ausgewählt und heruntergeladen werden sollen.

    n_documents :

    Returns
    -------
    None.
    """
    if visited_document_ids is None:
        visited_document_ids = set()

    # sicher stellen, dass document_id_pool eine saubere Kopie ist
    document_id_pool = [
        doc_id for doc_id in set(document_id_pool) if doc_id not in visited_document_ids
    ]

    result_document_infos = []

    while document_id_pool and n_documents > 0:
        # es sind keine Dokumente auszuwählen
        next_doc_id = random.choice(document_id_pool)
        document_id_pool.remove(next_doc_id)

        logger.info("hole Daten zu Dokument %s", next_doc_id)

        response = rq.post(
            "https://api.semanticscholar.org/graph/v1/paper/batch",
            params={"fields": ",".join(fields)},
            json={"ids": [next_doc_id]},
        )
        # Das Ergebnis ist eine Liste mit 0-1 Element
        json_result = response.json()
        if json_result and isinstance(json_result, list):
            # Der Endpoint hat ein Dokument geliefert
            doc_data = json_result[0]
            logger.info("Ergebnis des Endpoint-Aufrufs: %s", doc_data)
            doc_data["document_id"] = next_doc_id
            result_document_infos.append(doc_data)
            n_documents -= 1
        else:
            logger.error("Unerwartetes Ergebnis des Endpoint-Aufrufs: %s", json_result)

    return result_document_infos


logger.info("verwende Konfiguration %s", cfg.CONFIG)

if "random_seed" in cfg.CONFIG["download_raw_data"]:
    seed = cfg.CONFIG["download_raw_data"]["random_seed"]
    logger.info("Setze random seed auf %s für Reproduzierbarkeit", seed)
    random.seed(seed)

document_ids = cfg.CONFIG["download_raw_data"]["semantic_schoolar"][
    "initial_document_ids"
]

document_data = collect_documents(
    document_ids,
    n_documents=50,
)

print(json.dumps(document_data, indent=2))
