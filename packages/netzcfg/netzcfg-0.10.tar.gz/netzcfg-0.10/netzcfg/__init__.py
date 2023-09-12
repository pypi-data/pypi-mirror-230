import wmi
import pandas as pd

def get_nic_info(ipenabled=False):
    r"""
    Retrieve network adapter configuration information using Windows Management Instrumentation (WMI) and return it as a Pandas DataFrame.

    Parameters:
    - ipenabled (bool, optional): If True, filter network adapters by those with IP enabled (default is False).

    Returns:
    - pd.DataFrame: A DataFrame containing network adapter configuration information, with columns:
      - Configuration parameter names (e.g., 'SettingID', 'IPAddress', 'SubnetMask', etc.).
      - Values associated with each configuration parameter.

    Example:
    >>> nic_info = get_nic_info(ipenabled=True)
    >>> print(nic_info.head())
       SettingID IPAddress      SubnetMask      DefaultIPGateway
    0    {GUID}   192.168.1.2  255.255.255.0  192.168.1.1
    1    {GUID}   10.0.0.2    255.255.255.0  10.0.0.1
    ...
    """
    c = wmi.WMI()
    alldata = []
    for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=ipenabled):
        alldata.append([])
        for q in [(x, getattr(nic, x)) for x in list(nic.__dict__["_properties"])]:
            alldata[-1].append(q)
    df = pd.DataFrame(alldata)
    df.columns = [x[0] for x in df.iloc[:1].__array__().flatten()]
    for col in df.columns:
        df[col] = df[col].str[-1]

    return df
