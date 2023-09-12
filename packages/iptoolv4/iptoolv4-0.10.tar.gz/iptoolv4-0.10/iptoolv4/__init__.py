from disable_warnings import *
import io
import os
import subprocess
from functools import partial
from math import ceil
import pandas as pd
import numpy as np
import numexpr
import touchtouch
from PrettyColorPrinter import add_printer
from getpublicipv4 import get_ip_of_this_pc
from regex import regex
import re
import gc
from cprinter import TC
from umacajadada import read_async


add_printer(1)
flags = regex.I
firstfilter = regex.compile(
    rb"\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b",
    flags=flags,
)
firstfilterdf = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b",
    flags=flags,
)
int_array = np.frompyfunc(int, 2, 1)

print("Getting public IPv4 address of this PC...")
while True:
    thisip = get_ip_of_this_pc()
    if firstfilterdf.match(thisip):
        break
print('Done!')

def decode_backspace(x):
    return x.decode("utf-8", errors="backslashreplace")


def blackred(x, n=False):
    if n:
        return ""
    if str(x).startswith("aa_") or str(x).startswith("bb_"):
        x = x[3:]
    return f"{TC(str(x)).bg_black.fg_red}"


def blackcyan(x, n=False):
    if n:
        return ""
    return f"{TC(str(x)).bg_black.fg_cyan}"


def blackgreen(x, n=False):
    if n:
        return ""
    return f"{TC(str(x)).bg_black.fg_green}"


def blackyellow(x, n=False):
    if n:
        return ""
    return f"{TC(str(x)).bg_black.fg_yellow}"


def blackblue(x, n=False):
    if n:
        return ""
    return f"{TC(str(x)).bg_black.fg_blue}"


def greenblack(x, n=False):
    if n:
        return ""
    return f"{TC(str(x)).bg_green.fg_black}"


def cyanblack(x, n=False):
    if n:
        return ""
    return f"{TC(str(x)).bg_cyan.fg_black}"


def blackwhite(x, n=False):
    if n:
        return ""
    return f"{TC(str(x)).bg_black.fg_white}"


def redblack(x, n=False):
    if n:
        return ""
    return f"{TC(str(x)).bg_red.fg_black}"


def print_colored_console_output(wantedcols, omit_columns, j, i):
    return (
        (
            (
                (suba := j.iloc[:1][[t for t in j.columns if t in wantedcols]]),
                " ".join(
                    [
                        f'{blackred(x,omit_columns)}{blackcyan(":")}{blackgreen((suba[x].iloc[0]))}{blackcyan(":")}'
                        for x in suba.columns
                        if x in wantedcols
                    ]
                ),
            )[-1]
            + f" {blackyellow(decode_backspace(i))} "
        )
        .encode("utf-8", "backslashreplace")
        .replace(b"\n", b" ")
        .replace(b"\r", b"")
    )


def check_file(file, concurrent=True, return_string=False):
    resturn_string_list = []
    abspos = 0
    files = []
    allabspos = []
    qstarts = []
    qends = []
    ips = []
    co = 0

    if isinstance(file, str):
        if os.path.exists(file):
            f = open(file, mode="rb")
        else:
            file = file.encode("utf-8", "backslashreplace")
    if isinstance(file, bytes):
        f = io.BytesIO()
        f.write(file)
        f.seek(0)
    while data := f.readline():
        data = data.replace(b"\xe2", b"")
        data = data.replace(b"\x80", b"")

        for q in firstfilter.finditer(data, concurrent=concurrent, partial=False):
            files.append(
                file,
            )
            allabspos.append(
                co,
            )

            qstarts.append(
                q.start() + abspos,
            )
            qends.append(
                q.end() + abspos,
            )
            ips.append(
                (q.group(0)),
            )
        abspos += len(data)
        if return_string:
            resturn_string_list.append(data)
        co += 1
    f.close()
    df = pd.concat(
        [
            pd.Series(x[0], dtype=x[1])
            for x in (
                (files, "string"),
                (allabspos, np.uint32),
                (qstarts, np.uint64),
                (qends, np.uint64),
                (ips, "S"),
            )
        ],
        axis=1,
        ignore_index=True,
        copy=False,
    ).rename(
        columns={
            0: "aa_file",
            1: "aa_line",
            2: "aa_starts",
            3: "aa_ends",
            4: "aa_ip",
        }
    )
    oara = np.asarray(
        [
            int_array(q, 10)
            for q in np.char.array(df.aa_ip.__array__().astype("S")).split(b".")
        ],
        dtype=np.int64,
    )
    df["aa_ip_asint"] = numexpr.evaluate(
        "(maxip0 << 24) + (maxip1 << 16) + (maxip2 << 8) + (maxip3)",
        global_dict={},
        local_dict={
            "maxip0": oara[..., 0],
            "maxip1": oara[..., 1],
            "maxip2": oara[..., 2],
            "maxip3": oara[..., 3],
        },
    )
    foundips = df["aa_ip_asint"].unique()

    return df, foundips, resturn_string_list


