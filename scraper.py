import re
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import certifi
import ssl
import urllib.error
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser



STOPWORDS = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
            "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself",
            "she", "her", "hers", "herself", "it", "its", "itself", "they", "them",
            "their", "theirs", "themselves", "what", "which", "who", "whom", "this",
            "that", "these", "those", "am", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a",
            "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of",
            "at", "by", "for", "with", "about", "against", "between", "into", "through",
            "during", "before", "after", "above", "below", "to", "from", "up", "down", "in",
            "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
            "there", "when", "where", "why", "how", "all", "any", "both", "each", "few",
            "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don",
            "should", "now"]

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

        context = ssl.create_default_context(cafile=certifi.where())
        robot_parse = RobotFileParser()
        robot_parse.set_url((f'https://{domain}/robots.txt'))
        try:
            robot_parse.read()  # Pass the SSL context to urlopen or equivalent function
        except urllib.error.URLError as e:
            print(e.reason)
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
