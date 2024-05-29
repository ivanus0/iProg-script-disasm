[![en](https://img.shields.io/badge/lang-en-green.svg)](README.en.md)
[![ru](https://img.shields.io/badge/язык-ru-blue.svg)](README.md)

# iProg script and calculator disassembler
iProgDecompiler.py decrypts *scripts* (**.ipr** files) and *calculators* (**.cal** files) and produces an **assembly code**

For *scripts*, many explanations of commonly occurring patterns will be added to the comments.
It is not difficult to reproduce the source code from the listing, but this can only be done manually.

## Additional features
- For **.ipr** *scripts*, decrypted and unlocked file **{script}_decrypted.ipr** will be created
- You can relock *calculators* to a different serial by using the **--newsn** switch
- If the serial is unknown, you can use the **--bruteforce** switch

### Examples
The [examples/compiled](examples/compiled) folder contains several examples of compiled *scripts*.
Decompiled and restored result in [examples/decompiled](examples/decompiled)

### Contacts
See profile
