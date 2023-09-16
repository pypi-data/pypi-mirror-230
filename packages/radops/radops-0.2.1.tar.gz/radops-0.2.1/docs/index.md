# R&D Operations

`radops` is a Python package and command-line interface (CLI) for the Striveworks R&D team. It has four main components

1. [**Data Lake**](data_lake.md) The data lake functionality allows synchronization between local files and files stored in s3-compatible blob storage. The novelty of the Python API for the data lake is the supporting of data processing pipelines between objects in the data lake, with full graph based lineage of all files in the data lake.

2. [**Remote job execution**](remote_job_execution.md) The CLI handles provisioning and pushing of code to different executors, such as remote cloud GPU VMs or on-premise machines.

3. **Experiment tracking** (in progress) This module supports ML experiment tracking, with the same API for different backends. Initially the only supported backend is MLFlow but Chariot training v2 will also be supported when it's ready.

4. [**Serialization package**](serialization.md) This is the same package as used by Chariot, and supports the full serialization of Python objects (incuding those with large binary data, such as a `torch.nn.Module`) into JSON.

## Installation

Install via

```shell
pip install radops
```

This will install the python package as well as the CLI.

<!-- TODO: making this work (with lineage) for a non-monorepo -->
<!-- ```shell
pip install git+ssh://git@github.com/Striveworks/radops.git
``` -->

To check that the installation was successful, you can run

```shell
radops --help
```

which should display usage information for the `radops` CLI.

A one-time configuration is necessary for pointing `radops` to the backing s3 service as well as setting your e-mail address (used for file ownership). This can be done by running

```shell
radops config setup
```

and following the instructions.
