# Diviner
基于周易蓍草占卜原理实现的中国古占卜, 该项目适配于 Nonebot2.

感谢熊逸先生的《周易江湖》对本项目提供的基本原理支持.

## 安装
### 直接安装
使用`pip`安装:
```sh
pip install nonebot-plugin-uvdiviner
```

### Nonebot2 安装
依次执行指令:
```sh
pip install nb-cli
nb create
```

选择`bootstrap`并输入自定义的项目名称, 随后选择`fastapi`、`httpx`以及`websockets`, 适配器选择`Onebot V11`回车, 执行以下指令切入 Nonebot2 项目文件夹:
```sh
cd [你的项目名称]
```

随后执行:
```sh
nb plugin install nonebot-plugin-uvdiviner
nb run --reload
```