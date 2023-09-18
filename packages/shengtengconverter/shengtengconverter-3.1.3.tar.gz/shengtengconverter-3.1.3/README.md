# shengtengconverter

昇腾量化项目的模型转换器，暂时只支持onnx转换为pytorch模型。

## 安装

你可以使用 pip 来安装这个包：

```bash
pip install shengtengconverter
```
如果是python3，使用pip3：
```bash
pip3 install shengtengconverter
```

## 使用

导入所需的包：
```python
from shengtengconverter import trans
from shengtengconverter import utils
```

列出路径下的所有onnx模型：
```python
onnx_model_paths = utils.list_onnx_models('path')
print(onnx_model_paths)
```

列出路径下的所有pytorch模型：
```python
pytorch_model_paths = utils.list_pytorch_models('path')
print(pytorch_model_paths)
```

将onnx模型转换为pytorch模型：
```python
for i in onnx_model_paths:
    trans.convert_onnx_to_pytorch(i)
```

你也可以在convert_onnx_to_pytorch()函数中指定experimental=True，此时允许转换得到的pytorch模型的输入batch_size>1。该参数默认为False：
```python
for i in onnx_model_paths:
    trans.convert_onnx_to_pytorch(i, experimental=True)
```

直接调用convert_onnx_to_pytorch_batch()函数也能实现上述功能：
```python
for i in onnx_model_paths:
    trans.convert_onnx_to_pytorch_batch()(i)
```

convert_onnx_to_pytorch()函数默认在当前路径下保存转换得到的pytorch模型，你也可以用pytorch_path指定保存路径：
```python
for i in onnx_model_paths:
    trans.convert_onnx_to_pytorch(i, pytorch_path='path/to/save')
```

另外，你可以直接通过main()函数一键运行以上流程，只需输入path，就会自动检索路径下的onnx模型并转换为pytorch模型：
```python
trans.main('path/contain/onnx')
```

删除路径下的所有onnx模型：
```python
utils.delete_onnx_models('path/to/delete')
```

删除路径下的所有pytorch模型：
```python
utils.delete_pytorch_models('path/to/delete')
```

获取onnxruntime在本机器支持的所有provider：
```python
providers = utils.get_onnxruntime_provider()
print(providers)
```

获取onnx模型的输入和输出，返回一个列表，每个元素是一个字典，键为name, type, shape：
```python
input_info = utils.get_onnx_input('path/to/onnx')
print(input_info)
output_info = utils.get_onnx_output('path/to/onnx')
print(output_info)
```

## 依赖
    Python>=3.6
    onnx>=1.13.1
    torch>=1.11.0

## 版本历史
- **1.0.0** (2023-09-12): 第一个正式版本
- **1.0.1** (2021-09-12): 删除了list_onnx_models()函数中不必要的递归调用
- **1.0.2** (2021-09-12): 增加了__version__属性
- **1.0.3** (2021-09-12): 修复NotImplementedError: Conversion not implemented for op_type=Relu6.
- **1.0.4** (2021-09-12): 把trans包中与模型检索和删除相关的函数移动到新的包utils
- **1.0.5** (2021-09-12): 添加了删除文件的提示
- **2.0.0** (2021-09-13): utils包增加了获取onnx模型输入输出信息的函数
- **2.0.1** (2021-09-13): 修复utils包不在shengtengconverter的__init__文件中定义
- **3.0.0** (2021-09-14): 
  - main()函数改名为convert_onnx_to_pytorch_all()
  - utils包增加检查pytorch模型是否包含结构信息的函数check_pytorch_model()
  - utils包增加获取pytorch模型字典的函数get_pytorch_state_dict()
  - utils包增加检索和删除tensorflow模型的函数list_tensorflow_models()和delete_tensorflow_models()
  - trans包增加转换pytorch模型为onnx模型的函数convert_pytorch_to_onnx()
  - trans包增加转换tensorflow_pb模型为onnx模型的函数convert_tensorflow_to_onnx()
  - trans包增加转换onnx模型为tensorflow_savedmodel模型的函数convert_onnx_to_tensorflow_savedmodel()
  - 规范了函数说明文档
- **3.1.0** (2021-09-14): 由于tensorflow-gpu库已经弃用，从requirements列表中移除
- **3.1.1** (2021-09-18): 
  - 修复NotImplementedError: auto_pad=SAME_UPPER functionality not implemented.
  - 修复ModuleNotFoundError: No module named 'onnx2pytorch'
- **3.1.2** (2021-09-18):
  - 修复NotImplementedError: Conversion not implemented for op_type=LRN.
  - 修复NotImplementedError: Extraction of attribute size not implemented.
  - 修复NotImplementedError: Extraction of attribute bias not implemented.
  - 修复TypeError: __init__() got an unexpected keyword argument 'weight_multiplier'，做了算子字典与构造函数参数的适配
- **3.1.3** (2021-09-18):
  - convert_onnx_to_pytorch_all()函数增加了异常处理，现在一个模型转换失败不会影响其他模型的转换
  - 增加了_convert_onnx_to_pytorch_test()函数，与前者的区别是没有异常处理，用于测试

## 作者
- **[张志扬](https://github.com/1963306815)**

## 联系方式
- **[张志扬](mailto:1963306815@qq.com)**