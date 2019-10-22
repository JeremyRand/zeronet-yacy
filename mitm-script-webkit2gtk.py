import urllib.parse
import requests

from selenium import webdriver
from selenium.webdriver.webkitgtk.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities    
import selenium.common.exceptions

from time import sleep

from mitmproxy import http
from mitmproxy.script import concurrent

def _wait_for_html(driver):
    logWrapperRemaining = 2
    logFrameRemaining = 1
    log404Remaining = 1

    duration = 10
    precision = 5
    for i in range(duration * precision):
        sleep(1 / precision)

        print("Checking console to see if page has loaded...")
        for entry in driver.get_log('browser'):
            print(entry['message'])
            if '"[Wrapper]"' in entry['message']:
                logWrapperRemaining = logWrapperRemaining - 1
            if '"WrapperZeroFrame"' in entry['message']:
                logFrameRemaining = logFrameRemaining - 1
            if 'the server responded with a status of 404 (Not Found)' in entry['message']:
                log404Remaining = log404Remaining - 1

        if logWrapperRemaining <= 0 and logFrameRemaining <= 0:
            print("Page has loaded according to console!")
            break

        if log404Remaining <= 0:
            print("Page gave 404 according to console!")
            break

        iframe_count = len(driver.find_elements_by_tag_name('iframe'))
        #print("iframe count =", iframe_count)
        if iframe_count == 0:
            #print("No iframe present")
            html_wrapper = driver.execute_script("return document.documentElement.innerHTML;")
            if "<h1>Not Found</h1>" in html_wrapper:
                html = html_wrapper
                return html
            continue

        try:
            driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))
        except selenium.common.exceptions.NoSuchElementException:
            driver.switch_to_default_content()
            continue
        html = driver.execute_script("return document.documentElement.innerHTML;")
        driver.switch_to_default_content()
        if "<h1>Not Found</h1>" in html:
            break
        #print(len(driver.get_log('browser')))
        #print("Log messages:")
        #for entry in driver.get_log('browser'):
        #    print(entry)

    print("Grabbing DOM...")

    driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))
    html = driver.execute_script("return document.documentElement.innerHTML;")
    driver.switch_to_default_content()

    return html
        

@concurrent
def request(flow):
    
    #print("User-Agent:", flow.request.headers["User-Agent"])
    is_yacy = "User-Agent" in flow.request.headers and "yacy" in flow.request.headers["User-Agent"].lower()

    url = flow.request.pretty_url

    if not is_yacy:
        # This is probably a request from Chromium looking for images or other subresources.  Just return a redirect.
        flow.request.port = 43110
        #print("Redirected Chromium to an image or other subresource:", url)
        return

    r = requests.get(url)
    if r.status_code in [200, 404]:
    #if url.endswith(".jpg") or url.endswith(".jpeg") or url.endswith(".gif") or url.endswith(".png") or urllib.parse.urlparse(url).path == "/robots.txt":
        # This is probably a request from YaCy looking for images.  Just return a redirect.
        # Note: "/robots.txt" has only been tested with a zite for which it returned a 404 error (which was HTML-formatted).
        flow.request.port = 43110
        #print("Redirected YaCy to an image:", url)
        return

    #print("Replacing YaCy", url, "with Selenium result")

    webkit_options = Options()
    # Old Chromium stuff
    #chrome_options.binary_location = "/usr/bin/chromium-browser"
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--window-size=1024,768")
    #chrome_options.add_argument("--no-sandbox")
    #print("Created Chrome options")
    
    dc = DesiredCapabilities.WEBKITGTK
    # Old Chromium stuff
    #dc['loggingPrefs'] = {'browser': 'ALL'}
    
    driver = webdriver.WebKitGTK(options=webkit_options, desired_capabilities=dc)
    #print("Created driver")
    driver.get(url)
    #print("Got page")
    #html = _wait_for_html(driver)
    #sleep(10)
    #print("Page has rendered")
    #print("iframe count:", len(driver.find_elements_by_tag_name('iframe')))
    try:
        #driver.switch_to_frame(driver.find_element_by_tag_name('iframe'))
        html = _wait_for_html(driver)
    except selenium.common.exceptions.NoSuchElementException:
        flow.request.port = 43110
        print("Redirected YaCy to an unknown resource without iframe:", url)
        driver.close()
        return
    #driver.switch_to_active_element()
    #print("Switched to iframe")
    #sleep(10)
    #driver.execute_script("var links = document.links; for(var i = 0; i < links.length; i++) { var anchor = links[i]; var pathnameComponents = anchor.pathname.split('/'); if(anchor.host == '127.0.0.1:43110' && pathnameComponents[0] == '' && pathnameComponents[1].endsWith('.bit')) {anchor.host = pathnameComponents[1]; anchor.port = '80'; anchor.pathname = '/' + pathnameComponents.slice(2).join('/');} }")
    #print("Patched links to use .bit")
    #driver.execute_script("var images = document.images; for(var i = 0; i < images.length; i++) { var img = images[i]; var src = img.src; var anchor = new URL(src); var pathnameComponents = anchor.pathname.split('/'); if(anchor.host == '127.0.0.1:43110' && pathnameComponents[0] == '' && pathnameComponents[1].endsWith('.bit')) {anchor.host = pathnameComponents[1]; anchor.port = '80'; anchor.pathname = '/' + pathnameComponents.slice(2).join('/'); img.src = anchor.href; } }")
    #print("Patched images to use .bit")
    #html = driver.execute_script("return document.documentElement.innerHTML;")
    #print("Got iframe innerHTML")
    #sleep(1)
    #driver.switch_to_default_content()
    #print("Restored driver to default")

    if "<h1>Not Found</h1>" in html:
        responseCode = 404
    else:
        responseCode = 200

    flow.response = http.HTTPResponse.make(responseCode, ("<!DOCTYPE html>\n<html>\n" + html + "\n</html>").encode('utf-8'), {"Content-Type": "text/html"})
    #print("Replaced response")
    driver.close()
