# ZeroNet YaCy Search Engine Scripts

This is a collection of scripts and instructions that can be used to set up a YaCy search engine instance that indexes ZeroNet sites.

Note: Testing is being done with Debian Buster on ppc64le.

## Instructions

### Install YaCy

You can build YaCy from source; follow the instructions at [YaCy's GitHub](https://github.com/yacy/yacy_search_server).

### Configure YaCy use case

YaCy Administration -> First Steps -> Use Case & Account -> Basic Configuration -> Use Case -> Intranet Indexing.

Then restart YaCy.

### Install ncdns

Right now, you need to use the experimental ZeroNet+YaCy fork of ncdns, which supports converting `zeronet` records to `A` records and supports converting DNS zonefiles to URL lists.  This fork is a very bad thing, and you really shouldn't be using it.  Best to wait until we've gotten it cleaned up and merged to master branch.  *We do these experiments so you don't have to!  -- Brainiac: Science Abuse*

Add the following in `ncdns.conf` and `ncdumpzone.conf`:

~~~
[noncompliance-experiments]

zeronet=true
zeronet-ip4="127.0.0.1"
only=true
~~~

### Install DNSSEC-Trigger

Configure DNSSEC-Trigger's Unbound instance to use ncdns for `bit.` as per the ncdns docs.

### Install ZeroNet

Make sure you enable transproxy mode, but leave the default port, like this:

~~~
python2 zeronet.py --ui_trans_proxy
~~~

Enable Tor if you like.

### Install mitmproxy

`pip3 install --user mitmproxy`

### Install Firefox

Must be ESR 52.  Anything else won't work.

### Install cmdlnprint

You need the ZeroNet fork of cmdlnprint.  This probably means you need to disable XPI signature checking in Firefox.

### Run mitmproxy

`./run-mitmproxy.sh`

### Test the transproxy with Firefox

Visit a ZeroNet site using its `.bit` domain in Firefox.  Make sure it looks okay.

### Test the transproxy with simulated YaCy

`./get-rendered-content.sh http://your-favorite-zeronet-domain.bit/`

Make sure the resulting content looks okay.

### Generate a URL list

Run `./gen-url-list-zeronet.sh`.

### Start a crawl

Start point: from file:<br>
*path to url-list-random-zeronet-only.txt*

Crawl depth:<br>
1 *(you can change this as you like)*

Crawler Filter: Load Filter on URL's: must match:<br>
`(http[s]?|ftp[s]?):\/\/[^\/]+\.bit\/.*`

Document Filter: Filter on Content of Document: must not match<br>
*Feel free to blacklist whatever spam you like here.  This probably isn't critical if you're just running a search engine, but if you intend to use the Index Browser for research purposes, spam blocking might be important.*

Double check rules:<br>
Reload 14 days *(change this if you like)*

Document Cache: Store to Web Cache:<br>
uncheck (might be needed to force the content blacklist to work?)

Index Attributes: index media:<br>
uncheck (might be needed to force the content blacklist to work?)

### Sit back and wait for it to index

You can use the Crawler Monitor and the Index Browser in YaCy to track progress.
