# structure
.
* [TeleMed](./)
  * [_build](./_build) 
  * [docs](./docs)
  * [telemed_sk](./telemed_sk) folder with codebase
    * [algorithms](./telemed_sk/algorithms) folder with modules with algorithms and utils to run models, experiments and jobs.
    * [analytics](./telemed_sk/analytics) folder with modules with evaluation metrics
    * [datahandler](./telemed_sk/datahandler) folder with modules for reading and writing files
    * [datapreparation](./telemed_sk/datapreparation) folder with modules for preprocessing data
    * [dataset](./telemed_sk/dataset)
    * [datavisualization](./telemed_sk/datavisualization) folder containing resources and scripts for effectively visualizing the data
    * [utility](./telemed_sk/utility) folder with utility files with support functions used throughout the library
  * [build.sh](./build.sh)
  * [tests](./tests) folder contains modules for conducting unit tests
  * [pyproject.toml](./pyproject.toml)
  * [README.md](./README.md)
  * [requirements.txt](./requirements.txt)

## To install the codebase, simply run the following command in your terminal:
```bash
python pip install telemed_sk
```
Once installed, it can be easily import into any Python environment.

