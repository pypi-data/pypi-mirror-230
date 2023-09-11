# spark_dql_mvp_tools

[![Github License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Updates](https://pyup.io/repos/github/woctezuma/google-colab-transfer/shield.svg)](pyup)
[![Python 3](https://pyup.io/repos/github/woctezuma/google-colab-transfer/python-3-shield.svg)](pyup)
[![Code coverage](https://codecov.io/gh/woctezuma/google-colab-transfer/branch/master/graph/badge.svg)](codecov)

spark_dql_mvp_tools is a Python library that implements quality rules in sandbox

## Installation

The code is packaged for PyPI, so that the installation consists in running:

## Usage

wrapper create hammurabies MVP

## Sandbox

## Installation

```sh
!yes| pip uninstall spark-dql-mvp-tools
```

```sh
pip install spark-dql-mvptools --user --upgrade
```

## IMPORTS

```sh
import os
import pyspark
from pyspark.sql import functions as func
from spark_generated_rules_tools import dq_path_workspace
from spark_generated_rules_tools import dq_generated_mvp
import spark_dataframe_tools 

```

## Variables

```sh
user_sandbox="P030772"
```

## Creating Workspace

```sh
dq_path_workspace(user_sandbox=user_sandbox)
```

## Run

```sh
table_raw_name = 't_klau_moe_adj_id_mthly_info'
table_master_name = 't_pmfi_moe_adj_id_mthly_info'
periodicity = 'Daily'
target_staging_path = '/in/staging/datax/klau/my_file_{?YEAR_MONTH}.csv'
is_uuaa_tag = False

dq_generated_mvp(table_master_name=table_master_name,
                 table_raw_name=table_raw_name,
                 periodicity=periodicity,
                 target_staging_path=target_staging_path,
                 is_uuaa_tag=is_uuaa_tag)
               
```

## License

[Apache License 2.0](https://www.dropbox.com/s/8t6xtgk06o3ij61/LICENSE?dl=0).

## New features v1.0

## BugFix

- choco install visualcpp-build-tools

## Reference

- Jonathan Quiza [github](https://github.com/jonaqp).
- Jonathan Quiza [RumiMLSpark](http://rumi-ml.herokuapp.com/).
