# Namecoin YaCy Search Engine (Plain DNS)

These instructions cover setting up a YaCy search engine instance that indexes Namecoin websites.  It will only index Namecoin domain names that use standard DNS types (i.e. darknets like Tor, ZeroNet, etc. will not be indexed).

Note: Testing is being done with Debian Buster on ppc64le.

## Instructions

### Install YaCy

You can build YaCy from source; follow the instructions at [YaCy's GitHub](https://github.com/yacy/yacy_search_server).

### Configure YaCy use case

YaCy Administration -> First Steps -> Use Case & Account -> Basic Configuration -> Use Case -> either "Community-based web search" or "Search portal for your own pages".  (This choice will decide whether your YaCy instance shares its index with the YaCy P2P network.)

Then restart YaCy.

### Install Namecoin Core

Right now, SPV clients will not work for this purpose.  However, enabling pruning should be fine.

### Install ncdns

Right now, you need to use the experimental YaCy fork of ncdns, which supports converting DNS zonefiles to URL lists.  It's [PR 93](https://github.com/namecoin/ncdns/pull/93).  Configure ncdns to use Namecoin Core as per the ncdns docs.

### Install DNSSEC-Trigger

Configure DNSSEC-Trigger's Unbound instance to use ncdns for `bit.` as per the ncdns docs.

### Generate a URL list

Run `./gen-url-list-plain-dns.sh`.

### Start a crawl

Start point: from file:<br>
*path to url-list-random-plain-dns.txt*

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

You'll probably want to regularly re-generate the URL list and start a new crawl with the new URL list, to make sure that you're capturing new content and new websites.

### Deleting non-Namecoin data

If you used the "Community-based web search" use case, then you'll periodically exchange index data with other YaCy users.  Many of those users will probably send you index data for some non-Namecoin websites.  If you don't want your YaCy resources to be utilized for non-Namecoin websites, you can go to Administration -> Index Administration -> Index Deletion -> Delete by Solr Query.  Enter the following query:

`-(host_s:*.bit)`

You'll need to do this regularly.
