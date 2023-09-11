
pydevmgr package dedicated for generic client communication with OPC-UA. 

The documentation is in progress. 

One may be interested to higher level package such as 
- [pydevmgr_elt](https://github.com/efisoft-elt/pydevmgr_elt)


Python package to by used as substitute of a real device manager running in a ELT-Software environment when the full ELT-Software environment cannot be used. 



Sources are [here](https://github.com/efisoft-elt/pydevmgr_ua)


# Install

```bash
> pip install pydevmgr_ua
```

# Basic Usage



```python
from pydevmgr_ua import UaRpc, UaNode, UaCom
from pydevmgr_core.nodes import InsideInterval
import time 

com = UaCom(address="opc.tcp://192.168.1.11:4840", prefix="MAIN")

target = 7.0

move = UaRpc( com=com, suffix="Motor1.RPC_MoveAbs", arg_parsers=[float, float])
pos = UaNode( com=com,  suffix="Motor1.stat.lrPosActual" )
test = InsideInterval( node = pos, min=target-0.1, max=target+0.1 )


try:
    com.connect()
    move.call( 7.0, 1 )
    while not test.get():
        time.sleep(0.1)

    print( "posisiotn is", pos.get() )
finally:
    com.disconnect()

```
