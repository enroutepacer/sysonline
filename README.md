<div align="right">
  <strong>English</strong> | <a href="README_zh.md">中文</a>
</div>

# SysOnline

A simple automation script built with Python and Selenium for users of `Sysu Online Edu Platform `

## Overview
This script automatically plays all the video courses inside one webpage efficiently, including reminders for possible quizzes (Yeah you have to finish the annoying lil test yourself).

* Declare:
It aims to help those *WHO ARE IN GREAT NEED OF COMPLETING ONLINE COURSE BECAUSE OF TIME AND ACADEMIC CONFLICT*

## Prerequisites
To run the script on your own PC successfully, the environments below are required.
1. > Python (3.13+ recommended)

2. > Webdriver (corresponding to your browser)---[Download Webdriver](#webdriver-download)

## Instructions
Two versions are provided, `multi-core` and `single-core`, of course if your PC is not a brick, I'd recommend the former one.


Make sure these three files are under the same path : 
> File
>> sysu_core.py \
>> driver.exe \
>> config.json 

Take care of the text in terminal, it tells everything

To modify the window count, either for a bad network condition, or for better efficiency, go to `config.json`.

If the instruction text in terminal does not pop up in the first place after the script run, it's mostly a network issue, try again later in a better network condition

## Add

### Webdriver download
Choose the driver that matches your browser version
* [Webdriver for Edge](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/)
* [Webdriver for Chrome](https://googlechromelabs.github.io/chrome-for-testing/#stable)
* [Webdriver for Firefox](https://github.com/mozilla/geckodriver/releases)

### Course on other platforms
If you are a student from another college or have video courses on other platform

go check and support [NoMooc](https://github.com/honghongzhong/NoMooc)