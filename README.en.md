[![en](https://img.shields.io/badge/lang-en-green.svg)](README.en.md)
[![ru](https://img.shields.io/badge/язык-ru-blue.svg)](README.md)

# iProg script and calculator disassembler

iProgDecompiler.py decrypts .ipr and produces an assembly code listing and approximate source code.
Since there is no optimization in the iProg compiler, obtaining the script's source code is quite easy.
Of course, without saving the names of functions and variables.

As a bonus, it allows you to unbind the script from the serial number.

Also supports disassembly of calculators - .cal files

The [examples/compiled](examples/compiled) folder contains several examples of compiled scripts.
Decompiled and restored result in [examples/decompiled](examples/decompiled)
