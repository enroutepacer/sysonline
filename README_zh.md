<div align="right">
  <a href="README.md">English</a> | <strong>中文</strong>
</div>

# SysOnline

一个基于 Python 和 Selenium 的简单自动化脚本，面向 `Sysu Online Edu Platform` 用户。

## 简介
该脚本会自动播放同一个课程页面里的所有视频。同时提供 API 接口以自动完成小测（默认情况下为手动）

* 声明：
该项目旨在帮助那些 **因时间和学业冲突而迫切需要完成线上课程的人**。

你可以在下面查看完整介绍，或者直接 [快速查看并下载](#快速查看并下载)

## 环境
为能够在个人电脑上运行，需要具备以下环境：
1. > Python ( 建议 3.13+ )

2. > 与你浏览器版本对应的 Webdriver 驱动 --- [下载 Webdriver](#下载-webdriver)

## 使用说明
提供 `multi-core` 和 `single-core` 两个安全版本，除非你电脑是砖头，否则都推荐前者。

`multi_core` 使用 **窗口池** 和 **API 配置**，`single_core` 是原始基准版本，包含基础的网页操作逻辑。

运行前，确保这三个文件在同一路径下：
> File
>> sysu_core.py \
>> driver.exe \
>> config.json 

留意终端里的文本提示，它会说明一切。

如果脚本运行后，终端里的提示文字没有在第一时间出现，通常是网络问题，等网络状况好一些再重试。

要修改 **窗口数量**，无论是因为网络较差还是想提升效率，都去 `config.json` 里调整。

API 配置是可选的。要配置你自己的 **API**，同样去 `config.json` 里填写。


## 快速查看并下载

* **sysu_multi_core.exe**：安全版（不会请求轰炸），速度 100%
* **sysu_risky_core.exe**：风险版（请求轰炸），速度 500%
* **sysu_test_redo.exe**：使用 AI 重新完成所有测试，获得更好的分数

**点击 [此处](https://github.com/EnroutePacer/SysOnline/releases/download/v2.1.0/dist.rar) 以下载**


## 附加

### 下载 Webdriver
选择与你浏览器版本匹配的驱动：
* [Edge Webdriver](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/)
* [Chrome Webdriver](https://googlechromelabs.github.io/chrome-for-testing/#stable)
* [Firefox Webdriver](https://github.com/mozilla/geckodriver/releases)

### 自动答题（multi-core only）
多核心版本可以使用任何兼容 OpenAI 的 API 来自动回答测验问题。

在 `config.json` 中配置以下字段（留空则回退到手动）：

| 字段 | 内容 |
|------|------|
| `APIKEY` | API 密钥 |
| `BASEURL` | 请求地址 |
| `MODELNAME` | 模型名称 |

### 其他平台课程
如果你是其他学院的学生，或者你的课程视频在别的平台：

去支持 [NoMooc](https://github.com/honghongzhong/NoMooc)
