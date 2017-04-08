## Bangkok Transit

Scrape data from [transitbangkok.com](http://www.transitbangkok.com/) and put it online. Adding some tiny snippet for querying commute instruction.

### Usage

```python
import transit
stations = transit.read_stations('data/stations.csv')
route_descriptions = transit.get_commute_instruction('บางรัก', 'สีลม', stations) # return route instruction
```

**Ouput**

```python
[{'action': 'Walk by foot to',
  'lines': [],
  'station': 'Sathorn/Saphan Taksin'},
 {'action': 'Travel to',
 'lines': ['544', '547'],
 'station': 'Sala Daeng'},
 {'action': 'Walk by foot to',
 'lines': [],
 'station': 'Si Lom'}]
```

The output (if both stations start and end match with their database)
will be list of instructions to go to the destination.

### Download

Clone or download the zip file of the repository.

```bash
git clone https://github.com/titipata/bangkok_transit
```
