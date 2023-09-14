import shutil
import subprocess
import pandas as pd
import re as regex

netstatexe = shutil.which("netstat.exe")


def get_netstat_ipv4_df():
    r"""
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

    """
    udp = subprocess.run(
        [netstatexe, "-a", "-b", "-n", "-o", "-p", "UDP"], capture_output=True
    )
    tcp = subprocess.run(
        [netstatexe, "-a", "-b", "-n", "-o", "-p", "TCP"], capture_output=True
    )

    udp_stdout = udp.stdout.decode("utf-8", "backslashreplace")
    tcp_stdout = tcp.stdout.decode("utf-8", "backslashreplace")

    df = pd.DataFrame(
        columns=[
            "aa_proto",
            "aa_local_address_and_port",
            "aa_foreign_address_and_port",
            "aa_status",
            "aa_pid",
            "aa_executeable",
        ]
    )
    try:
        df = pd.concat(
            [
                pd.concat(
                    [
                        pd.DataFrame(
                            [
                                g.split(maxsplit=4)
                                for y in x[0].splitlines()
                                if (g := y.strip())
                            ]
                        ).assign(executeable=x[1].strip("[] "))
                    ]
                )
                for x in regex.findall(
                    r"(TCP.*?)(\[.*?\])", tcp_stdout, flags=regex.DOTALL
                )
            ]
        )
        df = df.loc[df[0] == "TCP"].reset_index(drop=True)
        df.columns = [
            "aa_proto",
            "aa_local_address_and_port",
            "aa_foreign_address_and_port",
            "aa_status",
            "aa_pid",
            "aa_executeable",
        ]
    except Exception:
        pass
    df2 = pd.DataFrame(
        columns=[
            "aa_proto",
            "aa_local_address_and_port",
            "aa_foreign_address_and_port",
            "aa_pid",
            "aa_executeable",
            "aa_status",
        ]
    )
    try:
        df2 = pd.concat(
            [
                pd.concat(
                    [
                        pd.DataFrame(
                            [
                                g.split(maxsplit=4)
                                for y in x[0].splitlines()
                                if (g := y.strip())
                            ]
                        ).assign(executeable=x[1].strip("[] "))
                    ]
                )
                for x in regex.findall(
                    r"(UDP.*?)(\[.*?\])", udp_stdout, flags=regex.DOTALL
                )
            ]
        )
        df2 = df2.loc[df2[0] == "UDP"].reset_index(drop=True)
        df2.columns = [
            "aa_proto",
            "aa_local_address_and_port",
            "aa_foreign_address_and_port",
            "aa_pid",
            "aa_executeable",
            "aa_status",
        ]
    except Exception:
        pass
    df = pd.concat([df, df2], ignore_index=True, axis=0)
    df = pd.concat(
        [
            df,
            df.aa_local_address_and_port.str.extractall(
                r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)"
            )
            .reset_index(drop=True)
            .rename(columns={0: "aa_local_address", 1: "aa_local_port"}),
        ],
        axis=1,
    )
    df = pd.concat(
        [
            df,
            df.aa_foreign_address_and_port.str.extractall(
                r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)"
            )
            .reset_index(drop=True)
            .rename(columns={0: "aa_foreign_address", 1: "aa_foreign_port"}),
        ],
        axis=1,
    )
    df.aa_pid = df.aa_pid.astype("Int64")
    df.aa_local_port = df.aa_local_port.astype("Int64")
    df.aa_foreign_port = df.aa_foreign_port.astype("Int64")
    df = df.fillna(pd.NA)

    return df


