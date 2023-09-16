# Fastapi CLI
在使用FastAPI前，我个人使用Flask居多，比较喜欢Flask的CLI，使用起来比较方便，这个项目就是解决FastAPI没有CLI的问题

使用它自动加载项目中已有的Typer实例

#### 使用前
假设我们的CLI代码在下面的路径**app/cli/__init__.py**
```python
import typer

app = typer.Typer()

@app.command()
def version():
    return "1.0.0"
```
为了方便执行，我们需要在项目根目录新增一个入口文件如**cli.py**并添加下面的内容
```python
from app.cli import app

if __name__ == __main__:
    app()
```
最后执行
```shell
python cli.py --help
```
#### 使用后
使用fastcli由于app.cli:app在默认路径下，因此会自动加载，我们只需要运行下面的命令即可
```shell
fastcli --help
```
## 安装使用
#### 安装
```shell
pip install fastapi-fastcli

# 安装TAB自动补全
fastcli --install-completion
```
#### 查看路由列表
```shell
fastcli routes
```
![fastcli run](https://github.com/wezhai/fastapi-fastcli/raw/release/src/img/fastcli_run.png)
#### 启动FastAPI应用
```shell
fastcli run
```
![fastcli routes](https://github.com/wezhai/fastapi-fastcli/raw/release/src/img/fastcli_routes.png)


在运行时所在的目录 查找下列路径
```txt
- app.commands:app
- app.cli:app
- cli:app
- main:cli
- manage:cli
- app:cli
```
你也通过环境变量 **TYPER_APP**指定

功能
- 查看路由
- 启动FastAPI应用（uvicron）