def get_ip_df(df2, start="aa_startip", end="aa_endip"):
    if isinstance(df2, str):
        df2 = pd.read_pickle(df2)
    elif isinstance(df2, list):
        if not isinstance(df2[0], (list, tuple, np.ndarray)):
            df2 = [df2]
        df2 = pd.DataFrame(df2)
        df2.columns = [start, end]
    df2 = df2.loc[
        df2[start].str.match(firstfilterdf) & df2[end].str.match(firstfilterdf)
    ].reset_index(
        drop=True,
    )

    ipstarts = (
        df2[start]
        .str.split(".", regex=False, expand=True)
        .rename(columns={0: "ips_0", 1: "ips_1", 2: "ips_2", 3: "ips_3"})
    )
    ipends = (
        df2[end]
        .str.split(".", regex=False, expand=True)
        .rename(columns={0: "ips_0", 1: "ips_1", 2: "ips_2", 3: "ips_3"})
    )

    for key, item in {0: "ips_0", 1: "ips_1", 2: "ips_2", 3: "ips_3"}.items():
        ipstarts.loc[:, item] = ipstarts[item].astype(np.int64)
        ipends.loc[:, item] = ipends[item].astype(np.int64)
    df2[f"aa_startip_int"] = numexpr.evaluate(
        "(maxip0 << 24) + (maxip1 << 16) + (maxip2 << 8) + (maxip3)",
        global_dict={},
        local_dict={
            "maxip0": ipstarts.__array__()[..., 0].astype(np.int64),
            "maxip1": ipstarts.__array__()[..., 1].astype(np.int64),
            "maxip2": ipstarts.__array__()[..., 2].astype(np.int64),
            "maxip3": ipstarts.__array__()[..., 3].astype(np.int64),
        },
    )
    df2[f"aa_endip_int"] = numexpr.evaluate(
        "(maxip0 << 24) + (maxip1 << 16) + (maxip2 << 8) + (maxip3)",
        global_dict={},
        local_dict={
            "maxip0": ipends.__array__()[..., 0].astype(np.int64),
            "maxip1": ipends.__array__()[..., 1].astype(np.int64),
            "maxip2": ipends.__array__()[..., 2].astype(np.int64),
            "maxip3": ipends.__array__()[..., 3].astype(np.int64),
        },
    )
    return df2


def _subs_function(function, data3, result3):
    a = np.frombuffer(bytearray(b"".join(data3)), dtype="S1")
    stali = result3.bb_starts.to_list()
    endli = result3.bb_ends.to_list()
    splitlist = sorted(stali + endli)
    if splitlist[0] != 0:
        splitlist.insert(0, 0)
    if splitlist[-1] != a.shape[0] - 1:
        splitlist.append(a.shape[0])
    allen = 0
    aspi = np.split(a, splitlist)
    allnewlines = []
    for axa in aspi:
        orig = b"".join(axa)
        if allen in stali:
            result3df = result3.loc[result3.bb_starts == allen]
            nli = function(result3df, orig)
            allnewlines.append(nli)
        else:
            allnewlines.append(orig)
        allen = allen + len(orig)
    return (
        b" ".join(allnewlines)
        .replace(b"127.0.0.1", cyanblack("127.0.0.1").encode("utf-8"))
        .replace(thisip.encode("utf-8"), greenblack(thisip).encode("utf-8"))
    )


