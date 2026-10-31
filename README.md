# pymilight

This package provides packet parsing/creation for the protocol needed to talk to  Milight/LimitlessLED lights.

It leverages the awesome work of [Chris Mullin's esp8266_milight_hub](https://github.com/sidoh/esp8266_milight_hub) which
in turn leverages [Henryk Plötz's awesome reverse-engineering work](https://hackaday.io/project/5888-reverse-engineering-the-milight-on-air-protocol).

## Why split this out

Splitting the packet handling out was initially motivate by wanting to run a gateway as an ethernet/RF gateway
rather than WIFI/RF. The simplest way of doing that for me is on a Raspberry Pi, hooked up to a NRF24L01.

This is the first step in that journey with the next steps getting the RF part sending the commands from this
package along with a web application and MQTT integration similar to esp8266_milight_hub.


## Getting started

1. Get a Python environment going on Linux (`pyrf24` doesn't support macOS or Windows).
1. Install the package and its test dependencies (this is really for developement use at the moment... watch this space):
```
pip install -e ".[test]"
```
1. Run the tests:
```
python -m pytest tests
```
