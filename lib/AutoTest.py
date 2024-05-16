from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time

class Browser:
    def __init__(self, log):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1080")  
        #options.add_argument('--start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--incognito')

        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
        options.add_argument(f'--user-agent={user_agent}')

        self.log = log
        #service = Service('chromedriver.exe')
        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10) 
        self.driver.implicitly_wait(10)
        
    def quit(self):
        if self.driver:
            self.driver.quit()

    def get_info(self):
        try:
            capabilities = self.driver.capabilities
            self.log.info("Browser Capabilities:")
            for key, value in capabilities.items():
                self.log.info(f"{key}: {value}")
        except Exception as e:
            self.log.error(f"Get chromedriver information Error: {e}")
        finally:
            self.quit()
            
    def check_page_msg(self, by, value, expected_text):
        try:
            element = self.wait.until(EC.presence_of_element_located((by, value)))
            text = element.text.strip()
            self.log.info(f"Page title: {text}")
            if text == expected_text:
                self.log.info(f"Check page title PASS")
                return "PASS"
            else:
                self.log.error(f"Check page title FAIL")
                return "FAIL"
        except:
            self.log.error(f"Check page title ERROR")
            return "FAIL"
        
    def check_calender_msg(self, by, value):
        try:
            element = self.wait.until(EC.presence_of_element_located((by, value)))
            text = element.get_attribute("value")
            
            day = str(datetime.now().day).zfill(2)
            month = str(datetime.now().month).zfill(2)
            year = str(datetime.now().year)[2:]
            expected_text = f"{day}/{month}/{year}"    
                
            if text == expected_text:
                self.log.info(f"Expected text: {expected_text}")
                self.log.info(f"Check calender edit result PASS")
                return "PASS"
            else:
                self.log.error(f"Check calender edit result FAIL")
                return "FAIL"
        except:
            self.log.error(f"Check calender edit result FAIL")
            return "FAIL"
            
    def action(self, text, by, value, click=False, input=False, input_text=None, quit=True):
        try:
            if click:
                button = self.wait.until(EC.presence_of_element_located((by, value))).click()
                self.log.info(f"Click [{text}] button SUCCESS")
                return button
            elif input:
                Input = self.wait.until(EC.presence_of_element_located((by, value)))
                Input.send_keys(input_text)
                self.log.info(f"Input [{text}] {input_text} SUCCESS")
                return Input
            else:
                loc = self.wait.until(EC.presence_of_element_located((by, value)))
                self.log.info(f"Find [{text}] location SUCCESS")
                return loc
        except:
            self.log.error(f"Find [{text}] location FAIL")
            if quit:
                self.quit()
            raise ValueError(f"Find [{text}] location FAIL")
            
        
    def email_login(self, url, user, pwd, type='button', login=True, quit=True):
        try:
            self.driver.get(url) 
            self.log.info(f"Enter: {url}")
            self.action("Login", By.XPATH, "//a[contains(@class, 'MuiButtonBase-root css-1bgy2za')]", click=True)
            self.action("Email", By.NAME, "username", input=True, input_text=user)
            password_input = self.action("Password", By.NAME, "password", input=True, input_text=pwd)
            
            if type == "button":
                self.action("Continue", By.NAME, "action", click=True)
            elif type == "enter":
                password_input.send_keys(Keys.ENTER)

            if login:
                result = self.check_page_msg(By.CSS_SELECTOR, "div.MuiTypography-root.MuiTypography-subtitle2.css-1qy3x3m span", "Discover")
                if result == "PASS":
                    self.log.info(f"Email sign in PASS")
            else:
                msg = self.action("Wrong password", By.ID, "error-element-password")
                msg = msg.text
                self.log.info(f"Response: {msg}")
                if msg:
                    self.log.info(f"Email sign in FAIL")
                    result = "PASS"
                else:
                    result = "FAIL"
  
            if quit:
                self.quit()
            return result
            
        except:
            self.quit()
            return "FAIL"
            
    def google_oauth(self, url, email, pwd, login=True):
        try:
            self.driver.get(url)
            self.action("Login", By.XPATH, "//a[contains(@class, 'MuiButtonBase-root css-1bgy2za')]", click=True)
            self.action("Google Oauth", By.XPATH, '//button[@data-provider="google"]', click=True)
            self.action("Email", By.CSS_SELECTOR, 'input[type="email"]', input=True, input_text=email)
            self.action("Continue", By.XPATH, '//*[@id="identifierNext"]', click=True)
            time.sleep(5)
            self.action("Password", By.CSS_SELECTOR, 'input[type="password"]', input=True, input_text=pwd)
            self.action("Continue", By.XPATH, '//*[@id="passwordNext"]', click=True)

            if login:
                result = self.check_page_msg(By.CSS_SELECTOR, "div.MuiTypography-root.MuiTypography-subtitle2.css-1qy3x3m span", "Discover")
                if result == "PASS":
                    self.log.info(f"Google OAuth sign in PASS")
            else:
                msg = self.action("Wrong password", By.XPATH, "//div[@jsname='B34EJ']/span")
                msg = msg.text
                self.log.info(f"Response: {msg}")
                if msg:
                    self.log.info(f"Google OAuth sign in FAIL")
                    result = "PASS"
                else:
                    result = "FAIL"
            self.quit()
            return result
        except:
            self.quit()
            return "FAIL"

    def log_out(self, url, profile_url, user, pwd):
        try:
            self.email_login(url, user, pwd, quit=False)
            self.driver.get(profile_url)            
            self.log.info(f"Switch to profile page: {profile_url}")
            self.action("Logout", By.XPATH, "//button[contains(@class, 'MuiButtonBase-root css-1boyka8') and contains(., 'Log out')]", click=True)
            self.action("Logout check", By.XPATH, "//button[contains(@class, 'MuiButtonBase-root css-19nb63g') and contains(., 'Yes')]", click=True)
            result = self.check_page_msg(By.XPATH, "//h5[contains(@class, 'MuiTypography-root MuiTypography-h5 css-1vo4g6s')]", "Login to Practice")
            self.quit()
            return result
        except:
            self.quit()
            return "FAIL"
                
    def calendar_change(self, url, profile_url, user, pwd):
        try:
            self.email_login(url, user, pwd, quit=False)
            self.driver.get(profile_url)            
            self.log.info(f"Switch to profile page: {profile_url}")
            self.action("Edit Profile", By.XPATH, "//a[@href='/profile/account/edit']", click=True)
            self.action("Birthday", By.XPATH, "//div[contains(@class, 'MuiBox-root css-ilwfk7') and contains(., 'Birthday')]", click=True)            
            cal = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[3]/div/div[2]/div/div[2]/div[1]/div'))).find_elements(By.CLASS_NAME, 'css-1rmp3tn')
            
            try:
                now = datetime.now()
                date = (now.year, now.month, now.day)
                self.log.info(f"Selected calender date: {date}")
                a = 0 
                for w, we in enumerate(cal, start=1):
                    week = we.find_elements(By.CLASS_NAME, 'css-ltumv2')
                    for i in range(len(week)):
                        z = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[3]/div/div[2]/div/div[2]/div[1]/div/div[' + str(w+1) +']/div[' + str(i+1) +']/div/button')))
                        if z.text == str(datetime.now().day) and z.get_attribute('tabindex') == '0':
                            z.click()
                            a+=1
                            break
                    if a != 0:
                        break            
            except:
                self.log.error(f"Selected calender date FAIL")
                raise ValueError(f"Selected calender date FAIL")
                
            self.action("Edit Calender OK", By.XPATH, "//button[contains(@class, 'MuiButtonBase-root css-1t3xflr') and contains(., 'OK')]", click=True)    
            self.action("Save", By.XPATH, "//div[contains(@class, 'em-button-base')]", click=True)   
            
            # Check
            time.sleep(3)
            self.action("Edit Profile", By.XPATH, "//a[@href='/profile/account/edit']", click=True)
            result = self.check_calender_msg(By.CSS_SELECTOR, ".MuiInputBase-root.MuiInputBase-colorPrimary.Mui-readOnly.ia-form-layout_date.MuiInputBase-readOnly.css-5ozf5f input")
            self.quit()
            return result
        except:
            self.quit()
            return "FAIL"    
        
    def google_oauth_sign_up(self, url, user, pwd):
        try:
            self.driver.get(url)
            self.action("Sign up", By.XPATH, '//a[@class="MuiButtonBase-root css-158skc7"]', click=True)
            self.action("Google Oauth", By.XPATH, '//button[@data-provider="google"]', click=True)
            self.action("Email", By.CSS_SELECTOR, 'input[type="email"]', input=True, input_text=user)
            self.action("Continue", By.XPATH, '//*[@id="identifierNext"]', click=True)
            time.sleep(5)
            self.action("Password", By.CSS_SELECTOR, 'input[type="password"]', input=True, input_text=pwd)
            self.action("Continue", By.XPATH, '//*[@id="passwordNext"]', click=True)
            time.sleep(5)
            
            try:
                self.action("Verify", By.CSS_SELECTOR, 'div[jsname="uRHG6"] button span[jsname="V67aGc"]', click=True, quit=False)
            except:
                self.log.warning("This account has already been signed up.")
            
            result = self.check_page_msg(By.CSS_SELECTOR, "div.MuiTypography-root.MuiTypography-subtitle2.css-1qy3x3m span", "Discover")
            self.quit()
            return result
        
        except:
            self.quit()
            return "FAIL"            

               
