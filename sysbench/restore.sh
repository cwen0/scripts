#!/bin/bash
ansible-playbook stop.yml
ansible -i inventory.ini tikv_servers -m shell -a "cd /tmp/tidb/deploy/; rm -rf data; cp -R data.bak data"
ansible -i inventory.ini pd_servers -m shell -a "cd /tmp/tidb/deploy/; rm -rf data.pd; cp -R datapd.bak data.pd"
ansible-playbook start.yml
