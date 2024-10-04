# akamai-linode CLI

## Getting started

Create a READ-ONLY API Token in Cloud Manager.
Create an INI configuration file (by default we use `~/.edgerc`)

```INI
[default]
; Linode integration credentials
linode_hostname = api.linode.com  # Do not prepend https://
linode_token = XXXXXXXXXXXX       # Read-only permission suffices
```

Please make sure you enter the hostname **without** any scheme (`http://` or `https://`)


## Usage

### Audit logs
Setup the .edgerc file as described [here](#authentication)
```bash
akamai-linode events audit --follow
```

### Objects utilization
```
akamai-linode utilization --follow
```

In follow mode, it will print the different counters by object type from your account.  
Example:
```json
{
    "time": "2024-10-03T18:40:25.164050+00:00", 
    "account": "My company name", 
    "linode": 25, 
    "lke_cluster": 0, 
    "vpc": 1, 
    "vlan": 0, 
    "cloud_firewall": 2, 
    "node_balancer": 0, 
    "object_storage": 0, 
    "volume": 2,
    "stackscript": 12
}
```

Note the last counter, `stackscript` will be reported only when using `--include-stackscripts` argument is added to the command line.

To send these events into your SIEM, please checkout [Akamai Unified Log Streamer](https://github.com/akamai/uls)
