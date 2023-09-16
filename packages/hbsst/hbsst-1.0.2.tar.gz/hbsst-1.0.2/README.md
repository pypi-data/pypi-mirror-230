### 百度搜索提交工具

本工具将百度站长API提交的命令集成优化，改成利于使用的Python函数，方便程序调用。

本工具由heStudio开发，你可以通过 https://www.hestudio.net/ 前往heStudio博客。

### 结构
- `hbsst.py` (主程序, 隐藏)
- `hbsst_config.json` (预设文件)
- `hbsst_return.json` (系统返回值的文件)

### 使用方法
1. 首次使用

1.1. 你的设备需要安装Python 3，wget

1.2. 安装hbsst

```
pip install hbsst
```

1.3. 在工作目录创建预设

1.3.1. 新建 hbsst_config.json 文件

1.3.2. 写入预设

```json
{
    "预设名称": "百度站长的API接口调用地址"
}
```

例如：

```json
{
    "demo": "http://data.zz.baidu.com/urls?site=https://www.example.com&token=xxxxxxxxx"
}
```

2. 调用方法

例如：

```
python3 -c "import hbsst;hbsst.submit(config='demo', url='https://www.example.com/1.html')"
```

如果需要提交多个，可以用换行符`\n`隔开。

例如：
```
python3 -c "import hbsst;hbsst.submit(config='demo', url='https://www.example.com/1.html\nhttps://www.example.com/2.html')"
```

3. 获取返回结果

返回结果会保存在 `hbsst_return.json` 内，在执行命令是结果会直接输出人类可以看懂的文字。开发者可以通过获取success或error的存在状态来判断是否成功提交，可以通过获取error的值来获取错误码。有关 `hbsst_return.json` 的内容结构，你可以访问 https://ziyuan.baidu.com/linksubmit/index 获取。


### 贡献
你可以直接提交PR到本仓库。

### 反馈&建议
你可以使用以下方法：
- 向本仓库提交Issue
- 在 [heStudio Talking](https://www.hestudio.net/talking) 提交：https://www.hestudio.net/talking

### 赞助
https://www.hestudio.net/donate/
