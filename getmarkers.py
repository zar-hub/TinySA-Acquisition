# https://tinysa.org/wiki/pmwiki.php?n=Main.USBInterface

import tinysa
import numpy as np
import time

# get the tinysa object
tsa = tinysa.TinySA()

# tsa.set_span(20e6)
# tsa.set_center(4e9)



# get 3 measurements of the marker
for i in range(2):
    tsa.send_command("marker 1 5800M\r")
    tsa.send_command("marker 1\r")
    data = tsa.fetch_data()
    # data = tsa.marker_value(1)
    print(data)
    
    time.sleep(1)
