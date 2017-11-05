import Tkinter as tk
import webbrowser

from TwitterAPI import TwitterAPI
import csv
import wikipedia as wiki
import datetime as dt
import time, ast, threading
import matplotlib.pyplot as plt
from math import sqrt

from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as Features

api = TwitterAPI(consumer_key ='',
                  consumer_secret='',
                  access_token_key = '',
                  access_token_secret = '')

natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2017-02-27',
    username="",
    password="")

#ghetto config file
LOCAL_CSV_FILE = 'output.csv'
user_depth = 5
startTweetID = 926311454810112000

class Application(tk.Frame):
    
    def createDefaultWidgets(self):
        self.companybutton = tk.Button(self, text="Company")
        self.companybutton.pack()
        self.productbutton = tk.Button(self, text="Product")
        self.productbutton.pack()
        self.companybutton["command"] = self.company
        self.productbutton["command"] = self.product
    
    def product(self):
        self.companybutton.destroy()
        self.productbutton.destroy()
        self.productlabel = tk.Label(self,text="Please enter the product you wish to observe:")
        self.productlabel.pack()
        self.productnameentry = tk.Entry(self)
        self.productnameentry.pack()
        self.productsubmit = tk.Button(self,text="Submit")
        self.productsubmit["command"] = self.prodsub
        self.productsubmit.pack()
        self.update()
        
    def prodsub(self):
        self.termlist = [self.productnameentry.get()]
        self.productbutton.destroy()
        self.productlabel.destroy()
        self.productnameentry.destroy()
        self.productsubmit.destroy()
        self.asscompanylabel = tk.Label(self,text="What company is this product associated with?")
        self.assentry = tk.Entry(self)
        self.submitbutton = tk.Button(self,text="Submit")
        self.submitbutton["command"] = self.run
        self.asscompanylabel.pack()
        self.assentry.pack()
        self.submitbutton.pack()
        self.update()
    
    def company(self):
        self.companybutton.destroy()
        self.productbutton.destroy()
        self.companylabel = tk.Label(self, text="Please enter the company you wish to observe:")
        self.companylabel.pack()
        self.companynameentry = tk.Entry(self)
        self.companynameentry.pack()
        self.companysubmitbutton = tk.Button(self, text = "Submit")
        self.companysubmitbutton.pack()
        self.companysubmitbutton["command"] = self.companysubmit
        self.update()
        
    def companysubmit(self):
        self.index = 0
        self.companyname = self.companynameentry.get()
        self.namelist = getWikiPages(self.companyname)
        self.companynameentry.destroy()
        self.companysubmitbutton.destroy()
        self.companylabel.destroy()
        self.checklabel = tk.Label(self, text="Is this the Wikipedia page to the company in question?")
        self.checklabel.pack()
        self.link = tk.Label(self, text=r"http://en.wikipedia.org/?curid=%s"%wiki.page(self.namelist[self.index]).pageid,fg="blue",cursor="hand2")
        self.link.pack()
        self.link.bind("<Button-1>",lambda event: self.callback(event,wiki.page(self.namelist[self.index]).pageid))
        self.yesbutton = tk.Button(self,text="Yes",fg='green')
        self.yesbutton.pack()
        self.nobutton = tk.Button(self,text="No",fg='red')
        self.nobutton.pack()
        self.yesbutton["command"] = self.yes
        self.nobutton["command"] = self.no
        self.update()
              
        
    def yes(self):
        self.termlist = wikiGetConcepts(wiki.page(self.namelist[self.index]))
        self.checklabel.destroy()
        self.link.destroy()
        self.yesbutton.destroy()
        self.nobutton.destroy()        
        self.termlabel = tk.Label(self, text="The following terms have been identified as related to the company of interest. \n Do you wish to edit?")
        self.termlabel.pack()
        delim = ', '
        terms = delim.join(self.termlist)
        termtext = tk.StringVar()
        termtext.set(terms)
        self.termslabel =tk.Label(self, textvariable=termtext)
        self.termslabel.pack()
        self.termsyes = tk.Button(self,text="Yes",fg='green')
        self.termsyes.pack()
        self.termsno = tk.Button(self,text="No", fg= 'red')
        self.termsno.pack()
        self.termsyes["command"] = self.yesforterms
        self.termsno["command"] = self.run
        self.update()
        
        
        
    def run(self):
        self.waitlabel = tk.Label(self, text="Please wait, mining and anaylzing twitter data.\n This may take hours, do not close.")
        self.waitlabel.pack()
        self.update()
        tweetMiner(self.termlist)
        
    def yesforterms(self):
        self.termlabel.destroy()
        self.termslabel.destroy()
        self.termsyes.destroy()
        self.termsno.destroy()
        self.runbutton = tk.Button(self,text='Run', fg='green')
        self.runbutton["command"] = self.run
        self.runbutton.pack()
        self.labels = []
        self.buttons = []
        self.addtermbox = tk.Entry(self)
        self.addtermbox.pack()
        self.addtermbutton = tk.Button(self,text='Add Term')
        self.addtermbutton["command"] = self.updateterms
        self.addtermbutton.pack()
        for i,term in enumerate(self.termlist):
            termtext = tk.StringVar()
            termtext.set(term)
            self.labels.append(tk.Label(self,textvariable=termtext))
            self.buttons.append(tk.Button(self,text='Delete',fg='red',command = lambda i=i: self.associatedDelete(i)))
        for label,button in zip(self.labels,self.buttons):
            label.pack()
            button.pack()
        self.update()
            
            
    
    def updateterms(self):
        text = self.addtermbox.get()
        self.termlist.append(text)
        textvar = tk.StringVar()
        textvar.set(text)
        self.labels.append(tk.Label(self,textvariable=textvar))
        self.buttons.append(tk.Button(self,text="Delete",fg='red',command = lambda i = len(self.labels) - 1: self.associatedDelete(i)))
        self.labels[-1].pack()
        self.buttons[-1].pack()
        self.update()
        
    def associatedDelete(self,index):
        term = self.labels[index].cget("text")
        self.labels[index].destroy()
        self.buttons[index].destroy()
        self.termlist.remove(term)
        self.update()
    
    def no(self):
        self.checklabel.destroy()
        self.link.destroy()
        self.yesbutton.destroy()
        self.nobutton.destroy()
        if self.index == len(self.namelist) - 1:
            self.checklabel.destroy()
            self.link.destroy()
            self.yesbutton.destroy()
            self.nobutton.destroy()
            self.update()
            self.failure()
        else:
            self.index += 1
            if self.namelist[self.index].find("disambiguation") >= 0:
                self.index += 1
            self.checklabel = tk.Label(self, text="What about this link?")
            self.checklabel.pack()
            self.link = tk.Label(self, text=r"http://en.wikipedia.org/?curid=%s"%wiki.page(self.namelist[self.index]).pageid,fg="blue",cursor="hand2")
            self.link.pack()
            self.link.bind("<Button-1>",lambda event: self.callback(event,wiki.page(self.namelist[self.index]).pageid))
            self.yesbutton = tk.Button(self,text="Yes",fg='green')
            self.yesbutton.pack()
            self.nobutton = tk.Button(self,text="No",fg='red')
            self.nobutton.pack()
            self.yesbutton["command"] = self.yes
            self.nobutton["command"] = self.no
            self.update()
        
        
    def failure(self):
        self.failedlabel = tk.Label(text="""You seem to have exhausted all of the suggested Wikipedia entries. \nPerhaps you mistyped something. Please exit and try again.""")
        self.exitbutton = tk.Button(self,text='EXIT',fg='red',command = self.master.destroy)
        self.failedlabel.pack()
        self.exitbutton.pack()
        
    def callback(self,event,pageid):
       webbrowser.open_new(r"http://en.wikipedia.org/?curid=%s"%pageid)
        
    
    def on_exit(self):
        return
    
    def __init__(self,master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createDefaultWidgets()
        self.master.protocol("WM_DELETE_WINDOW", self.on_exit)
        



def getWikiPages(name):
    return wiki.search(name)


def wikiGetConcepts(page):
    wikitext = page.summary
    response = natural_language_understanding.analyze(
            text=wikitext,
            features=[Features.Concepts()])
    queryTerms = {}
    for concept in response['concepts']:
        if concept['relevance'] > 0.5:
            queryTerms[concept['text'].encode('ascii','ignore')] = concept['relevance']
    sortedTerms = sorted(queryTerms, key=queryTerms.get, reverse=True)
    charlen = 0
    for i,term in enumerate(sortedTerms):
        charlen += len(term)
        if charlen >= 350:
            index = i
            break
        else:
            index = i
    return sortedTerms[:index]

def dateSterilzer(shit_date):
    return dt.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(shit_date,'%a %b %d %H:%M:%S +0000 %Y')),'%Y-%m-%d %H:%M:%S')

