#!/usr/bin/python3

# cookidump
# Original GitHub project:
# https://github.com/auino/cookidump

import argparse
import io
import pathlib
import time
from os import path
from os import walk
from urllib.parse import urlparse
from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PAGELOAD_TO = 3
SCROLL_TO = 1
MAX_SCROLL_RETRIES = 50
LOGIN_RETRIES = 10

username = ""
password = ""


def startBrowser(chrome_driver_path):
    """Starts browser with predefined parameters"""
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
    return driver


def listToFile(browser, baseDir):
    """Gets html from search list and saves in html file"""
    filename = baseDir + 'index.html'
    # creating directories, if needed
    path = pathlib.Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    # getting web page source
    # html = browser.page_source
    html = browser.execute_script("return document.documentElement.outerHTML")
    # saving the page
    with io.open(filename, 'w', encoding='utf-8') as f: f.write(html)


def recipeToFile(browser, filename):
    """Gets html of the recipe and saves in html file"""
    # creating directories, if needed
    path = pathlib.Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    # getting web page source
    html = browser.page_source
    # saving the page
    with io.open(filename, 'w', encoding='utf-8') as f: f.write(html)


def downloadRecipe(recipeURL, brw, outputdir):
    try:
        # building urls
        u = str(urlparse(recipeURL).path)
        u = u.replace("../", "")
        if u[0] == '/':
            u = u[1:]
        relative_root = "".join(["../"] * u.count('/'))
        outputPath = outputdir + u + '.html'
        if path.exists(outputPath):
            return
        # opening recipe url
        redirect(brw, recipeURL)
        time.sleep(PAGELOAD_TO)
        # removing the base href header
        try:
            brw.execute_script("var element = arguments[0];element.parentNode.removeChild(element);",
                               brw.find_element_by_tag_name('base'))
        except:
            pass
        # removing the name
        brw.execute_script("var element = arguments[0];element.parentNode.removeChild(element);",
                           brw.find_element_by_tag_name('core-transclude'))
        # changing the top url
        brw.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);",
                           brw.find_element_by_class_name('page-header__home'), 'href', relative_root + 'index.html')

        els = brw.find_elements_by_class_name('link--alt')
        for el in els:
            recipeURL = el.get_attribute('href')
            u = urlparse(recipeURL).path
            if len(u) > 1:
                brw.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);", el, 'href',
                                   relative_root + (u[1:] if u[0] == '/' else u) + '.html')

        # saving the file
        recipeToFile(brw, outputPath)
    except:
        pass


def formatUrl(url):
    if url.endswith(".html"):
        url = url[:-5]
    while url.count("//"):
        url = url.replace("//", "/")
    return url


