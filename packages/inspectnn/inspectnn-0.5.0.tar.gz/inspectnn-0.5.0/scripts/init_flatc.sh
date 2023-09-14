#!/bin/bash
flatc --python tool/schema_v3a.fbs

for i in $(find tflite -name '*.py' |grep -v -e "__init__"| sort ); 
do 
    name=$(basename ${i})
    name=${name%.py} 
    echo "from tflite.${name} import *"; 

done > tflite/__init__.py   

echo  "BUILTIN_OPCODE2NAME = {" > tflite/utils.py 

grep "=" tflite/BuiltinOperator.py | sed "s/\s//g" | awk -v OFS=":" -F"=" '{print $2, "\""$1"\","}' >> tflite/utils.py 

echo  "}" >> tflite/utils.py 

echo "from tflite.utils import *">> tflite/__init__.py 