## WebUI 模块

- `WebuiXyzArgs`: 此类用于表示和管理XYZ绘图参数。它允许您使用不同的选项（例如 "Nothing", "Seed", "Steps", "Sampler" 等）设置X，Y和Z轴，并自定义绘图选项。

- `WebuiT2iClient`: 此类处理与T2i服务的交互。它允许您设置提示，负提示，采样器名称和其他参数，并向T2i服务发送请求。

<br>

### 如何生成XYZ图

以下是使用此代码库生成XYZ绘图的逐步指南：

1. **创建XYZ脚本参数**: 使用 `WebuiXyzArgs` 创建和管理XYZ绘图参数。
    - 不同变量对应的type名在[webui_xyz_args.py](https://github.com/troph-team/eval-it/blob/main/evalit/webui/webui_xyz_args.py)的`AXIS_TYPE_MAP` 
```python
args = WebuiXyzArgs(
    x_axis=["Prompt S/R", "girl, boy"],
    y_axis=["Seed", "12345, 54321"],
    z_axis=["Nothing", ""],
)
```

2. **初始化T2i客户端**: 使用XYZ脚本参数初始化客户端所需的参数。
    - 可以在 `WebuiT2iClient` 类中找到T2i请求的有效参数。 
```python
client = WebuiT2iClient(
    prompt="1girl",
    negative_prompt="(nsfw:1.5),...[rest of the content here]",
    sampler_name="Euler",
    xyz_script_args=list(args),
)
```

3. **发送请求**: 发送请求并接收包含图像的响应。

```python
res = client.send_request()

images = res["images"]
for i in range(len(images)):
    images[i].show()
```

<br>

### 查找参数

**XYZ绘图参数**: 您可以在 `WebuiXyzArgs` 类中的 `AXIS_TYPE_MAP` 中找到X，Y和Z轴的有效选项。

- 在[webui_xyz_args.py](https://github.com/troph-team/eval-it/blob/main/evalit/webui/webui_xyz_args.py)里有xyz轴可用变量的完整列表(`AXIS_TYPE_MAP`)。
- 实际变量在webui的[xyz plot脚本](https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/master/scripts/xyz_grid.py)里 `axis_options` 变量被定义, 如果出错以那个为准;
