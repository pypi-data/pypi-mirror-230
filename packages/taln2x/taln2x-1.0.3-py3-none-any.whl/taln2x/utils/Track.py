class Track(object):

    def __init__(self, dir_name):
        self.trackid        = dir_name
        self.accept         = '' #semi-colon-separated list of acceptance keywords
        self.chairs         = '' #comma-separated list of names
        self.volume         = '' #track id (used for anthology formatting)
        self.articles       = [] #list of Article objects
        self.authors        = {} #dict associating paper ID with an ordered list of author objects
        self.partition      = {} #dict mapping session id to lists of paper ids
        self.sessions       = '' #semi-colon-separated list of session ids
        self.startpage      = -1 #for setting alternative first page number (cf reverse-engineering)
        self.order          = '' #not set by default here
        self.base_url       = '' #for TALN archive storage
        self.fullname       = '' #for track volume title
        self.texfullname    = '' #for track volume title with latex symbols (i.e. carriage return)

    def update_sessions(self, session, paper_id):
        if session not in self.partition:
            self.partition[session] = []
        self.partition[session].append(paper_id)
             
    def __str__(self):
        s = ''
        for t,i in self.__dict__.items(): 
            s += '\n' + t + '\n'
            if type(i) == list: #articles
                s += '\t:' + '\n  '.join(list(map(lambda x: str(x), i))) + '\n'
            elif type(i) == dict: #authors
                flat_list = [item for sublist in i.values() for item in sublist]
                s += '\t:' + '\n  '.join(list(map(lambda x: str(x), flat_list))) + '\n'
            else:
                s += '\t:' + str(i) + '\n'
        return s
