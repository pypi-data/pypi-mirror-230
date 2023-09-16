# DISCODATA driver

This drb-driver-discodata module implements DISCODATA databases access with DRB data model. It is able to navigates among the database contents.

For more information about DISCODATA see: https://discodata.eea.europa.eu/Help.html

## DISOCDATA Factory and DISCODATA Node

The module implements the basic factory model defined in DRB in its node resolver. Based on the python entry point mechanism, this module can be dynamically imported into applications.

The entry point group reference is `drb.driver`.<br/>
The driver name is `discodata`.<br/>
The factory class `DrbDiscodataFactory` is encoded into `drb.drivers.factory`
module.<br/>

## Nodes

### DrbDiscodataServiceNode

Represent a node for browsing Discodata databases.
Its attribute _databases_ contain the list of all the available databases in the discodata service.
Its children is a list of `DrbDiscodataDataBaseNode` that can be browsed by name (of the database).
This node has no implementations.

### DrbDiscodataDataBaseNode

Represent a discodata database.
Its attribute _tables_ contain the list of the tables available in this database.
Its children is a list of `DrbDiscodataTableNode` that can be browsed by name.

### DrbDiscodataTableNode

Represent a table of discodata.
Its attribute _columns_ contain the list of the columns namof this table.
Its children is a list of `DrbDiscodataRowList`.
A panda DataFrame and xarray Dataset representations are available using the `get_impl()` method

## limitations

The current version does not manage child modification and insertion. `DrbDiscodataNode` is currently read only.
The factory to build DrbDiscodataNode supports file directly opening it with path, for other implementation ByteIO or BufferedIOBase, they are manged with a local temporary file, removed when the node is closed..

## Using this module

To include this module into your project, the `drb-driver-discodata` module shall be referenced into `requirements.txt` file, or the following pip line can be run:

```commandline
pip install drb-driver-discodata
```

## Examples

This example shows how to create a `DrbDiscodataServiceNode` then look for the first 3 databases using the attribute of the service:

```python
from drb.drivers.discodata import DrbDiscodataServiceNode

service = DrbDiscodataServiceNode(path="https://discodata.eea.europa.eu")
databases = service @ "databases"
for database in databases[:3]:
    print(database)
```

Output :

```
AirQualityDataFlows
BISE
CataloguePolicyEvaluations
```

Then we can get the list of tables from a specific database:

```
database = service["AirQualityDataFlows"]
tables = database @ "tables"
for table in tables:
    print(table)
```

Output :

```
AirQualityStatistics
AssessmentRegimeMethods
AssessmentRegimes
AttainmentMethods
Attainments
Measurements
Models
Zones
```

Finaly, we can get a pandas.DataFrame implementation:

```
import pandas as pd

table = database["Models"]
print(table.get_impl(pd.DataFrame))
```

Output :

```
       Country CountryCode  B2G_Namespace  ...             AuthorityAddress                                      SourceDataURL                 Imported
0      Austria  AT          AT.0008.20.AQ  ...                               http://cdr.eionet.europa.eu/at/eu/aqd/e1b/envx...  2021-11-20T18:38:50.493
1      Austria  AT          AT.0008.20.AQ  ...                               http://cdr.eionet.europa.eu/at/eu/aqd/e1b/envx...  2021-11-20T18:38:50.493
2      Austria  AT          AT.0008.20.AQ  ...                               http://cdr.eionet.europa.eu/at/eu/aqd/e1b/envx...  2021-11-20T18:38:50.493
3      Austria  AT          AT.0008.20.AQ  ...                               http://cdr.eionet.europa.eu/at/eu/aqd/e1b/envx...  2021-11-20T18:38:50.493
4      Austria  AT          AT.0008.20.AQ  ...                               http://cdr.eionet.europa.eu/at/eu/aqd/e1b/envx...  2021-11-20T18:38:50.493
...        ...         ...            ...  ...                          ...                                                ...                      ...
2495  Slovenia  SI             SI.ARSO.AQ  ...  Vojkova 1b, LJUBLJANA, 1000  http://cdr.eionet.europa.eu/si/eu/aqd/e1b/envy...  2021-11-20T19:08:05.693
2496  Slovenia  SI             SI.ARSO.AQ  ...  Vojkova 1b, LJUBLJANA, 1000  http://cdr.eionet.europa.eu/si/eu/aqd/e1b/envy...  2021-11-20T19:08:05.693
2497  Slovenia  SI             SI.ARSO.AQ  ...  Vojkova 1b, LJUBLJANA, 1000  http://cdr.eionet.europa.eu/si/eu/aqd/e1b/envy...  2021-11-20T19:08:05.693
2498  Slovenia  SI             SI.ARSO.AQ  ...  Vojkova 1b, LJUBLJANA, 1000  http://cdr.eionet.europa.eu/si/eu/aqd/e1b/envy...  2021-11-20T19:08:05.693
2499  Slovenia  SI             SI.ARSO.AQ  ...  Vojkova 1b, LJUBLJANA, 1000  http://cdr.eionet.europa.eu/si/eu/aqd/e1b/envy...  2021-11-20T19:08:05.693

[2500 rows x 39 columns]
```
