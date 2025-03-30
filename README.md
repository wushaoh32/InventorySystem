# 基于Python+SQLite + Tkinter的备件库管理系统	

#### 1、页面设计：Tkinter

#### 2、模块安装

​	pandas模块

​	openyxal模块

#### 3、软件打包

​	安装pyinstaller
​        执行打包程序

```python
pyinstall -F main.py	
```



#### 注意：

​    ①安装Visual studio Code
​    ②下载python解释器
​    ③vscode配置python插件
​    ④在vscode的终端：检查pip是否最新 

```
python -m pip install --upgrade pip
```

 ⑤ 更换pip源

```
pip install pandas -i https://pypi.tuna.tsinghua.edu.cn/simple
```

 ⑥下载git , 在vscode的终端配置用户名和邮箱

```python
git config --global user.name "你的GitHub用户名"       
git config --global user.email "你的GitHubemail"  
```

 ⑦验证是否成功 

```
git config --globle --list
```

​    **1. 在 GitHub 上创建仓库**
   \- **步骤**：

​     1. 访问 [GitHub New Repository](https://github.com/new)。

​     2. 填写仓库名称 `innoventrySystem`。

​     3. 选择 **Public（公开）** 或 **Private（私有）**。

​     4. **不要勾选** “Initialize this repository with a README”（避免与本地仓库冲突）。

​     5. 点击 **Create repository**。



   **结果**：获取远程仓库的 URL，如：https://github.com/你的用户名/innoventrySystem.git
 **2. 在 VS Code 中关联并推送代码**
   \- **步骤**：

1、打开项目根目录（确保已初始化 Git 仓库）。

2、在终端执行以下命令关联远程仓库（替换为你的 URL）
git remote add origin https://github.com/你的用户名/innoventrySystem.git

3、**强制推送**（如果本地仓库已有文件且与远程冲突）：
git push -u origin main --force
\- 如果分支是 `master`，替换 `main` 为 `master`。

4、**正常推送**（如果本地是全新仓库）
	点击推送

