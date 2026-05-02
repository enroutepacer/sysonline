<div align="right">
  <a href="README.md">English</a> | <strong>中文</strong>
</div>

# SysOnline

基于 Python 和 Selenium 的自动刷课脚本，面向 `Sysu online edu platform` 用户。

## 简介
该脚本会自动播放同一个课程页面里的所有视频。同时提供 API 接口以自动完成小测（默认情况下为手动）

* 声明：
该项目是为了帮助 **因学术、时间冲突而有此需求的学生完成线上课程**。

## 环境
为能够在个人电脑上运行，需要具备以下环境：
1. > Python ( 建议 3.13+ )

2. > 与你浏览器版本对应的 Webdriver 驱动 --- [下载 Webdriver](#下载-webdriver)

## 使用指南
提供 `multi-core` 和 `single-core` 两个版本，除非你电脑是砖头，否则都推荐前者

运行前，确保这三个文件在同一路径下里：
> File
>> sysu_core.py \
>> driver.exe \
>> config.json 

留意终端的文本提示，终端会告诉一切

如果点了运行后，终端里 10s 内没弹出提示文字，说明你网络很差，等网好点再重试。

多开窗口数量可在 `config.json` 里修改，网差调少，加速调多

大模型 API 为可选项。如需配置，在 `config.json` 里填写


## 补充

### 下载 Webdriver
下载你浏览器版本对应的 webdriver :
* [Edge 驱动](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/)
* [Chrome 驱动](https://googlechromelabs.github.io/chrome-for-testing/#stable)
* [Firefox 驱动](https://github.com/mozilla/geckodriver/releases)

### 自动答题（multi-core only）
支持接入任意兼容 OpenAI 接口的 API 来自动答题。配置 API 后无报错情况下能实现全自动完成 100% 的课程

可以留空。执行到小测章节时，终端会出现手动答题提示

在 `config.json` 中配置以下字段：

| 字段 | 内容 |
|------|------|
| `APIKEY` | API 密钥 |
| `BASEURL` | 请求地址 |
| `MODELNAME` | 模型名称  |


### 其他网课平台
如果你是其他学校的同学，或者需要在别的平台刷课：

前去支持 —— [NoMooc](https://github.com/honghongzhong/NoMooc)
