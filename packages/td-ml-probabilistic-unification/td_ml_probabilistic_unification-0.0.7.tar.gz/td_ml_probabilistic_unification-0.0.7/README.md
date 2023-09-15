# td-ml-probabilistic-unification

## Introduction
The `td-ml-probabilistic-unification` is a Python package designed for Probabilistic Unification within the Treasure Data environment. It provides functionality to unify and cluster records probabilistically based on various attributes, making it useful for a wide range of data integration and analysis tasks.

In order to perform probabilistic unification using this package, you should have an input table containing the data you want to unify. The package will use the specified configuration parameters to perform probabilistic unification and generate an output table with clustered records.

## Configuration
Before using this package, you need to set the following environment variables:

```python
# Configuration variables
TD_SINK_DATABASE = os.environ.get('TD_SINK_DATABASE')
TD_API_KEY = os.environ.get('TD_API_KEY')
TD_API_SERVER = os.environ.get('TD_API_SERVER')

id_col = os.environ.get('id_col')
cluster_col_name = os.environ.get('cluster_col_name')
convergence_threshold = float(os.environ.get('convergence_threshold'))
cluster_threshold = float(os.environ.get('cluster_threshold'))
string_type = os.environ.get('string_type')
fill_missing = os.environ.get('fill_missing')
feature_dict = json.loads(os.environ.get('feature_dict'))
blocking_table = os.environ.get('blocking_table')
output_table = os.environ.get('output_table')

record_limit = int(os.environ.get('record_limit'))
lower_limit = int(os.environ.get('lower_limit'))
upper_limit = int(os.environ.get('upper_limit'))
range_index = os.environ.get('range_index')
paralelism = os.environ.get('paralelism')
input_table = blocking_table

Thank you for choosing td-ml-probabilistic-unification for your probabilistic unification needs! 📊🚀

`Copyright © 2022 Treasure Data, Inc. (or its affiliates). All rights reserved`
