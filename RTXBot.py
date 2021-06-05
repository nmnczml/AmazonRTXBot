from selenium import webdriver
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from time import sleep
import random
import ssl
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import telegram_send
import logging

# can use proxies,
def get_proxies(ua):
    proxies = []
    proxies_req = Request('https://www.sslproxies.org/')
    proxies_req.add_header('User-Agent', ua.random)
    context = ssl._create_unverified_context()

    proxies_doc = urlopen(proxies_req, context=context).read().decode('utf8')

    soup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_table = soup.find(id='proxylisttable')

  # Save proxies in the array
    for row in proxies_table.tbody.find_all('tr'):
        proxies.append({
            'ip':   row.find_all('td')[0].string,
            'port': row.find_all('td')[1].string})
    return proxies


def random_proxy(proxies):
    return random.choice(proxies)


def read_config(config_string):
    userName = parse_line(config_string[0])
    passWord = parse_line(config_string[1])
    driverPath = parse_line(config_string[2])
    userDataDir = parse_line(config_string[3])
    return  userName, passWord, driverPath, userDataDir


def parse_line(line):
    delim_loc = line.find('=')
    return line[delim_loc+1:].strip()


def Logger(str):
    logging.debug(str)
    # telegram_send.send(messages=[str])
    print(str)

def LoggerImportant(str):
    logging.debug(str)
    telegram_send.send(messages=[str])
    print(str)

def addItemToChart(driver):
    print(driver.current_url)
    # Checking for currently unavailable

    currentlyUnavailable = driver.find_elements_by_xpath(
        "//span[contains(@class,'a-size-medium a-color-price')]")

    if(len(currentlyUnavailable) > 0):
        cUDetails = currentlyUnavailable[0]
        if(str(cUDetails.text).lower() == "currently unavailable." or str(cUDetails.text).lower() == "derzeit nicht verfügbar." or str(cUDetails.text).lower() == "temporairement en rupture de stock." or str(cUDetails.text).lower() ==  "no disponible."  or str(cUDetails.text).lower() == "non disponibile."):
            Logger("Currently Unavailable.")
            return False

    

    # Checking for currently unavailable
    shipsToYourLocations = driver.find_elements_by_xpath(
        "//div[@id='ddmDeliveryMessage']/span[@class='a-color-error']")

    if(len(shipsToYourLocations) > 0):
        Logger("Doesnt ships to your location")
        return False
        
    # Checking for direct add to chart button
    isThereDirectAddToChartButtons = driver.find_elements_by_xpath(
        "//input[@id='add-to-cart-button']")

    isAmazonSeller = driver.find_elements_by_xpath("//a[@id='sellerProfileTriggerId']")
    
    if(len(isThereDirectAddToChartButtons) > 0 and len(isAmazonSeller)>0):
        if("amazon" in str(isAmazonSeller[0].text).lower()):
            addToChartButton = isThereDirectAddToChartButtons[0]
            addToChartButton.click()
            Logger("Clicked add to chart")
            return True

    # Available from these sellers link
    availableFromTheseSellersLinks = driver.find_elements_by_xpath(
        "(//span[@data-action='show-all-offers-display']//a)[2]")
    
    #Alternative sellers link
    if(len(availableFromTheseSellersLinks) == 0):
        availableFromTheseSellersLinks = driver.find_elements_by_xpath(
            "//span[@id='buybox-see-all-buying-choices']/span[@class='a-button-inner']/a[@class='a-button-text']")

    
    if(len(availableFromTheseSellersLinks) > 0):
        availableFromTheseSellersLink = availableFromTheseSellersLinks[0]
        availableFromTheseSellersLink.click()
        Logger("Clicked available sellers")

        availableSellerArray = driver.find_elements_by_xpath(
            "//div[@id='aod-offer']")

        for i in range(len(availableSellerArray)):

            cnt = str(i + 1)

            soldByHtml = driver.find_element_by_xpath(
                "//div[@id='aod-offer']["+cnt+"]/*[contains(@id,'aod-offer-soldBy')]").text

            if("amazon" in str(soldByHtml).lower()):
                Logger("found amazon.com seller, added to chart")
                driver.find_element_by_xpath(
                    "//div[@id='aod-offer'][" + cnt + "]//*[contains(@class,'a-button-input')]").click()
                return True

        Logger("Nothing found")

        return False

 
