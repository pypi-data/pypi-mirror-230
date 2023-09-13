![](./taln2x.png)

## Description
`taln2x` is a Python program which converts a set of scientific articles to a ready-to-ingest dataset for open archives. Currently supported output formats include pdf (for printable full proceedings), [TALN archives](http://talnarchives.atala.org), [HAL](https://hal.science), [ACL anthology](https://aclanthology.org), and [DBLP](https://dblp.org).

## User interface
`taln2x` is a command-line tool which expects as input a directory containing specific pieces of information (gathered either manually or else via an abstract management system such as easychair) and relying on a given structure (see documentation), and outputs a directory whose internal structure depends on the target online archive.

![](./mkdocs/docs/img/taln2x.gif)

## Installation
The recommanded way to install `taln2x` is to use the `pip` package manager (within a virtual environment to avoid conflicts with installed libraries):

```bash
python -m venv venv
source venv/bin/activate
pip install taln2x
```
## Basic usage

```bash
taln2x COMMAND [OPTIONS]
```
Where `COMMAND` is either `new` (to set up an input directory containing the expected structure and ready-to-fill config files), `build` (to compile proceedings in a given target format according to the config file, see documentation), `clean`  (to remove proceedings from output directory), or `list` (to check which articles can be found on the [HAL](https://hal.science) open archive).

For a full list of options, invoke:
```bash
taln2x --help
```

## Documentation

`taln2x` documentation is available at [https://talnarchives.gitlabpages.inria.fr/taln2x](https://talnarchives.gitlabpages.inria.fr/taln2x).

## Authors and acknowledgment
`taln2x` has been developed by Yannick Parmentier, with the help of Sylvain Pogodalla, on behalf of [ATALA](https://atala.org) (the French Association for Computational Linguistics).

The `taln2x` logo has been created using the [Letterblocks fonts](https://www.1001fonts.com/letterblocks-font.html) made by Vladimir Nikolic.

## License
`taln2x` is released under the terms of the GNU GPLv3 license (see LICENSE).

## Project status
The `taln2x` is a sequel of the [`taln2acl`](https://gitlab.com/parmenti/taln2acl) project which has started in 2020 and has been used (among others) to ingest the proceedings of the [TALN conferences](https://atala.org/-Conference-TALN-RECITAL) from 1999 til 2022 to the [ACL anthology](https://aclanthology.org/venues/jeptalnrecital/) and [TALNarchives](http://talnarchives.atala.org).
