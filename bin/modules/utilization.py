import datetime
import json
import requests
import threading
import time

import modules.aka_log as aka_log
import ln_config.default_config as default_config

#follow_interval_sec = default_config.utilization_loop_time

class linode_count(object):

    LINODE_API = 'https://api.linode.com/v4'

    def __init__(self, api_headers):
        self.api_headers = api_headers

    def instances(self):
        resp_instances = requests.get(f'{linode_count.LINODE_API}/linode/instances', headers=self.api_headers)
        return resp_instances.json().get('results')

    def lkes(self):
        resp_lkes = requests.get(f'{linode_count.LINODE_API}/lke/clusters', headers=self.api_headers)
        return resp_lkes.json().get('results')

    def vpcs(self):
        resp_vpcs = requests.get(f'{linode_count.LINODE_API}/vpcs', headers=self.api_headers)
        return resp_vpcs.json().get('results')

    def vlans(self):
        resp_vlans = requests.get(f'{linode_count.LINODE_API}/networking/vlans', headers=self.api_headers)
        return resp_vlans.json().get('results')

    def cloudfws(self):
        resp_cloudfws = requests.get(f'{linode_count.LINODE_API}/networking/firewalls', headers=self.api_headers)
        return resp_cloudfws.json().get('results')

    def nodebalancers(self):
        resp_nbs = requests.get(f'{linode_count.LINODE_API}/nodebalancers', headers=self.api_headers)
        return resp_nbs.json().get('results')
    
    def object_storage(self):
        resp_os = requests.get(f'{linode_count.LINODE_API}/object-storage/buckets', headers=self.api_headers)
        return resp_os.json().get('results')

    def stackscripts(self):
        page_size = 500 # Reduce chances to get HTTP/429 too many requests
        resp_ss = requests.get(f'{linode_count.LINODE_API}/linode/stackscripts', params={'page_size': page_size}, headers=self.api_headers)
        if resp_ss.status_code != 200:
            aka_log.log.warning(f"HTTP/{resp_ss.status_code} {resp_ss.url}")
            aka_log.log.warning(resp_ss.text)
            return None
        total = 0
        for script in resp_ss.json().get('data'):
            if script.get('mine') is True:
                total += 1

        if resp_ss.json().get('pages') == 1:
            return total
        else:
            # We receive all Stackscript, including the one shared from other Linode customers
            for extra_page in range(resp_ss.json().get('pages')-1):
                page_num = extra_page + 1
                resp_page_ss = requests.get(f'{linode_count.LINODE_API}/linode/stackscripts', params={'page_size': page_size, 'page': page_num}, headers=self.api_headers)
                if resp_page_ss.status_code == 200:
                    for script in resp_page_ss.json().get('data', []):
                        if script.get('mine') is True:
                            total += 1
                else:
                    aka_log.log.warning(f"HTTP/{resp_page_ss.status_code} {resp_page_ss.url}")
                    aka_log.log.warning(resp_page_ss.text)
        return total

    def volumes(self):
        resp_volumes = requests.get(f'{linode_count.LINODE_API}/volumes', headers=self.api_headers)
        return resp_volumes.json().get('results')


def stats_one(ln_edgerc, stackscripts: bool = False):

    linode_api_headers = {
        'Authorization': 'Bearer ' + ln_edgerc['linode_token'],
    }

    account_info = requests.get('https://api.linode.com/v4/account', headers=linode_api_headers)
    company = account_info.json().get('company')

    c = linode_count(linode_api_headers)

    info = {
        # for consistency, keep key as a singular word
        "time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "account": company,
        "linode": c.instances(),
        "lke_cluster": c.lkes(),
        "vpc": c.vpcs(),
        "vlan": c.vlans(),
        "cloud_firewall": c.cloudfws(),
        "node_balancer": c.nodebalancers(),
        "object_storage": c.object_storage(),
        "volume": c.volumes(),
    }
    if stackscripts:
        info["stackscript"] = c.stackscripts()

    print(json.dumps(info), flush=True) # Flush to allow process pipelining like ULS


def stats(ln_edgerc, stackscript: bool=False, follow=False, stop_event: threading.Event=None, follow_interval_sec=default_config.utilization_loop_time):
    if follow and stop_event:
        while not stop_event.is_set():
            tick = time.time()
            stats_one(ln_edgerc, stackscript)
            stop_event.wait(follow_interval_sec - (time.time() - tick))
    else:
        stats_one(ln_edgerc, stackscript)