def clickAndWaitForPageToLoadXPath(driver, elementLocator):

    elements = driver.find_elements_by_xpath(elementLocator)
    if (len(elements) == 0):

        Logger("No elements " + elementLocator + " ClickAndWaitForPageToLoad")
        return

    element = elements[0]
    element.click()
    
def clickAndWaitForPageToLoad(driver, elementLocator):

    elements = driver.find_elements_by_id(elementLocator)
    if (len(elements) == 0):

        Logger("No elements " + elementLocator + " ClickAndWaitForPageToLoad")
        return

    element = elements[0]
    element.click()


def buyItem(driver):

    # proceed check out
    clickAndWaitForPageToLoadXPath(driver, "//a[@id='hlb-ptc-btn-native']")
    LoggerImportant('Proceed To Checkout')
    
    # deliver to this address.
    clickAndWaitForPageToLoadXPath(
        driver, "//form[@class='a-nostyle'][1]/div[@class='a-spacing-base address-book']//*[normalize-space(text()) = 'Deliver to this address']")

    LoggerImportant('Proceed To deliver to this address')
    
    # click continue button shipping options
    continueButtons = driver.find_elements_by_xpath(
        "//input[@class='a-button-text']")
    
    
    for element in continueButtons:
        element.click()
        break
    LoggerImportant('Proceed To continue shipping')

    # click continue button payment options
    continueButtonsPayments = driver.find_elements_by_xpath(
        "//input[@name='ppw-widgetEvent:SetPaymentPlanSelectContinueEvent']")

    for element in continueButtonsPayments:
        element.click()
        break

    LoggerImportant('Proceed To Payment Options')

    # place your order button
    placeYourOrder = driver.find_elements_by_xpath(
        "//input[@class='a-button-text place-your-order-button']")

    for element in placeYourOrder:
        element.click()
        break
    
    importantMsg = driver.find_elements_by_xpath(
        "//div[@class='a-box-inner a-alert-container']")
    
    if(len(importantMsg)>0):
        LoggerImportant("Important message"+importantMsg[0].text)
        return
    
    LoggerImportant('Proceed To Place Order')

    sleep(300)

def getURIList(driver,store):
    urlList = []
    pageCount=0
    while(True):
        delay = 3 # seconds
        sleep(delay)
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'a-last')))
        searchResults = driver.find_elements_by_xpath("//*[contains(@class, 'a-section a-spacing-medium')]") #search Result

        for result in searchResults:
            innerText = result.text
            if('3070' not in innerText and '3080' not in innerText):
                continue
            
            # if store=='.com' and 'Ships to Turkey' in innerText:
            if store=='.com' and 'Temporarily' not in innerText:
               
                urlList.append(result.find_elements_by_xpath('.//h2/a')[0].get_attribute('href'))

            if store=='.co.uk' and 'Temporarily' not in innerText:
               
                urlList.append(result.find_elements_by_xpath('.//h2/a')[0].get_attribute('href'))
            
            if store=='.ca' and 'Temporarily' not in innerText:
               
                urlList.append(result.find_elements_by_xpath('.//h2/a')[0].get_attribute('href'))
    
            if store=='.fr' and 'Temporairement' not in innerText:
               
                urlList.append(result.find_elements_by_xpath('.//h2/a')[0].get_attribute('href'))

            if store=='.de' and 'Temporarily' not in innerText:
               
                urlList.append(result.find_elements_by_xpath('.//h2/a')[0].get_attribute('href'))

            if store=='.es' and 'Temporalmente' not in innerText:
               
                urlList.append(result.find_elements_by_xpath('.//h2/a')[0].get_attribute('href'))
                
    
    
        nextResult = driver.find_elements_by_xpath("//li[@class='a-last']/a")
        pageCount=pageCount+1
        print('Page:'+str(pageCount))
        if(len(nextResult)>0):
            nextResult[0].click()
        else:
            break
    return urlList     


