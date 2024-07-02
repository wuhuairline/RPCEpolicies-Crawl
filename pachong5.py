#encoding=utf-8

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import csv
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

# 创建浏览器实例
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
driver = webdriver.Chrome(options=chrome_options)

driver.implicitly_wait(10)  # 在创建WebDriver实例后添加隐式等待，等待时间为5秒
prev_titles = set()  # 用于存储前一页的标题

# 打开指定的网页
url = "https://sousuo.www.gov.cn/zcwjk/policyDocumentLibrary?q=&t=zhengcelibrary"#q=&t=需要检索的关键字
driver.get(url)
driver.set_window_size(1920, 1080)  # 设置窗口大小为1920x1080
# 点击“全文”标签
full_text_button=driver.find_element(By.XPATH,"//*[@id='app']/div/div[2]/div[3]/div[2]/div[1]/ul/li[1]/div[2]/a[1]")
full_text_button.click()
date_order_button=driver.find_element(By.XPATH,"//*[@id='app']/div/div[2]/div[3]/div[2]/div[1]/ul/li[1]/div[1]/a[2]")
date_order_button.click()


# 创建一个CSV文件并写入表头
csv_filename = "D:\桌面文件\BIT_管理科学与工程_博士\论文1\数据收集\语料库self\语料url.csv"
csv_file = open(csv_filename, "w", newline="", encoding="utf-8-sig")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["标题", "URL", "发布时间"])

papers_need=58491
# 赋值序号, 控制爬取的文章数量
count = 1

# 找到所有包含页码的<li>标签
# 等待加载完全，休眠3S
time.sleep(1)
page_elements = driver.find_elements(By.CLASS_NAME, 'number')

max_page=0
# 循环遍历每个页码<li>标签
for page_element in page_elements:
    # 提取页码文本并转换为整数
    page_number = int(page_element.text)
    print(page_number)
    # 更新最大页码
    if page_number > max_page:
        max_page = page_number

print(f'最大页码为：{max_page}')
while count <= papers_need:
    # 等待加载完全，休眠3S
    time.sleep(3)
    #循环快
    block_list=driver.find_elements(By.CLASS_NAME,'middle_result_con')
    #block_list = WebDriverWait(driver, 50).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'middle_result_con')))
    for parent_div in block_list:
        if count == papers_need: break
        try:
            print("find_parent")
            # 检查parent_div是否包含子元素
            if parent_div.find_elements(By.CLASS_NAME, 'dys_middle_result_content_item'):
                child_divs = parent_div.find_elements(By.CLASS_NAME, 'dys_middle_result_content_item')
                print("find_child")
            else:
                print("No child elements found in parent_div")
                # 如果没有子元素，跳出循环
                break  # 跳出当前循环
            # 循环遍历所有子<div>
            for div in child_divs:
                try:

                    # 在当前<div>标签块内查找<h5>标签
                    title_tag = div.find_element(By.XPATH,
                        './/h5[@class="dysMiddleResultConItemTitle"]')  # 将"class-name"替换为你的class名
                    # 提取<h5>标签内的文本
                    title = title_tag.text

                    #避免重复
                    if title in prev_titles:
                        continue

                    # 在当前子<div>内进行操作，例如提取文本或属性
                    # 在当前<div>标签块内查找<a>标签
                    a_tag = div.find_element(By.XPATH,'.//a')
                    # 获取<a>标签的href属性
                    href = a_tag.get_attribute("href")

                    parent_date_element = div.find_element(By.XPATH,'./p[@class="dysMiddleResultConItemRelevant clearfix1"]')
                    # 获取日期元素
                    date_element = parent_date_element.find_element(By.XPATH, './span[2]')
                    date = date_element.text

                    # 将数据写入CSV文件
                    # 写入文件
                    csv_writer.writerow([title, href, date])
                    #res = f"{href}\t{text}".replace(
                        #"\n", "") + "\n"
                    #print(f"第{count}条：{res}")
                    #with open('res.tsv', 'a', encoding='gbk') as f:
                        #f.write(res)
                except Exception as e:
                    print("error::", str(e))
                    print(f" 第{count} 条爬取失败\n")
                    # 跳过本条，接着下一个
                finally:
                    # 计数,判断需求是否足够
                    count += 1
                    if count == papers_need: break
        except Exception as e:
            print("An error occurred:", str(e))


    # // *[ @ id = "app"] / div / div[2] / div[3] / div[2] / div[2] / div / div[1] / div[1]
    # // *[ @ id = "app"] / div / div[2] / div[3] / div[2] / div[2] / div / div[1] / div[2]
    # // *[ @ id = "app"] / div / div[2] / div[3] / div[2] / div[2] / div / div[1] / div[2] / a
    # // *[ @ id = "app"] / div / div[2] / div[3] / div[2] / div[2] / div / div[1] / div[2] / a / h5
    #date.Xpath=//*[@id="app"]/div/div[2]/div[3]/div[2]/div[2]/div/div[2]/div/p[2]/span[2]
    # 检查当前页码是否已达到最大页码，如果是，则停止循环
    current_page = int(driver.find_element(By.CSS_SELECTOR, 'li.number.active').text)
    print(f"current_page:{current_page}")
    if current_page == max_page:
        print("break")
        break
    # 切换到下一页
    WebDriverWait(driver, 150).until(EC.presence_of_element_located((By.CLASS_NAME, "btn-next"))).click()

csv_file.close()
driver.quit()