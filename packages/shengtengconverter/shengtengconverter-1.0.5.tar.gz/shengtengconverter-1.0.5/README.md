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

## 作者
- **[张志扬](https://github.com/1963306815)**

## 联系方式
- **[张志扬](mailto:1963306815@qq.com)**