from selenium.webdriver.common.by import By

def by_text_click(self, text):
    self.driver.find_element_by_android_uiautomator(f"new UiSelector().text(\"{text}\")").click()

def by_text_disp(self, text):
    self.driver.find_element_by_android_uiautomator(f"new UiSelector().text(\"{text}\")").is_displayed()

def by_text_contains_disp(self, text):
    self.driver.find_element_by_android_uiautomator(f'new UiSelector().textContains("{text}")').is_displayed()

def by_text_contains_click(self, text):
    self.driver.find_element_by_android_uiautomator(f'new UiSelector().textContains("{text}")').click()

def by_text_scroll_click(self, text):
    self.driver.find_element_by_android_uiautomator(f"new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollIntoView(new UiSelector().text(\"{text}\").instance(0));").click()

def by_text_scroll_disp(self, text):
    self.driver.find_element_by_android_uiautomator(f"new UiScrollable(new UiSelector().scrollable(true).instance(0)).scrollIntoView(new UiSelector().text(\"{text}\").instance(0));").is_displayed()

def by_id_click(self, ID):
    self.driver.find_element(By.ID, f"{ID}").click()
def by_id_disp(self, ID):
    self.driver.find_element(By.ID, f"{ID}").is_displayed()
def by_id_send_keys(self, ID, text):
    self.driver.find_element(By.ID, f"{ID}").send_keys(text)
def by_xpath_click(self, xpath):
    self.driver.find_element(By.XPATH, f"{xpath}").click()
def by_xpath_disp(self, xpath):
    self.driver.find_element(By.XPATH, f"{xpath}").is_displayed()
def by_xpath_send_keys(self, xpath, text):
    self.driver.find_element(By.XPATH, f"{xpath}").send_keys(text)
def get_text_by_id(self,ID):
    self.driver.find_element(By.ID, f"{ID}").text
def get_text_by_xpath(self, xpath):
    self.driver.find_element(By.XPATH, f"{xpath}").text