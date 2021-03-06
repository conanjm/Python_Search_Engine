import urllib2
import pickle
import random
import sys
import string

# ----- CRAWLER ----- #
#__GLOBALS__
MAX_DEPTH = 3
urlGraph = {}   #Store EVERY URL contained by each URL {Key: [url1, url2, url3, etc]}
crawled=[]      #Store Unique URLs visited

#__INTERACE__
def crawl(urlSeed):
    global crawled, urlGraph# no return, reset
    crawled, urlGraph = [],{}
    
    toCrawl=[[urlSeed,0]] #becomes a list of lists - each element in the list is a list containing two items, URL and depth location.
    while toCrawl:
        nextPage = toCrawl.pop()#Get "hub" url and its depth level (depth x+1)
        nextURL = nextPage[0]   #Retrieve URL
        nextIndex = nextPage[1] #Retrieve URL depth
        
        #crawled.append(nextURL) #Record that we have crawled the url(doing it now...)
        if nextIndex < MAX_DEPTH:
                newLinks = getLinksOnPage(nextURL, crawled)  #find all links at depth x
                crawled.append(nextURL)
                for links in newLinks:
                        toCrawl.append([links, nextIndex+1])    #found links are x+1 deep

#__IMPLEMENTATION__
#Sets ALL Links on each page <- assigned to global URL graph
#Returns UNIQUE Links on each page <- used by crawler
def getLinksOnPage(page,prevLinks):
        response = urllib2.urlopen(page)
        html = response.read()

        poodleDebugOutput("Crawling " + page)

        allLinks,links,pos,allFound=[],[],0,False
        while not allFound:
                aTag=html.find("<a href=",pos)
                if aTag>-1:
                        href=html.find('"',aTag+1)
                        endHref=html.find('"',href+1)
                        url=html[href+1:endHref]
                        if url[:7]=="http://":
                                if url[-1]=="/":
                                        url=url[:-1]

                                allLinks.append(url)    #store ALL links
                                if not url in links and not url in prevLinks:   #store UNIQUE links
                                        poodleDebugOutput("Unseen page: " + url)
                                        links.append(url)     
                        closeTag=html.find("</a>",aTag)
                        pos=closeTag+1
                else:
                        allFound=True   

        global urlGraph
        urlGraph[page] = allLinks
        return links
    
# ----- /CRAWLER ----- #

# ----- SCRAPER ----- # #Indexes unique words from a set of urls 
#__GLOBALS__
index = {}
pageWords = []

#__INTERFACE__
def scrape(urls):   #creates an index and saves in a file
        global index, pageWords #no return, reset
        index, pageWords = {},[]
        
        for url in urls:
                poodleDebugOutput("Scraping: {}".format(url))
                #get Page text for the current url
                pageWords = getPageText(url)
                #add page to index - correspond to keyword
                addPageToIndex(index,pageWords,url)

#__IMPLEMENTATION__
def getPageText(url):   #Gets every unique word on a page
    response = urllib2.urlopen(url)
    html = response.read()

    pageText,pageWords="",[]
    html=html[html.find("<body")+5:html.find("</body>")]

    startScript=html.find("<script")
    while startScript>-1:
        endScript=html.find("</script>")
        html=html[:startScript]+html[endScript+9:]
        startScript=html.find("<script")
    
    ignore=set()
    fin=open("ignore.txt","r")
    for word in fin:
        word = word.lower()
        ignore.add(word.strip())
    fin.close()
        
    finished=False
    while not finished:
        nextCloseTag=html.find(">")
        nextOpenTag=html.find("<")
        if nextOpenTag>-1:
            content=" ".join(html[nextCloseTag+1:nextOpenTag].strip().split())
            #Remove punctuation
            content = content.translate(None, string.punctuation)
            pageText=pageText+" "+content
            html=html[nextOpenTag+1:]
            
        else:
            finished=True
        
    for word in pageText.split():
        if word[0].isalnum() and not word.lower() in ignore:
            if not word in pageWords:
                pageWords.append(word)
    
    return pageWords

def addPageToIndex (index,pageWords,url):       #Page added "implicitly"
	for word in pageWords:  #for each unique word on the current page
		addWordToIndex(index,word,url)  #add the word to the scraper's index

def addWordToIndex(index,word,url):
        if word in index:
                index[word].append(url) #go to Key: "Word", add the current page URL
        else:
                index[word] = [url]               
# ----- /SCRAPER ----- #

# ----- PAGE RANKER ----- #
#__GLOBALS__
pageRanks = {}

