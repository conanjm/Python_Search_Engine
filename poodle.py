print "POODLE"
print "-----"
import urllib2

# ----- CRAWLER ----- #
MAX_DEPTH = 1
urlGraph = {}

def getAllNewLinksOnPage(page,prevLinks,graph):

        response = urllib2.urlopen(page)
        html = response.read()

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
                                        links.append(url)     
                                        print "Unseen URL Found: " + url
                        closeTag=html.find("</a>",aTag)
                        pos=closeTag+1
                else:
                        allFound=True   

        graph[page] = allLinks
        graphAndLinks = [graph, links]
        return graphAndLinks
        #return links

def crawl(urlSeed):
    toCrawl=[[urlSeed,0]] #becomes a list of lists - each element in the list is a list containing two items, URL and depth location.
    crawled=[]
    while toCrawl:
        nextPage = toCrawl.pop()#Get "hub" url and its depth level (depth x+1)
        nextURL = nextPage[0]   #Retrieve URL
        nextIndex = nextPage[1] #Retrieve URL depth
        
        crawled.append(nextURL) #Record that we have crawled the url(doing it now...)

        if nextIndex < MAX_DEPTH:
                newLinks = getAllNewLinksOnPage(nextURL, crawled, urlGraph)  #find all links at depth x      
                for links in newLinks[1]:
                        toCrawl.append([links, nextIndex+1])    #found links are x+1 deep

# ----- /CRAWLER ----- #
crawl("http://adrianmoore.net/finalyear")