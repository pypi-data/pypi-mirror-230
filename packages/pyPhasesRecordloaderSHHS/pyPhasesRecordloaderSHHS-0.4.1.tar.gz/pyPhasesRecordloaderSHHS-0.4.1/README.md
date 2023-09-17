# Extension for pyPhasesRecordloader

Extension to load data records from the Sleep Heart Health Study (SHHS) database. Inlcuding both parts (shhs1 and shhs2).

The extensions requires a downloaded version of the shhs dataset. The location can be set through the config value `shhs-path`.

## Usage

In a phase you can acess the data through the `RecordLoader`:

Add the plugins and config values to your `project.yaml`:

```yaml
name: SHHSProject
plugins:
  - pyPhasesML
  - pyPhasesRecordloaderSHHS
  - pyPhasesRecordloader

phases:
  - name: MyPhase

config:
  shhs-path: C:/datasets/shhs

```

In a phase (`phases/MyPhase.py`) you can acess the records through the `RecordLoader`:

```python
from pyPhasesRecordloader import RecordLoader
from pyPhases import Phase

class MyPhase(Phase):
    def run(self):
      recordIds = recordLoader.getRecordList()
      for recordId in recordIds:
        record = recordLoader.getRecord(recordId)
```

Run Your project with `python -m phases run MyPhase`