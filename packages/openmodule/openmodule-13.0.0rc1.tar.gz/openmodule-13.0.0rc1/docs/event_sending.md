# Event sending

To send an event in correct format to the eventlog, just use the `send_event` function. Create the event infos, use the 
`EventInfo.create` function

```python
send_event(EventInfo.create("test_1", license_plate="G ARIVO 1"), "LPR {lpr}", lpr=MessageKwarg.lpr("G ARIVO 1"))
```
