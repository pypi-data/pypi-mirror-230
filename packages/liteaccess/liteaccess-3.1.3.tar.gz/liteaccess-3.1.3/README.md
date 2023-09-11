# liteAccess
Access to Process Variables, served by liteServer

# Example
```python
import liteaccess as LA 
from pprint import pprint

Host = 'localhost'
LAserver = Host+':server'
LAdev1   = Host+':dev1'
LAdev2   = Host+':dev2'

#``````````````````Simplified programmatic way`````````````````````````````````
LA.Access.info((Host+':*','*'))# map of all devices and parameters the Host
LA.Access.info((LAserver,'*'))
LA.Access.get((LAserver,'*'))

# The commands below assume that the liteScaler server is running on the same host.
LA.Access.set((LAdev1,'frequency',2.0))
# subscription example:
def testCallback(*args): print(f'callback args: {args}')
LA.Access.subscribe(testCallback,(LAdev1,'cycle'))
LA.Access.unsubscribe()
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#``````````````````Object-oriented way`````````````````````````````````````````
# Advantage: The previuosly created PVs are reused.
allServerParameters = LA.PVs((LAserver,'*'))
pprint(allServerParameters.info())
pprint(allServerParameters.get())# get all parameters from device LAserver
# get all readable parameters from device Scaler1:server, which have been 
# modified since the last read:
pprint(allServerParameters.read())

allDev1Parameters = LA.PVs((LAdev1,'*'))
pprint(allDev1Parameters.info())

server_performance = LA.PVs((LAserver,'perf'))
pprint(server_performance.info())
pprint(server_performance.get())
# simplified get: returns (value,timestamp) of a parameter 'perf' 
pprint(server_performance.value)

server_multiple_parameters = LA.PVs((LAserver,('perf','run')))
pprint(server_multiple_parameters.info())
pprint(server_multiple_parameters.get())

server_multiple_devPars = LA.PVs((LAdev1,('time','frequency')),(LAserver,('statistics','perf')))
pprint(server_multiple_devPars.get())

# setting
dev1_frequency = LA.PVs((LAdev1,'frequency'))
#TODO#dev1_frequency.set([1.5])
#TODO#dev1_frequency.value
dev1_multiple_parameters = LA.PVs([LAdev1,('frequency','coordinate')])
dev1_multiple_parameters.get() 
#TODO#dev1_multiple_parameters.set([8.,[3.,4.]])

# subscribing
ldo = LA.PVs([LAdev1,'cycle'])
ldo.subscribe()# it will print image data periodically
ldo.unsubscribe()# cancel the subscruption

# test for timeout, should timeout in 10s:
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#``````````````````Observations````````````````````````````````````````````````
Timing of Access.get using ipython on localhost.
    from liteserver import liteAccess as LA
    Host='localhost'
    LAdev1   = Host+':dev1'
    %timeit image = LA.Access.get((LAdev1,['image']))
    145 µs ± 1.95 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
    image[(LAdev1,'image')]['value'].shape
    (120, 160, 3)
Retrieving time of 57600 values (120*160*3) is 145 µs,
which corresponds to 400 mValues/s

Retrieving time of 57600 values (120*160*3) 220 µs,
which corresponds to 260 MValues/s (on entry-level workstation). 
It was 400 MValues/s on top-level workstation.
Note: Msgpack was 4% faster.
#``````````````````Tips````````````````````````````````````````````````````````
# To enable debugging: LA.PVs.Dbg = True
# To enable transaction timing: LA.Channel.Perf = True
```
