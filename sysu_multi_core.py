import os
import time
import json
from collections import deque
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.action_chains import ActionChains
# 读取配置
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

class Window_worker:
    Is_new = 1
    Is_ended = 0
    id = ''

# 抓取视频函数
def Get_video_links(driver, href_prefix):
    links = []
    # 找到所有 fsresource li
    li_items = driver.find_elements(By.CSS_SELECTOR, "li.activity.fsresource.modtype_fsresource")

    for li in li_items:
        try:
            # 找到 badge-pill
            badge_elem = li.find_elements(By.CSS_SELECTOR, "span.badge-pill")
        except:
            badge_elem = ""
            
        for elem in badge_elem:
            badge_class = elem.get_attribute("class")
            # 如果没有 alert-success，说明未完成
            if "alert-success" not in badge_class:
                try:
                    a_elem = li.find_element(By.CSS_SELECTOR, f'a[href^="{href_prefix}"]')
                    link = a_elem.get_attribute("href")
                    links.append(link)
                except:
                    continue
    return links

# 注入 JS 函数
def Inject_and_check(driver):
    status = driver.execute_script(f"""
                        // 只注入一次全局控制
                                        
                        if (!window.Is_Injected) {{
                            // 覆盖原有的 alert 弹窗
                            window.alert = function(msg) {{ console.log("已阻止后台 alert:", msg); }};
                            
                            window.findvideo = function(root) {{
                                let v = root.querySelector('video');
                                if (v) return v;
                                let els = root.querySelectorAll('*');
                                for (let el of els) {{
                                    if (el.shadowRoot) {{
                                        v = window.findvideo(el.shadowRoot);
                                        if (v) return v;
                                    }}
                                }}
                                return null;
                            }};
                            
                            const video = window.findvideo(document) || document.getElementById('{VIDEO_ID}');
                            if (!video) return {{ found: false }};
                            
                            window.ActiveVideo = video;
                            // 该学校使用的是心跳请求，因此倍速没有意义
                            window.ActiveVideo.playbackRate = 1.0;
                            
                            // 启动持续监测，自动强制播放
                            window.Watcher = setInterval(() => {{
                                if (window.ActiveVideo && window.ActiveVideo.paused && !window.ActiveVideo.ended) {{
                                    console.log('检测到视频暂停，尝试播放...');
                                    window.ActiveVideo.play();
                                }}
                            }}, 1000);
                            
                            window.Is_Injected = true;
                        }}
                        
                        // 快速返回状态给 Python
                        if (!window.ActiveVideo) return {{ found: false }};
                        
                        return {{
                            found: true,
                            ended: window.ActiveVideo.ended,
                        }};
                    """)
    return status

# 阶段性检查函数
def Check_Do_test(driver, video_links, VIDEO_LIST, VIDEO_PREFIX):
    # 操作器回到主窗口
    driver.switch_to.window(Main_window)
    Is_test = 1
    is_test = driver.find_elements(By.CSS_SELECTOR, "div.availabilityinfo.isrestricted")

    if is_test:
        Is_test = 1
        input("\nTEST_______\n     ! 发现练习\n     ! 发现练习\n     ! 发现练习\n     完成练习后点击回车继续\n")
        input("确定已完成？如确定练习已完成，请再次点击回车\n")
        driver.get(VIDEO_LIST)
        new_count = 0
        new_all_links = Get_video_links(driver, VIDEO_PREFIX)
        
        # 更新待处理视频
        for new_link in new_all_links:
            if new_link not in video_links:
                video_links.append(new_link)
                new_count +=1

        if new_count != 0:
            print(f'\n发现{new_count}个新解锁视频\n进程继续中...\n')
        else:
            print('没有检测到新视频，该课程可能已完成\n') 
    else:
        # 用内部 is_test 来准确修改外部 Is_test
        Is_test = 0
        print("未进一步发现练习\n")

    return Is_test




    

'''-------------------------------驱动部分-------------------------------'''


print("\n等待 “操作提示” 出现后再执行操作，若十秒内没有出现，则是网络问题，关闭重开\n")


# 启动浏览器，跳转登陆界面
service = Service(executable_path="msedgedriver.exe")
driver = webdriver.Edge(service=service)
driver.set_window_size(800, 600)  
driver.get('https://lms.sysu.edu.cn/my/')
time.sleep(1.2)

btn_elem = None
LOGIN_POSTFIX = '/login/index.php?authCAS=CAS'
while not btn_elem:
    try:
        btn_elem = driver.find_element(By.CSS_SELECTOR, f'a[href^="{LOGIN_POSTFIX}"]')
    except Exception:
        time.sleep(0.2)
