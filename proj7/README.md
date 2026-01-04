# Hack VM Translator

Translates Hack VM code to Hack Assembly. Writes bootstrap code. Translates multiple VM files, or a single VM file, into a single `.asm` file.

## Design

[VMTranslator.py](VMTranslator.py) drives translation from source VM code to assembly. [parser.py](parser.py) handles parsing of VM commands. [code_writer.py](code_writer.py) translates VM commands into Hack assembly code. Assumes the source VM code is error-free, i.e. no error checking or handling is performed.

## Usage

```shell
python3 VMTranslator.py [path/to/]Prog.vm
```

The file name may contain a file path. If no path is specified, the VM translator operates on the current folder. The first character in the file name must be an uppercase letter, and the vm extension is mandatory. The file contains a sequence of one or more VM commands. In response, the translator creates an output file, named Prog.asm, containing the assembly instructions that realize the VM commands. The output file Prog.asm is stored in the same folder as that of the input. If the file Prog.asm already exists, it will be overwritten.

## Works Cited

Nisan, Noam, and Shimon Schocken. The Elements of Computing Systems, Second Edition : Building a Modern Computer from First Principles, MIT Press, 2021. ProQuest Ebook Central, [https://ebookcentral.proquest.com/lib/harvard-ebooks/detail.action?docID=6630880](https://ebookcentral.proquest.com/lib/harvard-ebooks/detail.action?docID=6630880).
