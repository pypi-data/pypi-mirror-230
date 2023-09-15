project = "powerfit"
copyright = "2023, Tom de Geus"
author = "Tom de Geus"
html_theme = "furo"
autodoc_type_aliases = {"Iterable": "Iterable", "ArrayLike": "ArrayLike"}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_mdinclude",
]