def scrapeSearchListCa():
    storeCa = 'https://www.amazon.ca/s?i=electronics&bbn=677243011&rh=n%3A677243011%2Cp_36%3A60000-200000%2Cp_72%3A11192169011%2Cp_89%3AAsus%7CEVGA%7CMSI%7CZotac&dc&qid=1617970100&rnid=7590290011&ref=sr_nr_p_89_4'
    scrapeSearchList(storeCa)
    
def scrapeSearchListCom():
    storeCom ='https://www.amazon.com/s?i=computers-intl-ship&bbn=16225007011&rh=n%3A16225007011%2Cn%3A193870011%2Cn%3A17923671011%2Cn%3A284822%2Cp_n_feature_four_browse-bin%3A16955282011%7C6066318011%2Cp_n_feature_twenty-one_browse-bin%3A21563385011&dc&qid=1617969135&rnid=21563384011&ref=sr_nr_p_n_feature_twenty-one_browse-bin_3'
    scrapeSearchList(storeCom)
    
def scrapeSearchListDe():
    storeDe = 'https://www.amazon.de/s?k=Graphics+Cards&i=computers&bbn=430161031&rh=n%3A430161031%2Cp_6%3AA301WKE65PGVT5%7CA3JWKAKR8XB7XF%7CA3OJWAJQNSBARP%2Cp_n_feature_seven_browse-bin%3A15664227031&dc=&language=en&_encoding=UTF8&c=ts&qid=1617969888&rnid=428358031&ts_id=430161031&ref=sr_nr_p_36_6&low-price=500&high-price=1500'
    scrapeSearchList(storeDe)
    
def scrapeSearchListFr():
    storeFr = 'https://www.amazon.fr/s?keywords=Cartes+graphiques&i=computers&bbn=430340031&rh=n%3A430340031%2Cp_36%3A50000-150000%2Cp_6%3AA1X6FK5RDHNB96&dc&_encoding=UTF8&c=ts&qid=1617969576&rnid=437864031&ts_id=430340031&ref=sr_nr_p_6_7'
    scrapeSearchList(storeFr)
    
def scrapeSearchListEs():
    storeEs = 'https://www.amazon.es/s?i=computers&bbn=937935031&rh=n%3A937935031%2Cp_n_feature_seven_browse-bin%3A16069169031%2Cp_36%3A50000-150000%2Cp_6%3AA1AT7YVPFBWXBL&dc&qid=1617970181&rnid=831275031&ref=sr_nr_p_6_3'
    scrapeSearchList(storeEs)
    
def scrapeSearchListIt():
    storeIt = 'https://www.amazon.it/s?i=computers&bbn=460090031&rh=n%3A460090031%2Cp_n_feature_seven_browse-bin%3A16067946031%2Cp_6%3AA11IL2PNWYJU7H&dc&qid=1617970325&rnid=490203031&ref=sr_nr_p_6_2'    
    scrapeSearchList(storeIt)
 

def scrapeSearchList(productURI):
    store ='.com'
    
    if 'https://www.amazon.com' in productURI:
        store='.com'
    elif 'https://www.amazon.ca' in productURI:
        store='.ca'
    elif 'https://www.amazon.es' in productURI:
        store='.es'
    elif 'https://www.amazon.it' in productURI:
        store='.it'
    elif 'https://www.amazon.fr' in productURI:
        store='.fr'
    elif 'https://www.amazon.de' in productURI:
        store='.de'
        
    
    
    driver = getDriverByCountry(store)

    try:
        driver.get(productURI)



        print('going For '+store)
        urlList = getURIList(driver, store)
        
        for uri in urlList:
            search_and_click(uri,store)
                    
      
        


    except Exception as e:
        print(e)
        # driver.quit()

 

def search_and_click(productURI, store):

    driver = getDriverByCountry(store)

    try:
        driver.get(productURI)

        # check for dogs

        dogs = driver.find_elements_by_xpath(
            "//div[@class='nav-footer-line'] | //img[@alt='Dogs of Amazon']")

        if(len(dogs) > 0):
            if dogs[0].tag_name == "img":
                Logger("Saw dogs, continue...")
                sleep(600)
                # driver.quit()
                return

        addedToChart = addItemToChart(driver)

        if(addedToChart):
            buyItem(driver)

         

    except Exception as e:
        print(e)
        # driver.quit()

