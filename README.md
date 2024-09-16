# RNA-Seq registry

API to store RNA-Seq datasets.

The RNA-Seq registry is used to keep track of all the RNA-Seq datasets loaded for production. It stores the datasets and their samples with some metadata, and keeps a record of the history.

## Requirements

Have the rnaseq-registry repo loaded and installed in your environment (or better yet, in a virtual environment like penv). For example:

```bash
cd $repo_dir
git clone git@github.com:Ensembl/rnaseq-registry.git
cd rnaseq-registry/
pip install .
```

Make sure you have a build version set in your environment, used to distinguish different production releases e.g.

```bash
export BUILD_VERSION=70
```

## Working with the registry

The registry loads a json file in the format, containing unique dataset_name, organism_abbrv, samples and SRA number.

```json
 [{
  "component": "Fungi",
  "name": "dataset_name",
  "runs": [
   {
    "accessions": [
     "SRR"
    ],
    "name": "sample1"
   },
   {
    "accessions": [
     "SRR"
    ],
    "name": "sample2"
   }
  ],
  "species": "organism_abbrv"
 }]
```

## New datasets loading

To add a new dataset to the registry, you need to create a new json file with the dataset. I.e. if you put your data in a file `all.json`:

```bash
rnaseq_registry dataset $DB_FILE --release $BUILD_VERSION --load all.json
```

If you get the following output:

SKIP organism 'organism_name' not in the registry
x/x datasets can not be loaded (use ```--replace``` or ```--ignore```)

SKIP dataset organism_name/dataset_name already in release xx
x/x datasets can not be loaded (use ```--replace``` or ```--ignore```)
to update.

You can set the flag ```--replace``` if there is to automatically retire the previous version and replace it with the new dataset.

Note: the old version will still be stored in the registry but will have its latest flag set to False, and its retired field set to the release version provided.

## Remapping

If you have RNA-Seq to remap from one organism to another, you first need to make sure the new organism is registered (assuming we set NEW_ORG):

```bash
rnaseq_registry organism $DB_FILE --get $NEW_ORG
rnaseq_registry dataset $DB_FILE --remap $OLD_ORG,$NEW_ORG
```

If you get an error No organism named NEW_ORG, add it yourself (make sure to provide the component database too):

To add a new organism_abbrev

```bash
rnaseq_registry organism $DB_FILE --add $NEW_ORG --component $COMPONENT
```

Remove a dataset:

```bash
rnaseq_registry dataset $DB_FILE --organism $NEW_ORG --dataset $DATASET_NAME --remove
```

## Dump to JSON for the RNA-Seq pipeline

Once you have loaded all the new data, you can dump all the datasets for the build in a JSON file:

```bash
rnaseq_registry dataset $DB_FILE --release $BUILD_VERSION --dump_file ./dump_${BUILD_VERSION}.json
```

```bash
rnaseq_registry dataset $DB_FILE --organism $ORGANISM --dump_file ./dump_${ORGANISM}.json
```

All the datasets for that organism will be dumped into a JSON file to be used in the RNA-Seq pipeline.

NB:
You can have a look at what is in the registry with the 3 main submenus (use ```--help``` in any submenu for more details):

```bash 
rnaseq_registry component $DB_FILE --list
rnaseq_registry organism $DB_FILE --list --with_datasets --component TrichDB
rnaseq_registry dataset $DB_FILE --list --organism tvagG32022
```

*Note*:

1. The organism and dataset lists can get very long, so you should use the filters (depending on the submenu): ```--release```, ```--component```, ```--organism```, ```--dataset```

2. By default, only the current datasets are shown. To see the ones that have been retired, add the flag ```--not_latest```

3. The ```--organism``` argument lists all registered organisms, even those without datasets.

4. You can add the flag ```--with_datasets``` to only see the ones with datasets.