class Test:
    def __init__(self, setting, log):
        self.log = log
        self.url = setting['URL']
        self.profile_url = setting['Profile_URL']
        self.email = setting['Email']
        self.gouth_email = setting['Gouth_email']
        self.pwd = setting['Password']
        self.g_pwd = setting['Gouth_password']
        self.wrong_pwd = "alatest123456789"
        
    def get_chromedriver_info(self):
        browser = Browser(self.log)
        browser.get_info()

    def Email_login_pass_w_button(self):
        browser = Browser(self.log)
        res = browser.email_login(self.url, self.email, self.pwd, type = "button")         
        return res
        
    def Email_login_pass_w_enter(self):
        browser = Browser(self.log)
        res = browser.email_login(self.url, self.email, self.pwd, type = "enter")  
        return res    
    
    def Email_login_fail(self):
        browser = Browser(self.log)
        res = browser.email_login(self.url, self.email, self.wrong_pwd, type = "button", login=False)  
        return res    
        
    def Google_oauth_login_pass(self):
        browser = Browser(self.log)        
        res = browser.google_oauth(self.url, self.gouth_email, self.g_pwd)   
        return res
    
    def Google_oauth_login_fail(self):
        browser = Browser(self.log)        
        res = browser.google_oauth(self.url, self.gouth_email, self.wrong_pwd, login=False)   
        return res
        
    def Logout(self):
        browser = Browser(self.log)     
        res = browser.log_out(self.url, self.profile_url, self.email, self.pwd)    
        return res
        
    def Calendar_Change(self):
        browser = Browser(self.log)  
        res = browser.calendar_change(self.url, self.profile_url, self.email, self.pwd)
        return res
    
    def Google_oauth_signup(self):
        browser = Browser(self.log)        
        res = browser.google_oauth_sign_up(self.url, self.gouth_email, self.g_pwd)   
        return res        



