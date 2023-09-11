![](docs/source/timewise_sup.png)
# The Timewise Subtraction Pipeline

This is all very new and exciting....


## Installation

It's highly recommended to install using `poetry`. This ensures an exact replica of the
tested envronment with the verisions of all dependecnies resolved as documented in `poetry.lock`.

```shell
poetry install
```

Note that some systems might have problems with `poetry`s experimental (parallel) installer 
(see [this](https://github.com/python-poetry/poetry/issues/3352) issue on GitHub).
If the installation is stuck at `pending...` try interrupting, `poetry config experimental.new-installer false` and
then try installing again.

If this does not work you can resort to `pip`

```shell
pip install ./
```

or if you want to install in editable mode

```shell
pip install -e ./
```


## Set-up

For running `timewise`, `MongoDB` and some other things, some environment variables should be specified. 
You should check out the [`timewise` documentation](https://timewise.readthedocs.io/en/latest/?badge=latest).



#### Using the DESY cluster

To run the DESY cluster it is necessary to use [`conda`](https://conda.io). The part of the code that 
produces the submit file for `HTCondor` will read your environment and activate your `conda` environment on the 
cluster nodes.
