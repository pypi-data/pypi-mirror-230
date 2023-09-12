# Retrieves network adapter configuration information using Windows Management Instrumentation (WMI) and return it as a Pandas DataFrame.

## Tested against Windows 10 / Python 3.10 / Anaconda

### pip install netzcfg


```python
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

```