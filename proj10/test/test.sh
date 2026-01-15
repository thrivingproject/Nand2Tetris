#!/bin/bash

tsc
node dist/JackAnalyzer.js test/ArrayTest
node dist/JackAnalyzer.js test/Square
diff -w test/ArrayTest/MainC.xml test/ArrayTest/Main.xml
diff -w test/Square/MainC.xml test/Square/Main.xml
diff -w test/Square/SquareC.xml test/Square/Square.xml
diff -w test/Square/SquareGameC.xml test/Square/SquareGame.xml