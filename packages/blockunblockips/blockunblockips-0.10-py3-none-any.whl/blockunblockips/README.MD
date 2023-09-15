# Block / unblock ips using the Windows Firewall 

## Tested against Windows 10 / Python 3.11 / Anaconda

### pip install blockunblockips


```python
from blockunblockips import unblock_out, unblock_in, block_out, block_in

# Example 1: Unblock outgoing traffic to a specific IP address
ip_to_unblock = "192.168.1.100"
unblock_out(ip_to_unblock)
# This will delete a Windows Firewall rule that allows outgoing traffic to IP 192.168.1.100.

# Example 2: Unblock incoming traffic from a specific IP address
ip_to_unblock = "10.0.0.5"
unblock_in(ip_to_unblock)
# This will delete a Windows Firewall rule that allows incoming traffic from IP 10.0.0.5.

# Example 3: Block outgoing traffic to a specific IP address
ip_to_block = "203.0.113.25"
block_out(ip_to_block)
# This will create a Windows Firewall rule to block outgoing traffic to IP 203.0.113.25.

# Example 4: Block incoming traffic from a specific IP address
ip_to_block = "172.16.0.50"
block_in(ip_to_block)
# This will create a Windows Firewall rule to block incoming traffic from IP 172.16.0.50.

```