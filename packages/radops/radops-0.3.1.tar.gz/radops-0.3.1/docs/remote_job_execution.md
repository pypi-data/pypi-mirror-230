# Remote job execution

The remote job execution functionality of `radops` allows for the execution of code on remote machines. This is useful for running code on machines with GPUs, such as on virtual machines on a cloud provider or on-premise machines.

A core concept is that of an `Executor`, which is a machine that can run docker containers. There is a `local` executor, which is seutp automatically, that uses the local machine to run. This is primarily useful for developing debugging workflows. The main utlity comes from remote executors which are machines that are accessible via ssh.

## Usage

This section goes over basic usage. You can run

```shell
radops executors --help
```

to see a list of all available commands.

### Registering a new remote executor

To register a new (remote) executor, run

```shell
radops executors add
```

and follow the prompts, which will ask for the hostname, username, and path to the docker executable on the remote machine. It is assumed that public key ssh authentication is setup for the remote machine.

#### Setting up a GCP VM as an executor

The above command requires a remote machine to be already setup (either on-prem compute or a cloud machine). For GCP VMs, `radops` supports provisioning a new VM and creating a new executor associated to it.

The command

```shell
radops executors gcp create <TEMPLATE NAME> <NAME>
```

will spin up a VM on GCP using the specified template and then create an executor (with name `<NAME>`) to connect to it.

To view available templates (i.e. VM types) run the command

```shell
radops executors gcp list-templates
```

### Running a job

To run a job on an execturor, run

```shell
radops executors run <EXECUTOR NAME> <PATH> <COMMAND>
```

where

- `<EXECUTOR NAME>` is the name of the executor to run the job on
- `<PATH>` is a folder that contains the Dockerfile to build the image from, and will be used for the docker context in building the image.
- `<COMMAND>` is the command to run (what gets sent to the entrypoint of the container).

The above command will do the following:

1. Build the docker image
2. Push it to GitHub container registry
3. SSH into the executor machine and pull the image
4. Run the image on the remote machine

The final output of the command will print the job id, which can be used to view the logs of the job via the command

```shell
radops executors logs <EXECUTOR NAME> <JOB ID>
```

## Example

The `radops` repo has an example job folder in `demos/remote_execution`. You can verify that everything is working by running

```shell
radops executors run local demos/remote_execution "testing remote execution"
```

Then you can view the logs via

```shell
radops executors logs local <JOB ID>
```

where `<JOB ID>` is the id of the job that was printed out by the previous command.

You can also run the same command but with `local` replaced with the name of a remote executor that you have setup.
