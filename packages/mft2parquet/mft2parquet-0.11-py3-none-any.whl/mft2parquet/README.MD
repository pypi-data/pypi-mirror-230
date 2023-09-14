# mft to parquet (pyarrow dtypes)

## Tested against Windows 10 / Python 3.11 / Anaconda

### pip install mft2parquet


```python
Reads HDD (Hard Disk Drive) information from a specified drive and returns it as a pandas DataFrame.

Args:
drive (str, optional): The drive path to read from. Default is "c:\\".
outputfile (str, optional): If provided, the DataFrame will be saved as a Parquet file at this path.
					  Default is None.

Returns:
pd.DataFrame: A DataFrame with pyarrow dtypes containing HDD information with the specified columns.

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
```