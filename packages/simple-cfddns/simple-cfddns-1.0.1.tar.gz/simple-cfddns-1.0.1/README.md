# simple cfddns

A simple that conviently set up a DDNS service based on Cloudflare.

## install 

```
pip3 install simple-cfddns
```

## usage

**update** a record, or create if not exist:

``` bash
cfddns \
    -z <zone_id>\
    -t <token>\
    -n example-ddns.yourdomain\
    update
```

**list** all records on a domain:

``` bash
cfddns \
    -z <zone_id>\
    -t <token>\
    -n example-ddns.yourdomain\
    list
```

**delete** all records on a domain:
``` bash
cfddns \
    -z <zone_id> \
    -t <token> \
    -n example-ddns.yourdomain \
    delete
```

## run as a systemd service

In general, we want this program to run periodically and automatically restart in the event of 
any exception. To achieve this, we can install "simple-cfddns" as a systemd service.

**install** a new cfddns service:

``` bash
prog=$(which cfddns)
sudo $prog \
    -z <zone_id> \
    -t <token> \
    -n example-ddns.yourdomain \
    install default
```

this will create a service with name "cfddns-default". you can create 
multiple cfddns services given that they have different names.

then, start and enable it:

``` bash 
sudo systemctl start cfddns-default
sudo systemctl enable cfddns-default
```

**list** all cfddns services

``` bash
cfddns services
```

**uninstall** a service

``` bash
prog=$(which cfddns)
sudo $prog uninstall default
```