def get_valid_ips(df, df2, foundips, chunks=30000):
    foundips = np.ascontiguousarray(foundips)
    allresults = []
    dfcolsb = {x: "bb_" + x[3:] for x in df.columns}
    for df3 in np.array_split(df2, ceil(len(df2) / chunks)):
        df3.index = np.arange(len(df3), dtype=np.uint32)
        stristri = np.lib.stride_tricks.as_strided(
            foundips, (len(foundips), len(df3)), (foundips.itemsize, 0)
        )
        nonz = np.nonzero(
            numexpr.evaluate(
                "(stacked_view>=aa_startip_int) & (stacked_view<=aa_endip_int)",
                local_dict={
                    "stacked_view": stristri,
                    "aa_startip_int": df3[f"aa_startip_int"].__array__(),
                    "aa_endip_int": df3[f"aa_endip_int"].__array__(),
                },
                global_dict={},
            )
        )

        try:
            if len(nonz[0]) > 0:
                df3 = (
                    df3.loc[np.unique(df3.index[nonz[1]])]
                    .loc[nonz[1]]
                    .assign(aa_match=nonz[0])
                ).reset_index(drop=True)
                cte = foundips[df3.aa_match]
                df3["aa_got_match"] = cte
                # df5 =
                df6 = pd.merge(
                    df3,
                    (
                        df.query("aa_ip_asint in @cte")
                        .rename(columns=dfcolsb)
                        .reset_index(drop=True)
                    ),
                    left_on="aa_got_match",
                    right_on="bb_ip_asint",
                    copy=False,
                )
                df6.drop(
                    columns=[
                        r
                        for r in ["aa_got_match", "bb_ip_cpy", "bb_singcol"]
                        if r in df6.columns
                    ],
                    inplace=True,
                )
                allresults.append(df6)
            gc.collect()

        except Exception:
            continue
    try:
        dfxx = pd.concat(allresults, ignore_index=True, copy=False)
        dfxx.loc[:, "bb_ip"] = dfxx.bb_ip.str.decode("utf-8")
        return dfxx
    except Exception:
        return pd.DataFrame()


