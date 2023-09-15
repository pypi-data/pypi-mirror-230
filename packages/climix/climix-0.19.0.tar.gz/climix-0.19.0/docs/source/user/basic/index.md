# Basic

Climix is a tool to calculate climate indices.
We focus on high performance for the efficient calculation of indices in large datasets, such as long simulations performed by high-resolution global or regional climate models, and on high-quality metadata, maximizing re-use and utility of these computations.

For now, we always base our calculations on daily input, though an extension to sub-daily input for specialized indices, or monthly input for long-running datasets with limited data availability may be considered in the future.

## Getting started
### Install
If you already have an installed version of Climix available, you can move on to {ref}`first-index`.

The easiest way to install Climix is using the Conda-forge distribution.

#### Conda-forge (recommended)
To install Climix from Conda-forge, you use the Conda package manager or its faster sibling Mamba.
If you don't already have a version of Conda or Mamba available to you, the best way to get started is by installing [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge), an installer for Mamba that will pre-configure your installation to use the Conda-forge distribution.

:::{tip}
If you prefer to use Conda instead of Mamba, for example because this has been pre-installed for you, just replace `mamba` with `conda` in the following commands.
:::

To install the latest version of Climix, just create an environment with the `climix` package in it by running
```{code-block} bash
mamba create -n my-climix climix
```
where `my-climix` is an arbitrary name you choose.

To use Climix at any time, you need to make sure that the `my-climix` environment is activated.
To do that, any time you want to use climix execute
```{code-block} bash
mamba activate my-climix
```

(first-index)=
### Calculating a first index
As a first example, let's calculate the index {ref}`idx-cdd` or consecutive dry days.
This index is based on precipitation, which we provide to Climix in the form of a Netcdf file.
Climix works with a wide variety of these files which are commonly used for climate and earth data.
Here, we use `pr.nc` as a standin, try to run the program with a precipitation data file of your choosing, for example from CMIP6.

```{code-block} bash
climix -x cdd -o cdd.nc pr.nc
```
Climix will store the result in a new Netcdf file in the current working directory.
You can specify the name with the `-o` option as we did above, or you can let Climix choose a filename.
You select the index you want to calculate with the `-x` option.
For an overview of the available indices, have a look at {ref}`available-indices` or use the call `climix -x list`.

For more information about available commandline options, have a look at the help available via `climix -h`.
