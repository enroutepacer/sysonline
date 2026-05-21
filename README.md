<div align="right">
  <strong>English</strong> | <a href="README_zh.md">中文</a>
</div>

# SysOnline

A simple automation script built with Python and Selenium for users of `Sysu Online Edu Platform `

## Overview
This script automatically plays all the video courses inside one webpage efficiently. Quizzes can also be finished by LLM if your own API is configured.

* Declare:
It aims to help those *WHO ARE IN GREAT NEED OF COMPLETING ONLINE COURSE BECAUSE OF TIME AND ACADEMIC CONFLICT*

you can view the full introduction in detail below, or [Quick check and download](#quick-check-and-download)

## Prerequisites
To run the script on your own PC successfully, the environments below are required.
1. > Python (3.13+ recommended)

2. > Webdriver (corresponding to your browser)---[Download Webdriver](#webdriver-download)

## Instructions
Two safe versions are provided, `multi-core` and `single-core`, of course if your PC is not a brick, I'd recommend the former one. 

`multi_core` uses **window pool** and **API configuration**, and `single_core` is the primitive baseline version, showing basical web-operating logic. 

Make sure these three files are under the same path : 
> File
>> sysu_core.py \
>> driver.exe \
>> config.json 

Take care of the text in terminal, it tells everything

If the instruction text in terminal does not pop up in the first place after the script run, it's mostly a network issue, try again later in a better network condition

To modify the **window count**, either for a bad network condition, or for better efficiency, go to `config.json`.

API configuration is optional. To configure your own **API**, go to `config.json`.


## Quick check and download

* **sysu_multi_core.exe**: Safe for account (No Request Flooding), 100% speed
* **sysu_danger_core.exe**: Risky for account (Request Flooding), 500% speed
* **sysu_test_redo.exe**: AI redo all the test for better score  

**Click [here](https://github.com/EnroutePacer/SysOnline/releases/download/v2.1.0/dist.rar) to download**

## Add

### Webdriver download
Choose the driver that matches your browser version
* [Webdriver for Edge](https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/)
* [Webdriver for Chrome](https://googlechromelabs.github.io/chrome-for-testing/#stable)
* [Webdriver for Firefox](https://github.com/mozilla/geckodriver/releases)

### LLM Auto-Answer (multi-core only)
The multi-core version can auto-answer quiz questions using any OpenAI-compatible API.

Set these fields in `config.json` (leave empty to fall back to manual):

| Field | Content |
|-------|------------|
| `APIKEY` | API key |
| `BASEURL` | Base URL  |
| `MODELNAME` | Model name |

### Course on other platforms
If you are a student from another college or have video courses on other platform

go check and support [NoMooc](https://github.com/honghongzhong/NoMooc)