import re
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup



STOPWORDS = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as",
             "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
             "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
             "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
             "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself",
             "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
             "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of",
             "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
             "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
             "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
             "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
             "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
             "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
             "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
             "yourself", "yourselves"]


def scraper(url, resp):
    # Storing links from the next pages.
    if resp.status != 200:
        return []
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

    
    links = list() # Storing all the links here...
    if resp.status != 200:
        return [] # Not Found...
    
    vistied_links = set() # Already seen link
    similar_url = set()          # http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL
    # Inorder not to see the link again.

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    
    for link in soup.find_all('a', href=True):
        absolute_link = urljoin(url, link['href'])  # Use urljoin directly here
        absolute_link = re.sub(r"#.*$", "", absolute_link)  # Remove URL fragment

        # Checkeing the above link is valid.
        if absolute_link not in vistied_links:
            links.append(absolute_link)
            vistied_links.add(absolute_link)

        # http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL
        
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if re.match(
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
                + r"|ttf|otf)$", parsed.path.lower()):
            return False
            
        #Checking if the domain is only of this form
        #Only ics.uci.edu
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        pattern = r"^(.*\.)?(ics|cs|informatics|stat)\.uci\.edu$"

        if re.match(pattern, domain) ==  False:
            return False
        
        # Checking for Traps..
        # Checking for Robot.txt

        robot_parse = RobotFileParser()
        robot_parse.set_url((f'https://{domain}/robots.txt'))
        
        robot_parse.read()
            # We are not allowed to crawl this website.
        if not robot_parse.can_fetch('*', url):
                return False
            
            # Checking for events it is a Trap.
        # Simple trap avoidance: Events and Calendar
        if "event" in parsed.path.lower() or "calendar" in parsed.path.lower():
            return False

            # Checking for calender... it is a infinite and the crawler will get Stuck.
        if re.match(r"^.calendar.$", url):
            return False
        
        # Checking for conitnously repeating Directories 
        # URL too long and repeating.
        path_of_url = parsed.path.lower()
        repeat_or_long_dir_pattern = r'(\/[\w-]{10,})\/\1|\/[\w-]{20,}'
        if re.search(repeat_or_long_dir_pattern, path_of_url):
            return False 
        

        # Checking for Low information value pages...
        # Criteria Matching more than 50% After 
        # removing the most Commong words.



        # The link has passed all the Tests.
        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise
