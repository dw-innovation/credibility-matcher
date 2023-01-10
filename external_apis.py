import requests
from diskcache import Cache
import pywikibot
from loguru import logger
from tldextract import extract

logger.add("out.log", rotation="500 MB")

WIKIPEDIA = 'wd'
DPBEDIA = "dp"
WIKIDATA = "wd"

WIKIDATA_SITE = pywikibot.Site("wikidata", "wikidata")
WIKIDATA_REPO = WIKIDATA_SITE.data_repository()

WIKIPEDIA_SITE = pywikibot.Site('wikipedia:en')

cache = Cache('tmp')

domain_keywords = ["news", "television", "newspaper", "media"]


@cache.memoize()
def entity_search(publisher_domain):
    api_url = f"https://mtab.app/api/v1/search?limit=3&m=a&info=1&q={publisher_domain}"

    response = requests.get(api_url).json()

    return response


def fetch_official_website_from_wdata(wdata):
    try:
        item = pywikibot.ItemPage(WIKIDATA_REPO, wdata)

        item_dict = item.get()
        clm_dict = item_dict["claims"]
        official_website = clm_dict["P856"][0].getTarget()
        return official_website

    except Exception as e:
        logger.error(f"Wikidata does not have information about the website of {wdata}.")
        return


def fetch_official_website_from_wikipedia(wikipedia_page):
    page = pywikibot.Page(WIKIPEDIA_SITE, wikipedia_page)
    all_templates = page.raw_extracted_templates

    for tmpl, params in all_templates:
        if tmpl.startswith('Infobox'):
            if 'url' in params:
                official_website = params["url"].replace("{{", "").replace("}}", "").split('|')[-1]
                return official_website

            if 'website' in params:
                official_website = params["website"].replace("{{", "").replace("}}", "").split('|')[-1]
                return official_website

    return None


def entity_linker(publisher_domain):
    candidate_documents = entity_search(publisher_domain)

    if int(candidate_documents["total"]) == 0:
        return None

    candidate_documents = entity_search(publisher_domain)["hits"]

    linked_document = None

    for candidate_document in candidate_documents:
        official_website = fetch_official_website(candidate_document)

        if not official_website:
            logger.error(f"{publisher_domain} does not have official website")
            continue

        if extract(official_website).domain == extract(publisher_domain).domain:
            linked_document = candidate_document
            break

    return linked_document


def fetch_official_website(candidate_document):
    official_website = fetch_official_website_from_wdata(candidate_document["wd"].split('/')[-1])
    if not official_website and "wp" in candidate_document:
        official_website = fetch_official_website_from_wikipedia(candidate_document["wp"].split('/')[-1])
    return official_website


if __name__ == '__main__':
    # example_id = "Q7806547"
    # fetch_official_website_from_wdata(example_id)

    example_id = "Times_Now"
    print(fetch_official_website_from_wikipedia(example_id))
