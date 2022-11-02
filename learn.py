# https://www.selenium.dev/documentation/webdriver/getting_started/first_script/

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def test_eight_components():
    # start the session
    driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()))

    # take action on browser - navigate to a web page
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")

    # request browser information 
    title = driver.title
    assert title == "Web form"

    # establish waiting strategy
    driver.implicitly_wait(0.5)

    # find an element
    text_box = driver.find_element(by=By.NAME, value="my-text")
    submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")

    # take action on element
    text_box.send_keys("Selenium")
    submit_button.click()

    message = driver.find_element(by=By.ID, value="message")
    # request element information
    value = message.text
    assert value == "Received!"

    # end the session
    driver.quit()


if __name__ == '__main__':
    test_eight_components()

