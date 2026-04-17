# Windows 桌面壳说明

本目录提供的是可选的 Windows 桌面包装层，不是项目主运行入口。

默认情况下，项目直接通过浏览器访问 `python -m a13_starter.api_server` 即可；只有在需要封装成桌面应用时，才需要使用本目录。

## 1. 作用

桌面壳会做两件事：

- 在本地进程内启动 A13 服务
- 使用 `pywebview` 把现有网页界面包成桌面窗口

## 2. 适用场景

- 需要给老师或评委演示“桌面应用形态”
- 需要生成 Windows 可执行程序
- 不适合把浏览器直接暴露给最终使用者的场景

## 3. 目录内文件

- `launcher.py`：桌面壳启动入口
- `build_windows_app.ps1`：Windows 打包脚本

## 4. Smoke Test

在仓库根目录执行：

```powershell
python a13_starter\desktop\launcher.py --smoke-test
```

如果返回 `server_ready`，说明内嵌服务启动正常。

## 5. Windows 打包

### 第一步：准备工具目录

可以通过环境变量指定工具目录：

```powershell
$env:A13_WINDOWS_TOOL_ROOT="D:\develop\a13-app-tools"
```

如果不设置，脚本会默认使用仓库根目录下的 `.desktop_tools`。

### 第二步：准备虚拟环境

确保下列路径存在：

```text
<A13_WINDOWS_TOOL_ROOT>\venv\Scripts\python.exe
```

### 第三步：执行打包

```powershell
powershell -ExecutionPolicy Bypass -File .\a13_starter\desktop\build_windows_app.ps1
```

打包输出位于：

```text
<A13_WINDOWS_TOOL_ROOT>\build\dist\CareerLoopA13App\CareerLoopA13App.exe
```

## 6. 注意事项

- 桌面壳只是现有 Web 项目的包装，不会替代核心逻辑
- 正式提交和答辩时，浏览器版已经足够，不必强制打包桌面版
- 如果要在 Windows 机器上打包，建议先用浏览器版把主流程联调稳定后再做
