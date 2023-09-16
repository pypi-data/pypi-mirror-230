# Data Lake

The data lake works by syncing a local storage path (which is automatically configured upon installation of `radops`) with an s3-compatible remote object store. Every file in the data lake has a UID, which makes code interoperable across various machines. When a file is requested, `radops` will first check if its in local storage and load from there. If it's not, then `radops` will automatically download it from the cloud. When creating files, `radops` will create in local storage and then automatically upload to the cloud.

!!! danger

    It is important that all files in local storage and the backing cloud service are created via `radops` methods. Creating files directly, outside of `radops`, can break lineage and cause out-of-sync issues between local and cloud storage.

`radops` has a robust API for data pipelines that allows the creation of data lake files from others, while tracking the following lineage information for each file in the data lake:

- The Python function used to create it.
- What files in the data lake were input into the above function.
- What additional parameters (such as strings, numbers, etc.) were passed to the function.
- The person who ran the function (specified by e-mail address)
- The `radops` version that was used when executing the function.

!!! note

    To ensure proper lineage, objects in the data lake are immutable.

## Walkthrough

We now walk through the basic usage of the `radops` data lake. This assumes `radops` has been installed and configured, following the instructions [here](index.md#installation).

### CLI

The command

```shell
radops datalake ls
```

lists all files in the cloud data lake. It will also warn you if there are local files that are out of sync with the cloud.

We'll now show one way that a file can be added to the data lake. Create a new sample file in your working directory, e.g. via

```shell
echo "this is some data" > ./myfile.txt
```

Then add this to the data lake using the command

```shell
radops datalake add ./myfile.txt name_in_datalake.txt --copy
```

The first argument to `radops datalake add` is the local file to add, the second is the desired name of the file in the datalake, and the `--copy` flag means to make a copy of this file in local storage. The other option is `--move` which moves the file to local storage. `radops datalake add` can also take in a url, in which case it will download the file to local storage (in this case the `--copy` and `--move` options do not apply).

You should now see the name `"name_in_datalake.txt"` listed in the output of the command `radops datalake ls`.

Info about the file can be accessed by running

```shell
radops datalake info name_in_datalake.txt
```

The file can be accessed programmatically. For example, the code

```python
from radops.data_lake import File

f = File("name_in_datalake.txt")
with f.open("r") as fileobj:
    print(fileobj.read())
```

will output `"this is some data"`.

### Data pipelines

The python API supports the creation of new files from other ones with complete tracking over lineage, down to the source code that was used. This is achieved using the `radops.data_lake.file_creator` decorator.

For example, suppose we create a file `pipeline.py` with the following code:

```python
from radops.data_lake import File, file_creator


@file_creator
def process(f: File, output_uid: str) -> File:
    with f.open("r") as fileobj:
        data = fileobj.read()

    data += "additional data"

    out_file = File(output_uid)
    with out_file.open("w") as fileobj:
        fileobj.write(data)

    return out_file


if __name__ == "__main__":
    process(f=File("name_in_datalake.txt"), output_uid="processed_file.txt")

    with f_out.open("r") as fileobj:
        print(fileobj.read())
```

and then run it:

```shell
python pipeline.py
```

This should print out

```
this is some data
additional data
```

To display lineage we can run the command

```shell
radops datalake info processed_file.txt
```

which will output something that looks like the following

```
╭────────────────────────╮    ╭──────────────────────────────╮    ╭────────────────────────────────────────╮
│ input files            │    │ creation method              │    │ output                                 │
│                        │ -> │                              │ -> │                                        │
│  name_in_datalake.txt  │    │  function  __main__.process  │    │  uid         processed_file.txt        │
╰────────────────────────╯    │                              │    │  originator  user@striveworks.com      │
                              ╰──────────────────────────────╯    ╰────────────────────────────────────────╯
creation method code: https://github.com/striveworks/radops/blob/77f7ac6a3652a1db5725b1c980169fab1e2944b8/pipeline.py#L5
radops version: 0.1.dev49+g0c5018a.d20230817
```

Here we have the following information:

- The left box shows the input files that when into creating the output file(s)
- The middle box shows the name of the function that was used to process the input to create the output
- The right box shows the name of all of the output file(s) together with the user who called the creation code.
- Below the graph is a link (assuming the code was committed and pushed to GitHub) of the exact code that was executed as well as the version of the `radops` package when the code was executed.

Suppose now we are on a different machine then the one that executed the pipeline. Running `radops datalake ls` should show something like

<pre>
['<i>name_in_datalake.txt</i>', '<i>processed_file.txt</i>']
</pre>

with both files italized since they are in the data lake but not in local storage on this machine. Now run the pipeline on this machine

```shell
python pipeline.py
```

This will show a log message that the execution of the `process` method is being skipped. This is because it has already be run and the output of it has been put in the data lake, so there is no need to run again. And, as before, you should see

```
this is some data
additional data
```

printed. Now if you run `radops datalake ls` you should see

<pre>
['<i>name_in_datalake.txt</i>', '<b>processed_file.txt</b>']
</pre>

i.e. `processed_file.txt` is now bold. This is because it was downloaded since the code execution was doing something with it. Noticed that the input file was not needed and therefore not downloaded.

In summary this example shows two key principles of the data lake python API

1. Skip processes whos output has already been computed.
2. Only download locally what's necessary.
3. Track lineage of all files, down to the exact code and dependencies that created them.

### End-to-end examples

Some end-to-end and realistic examples can be found [here](https://github.com/Striveworks/radops/tree/main/demos).
