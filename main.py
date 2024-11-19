from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from datetime import datetime
import requests
import random
import time

# читаем список user_id из файла
with open('id.txt', 'r') as file:
    user_ids = [line.strip() for line in file.readlines()]

# читаем пароль из файла
with open('password.txt', 'r') as file:
    metamask_password = file.read().strip()

# функция для закрытия браузера по user_id
def close_browser(user_id):
    try:
        close_url = f"http://local.adspower.net:50325/api/v1/browser/stop?user_id={user_id}"
        requests.get(close_url).json()
    except Exception as e:
        print(f"Error while closing browser for {user_id}: {str(e)}")

# основная функция
def main():
    # перемешиваем список user_ids случайным образом перед началом обработки
    random.shuffle(user_ids)

    # основной цикл по каждому user_id
    for user_id in user_ids:
        if user_id.lower() == 'stop':
            break

        driver = None
        start_time = datetime.now()

        try:
            # открываем браузер для текущего user_id
            open_url = f"http://local.adspower.net:50325/api/v1/browser/start?user_id={user_id}"
            response = requests.get(open_url).json()

            # настройка ChromeDriver для удалённого подключения
            chrome_driver = response["data"]["webdriver"]
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", response["data"]["ws"]["selenium"])

            service = Service(executable_path=chrome_driver)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_window_size(1200, 720)

            # открываем кошелек и вводим пароль
            driver.get('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#unlock')
            time.sleep(1)
            password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
            password_field.send_keys(metamask_password)
            time.sleep(2)
            continue_button = driver.find_element(By.XPATH, '//button[contains(text(), "Разблокировать")]')
            continue_button.click()
            time.sleep(2)

            # выполняем дейлик с ожиданием видимости кнопки
            driver.get('https://points.reddio.com/task')
            wait = WebDriverWait(driver, 10)
            task_button = wait.until(EC.visibility_of_element_located((By.XPATH, '//html/body/div[1]/main/div/div[8]/div/div[2]/div[1]/button')))
            task_button.click()
            time.sleep(3)

            end_time = datetime.now()
            print(
                f"Completed work: {user_id} from {start_time.strftime('%Y-%m-%d %H:%M:%S')} to"
                f" {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except Exception as e:
            print(f"Error while working with {user_id}: {str(e)}")
            with open('error.txt', 'a') as error_file:
                error_file.write(f"{user_id}: {str(e)}\n")

        finally:
            # закрытие браузера в любом случае
            close_browser(user_id)
            if driver:
                driver.quit()

if __name__ == "__main__":
    main()