class IpV4Tool:
    r"""
    IpV4Tool is a class for working with IPv4 addresses and IP-related data.

    It provides methods for loading, saving, and searching for IPv4 addresses in text data,
    as well as observing log files and subprocess output for IP-related information.

    Args:
    hide_my_ip (bool): If True, the tool will hide localhost and the local machine's IP address
                      when searching for IP addresses.

    Attributes:
    df (pd.DataFrame): A DataFrame containing the IPv4 address ranges to search for.
    myips (list): A list of IP addresses to hide when searching for IP addresses.
    hide_my_ip (bool): Indicates whether to hide localhost and the local machine's IP address.

    Methods:
    - load_wanted_ips(ips, start="aa_startip", end="aa_endip"): Load IPv4 address ranges from a file or DataFrame.
    - save_wanted_ips(path): Save the loaded IPv4 address ranges to a file.
    - search_for_ip_addresses(path_string_bytes, chunks=1000000, concurrent=True, substitute=None):
      Search for IPv4 addresses in text data and optionally substitute them with custom formatting.
    - observe_log_file(file_path, min_len=5, columns=(), print_df=True, omit_columns=True):
      Observe a log file for IPv4 addresses and related information.
    - observe_subprocess(cmdline, min_len=5, columns=(), print_df=True, omit_columns=True, **kwargs):
      Observe subprocess output for IPv4 addresses and related information.

    Example usage:
    >>> self = IpV4Tool(hide_my_ip=True)
    >>> self.load_wanted_ips("ipv4_ranges.pkl", start="aa_startip", end="aa_endip")
    >>> self.search_for_ip_addresses("log.txt", chunks=1000000, concurrent=True)
    >>> self.observe_log_file("logfile.txt", min_len=5, columns=("aa_country", "aa_city"), print_df=False)
    >>> self.observe_subprocess("netstat -b 1", min_len=5, columns=("aa_country", "aa_city"), print_df=False, shell=True)
    """

    def __init__(self, hide_my_ip=True):
        self.df = pd.DataFrame()
        self.myips = []
        self.hide_my_ip = hide_my_ip
        if hide_my_ip:
            self.myips.append(thisip)
            self.myips.append("127.0.0.1")

    def load_wanted_ips(self, ips, start="aa_startip", end="aa_endip"):
        r"""
        Load IPv4 address ranges from a file or DataFrame.

        Args:
        ips (str, pd.DataFrame): The file path or DataFrame containing the IPv4 address ranges.
        start (str): The name of the start IP column in the DataFrame.
        end (str): The name of the end IP column in the DataFrame.

        Returns:
        IpV4Tool: The IpV4Tool instance with loaded IPv4 address ranges.
        """
        if isinstance(ips, str):
            try:
                if os.path.exists(ips):
                    ips = pd.read_pickle(ips)
            except Exception:
                pass
        if isinstance(ips, pd.DataFrame):
            if "aa_startip_int" in ips.columns and "aa_endip_int" in ips.columns:
                self.df = ips
                return self

        self.df = get_ip_df(ips, start=start, end=end)
        return self

    def save_wanted_ips(self, path):
        r"""
        Save the loaded IPv4 address ranges to a file.

        Args:
        path (str): The file path to save the IPv4 address ranges.

        Returns:
        IpV4Tool: The IpV4Tool instance.
        """
        touchtouch.touch(path)
        self.df.to_pickle(path)
        return self

    def search_for_ip_addresses(
        self, path_string_bytes, chunks=1000000, concurrent=True, substitute=None
    ):
        r"""
        Search for IPv4 addresses in text data and optionally substitute them with custom formatting.

        Args:
        path_string_bytes (str): The path to the text data file.
        chunks (int): The chunk size for processing the data.
        concurrent (bool): Whether to perform concurrent searching.
        substitute (callable): A custom substitution function for formatting found IPv4 addresses.

        Returns:
        pd.DataFrame: A DataFrame containing found IPv4 addresses and related information.
        bytes: Substituted text data with formatted IPv4 addresses.
        """
        substitutestring = b""
        df, foundips, resturn_string_list = check_file(
            path_string_bytes,
            concurrent=concurrent,
            return_string=True if substitute else False,
        )

        if self.hide_my_ip:
            df = df.loc[~df.aa_ip.isin(self.myips),].reset_index(drop=True)
            foundips = [x for x in foundips if x not in self.myips]
        df3 = get_valid_ips(df, self.df, foundips, chunks=chunks)
        if self.hide_my_ip:
            df3 = df3.loc[~df3.bb_ip.isin(self.myips),].reset_index(drop=True)
        if substitute and not df3.empty:
            substitutestring = _subs_function(substitute, resturn_string_list, df3)
        return df3, substitutestring

    def observe_log_file(
        self,
        file_path,
        min_len=5,
        columns=(),
        print_df=True,
        omit_columns=True,
        chunks=30000,
        concurrent=True,
    ):
        r"""
        Observe a log file for IPv4 addresses and related information.

        Args:
        file_path (str): The path to the log file.
        min_len (int): Minimum length of lines to process.
        columns (tuple): A tuple of column names to include in the DataFrame.
        print_df (bool): Whether to print the DataFrame with found IPv4 addresses.
        omit_columns (bool): Whether to omit certain columns in the output.
        chunks (int): The chunk size for processing the data.
        concurrent (bool): Whether to perform concurrent searching.
        Returns:
        None
        """
        wantedcols = list(columns)
        subsfu = partial(print_colored_console_output, wantedcols, omit_columns)

        newfile = file_path
        stoptrigger = [
            False,
        ]
        allines = []
        t = read_async(
            file=newfile,
            asthread=True,
            mode="r",
            action=lambda line: allines.append(line),
            stoptrigger=stoptrigger,
        )
        try:
            while True:
                lenalli = len(allines)
                if lenalli > min_len:
                    data4 = "".join([allines.pop(0) for x in range(lenalli)]).encode(
                        "utf-8", "backslashreplace"
                    )
                    result4, substitutestring4 = self.search_for_ip_addresses(
                        path_string_bytes=data4,
                        chunks=chunks,
                        concurrent=concurrent,
                        substitute=subsfu,
                    )
                    if print_df:
                        print(result4)
                    if wantedcols:
                        for y in substitutestring4.splitlines():
                            y = y.strip()
                            if y:
                                print(y.decode("utf-8", errors="backslashreplace"))
        except KeyboardInterrupt:
            pass
        return t

    def observe_subprocess(
        obj,
        cmdline,
        min_len=5,
        columns=(),
        print_df=True,
        omit_columns=True,
        chunks=30000,
        concurrent=True,
        **kwargs,
    ):
        r"""Observe subprocess output for IPv4 addresses and related information.

        Args:
        cmdline (str): The command line to execute as a subprocess.
        min_len (int): Minimum length of lines to process.
        columns (tuple): A tuple of column names to include in the DataFrame.
        print_df (bool): Whether to print the DataFrame with found IPv4 addresses.
        omit_columns (bool): Whether to omit certain columns in the output.
        chunks (int): The chunk size for processing the data.
        concurrent (bool): Whether to perform concurrent searching.
        **kwargs: Additional keyword arguments to pass to subprocess.Popen.

        Returns:
        subprocess.Popen: The subprocess instance.
        ""\" """
        wantedcols = list(columns)
        subsfu = partial(print_colored_console_output, wantedcols, omit_columns)
        kwargs.update({"stdout": subprocess.PIPE})
        p = subprocess.Popen(cmdline, **kwargs)
        allines = []
        try:
            for rline in iter(p.stdout.readline, b""):
                allines.append(rline)
                lenalli = len(allines)
                if lenalli > min_len:
                    data4 = b"".join([allines.pop(0) for x in range((lenalli))])
                    result4, substitutestring4 = obj.search_for_ip_addresses(
                        path_string_bytes=data4,
                        chunks=chunks,
                        concurrent=concurrent,
                        substitute=subsfu,
                    )
                    if print_df:
                        print(result4)
                    if wantedcols:
                        for y in substitutestring4.splitlines():
                            y = y.strip()
                            if y:
                                print(y.decode("utf-8", errors="backslashreplace"))
        except KeyboardInterrupt:
            pass
        return p
