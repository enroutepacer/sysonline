import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.action_chains import ActionChains

# 抓取视频函数
def get_video_links(driver, href_prefix):
    links = []
    # 找到所有 fsresource li
    li_items = driver.find_elements(By.CSS_SELECTOR, "li.activity.fsresource.modtype_fsresource")

    for li in li_items:
        try:
            # 找到 badge-pill
            badge_elem = li.find_element(By.CSS_SELECTOR, "span.badge-pill")
            badge_class = badge_elem.get_attribute("class")
        except:
            badge_class = ""

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
def inject_and_return(driver):
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
                            currentTime: window.ActiveVideo.currentTime,
                            duration: window.ActiveVideo.duration
                        }};
                    """)
    return status


# 启动浏览器，跳转登陆界面
print("\n等待 “操作提示” 出现后再执行操作，若十秒内没有出现，则是网络问题，关闭重开\n")
service = Service(executable_path="msedgedriver.exe")
driver = webdriver.Edge(service=service)
driver.get('https://lms.sysu.edu.cn/my/')
time.sleep(2.0)

LOGIN_POSTFIX = '/login/index.php?authCAS=CAS'
btn_elem = driver.find_element(By.CSS_SELECTOR, f'a[href^="{LOGIN_POSTFIX}"]')
if  not btn_elem:
	print("\n ! ! ! 未找到登录按钮\n")
else:
	driver.execute_script("arguments[0].click();", btn_elem)



# 登录
input('\n================ 操作提示 ================\n\n1. 登录\n2. 选择一个课程，如《心理健康教育》，点进课程\n3. 请点击回车\n\n================ 操作提示 ================\n\n\n   ')


# 获取源网页和视频
VIDEO_LIST_URL = driver.current_url
VIDEO_PREFIX = 'https://lms.sysu.edu.cn/mod/fsresource/view.php?id='




'''
def get_video_links(web_driver, href_prefix):
	"""抓取页面中 href 以指定前缀开头的所有 a 元素，并返回链接列表。"""
	video_elements = web_driver.find_elements(By.CSS_SELECTOR, f'a[href^="{href_prefix}"]')
	video_links = [elem.get_attribute('href') for elem in video_elements]
	return video_links
'''

video_links = get_video_links(driver, VIDEO_PREFIX)

print(f'匹配到 {len(video_links)} 个视频链接')
for i, link in enumerate(video_links, 1):
	print(f'{i}. {link}')


VIDEO_ID = 'fsplayer-container-id_html5_api' # TODO: 替换为实际的 video 元素 ID
idx = 0;


while idx < len(video_links):
	link = video_links[idx]
	print(f'\n开始播放第 {idx+1} 个视频: {link}')
	driver.get(link)
	
	# 等待页面加载（可根据实际网络情况调整时长，或者改用显式等待 WebDriverWait）
	time.sleep(3)
	
	# 模拟点击页面空白处，解除"未交互阻止自动播放(autoplay policy)"的限制
	try:
		ActionChains(driver).move_to_element_with_offset(driver.find_element(By.TAG_NAME, 'body'), 10, 10).click().perform()
	except Exception:
		pass
	
	print("注入 JS 执行加速并开始监控播放进度...")
	while True:
		try:
			# 注入 JS
			status = inject_and_return(driver)
			
			if not status.get('found'):
				print("未找到视频元素，请检查 ID 是否正确或页面是否仍在加载...", end='\r')
				time.sleep(2)
				continue
				
			if status.get('ended'):
				print(f"\n第 {idx+1} 个视频播放完毕！准备切换下一个。")
				break
				
			currentTime = status.get('currentTime', 0)
			duration = status.get('duration', 1)
			
			# 如果未能成功获取到有效 duration，避免除零错误
			if duration > 0:
				progress = (currentTime / duration) * 100
				print(f"播放进度: {progress:.2f}% ({currentTime:.1f}s / {duration:.1f}s)", end='\r')
				
			time.sleep(2) # 每 2 秒读取一次数据，避免过于频繁干涉浏览器
			
		except Exception as e:
			print(f"\n执行 JS 获取数据出错: {e}")
			time.sleep(3)
	
	# 当处理完现有最后一个视频
	if idx == len(video_links) - 1:
		# 检查是否有做完练习题 才能看的视频
		driver.get(VIDEO_LIST_URL)
		is_test = driver.find_elements(By.CSS_SELECTOR, "div.availabilityinfo.isrestricted")

		if is_test:
			input("! 发现练习\n! 发现练习\n! 发现练习\n完成练习后点击回车继续\n")
			input("如确定练习已完成，请回车\n")
			new_count = 0
			new_all_links = get_video_links(driver, VIDEO_PREFIX)
			
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
			print("未发现练习\n")
	
	idx += 1


print("\n所有视频处理完成！")