def makePlots(file_loc):
    t = []
    exposure = []
    emotions = []
    sentiment = []
    useraverage = []
    
    
    with open(file_loc,'r') as csv_file:
        data = csv.reader(csv_file,delimiter='|')
        for row in data:
            exp = []
            for i,item in enumerate(row):
                if i == 0:
                    sentiment.append(item)
                if i == 1:
                    emotions.append(ast.literal_eval(item))
                if i == 2:
                    exp.append(item)
                if i == 3:
                    exp.append(item)
                if i == 4:
                    exp.append(item)
                    exposure.append(exp)
                if i == 5:
                    useraverage.append(ast.literal_eval(item))
                if i == 6:
                    t.append(dateSterilzer(item))
             
    emotion_parsed = {}
    for i,dictionary in enumerate(emotions):
        if i == 0:
            for key in dictionary.keys():
                emotion_parsed[key] = [dictionary[key]]
        else:
            for key in dictionary.keys():
                emotion_parsed[key].append(dictionary[key])
    
    
    plot_dict = {'sadness': 'b.' , "joy": 'g.', "fear": 'k.' , "disgust": 'c.' , "anger": 'r.'}
    ##################
    '''
    CATAGORY UNADJUSTED
    '''
    ##################
    plt.plot(t,sentiment,'m.')
    plt.xlabel('Time')
    plt.xticks(rotation='vertical')
    plt.ylabel('Sentiment')
    plt.title('Time vs Sentiment')
    F = plt.gcf()
    Size = F.get_size_inches()
    F.set_size_inches(Size[0]*1, Size[1]*2, forward=True)
    plt.savefig('unadjustedSentiment.png')
    plt.clf()
    
    for emotion,vect in emotion_parsed.iteritems():
        plt.plot(t,vect,plot_dict[emotion])
        plt.xlabel('Time')
        plt.xticks(rotation='vertical')
        plt.ylabel('%s'%(emotion.title()))
        plt.title('Time vs %s'%(emotion.title()))
        F = plt.gcf()
        F.set_size_inches(Size[0]*1, Size[1]*2, forward=True)
        plt.savefig('unadjusted%s.png'%(emotion.title()))
        plt.clf()
    
    ########################
    '''
    CATGORY EXPOSURE ADJUSTED
    '''
    #########################
    exposure_adj = []
    exposure_normed = []
    for vect in exposure:
        exposure_normed.append(sqrt(int(vect[0])**2+int(vect[1])**2+int(vect[2])**2))
    for normed_vect in exposure_normed:
        exposure_adj.append(normed_vect/max(exposure_normed))
        
    exp_adj_sent = []
    for i,adj in enumerate(exposure_adj):
        exp_adj_sent.append(float(sentiment[i])*adj)
        
    plt.plot(t,exp_adj_sent,'m.')
    plt.xlabel('Time')
    plt.xticks(rotation='vertical')
    plt.ylabel('Sentiment')
    plt.title('Time vs Exposure Adjusted Sentiment')
    F = plt.gcf()
    F.set_size_inches(Size[0]*1, Size[1]*2, forward=True)
    plt.savefig('expadjustedSentiment.png')
    plt.clf()
    
    emotion_adj = {}
    for emotion,vect in emotion_parsed.iteritems():
        emotion_adj[emotion] = []
        for i,val in enumerate(vect):
            emotion_adj[emotion].append(float(val)*exposure_adj[i])
    
    for emotion, vect in emotion_adj.iteritems():
        plt.plot(t,vect,plot_dict[emotion])
        plt.xlabel('Time')
        plt.xticks(rotation='vertical')
        plt.ylabel('%s'%(emotion.title()))
        plt.title('Time vs Exposure Adjusted %s'%(emotion.title()))
        F = plt.gcf()
        F.set_size_inches(Size[0]*1, Size[1]*2, forward=True)
        plt.savefig('expadjusted%s.png'%(emotion.title()))
        plt.clf()
            
    #########################
    '''
    History Adjusted 
    '''
    #########################
    hist_sent = []
    hist_emotions = {}
    to_delete = []
    for i,tup in enumerate(useraverage):
        hist_sent.append(tup[0])
        if i == 0:
            for key in tup[1].keys():
                hist_emotions[key] = [tup[1][key]]
        else:
            if len(tup[1].keys()) == 0:
                to_delete.append(i)
            for key in tup[1].keys():
                hist_emotions[key].append(tup[1][key])
           
    hist_exposure_adj = [i for j, i in enumerate(exposure_adj) if j not in to_delete]
    t_hist_emotions = [i for j, i in enumerate(t) if j not in to_delete]
    sent_hist_adj = []
    emotion_hist_adj = {}
    for i,avg in enumerate(hist_sent):
        sent_hist_adj.append((float(sentiment[i])-avg)/2.0)
    
    for emotion, avgs in hist_emotions.iteritems():
        emotion_hist_adj[emotion] =[]
    
        for i,val in enumerate(avgs):
            emotion_hist_adj[emotion].append((val-float(emotion_parsed[emotion][i]))/2.0)
    
    plt.plot(t,sent_hist_adj,'m.')
    plt.xlabel('Time')
    plt.xticks(rotation='vertical')
    plt.ylabel('Sentiment')
    plt.title('Time vs Historically Adjusted Sentiment')
    F = plt.gcf()
    F.set_size_inches(Size[0]*1, Size[1]*2, forward=True)
    plt.savefig('histadjustedSentiment.png')
    plt.clf()
    
    for emotion, vect in emotion_hist_adj.iteritems():
        plt.plot(t_hist_emotions,vect,plot_dict[emotion])
        plt.xlabel('Time')
        plt.xticks(rotation='vertical')
        plt.ylabel('%s'%(emotion.title()))
        plt.title('Time vs Historically Adjusted %s'%(emotion.title()))
        F = plt.gcf()
        F.set_size_inches(Size[0]*1, Size[1]*2, forward=True)
        plt.savefig('histadjusted%s.png'%(emotion.title()))
        plt.clf()
    
    ###############
    '''
    Double Adjusted
    '''
    ##############
    double_sent = []
    for i,val in enumerate(sent_hist_adj):
        double_sent.append(val*exposure_adj[i])
    double_emotion = {}
    for emotion, avg in emotion_hist_adj.iteritems():
        double_emotion[emotion] = []
        for i,val in enumerate(avg):
            double_emotion[emotion].append(hist_exposure_adj[i]*val)
    
    
    plt.plot(t,double_sent,'m.')
    plt.xlabel('Time')
    plt.xticks(rotation='vertical')
    plt.ylabel('Sentiment')
    plt.title('Time vs Historically and Exposure Adjusted Sentiment')
    F = plt.gcf()
    F.set_size_inches(Size[0]*1, Size[1]*2, forward=True)
    plt.savefig('histexpadjustedSentiment.png')
    plt.clf() 
    
    for emotion, vect in double_emotion.iteritems():
        plt.plot(t_hist_emotions,vect,plot_dict[emotion])
        plt.xlabel('Time')
        plt.xticks(rotation='vertical')
        plt.ylabel('%s'%(emotion.title()))
        plt.title('Time vs Historically and Exposure Adjusted %s'%(emotion.title()))
        F = plt.gcf()
        F.set_size_inches(Size[0]*1, Size[1]*2, forward=True)
        plt.savefig('histexpadjusted%s.png'%(emotion.title()))
        plt.clf()

