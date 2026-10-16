"""JEE question-bank content pipeline.

Stages: ingest -> normalize -> tag -> (solve, external) -> verify -> publish.

Only stdlib is required at runtime; the poppler CLI tools ``pdftotext`` and
``pdfimages`` must be installed for the PDF stages (ingest, keyparser).
"""

from . import ingest, normalize, schema, keyparser, verify, tag, taxonomy

__all__ = ["ingest", "normalize", "schema", "keyparser", "verify", "tag", "taxonomy"]

__version__ = "0.1.0"
