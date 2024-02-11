import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if resp.status != 200 or not resp.raw_response:
        return []
    
    links = []
    vistied_links = set() # Already seen link
    similar_url = set()
    # Inorder not to see the link again.

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        absolute_link = urljoin(url, link['href'])  # Use urljoin directly here
        absolute_link = re.sub(r"#.*$", "", absolute_link)  # Remove URL fragment

        # Checkeing the above link is valid.
        if is_valid(absolute_link):

            # http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL
            
            if absolute_link.split('#', 1)[0] not in similar_url:
                similar_url.add(absolute_link.split('#', 1)[0])
                if absolute_link not in vistied_links:
                    links.append(absolute_link)
                    vistied_links.add(absolute_link)
        
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|aac|flac|m4a"
            + r"|svg|webp|flv|3gp|webm"
            + r"|rar|zip|7z|gz|xz|tar.gz"
            + r"odt|ods|odp|rtf"
            + r"|sh|bat|cmd|vbs"
            + r"|json|xml|woff|woff2|eot"
            + r"|ttf|otf)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
