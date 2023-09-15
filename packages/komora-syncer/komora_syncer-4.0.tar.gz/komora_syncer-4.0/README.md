Netbox and Komora synchronizer
===

`komora_syncer` is a tool to synchronize data between Komora and Netbox application 

Installation
------------
- `git clone` this repository
- `pip install .`
- setup configuration files config.yml
   - paths: 
      - ~/.config/komora_syncer/
      - /etc/komora_syncer/config.yml
      - Or can be set with the env variable `CONFIG_FOLDER_PATH`. Example: `CONFIG_FOLDER_PATH=~/NETBOX/netbox_komora_syncer/configurations/ komora_syncer  synchronize`


Run
---

- `komora_syncer`

komora_syncer requires at least Python 3.6.
