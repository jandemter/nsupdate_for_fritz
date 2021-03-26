# nsupdate_for_fritz
nsupdate_for_fritz gets the current IPv4 address of your [AVM](https://avm.de/) [FRITZ!Box](https://en.avm.de/products/fritzbox/)
and then uses [BIND's](https://bind.isc.org/) [nsupdate](https://bind9.readthedocs.io/en/latest/manpages.html#nsupdate-dynamic-dns-update-utility)
to update one or more A records with it. It can also do the same for IPv6 addresses (AAAA records) of hosts on your network.

Additionally, sending TXT records, i.e. for Let's Encrypt, is possible.

## Install

### Requirements
nsupdate_for_fritz requires [Python](https://www.python.org) 3.6 or later, the [requests](https://requests.readthedocs.io/)
library (which will be auto-installed if you proceed as below) and nsupdate.

* Debian/Ubuntu: `apt install dnsutils`
* Red Hat/Fedora: `dnf install bind-utils`
* FreeBSD: `pkg install bind-tools python3`

### Global or User install
`cd` to this directory and
either

* `pip install .` for a global install or
  * Previously, you might want to create and activate a virtual environment
    (`python -m venv venv`, `source venv/bin/activate`).
* `pip install --user .` for a user-only install
  * Add `~/.local/bin` to your `PATH` environment variable if you have never used this before

### Via Docker
Run `docker build . --tag nsupdate_for_fritz`

## Configure

### Generate a Key
* `tsig-keygen -a HMAC-SHA512 KEY_NAME_HERE`

(Skip this step if you want to use some existing key.)

### Create a Configuration File

Copy `config.ini.example` to `config.ini`, edit and replace all the all-caps
placeholders with your nameserver, the zone name, the key from the step above etc.

Adjust the `[hosts]` and `[txt]` sections for your network, you can delete
the latter section if you do not need to update any TXT records.

### Configure Your Nameserver

If you are running your own nameserver, the configuration for it should be similar
to this one (the `key` section is the output of `tsig-keygen` step above):

```
key "KEYNAME" {
        algorithm hmac-sha512;
        secret "SOME_SECRET_HERE";
};

zone "test.example.com" {
        type master;
        allow-update {
                key "KEYNAME";
        };
        allow-query { any; };
        file "/usr/local/etc/namedb/dynamic/test.example.com";
};
```

## Run

Run `nsupdate_for_fritz --dry-run config.ini` to test your configuration, then run
`nsupdate_for_fritz config.ini` and add it to your crontab or any other task runner.

If `nsupdate_for_fritz` cannot be found, either try fixing your `PATH` environment
variable or running via `python -m nsupdate_for_fritz` instead.

### Via Docker
```shell
docker run -i localhost/nsupdate_for_fritz --dry-run - < config.ini
docker run -i localhost/nsupdate_for_fritz - < config.ini
```