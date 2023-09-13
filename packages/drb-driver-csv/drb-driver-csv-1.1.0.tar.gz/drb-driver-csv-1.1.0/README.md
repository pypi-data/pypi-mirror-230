# DRB Driver CSV
**_drb-driver-csv_** is a Python plugin for **DRB**, representing **DRB**
[driver](https://drb-python.gitlab.io/drb/user/concepts.html#driver)
allowing to recognize and to browse **_CSV_**
([Comma-Separated Values](https://csv-spec.org/)) data.

## Installation
```shell
pip install drb-driver-csv
```
## Quick Started
```python
from drb.drivers.csv import CsvNodeFactory

# generate the CSV node (DRB resolver can be used also)
node = CsvNodeFactory().create('url/to/csv/data.csv')

# select a row first row by index
row = node[0]
# select a row first row by name
row = node['row_0']

# select first value in a row by index
row[0]
# select a value in a row by name
row['header']

# retrieve value from row: 5, column 1
node[5][1].value
```

## Driver
The **_drb-driver-csv_** reads a _CSV_ data like it having a header, so the first
row is the second line of the _CSV_ data.

Each node defined in this driver represent a unitary part or whole content of
a _CSV_ data:

![csv content as node relationship](docs/static/csv_driver_nodes.png)

More details in the following section.

### Nodes
#### CsvBaseNode
The `CsvBaseNode` wraps another **DRB** node (_base_node_) representing the
_CSV_ data and allows to provide an entry point to the _CSV_ content.

##### Attributes
The `CsvBaseNode` has no attribute.

##### Children
Each child of the `CsvBaseNode` repersenting a row of the _CSV_ content. Those
children are accessible via:
 - index (int): _CSV_ row index
 - name (str): generic name following the pattern `row_N`:
    - `row_` is a string constant
    - `N` is the row index (int)

##### Implementations
The `CsvBaseNode` inherits from the _base_node_, plus a `pandas.DataFrame`
implementation to see the data as array.

Learn more about [pandas](https://pandas.pydata.org/).

#### CsvRowNode
A `CsvRowNode` represent a row from a _CSV_ content.

##### Attributes
The `CsvRowNode` has no attribute.

##### Children
A child of a `CsvRowNode` is a node containing the value for the associate
header. Those children can be accessible via:
 - index (int): using header index
 - name (str): using the header name

##### Implementations
The `CsvBaseNode` has no implementation.

#### CsvValueNode
A `CsvValueNode` represent a cell value from a _CSV_ content. The associated
value is accessible via the `value` property


##### Attributes
A `CsvValueNode` has no attribute.

##### Children
A `CsvValueNode` has no child.

##### Implementations
A `CsvValueNode` has no implementation

### Factory
The **_drb-driver-csv_** provide a factory `csv` generating only
[CsvBaseNode](#csvbasenode).

## Topic
The **_drb-driver-csv_** comes also with a **DRB**
[topic](https://drb-python.gitlab.io/drb/user/concepts.html#topic) allowing to
resolve and to recognize _CSV_ data.

```mermaid
graph RL
    A([CSV<br/>060f724c-9334-4fd5-9378-8d83c629fd1d])
```
| uuid                                 | from    | label | category   | factory |
|:-------------------------------------|:--------|:------|:-----------|:--------|
| 060f724c-9334-4fd5-9378-8d83c629fd1d | &empty; | CSV   | FORMATTING | csv     |
