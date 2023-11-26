from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException, TimeoutException,ElementNotInteractableException,NoSuchElementException,WebDriverException
from selenium.webdriver.chrome.options import Options
import pandas as pd
from random import randint
from time import sleep
import requests, os


class Bot:
    def __init__(self) -> None:
        os.makedirs('photos', exist_ok=True)
        chrome_options = Options()
        chrome_options.add_argument('--lang=en')  
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def find_element(self, element, locator, locator_type=By.XPATH,
            page=None, timeout=10,
            condition_func=EC.presence_of_element_located,
            condition_other_args=tuple()):
        """Find an element, then return it or None.
        If timeout is less than or requal zero, then just find.
        If it is more than zero, then wait for the element present.
        """
        try:
            if timeout > 0:
                wait_obj = WebDriverWait(self.driver, timeout)
                ele = wait_obj.until(EC.presence_of_element_located((locator_type, locator)))
                # ele = wait_obj.until( condition_func((locator_type, locator),*condition_other_args))
            else:
                print(f'Timeout is less or equal zero: {timeout}')
                ele = self.driver.find_element(by=locator_type,
                        value=locator)
            if page:
                print(
                    f'Found the element "{element}" in the page "{page}"')
            else:
                print(f'Found the element: {element}')
            return ele
        except (NoSuchElementException, TimeoutException) as e:
            if page:
                print(f'Cannot find the element "{element}"'
                        f' in the page "{page}"')
            else:
                print(f'Cannot find the element: {element}')


    def pagination(self):
        previous_url = self.driver.current_url
        page = int(previous_url.split('?page=')[-1]) if '?page=' in previous_url else 2
        url = previous_url + f'?page={page}' if '?page' not in previous_url else previous_url.split('?page=')[0] + f'?page={page + 1}'
        self.driver.get(url)
        return previous_url != self.driver.current_url

    def work(self):

        categories = []
        
        self.driver.get('https://www.machineseeker.com/#alphabetical-categories')
        # dropdown = driver.find_element(By.ID,'category-dropdown').click()
        sleep(randint(3,5))

        category_elements = self.driver.find_elements(By.CSS_SELECTOR,'.col-12 .row.mt-1.pt-1.border-top.align-items-start')

        for element in category_elements:
            # Extract category name
            category_name = element.find_element(By.CSS_SELECTOR,'.word-break h2 a').text.strip()

            # Extract category link
            category_link = element.find_element(By.CSS_SELECTOR,'.word-break h2 a').get_attribute('href')

            # Append to the categories list
            categories.append({'Category': category_name, 'Link': category_link})

        print(len(categories))
        try:
            df = pd.read_csv('machinary_deatils.csv')
        except:
            column_names = ['Title','Manufacturer','Model','Description','Category','Images','Product_link']
            df = pd.DataFrame(columns=column_names)
            df.to_csv('machinary_deatils.csv', index=False)
        # for i in categories:
        list_of_column = df[f'Product_link'].values.tolist()
        catagory = categories[0]['Category']
        self.driver.get(categories[0]['Link'])
        all_items = []
        get_all_in_page = self.driver.find_elements(By.XPATH,'//../section[3]/div[2]/div/a')
        for i in get_all_in_page:
            if i.get_attribute('href') not in list_of_column:
                df = pd.read_csv('machinary_deatils.csv')
                df = df.to_dict(orient='records')
                df.append({'Title':'', 'Manufacturer':'', 'Model':'', 'Description':'','Category': category_name, 'Images':'','Product_link': i.get_attribute('href')})
                pd.DataFrame(df).to_csv('machinary_deatils.csv', index=False)
        #     # cat = driver.find_element(By.ID,'main-content')
        #     # items = cat.find_elements(By.TAG_NAME,'section')
        # df = pd.read_csv('machinary_deatils.csv')
        # list_of_column = df[f'Product_link'].values.tolist()
        # while pagination():
        #     sleep(randint(3,5))
        #     get_all_in_page = driver.find_elements(By.XPATH,'//../section[3]/div[2]/div/a')
        #     for i in get_all_in_page:
        #         if i.get_attribute('href') not in list_of_column:
        #             df = pd.read_csv('machinary_deatils.csv')
        #             df = df.to_dict(orient='records')
        #             df.append({'Title':'', 'Manufacturer':'', 'Model':'', 'Description':'','Category': category_name, 'Images':'','Product_link': i.get_attribute('href')})
        #             pd.DataFrame(df).to_csv('machinary_deatils.csv', index=False)
        df = pd.read_csv('machinary_deatils.csv')
        print(len(df))
        breakpoint()
        for i in range(len(df)):
            if pd.isna(df.at[i, 'Title']):
                self.driver.get(df.at[i,'Product_link'])
                sleep(randint(3,5))
                print(i)
                title = self.driver.find_element(By.XPATH,'//*[@id="inserat-titel"]/div/div[1]').text.strip()
                manufact = self.driver.find_element(By.XPATH,'//*[@id="machine-data"]/div/div[2]/dl[2]/dd').text
                Model = self.driver.find_element(By.XPATH,'//*[@id="machine-data"]/div/div[2]/dl[3]/dd').text
                Description = self.driver.find_element(By.XPATH,'//*[@id="description"]/div/div[2]/div[1]/div').text
                Images = self.find_element('images','//*[@id="imageandplaceboxes"]/div/div[1]/div/div/div[1]/div/div/img',By.XPATH,timeout=4)
                if Images:
                    Images_url =Images.get_attribute('src')
                    response = requests.get(Images_url)
                    with open(f"{os.getcwd()}/photos/{title.replace(' ', '_').replace('.','').replace('/','')}.jpg", 'wb') as f:f.write(response.content)
                else:
                    slide = self.find_element('slide','//*[@id="imageandplaceboxes"]/div/div[1]/button[2]',By.XPATH)
                    if slide:
                        slide.click()
                        Images = self.find_element('images','//*[@id="imageandplaceboxes"]/div/div[1]/div/div/div[1]/div/div/img',By.XPATH)
                        if Images:
                            Images_url = Images.get_attribute('src')
                            response = requests.get(Images.get_attribute('src'))
                            with open(f"{os.getcwd()}/photos/{title.replace(' ', '_').replace('.','').replace('/','')}.jpg", 'wb') as f:f.write(response.content)
                df.at[i,'Title'] = title
                df.at[i,'Manufacturer'] = manufact
                df.at[i,'Model'] = Model
                df.at[i,'Description'] = Description
                df.at[i,'Images'] = Images_url if Images_url else ''
                df.to_csv('machinary_deatils.csv', index=False)


bot = Bot()
bot.work()