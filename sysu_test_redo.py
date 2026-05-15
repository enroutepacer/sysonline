import os
import sys
import time
import json
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service


def resource_path(relative_path):
    """获取资源文件的绝对路径（兼容 PyInstaller 打包模式和开发模式）"""
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        external_path = os.path.join(exe_dir, relative_path)
        if os.path.exists(external_path):
            return external_path
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


# 读取配置
config_path = resource_path('config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

APIKEY = config.get('APIKEY', '')
BASEURL = config.get('BASEURL', '')
MODELNAME = config.get('MODELNAME', '')


def call_llm(prompt_text):
    """调用 LLM 并返回解析后的答案列表"""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {APIKEY}"}
    api_url = BASEURL if BASEURL.endswith("/chat/completions") else BASEURL.rstrip("/") + "/chat/completions"

    payload = {
        "model": MODELNAME,
        "messages": [
            {"role": "system", "content": "你是一个严格输出 JSON 的人工智能。绝不能返回任何带有 Markdown 的解释，仅返回合法的 JSON 对象。"},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.1
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    content = response.json()['choices'][0]['message']['content']

    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        return json.loads(match.group(0)).get("answers", [])
    print("未能从 LLM 返回中解析 JSON:\n", content)
    return []


def parse_and_answer_page(driver):
    """解析当前页面的所有题目，调用 LLM 获取答案并勾选"""
    questions = driver.find_elements(By.CSS_SELECTOR, "div.que")
    if not questions:
        return False

    prompt_text = "你是一个专业助教。请你帮我解答以下的单选/多选题以及判断题。请严格以 JSON 格式返回答案，格式为：{\"answers\": [{\"id\": \"题目ID\", \"choices\": [\"A\"]}]}。\n\n"
    question_map = {}

    for q in questions:
        q_id = q.get_attribute("id")
        q_class = q.get_attribute("class")

        if "multichoice" not in q_class and "truefalse" not in q_class:
            continue

        q_type = "多选题" if "multichoiceset" in q_class else "单选题"
        try:
            q_text_elem = q.find_element(By.CSS_SELECTOR, "div.qtext")
            prompt_text += f"题目ID: {q_id} ({q_type})\n{q_text_elem.text}\n"
        except:
            prompt_text += f"题目ID: {q_id} ({q_type})\n(无法获取题目文本)\n"

        q_options_map = {}
        options_elems = q.find_elements(By.CSS_SELECTOR, "div.answer > div[class^='r']")
        for opt_idx, opt in enumerate(options_elems):
            try:
                letter_elem = opt.find_element(By.CSS_SELECTOR, "span.answernumber")
                letter = letter_elem.text.replace(".", "").strip()
            except:
                letter = chr(ord('A') + opt_idx)

            try:
                text_elem = opt.find_element(By.CSS_SELECTOR, "div.flex-fill")
                opt_text = text_elem.text
            except:
                opt_text = opt.text

            prompt_text += f" {letter}. {opt_text}\n"

            try:
                input_elem = opt.find_element(By.CSS_SELECTOR, "input[type='radio'], input[type='checkbox']")
                q_options_map[letter] = input_elem
            except:
                pass

        prompt_text += "\n"
        question_map[q_id] = {"options": q_options_map}

    if not question_map:
        print("  本页未能解析到有效题目，跳过。")
        return False

    print(f"  本页 {len(questions)} 道题目，正在调用 LLM...")
    answers_list = call_llm(prompt_text)
    if not answers_list:
        return False

    # 勾选答案
    click_count = 0
    for ans in answers_list:
        q_id = ans.get("id")
        choices = ans.get("choices", [])
        if q_id not in question_map:
            continue
        for choice in choices:
            choice = str(choice).strip().upper()
            input_elem = question_map[q_id]["options"].get(choice)
            if input_elem:
                is_checked = driver.execute_script("return arguments[0].checked;", input_elem)
                if not is_checked:
                    driver.execute_script("arguments[0].click();", input_elem)
                    click_count += 1
                    time.sleep(0.3)

    print(f"  已勾选 {click_count} 个选项")
    return True


def LLM_kill_full_quiz(driver):
    """解析当前页面全部题目，调用 LLM 答题后提交。严格遵循原版提交流程。"""
    # 等待题目渲染完成
    print("  等待题目加载...", end='')
    for _ in range(20):
        questions = driver.find_elements(By.CSS_SELECTOR, "div.que")
        if questions:
            print(f" {len(questions)} 道题目已加载")
            break
        print('.', end='')
        time.sleep(0.5)
    else:
        print(" 超时，未检测到题目")

    try:
        parse_and_answer_page(driver)
    except Exception as e:
        print(f"  解析或答题出错: {e}")

    # 提交答案（严格遵循原版流程）
    try:
        time.sleep(0.5)
        # 尝试翻页按钮，不存在的话直接提交（单页练习）
        end_btn = driver.find_elements(By.ID, "mod_quiz-next-nav")
        if end_btn:
            driver.execute_script("arguments[0].click();", end_btn[0])
            time.sleep(2.0)
        else:
            print("  单页练习，直接提交...")
            time.sleep(1.0)

        submit_all_btn = driver.find_element(By.XPATH, "//button[contains(text(), '全部提交并结束')]")
        driver.execute_script("arguments[0].click();", submit_all_btn)
        time.sleep(1.0)
        confirm_submit_btn = driver.find_element(
            By.XPATH, "//div[contains(@class, 'confirmation-buttons')]//input[@value='全部提交并结束']"
        )
        driver.execute_script("arguments[0].click();", confirm_submit_btn)

        print("\n......LLM 答题完毕......\n")
        time.sleep(1.5)
        return True

    except:
        print("\n尝试自动提交答卷时遇错，请自行提交\n")
        return False


def start_quiz_attempt(driver, quiz_url):
    """
    进入一个练习页面并开始答题。
    处理三种情况：
    1. 直接有"开始答题"按钮（从未作答）
    2. 已有尝试记录，需要点击"重新答题"
    3. 需要点击"继续上次答题"
    """
    driver.get(quiz_url)
    time.sleep(2.0)

    # 情况1: "开始答题"按钮
    start_btns = driver.find_elements(By.CSS_SELECTOR, "div.quizstartbuttondiv button[type='submit']")
    if start_btns:
        try:
            driver.execute_script("arguments[0].click();", start_btns[0])
            time.sleep(1.5)
            confirm_btn = driver.find_element(By.ID, "id_submitbutton")
            driver.execute_script("arguments[0].click();", confirm_btn)
            time.sleep(2.0)
            print("  → 开始新的答题尝试")
            return True
        except Exception as e:
            print(f"  点击开始答题按钮后出错: {e}")
            return False

    # 情况2: "重新答题"
    retry_texts = ['重新答题', '再次答题', '重新作答']
    for text in retry_texts:
        retry_links = driver.find_elements(By.XPATH, f"//a[contains(text(), '{text}')]")
        if retry_links:
            try:
                driver.execute_script("arguments[0].click();", retry_links[0])
                time.sleep(2.0)
                print(f"  → 点击「{text}」")
                # 点击后可能还需要确认或直接进入答题页面
                # 检查是否有启动按钮
                start_btns2 = driver.find_elements(By.CSS_SELECTOR, "div.quizstartbuttondiv button[type='submit']")
                if start_btns2:
                    driver.execute_script("arguments[0].click();", start_btns2[0])
                    time.sleep(1.5)
                    confirm_btn = driver.find_element(By.ID, "id_submitbutton")
                    driver.execute_script("arguments[0].click();", confirm_btn)
                    time.sleep(2.0)
                return True
            except:
                continue

    # 情况3: "继续上次答题"
    continue_links = driver.find_elements(By.XPATH, "//a[contains(text(), '继续')]")
    if continue_links:
        try:
            driver.execute_script("arguments[0].click();", continue_links[0])
            time.sleep(2.0)
            print("  → 继续上次答题")
            return True
        except:
            pass

    print("  × 未能自动进入答题，请手动检查页面。")
    return False


def main():
    print("\n========== SYSU 自动重做器 ==========")
    print("         将逐个重做课程中的全部练习\n")

    if not APIKEY or not MODELNAME:
        print("错误：请先在 config.json 中配置 APIKEY、BASEURL 和 MODELNAME")
        input("\n按回车退出...")
        return

    # 启动浏览器
    service = Service(executable_path=resource_path("msedgedriver.exe"))
    driver = webdriver.Edge(service=service)
    driver.set_window_size(1000, 800)
    driver.get('https://lms.sysu.edu.cn/my/')
    time.sleep(1.2)

    # CAS 登录跳转
    btn_elem = None
    LOGIN_POSTFIX = '/login/index.php?authCAS=CAS'
    while not btn_elem:
        try:
            btn_elem = driver.find_element(By.CSS_SELECTOR, f'a[href^="{LOGIN_POSTFIX}"]')
        except Exception:
            time.sleep(0.2)
    driver.execute_script("arguments[0].click();", btn_elem)

    input('\n================ 操作提示 ================\n'
          '\n1. 登录统一认证'
          '\n2. 进入一个课程（如《心理健康教育》）'
          '\n3. 回到此窗口，按回车开始自动做题'
          '\n\n========================================\n')

    course_url = driver.current_url

    # 扫描课程页面上所有练习
    print("正在扫描课程中的全部练习...")
    time.sleep(1.5)

    quizzes = driver.find_elements(By.CSS_SELECTOR, "li.activity.quiz.modtype_quiz")
    quiz_links = []

    for quiz in quizzes:
        try:
            link_elem = quiz.find_element(By.CSS_SELECTOR, "a.aalink.stretched-link")
            quiz_url = link_elem.get_attribute("href")
            # 尝试获取练习名称
            quiz_name = link_elem.text.strip()
            if not quiz_name:
                quiz_name = quiz.text.strip()[:60]

            # 标记完成状态
            badges = quiz.find_elements(By.CSS_SELECTOR, "span.badge-pill")
            status = "已完成" if any("alert-success" in b.get_attribute("class") for b in badges) else "未完成"

            quiz_links.append((quiz_name, quiz_url, status))
        except Exception as e:
            continue

    if not quiz_links:
        print("未在课程页面找到任何练习。请确认是否在课程主页。")
        input("\n按回车退出...")
        driver.quit()
        return

    print(f"\n共发现 {len(quiz_links)} 个练习：")
    for i, (name, url, status) in enumerate(quiz_links, 1):
        short_name = name[:50] if name else f"练习{i}"
        print(f"  {i}. [{status}] {short_name}")

    print("\n开始逐个处理全部练习...\n")

    completed = 0
    failed = 0

    for idx, (quiz_name, quiz_url, status) in enumerate(quiz_links, 1):
        print(f"\n{'='*55}")
        print(f"  [{idx}/{len(quiz_links)}] {quiz_name[:50]}")
        print(f"  状态: {status}")
        print(f"{'='*55}")

        # 尝试进入答题
        ok = start_quiz_attempt(driver, quiz_url)
        if not ok:
            failed += 1
            continue

        # LLM 答题
        print("\n  🤖 LLM 正在答题...\n")
        try:
            if LLM_kill_full_quiz(driver):
                completed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  LLM 答题过程异常: {e}")
            failed += 1

        # 回到课程页面，准备下一个练习
        driver.get(course_url)
        time.sleep(2.0)

    # 汇总
    print(f"\n\n{'='*55}")
    print(f"  全部练习处理完毕！")
    print(f"  成功提交: {completed}  失败/跳过: {failed}  总计: {len(quiz_links)}")
    print(f"{'='*55}")

    input("\n按回车退出...")
    driver.quit()


if __name__ == '__main__':
    main()
