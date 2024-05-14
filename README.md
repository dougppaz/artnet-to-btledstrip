# artnet-to-btledstrip

Add your Bluetooth LED Strips to your DMX network with Art-Net and the [btledstrip](https://github.com/dougppaz/python-bt-led-strip) Python library

## Usage

1. Install requirements
   ```console
   $ pip install -r requirements.txt
   ```
1. Create the LED Strip config file. Following [example.yml](./example.yml).
1. Run artnet_to_btledstrip module with Art-Net Server and btledstrip integration.
   ```console
   $ python -m artnet_to_btledstrip [led_strip_config_file]
   ```

Help:

```console
$ python -m artnet_to_btledstrip -h
```
