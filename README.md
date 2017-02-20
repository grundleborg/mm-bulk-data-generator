bulk-import-generator
=====================

This python script generates bulk import data for testing.

Usage
-----

1. Edit the constants at the top of `generate_data.py` to configure how many of each data type 
you want to generate.

2. Run the script to generate the data.
```
./generate_data.py data.json
```

3. Run the bulk importer.
```
platform import bulk data.json
```

