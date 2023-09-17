# LibreDR is an open-source ray-tracing differentiable renderer
[\[Codeberg Repo\]](https://codeberg.org/ybh1998/LibreDR)
[\[API Document\]](https://ybh1998.codeberg.page/LibreDR/libredr/)

LibreDR uses client-server-worker structure to better utilize multiple GPUs (or even multiple nodes on a cluster). \
Some code examples are under examples/ directory.

### To run server and worker under Linux:
1. Download `libredr_linux_*.tra.gz` under [\[releases\]](https://codeberg.org/ybh1998/LibreDR/releases).
2. Start server and worker using `examples/scripts/{server,worker}.sh` or with your own configuration. \
Example configurations are in `examples/scripts`. Use `clinfo` to verify OpenCL runtime.

### To run server and worker under Windows:
1. Download `libredr_windows_*.tra.gz` under [\[releases\]](https://codeberg.org/ybh1998/LibreDR/releases).
2. Start server and worker using `examples/scripts/{server,worker}.bat` or with your own configuration. \
Example configurations are in `examples/scripts`.

### To run the example Python codes or your own Python code
1. Download `libredr-*.whl` under [\[releases\]](https://codeberg.org/ybh1998/LibreDR/releases) and install using
`pip install`, or install from [\[PyPI\]](https://pypi.org/project/libredr/).
2. Run Python example codes `examples/scripts/run_example.{sh,bat}` or your own client codes.

### All the examples tested on the following platforms:

| OS | Device | Driver |
|----|--------|--------|
| Debian Bullseye Linux 6.1.0-0.deb11.7-amd64 | CPU: Intel Core i7-8550U     | PoCL v1.6                      |
| Debian Bullseye Linux 6.1.0-0.deb11.7-amd64 | GPU: NVIDIA GeForce RTX 3090 | NVIDIA Proprietary v470.161.03 |
| Windows 10 21H2 (OS Build 19044.1288)       | GPU: AMD Radeon RX 6700 XT   | AMD Proprietary v22.20.44      |

To build from source codes, check the build script for Linux in `examples/scripts_unix/build/`. Docker is used to build
manylinux-compatible wheels.

Copyright (c) 2022-2023 Bohan Yu. All rights reserved. \
LibreDR is free software licensed under GNU Affero General Public License version 3 or latter.