def run(webdriverfile, outputdir, elementClassName):
    """Scraps all recipes and stores them in html"""
    print('[CD] Welcome to cookidump, starting things off...')
    # fixing the outputdir parameter, if needed
    if outputdir[-1:][0] != '/': outputdir += '/'

    locale = str(input('[CD] Complete the website domain: https://cookidoo.'))
    baseURL = 'https://cookidoo.{}/'.format(locale)

    brw = startBrowser(webdriverfile)

    # opening the home page
    redirect(brw, baseURL)
    time.sleep(PAGELOAD_TO)

    # recipes base url
    rbURL = 'https://cookidoo.' + str(locale) + '/search/'
    redirect(brw, rbURL)
    redirect(brw, brw.current_url.replace('context=recipes', '&context=collections'))
    time.sleep(PAGELOAD_TO)

    # possible filters done here
    input('[CD] Set your filters, if any, and then enter y to continue: ')

    print('[CD] Proceeding with scraping')

    # removing the base href header
    brw.execute_script("var element = arguments[0];element.parentNode.removeChild(element);",
                       brw.find_element_by_tag_name('base'))

    # removing the name
    brw.execute_script("var element = arguments[0];element.parentNode.removeChild(element);",
                       brw.find_element_by_tag_name('core-transclude'))

    # clicking on cookie accept
    try:
        brw.find_element_by_class_name('accept-cookie-container').click()
    except:
        pass

    # showing all recipes
    elementsToBeFound = int(brw.find_element_by_class_name('search-results-count__hits').get_attribute('innerHTML'))
    previousElements = 0
    count = 0
    while True:
        # checking if ended or not
        currentElements = len(brw.find_elements_by_class_name(elementClassName))
        if currentElements >= elementsToBeFound:
            break
        # scrolling to the end
        brw.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_TO)
        # clicking on the "load more recipes" button
        try:
            brw.find_element_by_id('load-more-page').click()
            time.sleep(PAGELOAD_TO)
        except:
            pass
        print("Scrolling [" + str(currentElements) + "/" + str(elementsToBeFound) + "]")
        # checking if I can't load more elements
        count = count + 1 if previousElements == currentElements else 0
        if count >= MAX_SCROLL_RETRIES:
            break
        previousElements = currentElements

    # saving all recipes urls
    els = brw.find_elements_by_class_name(elementClassName)
    collectionURLs = []
    for el in els:
        el = el.find_element_by_xpath('a')
        collectionURL = el.get_attribute('href')
        collectionURLs.append(collectionURL)
        brw.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);", el, 'href',
                           '.' + urlparse(collectionURL).path + '.html')

    # removing search bar
    brw.execute_script("var element = arguments[0];element.parentNode.removeChild(element);",
                       brw.find_element_by_tag_name('search-bar'))

    # removing scripts
    for s in brw.find_elements_by_tag_name('script'): brw.execute_script(
        "var element = arguments[0];element.parentNode.removeChild(element);", s)

    # saving the list to file
    listToFile(brw, outputdir)

    # getting all recipes
    for idx, collectionURL in enumerate(collectionURLs):
        print(f"Downloading collections {collectionURL} [{idx} / {len(collectionURLs)}]")
        downloadRecipe(collectionURL, brw, outputdir)

    files = [path.join(dp, f) for dp, dn, filenames in walk(outputdir) for f in filenames]
    urls = []
    for idx, file in enumerate(files):
        print(f"Getting hrefs from files [{idx} / {len(files)}]")
        soup = BeautifulSoup(open(file, 'rb'), 'html.parser')
        urls = urls + [baseURL + formatUrl(href) for href in
                       [el['href'] for el in soup.find_all("a", class_="link--alt")] if href]

    for idx, recipeURL in enumerate(urls):
        print(f"Downloading recipes {recipeURL} [{idx} / {len(urls)}]")
        downloadRecipe(recipeURL, brw, outputdir)

    # logging out
    logoutURL = 'https://cookidoo.' + str(locale) + '/profile/logout'
    redirect(brw, logoutURL)
    time.sleep(PAGELOAD_TO)

    # closing session
    print('[CD] Closing session\n[CD] Goodbye!')
    brw.close()


def redirect(brw, url):
    brw.get(url)
    count = 0
    while not isLogedIn(brw) and count < LOGIN_RETRIES:
        count += 1
        logIn(brw)
        brw.get(url)
    raise Exception("log in failed")


def isLogedIn(brw):
    return bool(brw.find_elements_by_css_selector(f'span[data-username="{username}"]'))


def logIn(brw):
    logIn = brw.find_element_by_css_selector("a[data-ga-event-label=Login]")
    logIn.click()
    try:
        emailInBox = brw.find_element_by_id("email")
        emailInBox.send_keys(username)
        passwordInBox = brw.find_element_by_id("password")
        passwordInBox.send_keys(password)
        submitBtn = brw.find_element_by_id("j_submit_id")
        submitBtn.click()
    except:
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dump Cookidoo recipes from a valid account')
    parser.add_argument('webdriverfile', type=str, help='the path to the Chrome WebDriver file')
    parser.add_argument('outputdir', type=str, help='the output directory')
    parser.add_argument('username', type=str, help='the path to the Chrome WebDriver file')
    parser.add_argument('password', type=str, help='the output directory')
    args = parser.parse_args()
    username = args.username
    password = args.password
    run(args.webdriverfile, args.outputdir, 'core-tile--collection')
    # run(args.webdriverfile, args.outputdir, 'link--alt', lambda el: el.get_attribute('href'))

# email
# j_submit_id
