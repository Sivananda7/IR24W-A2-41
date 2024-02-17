import re
from urllib.parse import urlparse, urljoin, urldefrag
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
import certifi
import ssl
import urllib.error
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser


#GLOBAL VARIABLES
STOPWORDS = [
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers",
    "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've",
    "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me",
    "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over",
    "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while",
    "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
]
previous_pages_tokens = []

# Lenght gives all the unique Urls.
unique_urls =  set()  # colletion of Unique Urls. 
number_of_unique_urls = len(unique_urls)
ics_subdomains = {} # Key : Array [URLS]
unique_words = {} # Get all the Unique words.
longest_word_url = None 
longest_word = 0

def scraper(url, resp):
    links = extract_next_links(url, resp)

    # Storing links from the next pages.

    if resp.status != 200:
        return []
    else:
        valid_links = []
        for link in links:
            if is_valid(link):
                valid_links.append(link)
                extractWebsitesUnderDomain(link)
        LongestPageWord(url,resp)
    return valid_links

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
    

    soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
    # Some files are very large. Assuming Reading only 10MB pages. That is 1024*1024*10
    # with word limit of not more than 500. 

    # Tokenize the content of the current page
    content = soup.get_text()
    current_page_tokens = set(tokenize(content))
    # Skip pages with trivial or highly similar content
    if is_content_trivial_or_similar(current_page_tokens):
        return []
    # Add current page tokens to the global list for future comparisons
    previous_pages_tokens.append(current_page_tokens)
    
    words = len(soup.get_text().split()) # Number of words.
    size_of_page = len(str(soup))   # Size in Bytes
    

    if size_of_page < 10*1024*1024 and words > 200:
        # Then add the page to Links 

        for link in soup.find_all('a', href=True):

            absolute_link = urljoin(url, link['href'])
            if absolute_link:  # Use urljoin directly here
                if absolute_link.startswith(("http", "https")):
            
            # http://www.ics.uci.edu#aaa and http://www.ics.uci.edu#bbb are the same URL
            # Inorder not to see the link again.
                    without_fragment = urldefrag(absolute_link).url  # Remove URL fragment and gives the URL
                    links.append(without_fragment)
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

        # Checking for Files formats 

        # 
        #
            
        #Checking if the domain is only of this form
        #Only ics.uci.edu
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        pattern = r"^(.*\.)?(ics|cs|informatics|stat)\.uci\.edu$"

        if re.match(pattern, domain) ==  False:
            return False

        if url in unique_urls:
            return False
        
        if url.count("/") > 6:  # Very large URL avoiding it.
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
        

        # Checking for site Maps.
        
        if "sitemap" in parsed.path.lower():
            return False
        

        # Checking for Low information value pages...
        # Criteria Matching more than 50% After 
        # removing the most Commong words.



        # The link has passed all the Tests.

        
        unique_urls.add(url)  # since unique and passes all the check models 
        # We can add it to unique_urls.
        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise


def extractWebsitesUnderDomain(url):
    """
    Domian: ics.uci.edu 
    Takes the domain name and gives the 
    all the domain under it.

    Just adds the url to the ICS_SUBDOMAINS.

    parameter: Takes a URL ()
    return : None
    """
    
    domain = urlparse(url).netloc.lower() # To get the domain of the URL e ics.uci.edu 
    if (not url.endswith("ics.uci.edu")):
        return 
    subdomain = domain.replace(".ics.uci.edu", "")
    if subdomain in ics_subdomains:
        if url in ics_subdomains[subdomain]:
            pass # Already present in the array
        else:
            ics_subdomains[subdomain].append(url) # Adding the url to the subdomain
    else:  # subdomain not in main domains.
        ics_subdomains[subdomain] = [] # Create a array
        ics_subdomains[subdomain].append(url)  # Adding the url to the subdomain



def LongestPageWord(url, resp):
    """
    Finds the largest Page and The Common Words
    """
    global longest_word, longest_word_url, number_of_unique_urls
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    text = soup.get_text()

    words_tokenized = re.findall(r'[a-zA-Z0-9]+', text) # Get only the words in the text.

    for i in words_tokenized:
        if i in STOPWORDS or len(i)<=2:  # Not counting less than 2.
            pass
        elif i in unique_words:
            unique_words[i] += 1
        else:
            unique_words[i] = 1
        

    len_page = len(words_tokenized)
    if len_page > longest_word:
        longest_word = len_page
        longest_word_url = url

    number_of_unique_urls = len(unique_urls)


    

def tokenize(text):

    # Existing tokenization logic here

    list_data = []

    for i in text:  # Loop through the words eliminating the special chanracters only characters.
        word = ""
        for j in i:
            if j.isalnum() and j.isascii():
                word += j
            else:
                if word:
                    list_data.append(word.lower())
                word = ""
        if word not in STOPWORDS and word.isalnum():
            list_data.append(word.lower())
        # closing file a

    return list_data

# Checking for Low information value pages...
# Criteria Matching more than 50% After 
# removing the most Commong words.

def is_content_trivial_or_similar(current_page_tokens):

    # Check if the content is trivial (e.g., all tokens are the same) or similar to any previously fetched page
    if len(current_page_tokens) <= 1 or all(token == next(iter(current_page_tokens)) for token in current_page_tokens):
        return True
    for prev_tokens in previous_pages_tokens:
        common_tokens = current_page_tokens.intersection(prev_tokens)
        # Define your own similarity threshold
        similarity_threshold = 0.5
        if len(common_tokens) / min(len(current_page_tokens), len(prev_tokens)) > similarity_threshold:
            return True
    return False



def get_report():
    """

    It createss a Text File Report.txt what 
    the crawler has done. It Addes the unique Urls
    Length of Urls.

    return : None

    """

    # Sorting the unique_url lexiograhically.
    global longest_word,longest_word_url,unique_urls, number_of_unique_urls

    top_words = sorted(unique_words.items(), key = lambda f: (-f[1], f[0]))


    ics_subdomains = dict(sorted(ics_subdomains.items()))

    with open("Report.txt", "w") as myFile:
        myFile.write(
            f"Largest Page word is: {longest_word} and it's URl is: {longest_word_url}\n"
        )

        myFile.write(
            f"Number of Pages Crawler is: {unique_urls}\n"
        )

        for web in ics_subdomains:
            myFile.write(
                f"https://{web}.ics.uci.edu  => {len(ics_subdomains[web])}\n"  # Websites : Number
            )
        
        for i in range(50):
            myFile.write(
                f"{top_words[i][0]} => {top_words[i][1]}\n"
            )
            