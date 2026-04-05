<div align="right">
  <a href="README.md">English</a> | <strong>中文</strong>
</div>

# SysOnline

基于 Python 和 Selenium 的自动刷课脚本，面向 `Sysu online edu platform` 用户。

## 简介
该脚本会自动播放同一个课程页面里的所有视频。如果中途有小测，也会弹出提醒（没错测试还得自己做）。

* 声明：
该项目是为了帮助 **因学术、时间冲突而有此需求的学生完成线上课程**。

## 环境
为能够在个人电脑上运行，需要具备以下环境：
1. > Python ( 建议 3.13+ )

2. > 与你浏览器版本对应的 Webdriver 驱动 --- [下载 Webdriver](#下载-webdriver)

## 使用指南
有 `multi-core` 和 `single-core` 除非你电脑是砖头，否则都推荐前者

运行前，确保这三个文件在同一路径下里：
> File
>> sysu_core.py \
>> driver.exe \
>> config.json 

留意终端的文本提示，终端会告诉一切

多开窗口数量可在 `config.json` 里修改，网差调少，加速调多

如果点了运行，终端里半天没弹出提示文字，说明你网络很差，等网好点再重试。

## 补充

### 下载 Webdriver
下载你浏览器版本对应的 webdriver :
* [Edge 驱动](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/)
* [Chrome 驱动](https://googlechromelabs.github.io/chrome-for-testing/#stable)
* [Firefox 驱动](https://github.com/mozilla/geckodriver/releases)

### 其他网课平台
如果你是其他学校的同学，或者需要在别的平台刷课：

前去支持 —— [NoMooc](https://github.com/honghongzhong/NoMooc)
