# OASC
OASC从一个指定的OpenAPI文档目录下读取所有的.yaml文档，每一个文档生成一个同名的Class以及必要的数据结构，并生成基于CMake和Conan的工程文件。

其基本用法如下:

````
usage: oasc [-h] [--output OUTPUT] [--nsp NSP] [--project PROJECT] document_dir

Generate cpp sources from OpenAPI document.

positional arguments:
  document_dir       special input OpenAPI document directory.

options:
  -h, --help         show this help message and exit
  --output OUTPUT    special output directory.
  --nsp NSP          special namespace of all objects.
  --project PROJECT  special project name, if not, use 'mlapi'
````