#__INTERFACE__
def rankPages(graph): 
    d=0.85
    numLoops=10
    npages=len(graph)
    ranks = {}
    
    for page in graph:
        ranks[page]=1.0/npages
    
    for i in range(0,numLoops):
        newRanks={}
        for page in graph:
            newRank=(1-d)/npages
            for node in graph:
                if page in graph[node]:
                    newRank=newRank+d*(ranks[node]/len(graph[node]))
            newRanks[page]=newRank
        ranks=newRanks
    return ranks
# ----- /PAGE RANKER ----- #

# ----- POODLE ----- #
#__GLOBALS__
MAX_RESULTS_DISPLAYED = 10
DEBUG_MODE = False
cool_facts = ["POODLE rhymes with google. That type of rhyme is called assonance!", "POODLEs are ghastly looking dogs",
              "POODLE is going to get me 100% on my coursework!", "POODLE knows what you did last summer, if you put it online, that is..."]

def poodleOutput(pString):
    print "\nPOODLE: %s" % (pString)

def poodleDebugOutput(pString):
    if DEBUG_MODE == True:
        print "DEBUG: [ {} ]".format(pString)

def poodleSetup():
    rand = random.randint(0,len(cool_facts)-1)
    print cool_facts[rand]
    print "-----"    
    
def poodleHelp():
    print ""
    print "POODLE Functionality:"
    print "----- POODLE DATABASE -----"
    print "-build\t\tCreate a POODLE database (and set the depth of the web crawler)"
    print "-dump\t\tSave the POODLE database you built"
    print "-restore\tRetrieve the last saved POODLE database"
    print "-print\t\tShow the POODLE database (index, graph, and page ranks)"
    print "----- POODLE BEHAVIOUR -----"
    print "-search\t\tSet the maximum results returned by POODLE"
    print "-debug\t\tSet POODLE's debug mode (enables under the hood printing)"
    print "-ignore\t\tPrint POODLE's ignore list"
    print "----- META POODLE -----"
    print "-help\t\tWhat do you think you're looking at, pal?"
    print "-exit\t\tExit the world as we know it!"

def poodleBuild():
    poodleOutput("Give me a seed URL! >>")
    crawl_seed = raw_input().strip()
    #Invalid URL check
    try:
        urllib2.urlopen(crawl_seed)
    except:
        poodleOutput("Invalid URL")
        return poodleBuild()
    
    global MAX_DEPTH
    depthSet = False
    while depthSet != True:
        poodleOutput("Please set a maximum depth for the web crawl procedure! >>")
        depth_input = raw_input().strip()
        if depth_input.isdigit():
            try:
                depthSet = True
                MAX_DEPTH = int(depth_input)
            except:
                depthSet = False

    #2. Generate URL Graph
    crawl(crawl_seed)
    poodleOutput("\n----- CRAWLED PAGES -----")
    for url in crawled: #could use the url graph here - ordered with list though
        print url

    #3. Generate Index
    scrape(urlGraph)

    #4. Generate Ranks
    global pageRanks
    pageRanks = {}
    pageRanks = rankPages(urlGraph)

    #create a case-insensitive index
    global index    
    tempIndex = {}
    for word in index:
        tempIndex[word.lower()] = index[word]

    del index
    index = tempIndex
    poodleOutput("Database created!")

def poodleDump():   #heh
    if urlGraph:
        #create data structure to store in one file
        database = {}

        database["urlGraph"] = urlGraph
        database["index"] = index
        database["pageRanks"] = pageRanks

        #Save Page Ranks
        fout = open("database.txt", "w")
        pickle.dump(database, fout)
        fout.close()

        poodleOutput("Database saved!")
    else:
        poodleOutput("Nothing to dump!")

def poodleRestore():
    try:
        #Data structure to retrieve the site's graph, keyword index, and page ranks
        database = {}

        fin = open("database.txt", "r")
        database = pickle.load(fin)
        fin.close()
        
        #Load Crawled Index
        global urlGraph
        urlGraph = {}
        urlGraph = database["urlGraph"]

        #Load Scraped Index
        global index
        index = {}
        index = database["index"]

        #Load PageRank Values
        global pageRanks
        pageRanks = {}
        pageRanks = database["pageRanks"]

        poodleOutput("Database loaded!")
    except:
        poodleOutput("Couldn't access database.txt. Please check POODLE's directory!")