def login(store):
    
    driver = getDriverByCountry(store)
    driver.get('https://www.amazon%s' % store)
    
    # loggin in
    try:

        # cookie accept
        clickAndWaitForPageToLoad(driver, "sp-cc-accept")
        sleep(2)
    except:
        # there may not be cookie query;
        print("No accept cookie message")

    clickAndWaitForPageToLoad(driver, "nav-link-accountList")
    sleep(3)

    try:
        # userName
        apMail = driver.find_element_by_id("ap_email")
        apMail.send_keys(userName)
        clickAndWaitForPageToLoad(driver, "continue")
        sleep(3)
    except:
        Logger("Already Logged In")

    try:
        # passWord
        apPwd = driver.find_element_by_id("ap_password")
        apPwd.send_keys(passWord)
        driver.find_element_by_name("rememberMe").click()

        clickAndWaitForPageToLoad(driver, "signInSubmit")
        sleep(3)
    except:
        Logger("Already Logged In")

    
    return driver


    

def getDriverByCountry(d):
    global drv1
    global drv2
    global drv3
    global drv4
    global drv5
    global drv6
    global drv7
    
    if(d == '.com'):
        return drv1
    if(d == '.ca'):
        return drv2
    if(d == '.de'):
        return drv3
    if(d == '.fr'):
        return drv4
    if(d == '.es'):
        return drv5
    if(d == '.it'):
        return drv6
    
     

def init(d, driverPath,ua,userDataDir):
    global drv1
    global drv2
    global drv3
    global drv4
    global drv5
    global drv6
 
     
    options = webdriver.ChromeOptions()
    # options.add_argument('--proxy-server=%s'%(proxy['ip'] + ':' + proxy['port']))
    options.add_argument('user-agent=%s' % ua.random)
    options.add_argument('--no-sandbox')
    options.add_argument("--enable-file-cookies")
    options.add_argument("disable-infobars")
    options.add_argument("test-type")
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless")
    options.add_argument("--disable-extensions")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--disable-gpu")
    options.add_argument("--profile-directory=SeleniumTest")

 
    if(d == '.com'):
        drv1 = webdriver.Chrome(driverPath, chrome_options=options)
    if(d == '.ca'):
        options.add_argument(userDataDir+'2')
        drv2 = webdriver.Chrome(driverPath, chrome_options=options)
    if(d == '.de'):
        options.add_argument(userDataDir+'3')
        drv3 = webdriver.Chrome(driverPath, chrome_options=options)
    if(d == '.fr'):
        options.add_argument(userDataDir+'4')
        drv4 = webdriver.Chrome(driverPath, chrome_options=options)
    if(d == '.es'):
        options.add_argument(userDataDir+'5')
        drv5 = webdriver.Chrome(driverPath, chrome_options=options)
    if(d == '.it'):
        options.add_argument(userDataDir+'6')
        drv6 = webdriver.Chrome(driverPath, chrome_options=options)
 
 
if __name__ == "__main__":
    logging.basicConfig(handlers=[logging.FileHandler(filename="./logs.txt", 
                                                encoding='utf-8', mode='a+')],
                    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", 
                    datefmt="%F %A %T", 
                    level=logging.DEBUG)    # filename = 'credentials.txt'

    
    
    with open('config.txt', 'r') as config:
        config_values = config.readlines()

    userName, passWord, driverPath, userDataDir = read_config(config_values)

    ua = UserAgent(verify_ssl=False)
    storeList = ['.com','.ca','.de','.fr','.es']

    for store in storeList:
        init(store, driverPath,ua,userDataDir)
        login(store)
                
    while(True):
        for store in storeList:
            try:
            
                if(store=='.ca'):
                    scrapeSearchListCa()
                elif(store=='.com'):
                    scrapeSearchListCom()
                elif(store=='.de'):
                    scrapeSearchListDe()
                elif(store=='.fr'):
                    scrapeSearchListFr()
                elif(store=='.es'):
                    scrapeSearchListEs()
                elif(store=='.it'):
                    scrapeSearchListIt()
            except Exception as e:
                print(e)