# Дизассемблер скриптов и калькуляторов iProg
# iProg Script and Calculator Disassembler

## Русский

`iProgDecompiler.py` расшифровывает и создаёт **ассемблерный листинг** из скриптов **`.ipr`** и калькуляторов **`.cal`**.

Для скриптов в комментарии добавляются расшифровки часто встречающихся паттернов. Также создаётся черновой восстановленный исходник **`*_draft.blr`**, который может потребовать ручной проверки и исправления.

Этот репозиторий является форком оригинального проекта **[ivanus0/iProg-script-disasm](https://github.com/ivanus0/iProg-script-disasm)**.

В форке сохранена оригинальная логика декодирования и дизассемблирования, но расширен `iProgDecompiler.py`:

- добавлена пакетная обработка всех `.ipr` и `.cal` в каталоге;
- поддерживается передача каталога вместо одного файла;
- запуск без параметров обрабатывает файлы в каталоге самого декомпилятора;
- добавлен рекурсивный режим `-r / --recursive`;
- расширения `.ipr` и `.cal` обрабатываются без учёта регистра;
- ошибка одного файла не останавливает обработку остальных;
- после пакетной обработки выводится статистика `OK / Failed / Total`;
- добавлена стандартная поддержка `-h / --help`.

### Windows launcher

Для удобства в репозитории также есть `decompile_all.bat`.

Он позволяет запускать `iProgDecompiler.py` двойным кликом в Windows и оставляет окно консоли открытым после завершения, чтобы можно было увидеть результаты обработки и возможные ошибки.

BAT-файл является опциональным и не требуется для работы декомпилятора.

### Использование

Один файл:

```powershell
py iProgDecompiler.py script.ipr
```

Все поддерживаемые файлы в каталоге:

```powershell
py iProgDecompiler.py "C:\iProg\Scripts"
```

Все поддерживаемые файлы в каталоге рядом с `iProgDecompiler.py`:

```powershell
py iProgDecompiler.py
```

Рекурсивная обработка каталога и всех вложенных папок:

```powershell
py iProgDecompiler.py "C:\iProg\Scripts" -r
```

### Дополнительные возможности

Для `.ipr` создаются следующие файлы:

```text
script.lst
script_draft.blr
script_decrypted.ipr
```

`*_decrypted.ipr` создаётся только в том случае, если для исходного файла применяется расшифровка.

Калькуляторы `.cal` можно привязать к другому серийному номеру с помощью:

```text
--newsn
```

Если серийный номер неизвестен, можно использовать:

```text
--bruteforce
```

Оригинальные параметры командной строки сохранены.




## English
iProgDecompiler.py decrypts and creates an assembly listing from iProg .ipr scripts and .cal calculators.
For scripts, the generated listing contains comments describing many common iProg patterns. A draft reconstructed source file, *_draft.blr, is also generated and may require manual review and correction.
This repository is a fork of the original ivanus0/iProg-script-disasm project.
The original decoding and disassembly logic has been preserved, while iProgDecompiler.py has been extended with:
- batch processing of all .ipr and .cal files in a directory;
- directory input in addition to single-file input;
- automatic processing of files next to the decompiler when launched without arguments;
- recursive processing with -r / --recursive;
- case-insensitive .ipr and .cal extension handling;
- per-file error handling so one failed file does not stop the batch;
- OK / Failed / Total processing summary;
- standard -h / --help support.

### Windows launcher

The repository also includes an optional `decompile_all.bat` helper.

It allows `iProgDecompiler.py` to be launched by double-clicking it in Windows and keeps the console window open after execution so processing results and possible errors can be reviewed.

The BAT file is optional and is not required for the decompiler to work.

### Usage

Process a single file:

```powershell
py iProgDecompiler.py script.ipr
```

Process all supported files in a directory:

```powershell
py iProgDecompiler.py "C:\iProg\Scripts"
```

Process all supported files located next to `iProgDecompiler.py`:

```powershell
py iProgDecompiler.py
```

Process a directory recursively, including all subdirectories:

```powershell
py iProgDecompiler.py "C:\iProg\Scripts" -r
```

### Additional features

For `.ipr` files, the following files are generated:

```text
script.lst
script_draft.blr
script_decrypted.ipr
```

`*_decrypted.ipr` is created only when decryption is applicable to the source file.

`.cal` calculators can be rebound to another serial number using:

```text
--newsn
```

If the serial number is unknown, you can use:

```text
--bruteforce
```

The original command-line options are preserved.
