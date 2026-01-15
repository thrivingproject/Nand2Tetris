# Jack Syntax Analyzer

Performs both tokenizing and parsing. Currently implementing phase 2 of 2. Phase
1 involved implementing an Analyzer that recursively parses Jack and outputs the
structure of the program as an XML file with construct tags.

## Setup

Install dependencies ([typescript](https://www.npmjs.com/package/typescript) and
[@types/node](https://www.npmjs.com/package/@types/node)):

```sh
npm i && npx tsc
```

## Usage

To compile all `.jack` files in a directory or a single `.jack` file:

```sh
# From project root
node dist/JackAnalyzer.js source
```

Where `source` is the path to a directory that contains one or more Jack files
or the path to a single Jack file. Path should be relative to project root.