driver.execute_script("arguments[0].click();", btn_elem)



# 登录
input('\n================ 操作提示 ================\n\n1. 登录\n2. 选择一个课程，如《心理健康教育》，点进课程\n3. 请点击回车\n\n================ 操作提示 ================\n\n\n   ')



# 获取源网页和视频
VIDEO_LIST = driver.current_url
VIDEO_ID = 'fsplayer-container-id_html5_api' 
VIDEO_PREFIX = 'https://lms.sysu.edu.cn/mod/fsresource/view.php?id='

Main_window = driver.current_window_handle
video_links = Get_video_links(driver, VIDEO_PREFIX)
video_links = deque(video_links)

print(f'匹配到 {len(video_links)} 个视频链接')
for i, link in enumerate(video_links, 1):
	print(f'{i}. {link}')



# 创建窗口池
x = config.get('sysu_window_count', 1)
windows_pool = []
for k in range(x):
    driver.switch_to.new_window('window')
    driver.set_window_size(500, 600)
    driver.set_window_position(800+40*k, 80*k)

    w = Window_worker()
    w.id = driver.current_window_handle
    w.Is_new = 1
    windows_pool.append(w)
# 初始化窗口工作
On_working = 0
for k in range(x):
    driver.switch_to.window(windows_pool[k].id)
    if len(video_links) == 0:
        break
    driver.get(video_links[0])
    video_links.popleft()
    On_working += 1



# 默认有练习待进入大循环检查
Is_test = 1

# 总工作进度
while len(video_links) > 0 or On_working > 0 or Is_test == 1:

    print(f"\n工作窗口数量: {On_working}")
	# 遍历窗口池
    for k in range(x):
        
        driver.switch_to.window(windows_pool[k].id)
        # 检查是否为空窗口
        if driver.current_url == "about:blank":
            if(len(video_links) > 0):
                driver.get(video_links[0])
                video_links.popleft()
                On_working += 1
            elif not Is_test:
                time.sleep(0.5)
                continue

        else:
            # 检查窗口播放状态 (新视频需模拟点击)
            if windows_pool[k].Is_new:
                # 等待页面加载（可根据实际网络情况调整时长）
                time.sleep(2)
                windows_pool[k].Is_new = 0
                # 模拟点击页面空白处，解除 (autoplay policy) 的限制
                try:
                    ActionChains(driver).move_to_element_with_offset(driver.find_element(By.TAG_NAME, 'body'), 10, 10).click().perform()
                except Exception:
                    print("\n! ! ! 出现窗口未点击! ! ! 请确认窗口播放是否正常")
                    pass
            
            # 注入JavaScript，检查视频播放进度，并操作跳转新视频
            try: # 注入 JS
                status = Inject_and_check(driver)
                time.sleep(0.6)

                if not status.get('found'):
                    print("未找到视频元素，请检查 ID 是否正确或页面是否仍在加载...", end='\r')
                    time.sleep(2)
                    continue
                    
                if status.get('ended'):
                    if windows_pool[k].Is_ended == 0:
                        print(f"\n 一个视频播放完毕！({driver.current_url})\n剩余视频数: {len(video_links)}\n准备切换下一个...")
                    # 有剩余视频则切换
                    if len(video_links) > 0:
                        driver.get(video_links[0])
                        video_links.popleft()
                        windows_pool[k].Is_new = 1

                        # 视频是新补上来的则更新 On_working 数量
                        if windows_pool[k].Is_ended:
                            windows_pool[k].Is_ended = 0
                            On_working +=1
                    # 没有剩余视频则更新 On_working 数量
                    elif len(video_links) == 0 and not windows_pool[k].Is_ended:
                        windows_pool[k].Is_ended = 1
                        On_working -= 1
                        print(f"\n工作窗口数量: {On_working}")
                
            except Exception as e:
                print(f"\n执行 JS 获取数据出错: {e}")
                time.sleep(1)
                

    # 当处理完现有最后一个视频
    if len(video_links) == 0 and On_working == 0:
        # 检查是否有做完练习题 才能看的视频, 并更新待看链接
        Is_test = Check_Do_test(driver, video_links, VIDEO_LIST, VIDEO_PREFIX)
        time.sleep(5.0)
    time.sleep(3.0)



print("\nEND_______\n     自动进程已结束! ! !\n\n     可以检查是否有视频在其他页面\n\n     若没有, 则所有视频已处理完成! ! !\n")
