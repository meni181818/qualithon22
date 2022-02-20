from time import sleep
from pymongo import MongoClient
from websocket import create_connection 

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


# setup chrome webdriver
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.implicitly_wait(5)
driver.maximize_window()

driver.get('http://34.196.190.67/')
driver.find_element(By.CSS_SELECTOR, 'a[href="/static/build-a-bot.html"]').click()
driver.find_element(By.CSS_SELECTOR, 'img[src="/static/door.png"]').click()
driver.find_element(By.ID, 'start').click()

# try the difrent buttons
for i in range(1, 6):
    driver.find_element(By.ID, f'c1submitbutton{i}').click()
    sleep(3)
    if not driver.current_url.endswith('c1'):
        break

# video
actions = ActionChains(driver)
actions.send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.TAB, Keys.SPACE, Keys.RIGHT, Keys.RIGHT, Keys.RIGHT, Keys.RIGHT, 'm')
actions.pause(4)
actions.perform()
driver.find_element(By.ID, 'aVideoSubmit').click()

# maze
maze_solutions = (
    'rrdrruuulluuruurrdddrrddddrdrrr',
    'rruuuurrrdrrrrurr',
    'rrddrrurrrddldllldlddrrrrrruururr',
)

exit_block = driver.find_element(By.CSS_SELECTOR, 'td.green')
exit_classes = exit_block.get_attribute('class')

# try all solutions
for solution in maze_solutions:
    driver.execute_script(f'direction = "{solution}"')
    # deep-purple
    driver.execute_script(f"arguments[0].setAttribute('class', '{exit_classes.replace('green', 'deep-purple')}')", exit_block)
    driver.find_element(By.ID, 'crystalMazeFormSubmit').click()
    sleep(3)
    if not driver.current_url.endswith('crystal_maze'):
        break

# map
actions = ActionChains(driver)
actions.send_keys(Keys.TAB, 'i')
for i in range(40):
    actions.send_keys(Keys.LEFT)
for i in range(17):
    actions.send_keys(Keys.UP)
actions.perform()
driver.find_element(By.ID, 'mapsChallengeSubmit').click()
sleep(3)

# not a bot
driver.execute_script('document.getElementById("notABotCaptchaSubmit").onclick= function() \
    {document.getElementById("notABotCaptchaWord").value=""; document.getElementById("notABotForm").submit();}')
driver.find_element(By.ID, 'notABotCaptchaSubmit').click()

# mongodb
req_code = driver.find_element(By.ID, 'challenge_code').text
cluster = MongoClient(r'mongodb+srv://tester:qualithon22@cluster0.unfcl.mongodb.net/mango-mongo-gate')
db = cluster['mango-mongo-gate']
collection = db['challenge']
res_code = collection.find_one({'code': req_code})['response']
driver.find_element(By.ID, 'mangoMongoResponse').send_keys(res_code, Keys.TAB, Keys.ENTER)

# socket
ws_url = driver.find_element(By.ID, 'wsurl').text
ws_token = driver.find_element(By.CSS_SELECTOR, 'div.lighten-3').text
ws = create_connection(ws_url)
ws.send(ws_token)
driver.find_element(By.ID, 'socketGateMessage').send_keys(ws.recv(), Keys.TAB, Keys.ENTER)

sleep(10)