def _addAnalysis(text, sentimentArray, emotionsDict):
    try:
        result = natural_language_understanding.analyze(text=text,features=[Features.Sentiment(), Features.Emotion()])
        result['emotion']
    except:
        return
    sentiment_score = result['sentiment']['document']['score']
    sentimentArray.append(sentiment_score)
    emotions = result['emotion']['document']['emotion']
    for emo in emotions:
        if emo not in emotionsDict:
            emotionsDict[emo] = []
        emotionsDict[emo].append(emotions[emo])


def _addTweetStats(tweet, statList):
    try:
        result = natural_language_understanding.analyze(text=tweet['text'],features=[Features.Sentiment(), Features.Emotion()])
        result['emotion']
    except:
        return
    sentiment_score = result['sentiment']['document']['score']
    emotions = result['emotion']['document']['emotion']
    user_id = tweet['user']['id']
    userStats = averageUserStats(user_id)
    tweetObject = []
    tweetObject.append(sentiment_score)
    tweetObject.append(emotions)
    tweetObject.append(tweet['retweet_count'])
    tweetObject.append(tweet['favorite_count'])
    tweetObject.append(tweet['user']['followers_count'])
    tweetObject.append(userStats)
    tweetObject.append(tweet['created_at'])
    statList.append(tweetObject)
    
