class Article(object):

    def __init__(self):
        self.paperid   = ''
        self.title     = ''
        self.title2    = ''   #for second title
        self.language  = ''
        self.language2 = ''
        self.authors   = ''   #list of names
        self.abstract  = ''
        self.keywords  = ''
        self.pages     = ''   #of the form begin-end (used only for TALN import)
        self.numpages  = 0
        self.track     = ''
        self.session   = ''   #session id (related to paper type or topic)
        self.url       = ''
        self.idhal     = ''   #to specify an idhal in the article.csv file

    def __str__(self):
        s = ''
        for k,v in self.__dict__.items():
            s += k + ':' + str(v) + '\n'
        return s

    def update_title(self):
        if self.language == 'fr':
            if self.title2 != '':
                self.title = self.title + ' (' + self.title2 + ') [In French]' 
            else:
                self.title = self.title + ' [In French]'
