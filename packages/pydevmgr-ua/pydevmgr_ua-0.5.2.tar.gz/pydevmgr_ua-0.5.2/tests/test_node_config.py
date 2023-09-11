from pydevmgr_core import * 
from pydevmgr_ua import * 
from opcua import ua, Server
import time 
 
server = Server()
#server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
server.set_endpoint("opc.tcp://localhost:4840")

# setup our own namespace, not really necessary but should as spec
uri = "http://examples.freeopcua.github.io"
idx = server.register_namespace(uri)

# get Objects node, this is where we should put our nodes
objects = server.get_objects_node()

# populating our address space
myobj = objects.add_object(idx, "MyObject")
myvar = myobj.add_variable(f'ns={idx};s=MAIN.Temp001', f"{idx}:MyTemp", 6.7)

myvar.set_attribute(ua.AttributeIds.Description, ua.DataValue(ua.Variant( "This is a test", ua.VariantType.String)))
myvar.set_writable()    # Set MyVariable to be writable by clients

 
y = f"""
kind: Node
type: Ua
attribute: Value
suffix: MAIN.Temp001
parser: [float,UaDouble] 

com: 
    address: opc.tcp://localhost:4840
    namespace: {idx}
"""


if __name__ == "__main__":
    
    try:
        # starting!
        server.start()
        #time.sleep(2)
        n = build_yaml(y, "Temp")
        n.connect()
        assert n.config.attribute == ua.AttributeIds.Value 
        assert n.get() == 6.7
        n.set(99.0)
        n.config.attribute = ua.AttributeIds.Description
        print( n.get())
        assert n.get() == "This is a test"    
        
        
    finally:
        n.disconnect()
        server.stop()
        