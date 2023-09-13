"""
This non-exported module is used to create a yeast protein dataset.

The initial dataset comes from Horton & Nakai and is stored in
`jrpyintroduction/data_raw/yeast_ml.tsv`. That dataset contains predicted
subcellular location information about a collection of yeast proteins.

The Horton and Nakai dataset wasn't sufficiently rich to display the abilities
of pandas particularly well. As such, we have appended some additional data
about the proteins within that dataset. This data was obtained from UniProt.
"""

import os
import re
from pathlib import Path
import pkg_resources

import pandas as pd
from bioservices import UniProt

# ---- #

DIRECTORIES = {
    "raw_yeast": Path(
        pkg_resources.resource_filename(
            __name__,
            os.path.join("data_raw", "yeast")
        )
    ),
    "user_data": Path(pkg_resources.resource_filename(__name__, "data")),
}

YEAST_PATHS = {
    "horton_nakai": DIRECTORIES["raw_yeast"] / "horton_nakai.tsv",
    "uniprot": DIRECTORIES["raw_yeast"] / "uniprot.tsv",
    "combined": DIRECTORIES["user_data"] / "yeast.zip",
}

# ---- #


def combine_yeast_datasets(ml, uniprot):
    return ml.join(uniprot, how="right")


# ---- #


def run_uniprot_workflow(
    identifiers,
    path,
    sep="\t",
    organism="Saccharomyces cerevisiae",
    chunk_size=10,
    required_columns=None,
    go_process_regexes=None,
):
    """
    Download protein information from UniProt and filter to keep only
    those proteins with the selected identifiers.
    Returns a pandas DataFrame. By default the DataFrame has columns
    "Entry Name", "Length" and "Mass".
    """
    if not required_columns:
        base_columns = ["Entry Name", "Length", "Mass"]
        go_columns = [x for x in go_process_regexes.keys()]
        required_columns = base_columns + go_columns

    if not path.exists():
        raw = download_uniprot(identifiers, organism, chunk_size)
        go_annotated = append_go_columns(raw, go_process_regexes)
        go_annotated.to_csv(path, sep=sep)
    else:
        go_annotated = pd.read_csv(path, sep=sep)

    filtered = filter_uniprot(go_annotated, identifiers, required_columns)
    indexed = filtered.set_index("Entry Name").sort_index()

    return indexed


def download_uniprot(
    identifiers,
    organism="Saccharomyces cerevisiae",
    chunk_size=10,
    uniprot_service=None,
):
    if not uniprot_service:
        uniprot_service = UniProt()

    # When searching on UniProt we use "id:ADT1_YEAST" rather than "ADT1_YEAST" strings for the
    # queried protein ID, this limits false positives (the naive search returns any row that matches
    # "ADT1_YEAST" across all columns) and false negatives (a 'limit' determines how many rows are
    # allowed to match any given identifier)
    query_list = ["id:" + id for id in identifiers]

    raw_uniprot = uniprot_service.get_df(
        query_list, organism=organism, nChunk=chunk_size
    )

    return raw_uniprot


def append_go_columns(df, go_process_regexes):
    """
    Adds a Boolean column for each entry in the dictionary `go_process_regexes`.
    """
    if not go_process_regexes:
        return df

    go_process_column = "Gene Ontology (biological process)"

    for process, term_regex in go_process_regexes.items():
        contains_go_term = df[go_process_column].str.match(term_regex, na=False)
        df = append_column(df, process, contains_go_term)

    return df


def append_column(df, col_name, values):
    df[col_name] = values

    return df


def filter_uniprot(raw_uniprot, identifiers, columns):
    """
    Filter a DataFrame of protein information to keep only the requested
    columns, and keep only those proteins with an "Entry Name" in the list of
    "identifiers".
    """
    # Ensure only the requested set of proteins are present
    matching_identifiers = raw_uniprot[
        raw_uniprot["Entry Name"].isin(identifiers)
    ]

    # Ensure no duplicate rows
    unique_df = matching_identifiers.drop_duplicates()
    assert not unique_df.duplicated("Entry Name").any()

    # Keep only the requested columns
    column_filtered = unique_df[columns]
    return column_filtered


# ---- #


def import_horton_nakai(path):
    """
    Read in the Horton/Nakai yeast-protein localisation-prediction results from a tab-separated
    file.
    Then clean up the dataset (replace duplicate entries with a single row and use the UniProt
    identifier as an index)

    :param path: Location of the .tsv that contains the Horton/Nakai yeast-protein dataset.
    """
    raw_table = pd.read_csv(path, sep="\t")

    # Some duplicate rows are present
    # - Both the protein ID, the predicted values and the locations are duplicated so we are OK to
    # keep a single entry for any duplicated row
    filtered = raw_table.drop_duplicates()
    assert filtered["seq"].duplicated().sum() == 0

    # The "seq" column contains UniProt protein identifiers
    # - we use this as the index as there is now a unique row for each protein in the dataset and we
    # want to combine this dataset with a UniProt-derived dataset
    indexed = filtered.set_index("seq").sort_index()

    return indexed


# ---- #


def get_go_term_regex(process):
    """
    Returns a regex for finding GO terms that are associated with a biological process.
    The process may either be "DNA replication" or "cell division"
    """
    return as_regex(get_go_terms(process))


def get_go_terms(process):
    """
    Get a list of GO terms related to a given biological process.
    These include the principal GO term (e.g., "GO:0051301" for "cell division")
    and any of it's child terms.
    Note, we went no further than child terms, so the terms may miss some proteins
    that are annotated to an ancestor term.

    See https://www.ebi.ac.uk/QuickGO/term/GO:0051301 for example.

    'process' can be "DNA replication" or "cell division"
    """
    id_dict = {
        "DNA replication": [
            6260, 43137, 6261, 8156, 6275, 90592, 6271, 45740, 30894
        ],
        "cell division": [
            51301, 40016, 14872, 90510, 51782, 90511, 17145, 48137, 21869, 48860, 8356
        ],
    }
    ids = id_dict[process]

    return [as_go_term(x) for x in ids]


def as_go_term(x):
    """
    Converts an integer to a GO-term formatted string "GO:0012345"
    - "GO:" prefix
    - 7-digit suffix
    - digits are left-padded with 0
    """
    return "GO:{0:07d}".format(x)


def as_regex(xs):
    """
    Create a regex that matches any one of the strings in the list 'xs'
    """
    pattern = ".*(" + "|".join(xs) + ").*"
    return re.compile(pattern)


# ---- #


def main():
    go_process_regexes = {
        k: get_go_term_regex(k) for k in ["DNA replication", "cell division"]
    }

    yeast_ml = import_horton_nakai(YEAST_PATHS["horton_nakai"])
    yeast_uniprot = run_uniprot_workflow(
        list(yeast_ml.index),
        path=YEAST_PATHS["uniprot"],
        sep="\t",
        go_process_regexes=go_process_regexes
    )
    combined_dataset = combine_yeast_datasets(yeast_ml, yeast_uniprot)

    combined_dataset.to_csv(YEAST_PATHS["combined"], compression="zip")


# ---- #

if __name__ == "__main__":
    main()