def writeAllTweetStat(tweets):
    threads = []
    statList = []
    for tweet in tweets:
        thread = threading.Thread(target = _addTweetStats, args=(tweet,statList))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    print(len(statList))
    with open(LOCAL_CSV_FILE, 'a') as file:
        for stat in statList:
            wr = csv.writer(file, dialect='excel', delimiter='|')
            wr.writerow(stat)
            
def averageStats(tweets):
    threads = []
    all_sentiments = []
    all_emotions = {}
    for tweet in tweets:
        thread = threading.Thread(target = _addAnalysis, args=(tweet,all_sentiments, all_emotions))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    if len(all_sentiments) == 0:
        averageSentiment = 0
    else:
        averageSentiment = sum(all_sentiments)/len(all_sentiments)
    averageEmotions = {}
    for emotion in all_emotions:
        emotionScoreList = all_emotions[emotion]
        if len(emotionScoreList) == 0:
            averageEmotions[emotion] = 0
        else:
            averageEmotions[emotion] = sum(emotionScoreList)/len(emotionScoreList)
    return averageSentiment, averageEmotions


def averageUserStats(uid):
    try:
        tweet_search = api.request('statuses/user_timeline', {'user_id':uid, 'count':user_depth})
        tweets = [i['text'] for i in tweet_search]
        avgSentiment, avgEmotions = averageStats(tweets)
        return avgSentiment, avgEmotions
    except:
        time.sleep(30)
        return averageUserStats(uid)

