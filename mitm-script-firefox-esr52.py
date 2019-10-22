import urllib.parse
import requests
import subprocess
import os
import os.path
import random

from time import sleep
from pathlib import Path

from mitmproxy import http
from mitmproxy.script import concurrent

@concurrent
def request(flow):
    
    #print("User-Agent:", flow.request.headers["User-Agent"])
    is_yacy = "User-Agent" in flow.request.headers and "yacy" in flow.request.headers["User-Agent"].lower()

    url = flow.request.pretty_url.replace("127.0.0.1:81", flow.request.headers["Host"], 1)

    if not is_yacy:
        # This is probably a request from Firefox/Chromium looking for images or other subresources.  Just return a redirect.
        flow.request.port = 43110
        #print("Redirected Firefox/Chromium to an image or other subresource:", url)
        return

    r = requests.get(url)
    if r.status_code in [200, 404]:
        # This is probably a request from YaCy looking for images.  Just return a redirect.
        flow.request.port = 43110
        #print("Redirected YaCy to an image:", url)
        return

    #print("Replacing YaCy", url, "with rendered result")

    # Pick a random filename to store the rendered HTML
    print("Getting page...")
    outpath = "./rendered/" + ( '%064x' % random.SystemRandom().randrange(16**64) ) + ".html"

    # Ask Firefox to render the page
    try:
        subprocess.run(["firefox", "-print", url, "-print-mode", "html", "-print-file", outpath, "-print-delay", "10"], check=True)
    except subprocess.CalledProcessError:
        responseCode = 404
        flow.response = http.HTTPResponse.make(responseCode, ("<!DOCTYPE html>\n<html><body><h1>Not Found</h1></body></html>").encode('utf-8'), {"Content-Type": "text/html"})
        return

    # Wait for Firefox to write the rendered HTML to the file.
    while not os.path.isfile(outpath):
        sleep(1)
    sleep(1)

    # Set html to the rendered content
    html = Path(outpath).read_text()

    # Delete rendered file since we're done with it
    os.remove(outpath)

    if "<h1>Not Found</h1>" in html:
        responseCode = 404
    else:
        responseCode = 200

    flow.response = http.HTTPResponse.make(responseCode, html.encode('utf-8'), {"Content-Type": "text/html"})
    #print("Replaced response")

