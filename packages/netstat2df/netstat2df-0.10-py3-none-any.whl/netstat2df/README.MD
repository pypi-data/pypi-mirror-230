# Retrieves and parses network statistics related to IPv4 TCP and UDP connection returns this information as a Pandas DataFrame

## Tested against Windows 10 / Python 3.10 / Anaconda

### pip install netstat2df


```python
Retrieve and parse network statistics related to IPv4 TCP and UDP connections.

This function uses the 'netstat' command-line utility to gather information about
IPv4 TCP and UDP connections, including local and foreign addresses, ports, process
IDs (PIDs), and executable names. It then processes and returns this information
as a Pandas DataFrame.

Returns:
	pd.DataFrame: A DataFrame containing the following columns:
		- 'aa_proto': Protocol type ('TCP' or 'UDP').
		- 'aa_local_address': Local IP address.
		- 'aa_local_port': Local port number.
		- 'aa_foreign_address': Foreign IP address.
		- 'aa_foreign_port': Foreign port number.
		- 'aa_pid': Process ID (PID) of the associated process.
		- 'aa_executable': Executable name of the associated process.
		- 'aa_status': Status of the connection (may be empty or NaN if unavailable).

Note:
	- If any error occurs during the retrieval or parsing of network statistics,
	  the function returns an empty DataFrame.

Example:
	>>> from netstat2df import get_netstat_ipv4_df
	>>> df = get_netstat_ipv4_df()
	>>> print(df.head())

```