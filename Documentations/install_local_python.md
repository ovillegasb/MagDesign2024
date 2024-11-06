# Local installation of python

## From the source code

You can use the version of your choice that is available at https://www.python.org

```sh
wget https://www.python.org/ftp/python/3.11.10/Python-3.11.10.tar.xz
tar -xvf Python-3.11.10.tar.xz
cd Python-3.11.10
./configure --prefix=$USER/.local --enable-shared --enable-optimizations --enable-ipv6 LDFLAGS=-Wl,-rpath=$USER/.local/lib,--disable-new-dtags

mak
make install
```

This version will now be accessible at: `$USER/.local/bin/python3`

## PIP Installation

```sh
curl -O https://bootstrap.pypa.io/get-pip.py
$USER/.local/bin/python3 get-pip.py

$USER/.local/bin/pip -V
```

