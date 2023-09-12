# genpypress

This library contains several code generator helpers. It is connected to the `press` code generator.

This package will only run on Windows (submodule `table` uses external binary as dependency, the binary only exists for Windows).

## Usage

### Command line application

- `ph --help` - zobrazí nápovědu
- `ph apatch` - provede patch TPT skriptů pro asynchronní stage
- `ph cc` - připraví SQL a/nebo BTEQ skripty tabulek na podmíněné nasazení

### Markdown (mapping) parser

```python
from pathlib import Path
from genpypress import mapping

# import a file in markdown format
file = Path("TGT_ACCS_METH_RLTD_906_900_915_AMR_NIC_PCR_2_M2C.md", encoding="utf-8")
map = mapping.from_markdown(file.read_text(encoding="utf-8"))

# access table mapping property
print("Type of historization:", map.etl_historization)

# access a column mapping property (case insensitive)
print("hist_type =", map["hist_type"].transformation_rule)

# nonexisting column will - of course - blow the code up
try:
    print(map["not available"])
except KeyError as err:
    print(f"error: {err}")
```

### Table parser

Only supported on MS Windows.

```
from genpypress import table
filename = "ddl_script.sql"
data = table.from_file(filename)
t = data[0]

# access to table properties and/or columns
print("table name", t.name)
print("first column", t[0])
print("column by name", t["column_name"])

# deletion of columns by name and/or index
del t["another_column"]
del t[O]
```