def poodlePrint():
    if urlGraph:
        poodleOutput("----- INDEXED WORDS & RESPECTIVE LOCATIONS -----")
        for keyword in index:
            print "{}: {}".format(keyword, index[keyword])

        poodleOutput("----- URL GRAPH -----")
        for page in urlGraph:
            print "PAGE: {}\n".format(page)
            print "\t{}\n".format(urlGraph[page])

        poodleOutput("----- PAGE RANKS -----")
        for url in pageRanks:
            print "{} | RANK: {}".format(url, pageRanks[url])
    else:
        poodleOutput("No database loaded!")

def poodleIgnoreList():
	fin = open("ignore.txt", "r")
	for word in fin:
		print word.strip()
	fin.close()

def poodleSetMaxResults():
	global MAX_RESULTS_DISPLAYED
	poodleOutput("Please set the amount of search results to display! >>")

	maxDisplayedSet = False
	while maxDisplayedSet != True:
		user_input = raw_input().strip()
		if user_input.isdigit():
			try:
				maxDisplayedSet = True
				MAX_RESULTS_DISPLAYED = int(user_input)
			except:
				maxDisplayedSet = False;

def poodleDebug():
    global DEBUG_MODE
    poodleOutput("Current Debug Mode: {}".format(DEBUG_MODE))
    changeDebug = False;
    while changeDebug == False:
        poodleOutput("Set the debug mode? (yes or no) >>")
        user_input = raw_input().strip()
        if user_input.lower() == "yes":
            changeDebug = True
            break
        elif user_input.lower() == "no":
            changeDebug = False
            break
        
    debugSet = False
    while debugSet != True and changeDebug == True:
        poodleOutput("Please set debug to either true or false >>")
        user_input = raw_input().strip()
        if user_input.lower() == "true":
            debugSet = True
            DEBUG_MODE = True
        elif user_input.lower() == "false":
            debugSet = True
            DEBUG_MODE = False

#Search and Multi-keyword search function
def poodleSearch(term):
	user_inputs = [] #list to hold multiple search terms (if available)
	if "," in term:
		user_inputs = term.split(",")   #split list of search terms into individual terms

	for inputTerm in user_inputs:   #RECURSIVE TECHNIQUE
		inputTerm = inputTerm.strip()
		poodleSearch(inputTerm)

	#ONLY DO SEARCH OPERATION IF AN *INDIVIDUAL* TERM (Base "multi-keyword" caller won't enter this) - BASE CASE
	#Procedure: Collection of terms split into individuals. They do this operation and return. Base now finishes.
	if not user_inputs:	
		count = 0
		termFoundAt = []
		term = term.lower()
		if term in index:
		    for url in index[term]:
			    count += 1
			    termFoundAt.append(url)
	    
		linkAndRank = []
		for url in termFoundAt:
			linkAndRank.append([[url], pageRanks[url]])

		linkAndRank.sort(key = lambda x:x[1])   #lambda expression to sort by second list element (rank)

		if count == 0:
			poodleOutput("No results found.")
		elif count > 1:
			poodleOutput("[{}] {} results found!\n".format(term, count))
		elif count == 1:
			poodleOutput("[{}] {} result found!\n".format(term, count))
		maxResultCounter = 0
		for x in reversed(linkAndRank):
			maxResultCounter += 1
			if maxResultCounter >= MAX_RESULTS_DISPLAYED:
				break
			print "{} | RANK: {}".format(x[0], x[1])
    
def poodleIndex():
	poodleOutput("Enter -help for POODLE commands (if you don't know what you're doing), or enter a search term! >>")
	user_input = raw_input()
	user_input = user_input.strip()
	#Build options (Dictionary/switch structure)
	poodleOpts = {"-build": poodleBuild,
		      "-dump": poodleDump,
		      "-search": poodleSetMaxResults,
                      "-debug": poodleDebug,
		      "-restore": poodleRestore,
		      "-print": poodlePrint,
		      "-ignore": poodleIgnoreList,
		      "-help": poodleHelp,
		      "-exit": sys.exit}

	#POODLE INPUTS - Search & Build options
	if user_input in poodleOpts:
		poodleOpts[user_input]()
	elif user_input[0] == "-":
		poodleOutput("Please enter a valid command!")
	elif len(urlGraph) < 1:
		poodleOutput("You must build or restore a database before entering a search term!")
	else:
		poodleSearch(user_input)
	poodleIndex()

# ----- /POODLE -----#

# ----- MAIN ----- #
poodleSetup()
poodleIndex()

#TODO: Multi-keyword search (poodle)
