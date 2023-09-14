# Windows firewall rules to Pandas DataFrame

## Tested against Windows 10 / Python 3.10 / Anaconda

### pip install firewall2df


```python
from firewall2df import firewallrules2df
df = firewallrules2df()
             RuleName Direction   Profiles Protocol LocalIP                LocalPort RemoteIP               RemotePort Action    ActiveProfiles
0    RuleName: Core NetServices     Allow     Any     Any                       Any      Any                    Any  Allow       Domain,Private,Public
1  RuleName: Core System          Allow     Any     Any                       Any      Any                    Any  Allow       Domain,Private,Public
2  RuleName: DNS (UDP-Out)        Allow     Any     UDP     Any                53:53      Any                    Any  Allow             Domain,Private
3  RuleName: DHCP (UDP-In)        Allow     Any     UDP  67:67                 Any                       Any  Allow             Domain,Private
4    RuleName: DHCP (UDP-Out)     Allow     Any     UDP     Any                68:68      Any                    Any  Allow             Domain,Private


```