# Creating output plugins for the honeypot

To create additional output plugins, place Python modules in this directory.

The plugins need to subclass the class `core.output.Output` and to define at
least the methods `start`, `stop` and `write`:

```python
from core import output

class Output(output.Output):

    def start(self):
        pass

    def stop(self):
        pass

    def write(self, event):
        pass
```
