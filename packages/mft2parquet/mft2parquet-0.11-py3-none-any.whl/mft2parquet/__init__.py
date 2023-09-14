import gc
import os
import tempfile
from touchtouch import touch
import pandas as pd
import subprocess
from getfilenuitkapython import get_filepath

uffscom = get_filepath("uffs.com")

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
startupinfo.wShowWindow = subprocess.SW_HIDE
creationflags = subprocess.CREATE_NO_WINDOW
invisibledict = {
    "startupinfo": startupinfo,
    "creationflags": creationflags,
    "start_new_session": True,
}


def get_tmpfile(suffix: str = ".pqt") -> str:
    r"""
    Returns a temporary file path with the specified suffix.

    Args:
        suffix (str): The suffix for the temporary file. Default is ".pmc".

    Returns:
        str: The path to the temporary file.
    """
    tfp = tempfile.NamedTemporaryFile(delete=True, suffix=suffix)
    filename = os.path.normpath(tfp.name)
    tfp.close()
    return filename


def read_hdd(drive="c:\\", outputfile=None):
    r"""
    Reads HDD (Hard Disk Drive) information from a specified drive and returns it as a pandas DataFrame.

    Args:
        drive (str, optional): The drive path to read from. Default is "c:\\".
        outputfile (str, optional): If provided, the DataFrame will be saved as a Parquet file at this path.
                                   Default is None.

    Returns:
        pd.DataFrame: A DataFrame containing HDD information with the specified columns.

    Raises:
        subprocess.CalledProcessError: If the external command fails to execute.

    Note:
        - This function uses an external command-line utility https://github.com/githubrobbi/Ultra-Fast-File-Search to retrieve HDD information.
        - The DataFrame will have the following columns:
            - aa_path
            - aa_name
            - aa_path_only
            - aa_size
            - aa_size_on_disk
            - aa_created
            - aa_last_written
            - aa_last_accessed
            - aa_descendents
            - aa_read-only
            - aa_archive
            - aa_system
            - aa_hidden
            - aa_offline
            - aa_not_content_indexed_file
            - aa_no_scrub_file
            - aa_integrity
            - aa_pinned
            - aa_unpinned
            - aa_directory_flag
            - aa_compressed
            - aa_encrypted
            - aa_sparse
            - aa_reparse
            - aa_attributes

    Example:
        df = read_hdd(drive="d:\\", outputfile="hdd_info.parquet")
        # Reads HDD information from the 'D:' drive and saves it as 'hdd_info.parquet'.
    """
    csvtmp = get_tmpfile(".csv")
    subprocess.run(
        [
            uffscom,
            f"*",
            f"--drives={str(drive).lstrip()[0].lower()}",
            f"--out={csvtmp}",
            "--header=true",
            "--sep=;",
        ],
        **invisibledict,
    )
    df = pd.read_csv(
        csvtmp,
        sep=";",
        delimiter=None,
        header=None,
        names=[
            "aa_path",
            "aa_name",
            "aa_path_only",
            "aa_size",
            "aa_size_on_disk",
            "aa_created",
            "aa_last_written",
            "aa_last_accessed",
            "aa_descendents",
            "aa_read-only",
            "aa_archive",
            "aa_system",
            "aa_hidden",
            "aa_offline",
            "aa_not_content_indexed_file",
            "aa_no_scrub_file",
            "aa_integrity",
            "aa_pinned",
            "aa_unpinned",
            "aa_directory_flag",
            "aa_compressed",
            "aa_encrypted",
            "aa_sparse",
            "aa_reparse",
            "aa_attributes",
        ],
        index_col=None,
        usecols=None,
        dtype={
            "aa_path": "string[pyarrow]",
            "aa_name": "string[pyarrow]",
            "aa_path_only": "string[pyarrow]",
            "aa_size": "uint64[pyarrow]",
            "aa_size_on_disk": "uint64[pyarrow]",
            "aa_created": "timestamp[s][pyarrow]",
            "aa_last_written": "timestamp[s][pyarrow]",
            "aa_last_accessed": "timestamp[s][pyarrow]",
            "aa_descendents": "uint64[pyarrow]",
            "aa_read-only": "bool[pyarrow]",
            "aa_archive": "bool[pyarrow]",
            "aa_system": "bool[pyarrow]",
            "aa_hidden": "bool[pyarrow]",
            "aa_offline": "bool[pyarrow]",
            "aa_not_content_indexed_file": "bool[pyarrow]",
            "aa_no_scrub_file": "bool[pyarrow]",
            "aa_integrity": "bool[pyarrow]",
            "aa_pinned": "bool[pyarrow]",
            "aa_unpinned": "bool[pyarrow]",
            "aa_directory_flag": "bool[pyarrow]",
            "aa_compressed": "bool[pyarrow]",
            "aa_encrypted": "bool[pyarrow]",
            "aa_sparse": "bool[pyarrow]",
            "aa_reparse": "bool[pyarrow]",
            "aa_attributes": "uint32[pyarrow]",
        },
        engine="pyarrow",
        converters=None,
        true_values=None,
        false_values=None,
        skipinitialspace=False,
        skiprows=2,
        skipfooter=0,
        nrows=None,
        na_values=None,
        keep_default_na=True,
        na_filter=True,
        verbose=False,
        skip_blank_lines=True,
        parse_dates=None,
        # infer_datetime_format=_NoDefault.no_default,
        keep_date_col=False,
        # date_parser=_NoDefault.no_default,
        date_format=None,
        dayfirst=False,
        cache_dates=True,
        iterator=False,
        chunksize=None,
        compression="infer",
        thousands=None,
        decimal=".",
        lineterminator=None,
        quotechar='"',
        quoting=0,
        doublequote=True,
        escapechar=None,
        comment=None,
        encoding="utf-8",
        encoding_errors="backslashreplace",
        dialect=None,
        # on_bad_lines="warn",
        delim_whitespace=False,
        low_memory=True,
        memory_map=False,
        float_precision=None,
        storage_options=None,
        dtype_backend="pyarrow",
    )
    if outputfile:
        touch(outputfile)
        df.to_parquet(outputfile)
    try:
        os.remove(csvtmp)
    except Exception:
        pass
    gc.collect()
    return df


