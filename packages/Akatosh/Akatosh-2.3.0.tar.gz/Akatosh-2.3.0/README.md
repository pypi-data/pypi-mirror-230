#Akatosh

<p style="text-align: justify;">
<code>Akatosh</code> is a light-weighted disceret event simulation library. Unlike popular library <code>Simpy</code> which is progress-oriented and you have to write generator function for simulated events or events interaction, `Akatosh` is fully object-oriented that events are encapsulated as `InstantEvent`/`ContinousEvent` with states, priority and a life-cycle. The actual impact of events are simply regular python functions. You could create events all at once, or create event within event. In addition, `Akatosh` is async which means event that are happening at the same simulated time will be executed simultaneously for real, unless they have different priority.
</p>

<p style="text-align: justify;">
<code>Akatosh</code> also support <code>Resource</code>, provide all functionalities as it is in <code>Simpy</code> with extra utilities for telemetries collection and interaction with <code>Entity</code>. The <code>Entity</code> is unique to <code>Akatosh</code> which represents a abstract entity with a life-cycle, for example a follower. The <code>Entity</code> supports utility functions to interact with `Resource` and automatically releases all its occupied resources upon termination.
</p>

<p style="text-align: justify;">
You probably already noticed that <code>Akatosh</code> is the name of "Dragon God of Time" in elder scroll serie, therefore the singleton class <code>Mundus</code> is the core of the simulation. The <code>Mundus</code> will schedule the events, move forward time and engage async execution.
</p>

To use `Akatosh`:
```
pip install -U Akatosh
```

A basic example is showing below, for more information please look at *Examples* and *API Reference*, full documentation is available at https://ulfaric.github.io/Akatosh/.

```py
import logging

from Akatosh import event, Mundus

# create two instant event at simulation time 1.0 and 5.0
@event(at=5)
def hellow_world_again():
    print(f"{Mundus.now}:\tHello World! Again!")


@event(at=1)
def hellow_world():
    print(f"{Mundus.now}:\tHello World!")

# enable debug message
Mundus.set_logger(logging.DEBUG)

# run simulation for 6s
Mundus.simulate(6)
```