def tweetMiner(conceptlist):
    #tweets = []
    tweet_ids = []
    created_ats = []
    #print(tweets[len(tweets) - 1])
    #print(created_ats[len(created_ats) - 1])
    for term in conceptlist:
        while len(created_ats) == 0 or "Sat" not in created_ats[len(created_ats) - 1]:
                try:
                    tweet_search = api.request('search/tweets', {'q': term, 'result_type':'recent', 'count':30,'min_id':startTweetID, 'max_id':startTweetID+5*(10**11)})
                    for tweet in tweet_search:
                        break
                except:
                    print 'failed, sleeping...'
                    time.sleep(5)
                    continue
                tweets = [i['text'] for i in tweet_search]
                #print(tweets[len(tweets) - 1])
                tweet_ids = [i['id'] for i in tweet_search]
                created_ats = [i['created_at'] for i in tweet_search]
                writeAllTweetStat(tweet_search)
                if len(created_ats) > 0:
                    print created_ats[len(created_ats) - 1], tweet_ids[len(created_ats) - 1]
                    startTweetID = max(tweet_ids)
    makePlots(LOCAL_CSV_FILE)

     
root = tk.Tk()
app = Application(master=root)
root.wm_title("WSMSR")
root.iconbitmap('logo.ico')
app.mainloop()
