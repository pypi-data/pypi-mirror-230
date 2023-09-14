import shutil
import subprocess
import re
import pandas as pd

netshexe = shutil.which("netsh")


def firewallrules2df():
    r"""
    firewallrules2df - Extract and format Windows Firewall rules into a pandas DataFrame.

    This function uses the 'netsh' command to retrieve information about Windows Firewall rules
    and then processes and converts it into a pandas DataFrame.

    Returns:
        pd.DataFrame: A DataFrame containing information about Windows Firewall rules.

    Example:
        >>> from firewall2df import firewallrules2df
        >>> df = firewallrules2df()

                     RuleName Direction   Profiles Protocol LocalIP                LocalPort RemoteIP               RemotePort Action    ActiveProfiles
        0    RuleName: Core NetServices     Allow     Any     Any                       Any      Any                    Any  Allow       Domain,Private,Public
        1  RuleName: Core System          Allow     Any     Any                       Any      Any                    Any  Allow       Domain,Private,Public
        2  RuleName: DNS (UDP-Out)        Allow     Any     UDP     Any                53:53      Any                    Any  Allow             Domain,Private
        3  RuleName: DHCP (UDP-In)        Allow     Any     UDP  67:67                 Any                       Any  Allow             Domain,Private
        4    RuleName: DHCP (UDP-Out)     Allow     Any     UDP     Any                68:68      Any                    Any  Allow             Domain,Private

    Note:
        - This function relies on the 'netsh' command being available on the system.
        - The returned DataFrame will have columns such as 'RuleName', 'Direction', 'Profiles',
          'Protocol', 'LocalIP', 'LocalPort', 'RemoteIP', 'RemotePort', 'Action', and 'ActiveProfiles'.
        - If a rule attribute is not available, it will be filled with 'pd.NA' (pandas' missing data indicator).
        - Make sure to run this function with appropriate permissions as it accesses Windows Firewall settings.

    """
    p = subprocess.run(
        [netshexe, "advfirewall", "firewall", "show", "rule", "name=all"],
        capture_output=True,
    )
    decoded = p.stdout.decode("utf-8", "backslashreplace")
    sp = re.split(r"^Rule\s+Name:", decoded, flags=re.MULTILINE)
    stri = [[y for y in x.splitlines() if y.strip("- ")] for x in sp]
    stri = [x for x in stri if len(x) > 2]
    for s in range(len(stri)):
        stri[s][0] = f"RuleName: {stri[s][0]}"
    df = pd.concat(
        [
            pd.DataFrame(p)
            .rename(columns={0: "aa_cat", 1: "aa_data"})
            .assign(
                aa_cat=lambda x: x["aa_cat"].str.strip(),
                aa_data=lambda x: x["aa_data"].str.strip(),
            )
            .set_index("aa_cat")
            .T
            for p in ([y.split(":", maxsplit=1) for y in x if ":" in y] for x in stri)
        ],
        axis=0,
        ignore_index=True,
    ).fillna(pd.NA)
    return df
