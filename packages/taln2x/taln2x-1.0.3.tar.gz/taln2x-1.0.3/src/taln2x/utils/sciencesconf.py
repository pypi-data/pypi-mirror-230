import zipfile, sys, os, csv, re, json
from tqdm        import tqdm
from io          import StringIO
from unicodedata import normalize

def get_labs(s, affs):
    all_labs = re.findall(r'(\d+) - ([^\()]+) \(([^\)]+)\)', s)
    #print("**", all_labs)
    for x in all_labs:
        #print('**', x)
        idx, name, country = x
        affs[idx] = name + ', ' + country
        
def get_data(e, xzipfile, indir, verbose, xid_col, xauthors_col, xtitle_col, xidhal_col, xfile_col, xaccept_col, xkeywords_col):
    
    # Process the zip file to compute the expected tracks (csv and pdf dir/files) then call easychair interface
    articles    = ''  #csv input string
    zip_content = [] 
    eventname   = e.__dict__['abbrev'] + "_" + str(e.__dict__['year'])
    tracks_art  = {}  #track name <è> list of articles (each one being a csv string)
    tracks_abs  = {}  #track name <-> dict : paperid <-> abstract
    tracks_aut  = {}  #track name <-> dict : paperid <-> dict : rank <-> author

    ## read submissions.csv from zip file
    with zipfile.ZipFile(xzipfile, mode="r") as archive:
        #archive.printdir()
        articles = archive.read('export/submissions.csv').decode(encoding="utf8")        
        for filename in archive.namelist():
            zip_content.append(filename)
    
    # Fields in the submission page from easychair 
    PAPERINFO = ['DOCID', 'TYPE', 'DATE', 'STATUT','TYPDOC','ABSTRACT','TITLE',\
                 'SPEAKERS','CORRESPONDING', 'AUTHORS','LABOS','FILE','FILE_SRC','DATEPRODUCT','COMMENTAIRE',\
                 'LANGUE','CREATEUSERID','MAIL','TOPIC','MOTCLE','NOTE']

    # for each article retrieve the corresponding pieces of information
    csvfile= StringIO(articles)
    # get csv file length (stored in var count) and then go back to beginning of file
    reader = csv.reader(csvfile, delimiter='\t')
    count = sum(1 for _ in reader)
    csvfile.seek(0)
    reader = csv.reader(csvfile, delimiter='\t')
    # process articles (i.e. csv row)
    for row in tqdm(reader, total=count):
        #print("**",row)
        if not(row[0].isdigit()): #header row of csv file
            continue
        trackname= row[PAPERINFO.index('TYPDOC')].replace(' ', '-') # beware of spaces in dir names
        trackdir = os.path.join(indir, trackname)
        # the first time the track name is encountered
        # create the corresponding subdirectory
        if not(os.path.exists(trackdir)):
            os.makedirs(trackdir)
            os.makedirs(os.path.join(trackdir, 'pdf'))
        if trackname not in tracks_art:
            tracks_art[trackname] = []
            tracks_abs[trackname] = {}
            tracks_aut[trackname] = {}
        # we process the article info and format it as expected (compliently with config format)
        accept = row[PAPERINFO.index('STATUT')]
        # we create a list which will serve to compute the csv row of the processed article
        article = ['']*(max(xid_col, xauthors_col, xtitle_col, xidhal_col, xfile_col, xaccept_col, xkeywords_col)+1)
        # we update the article fields
        article[xid_col] = row[PAPERINFO.index('DOCID')]
        # we need to pre-process affiliations
        affiliations = row[PAPERINFO.index('LABOS')]
        laboratories = {} # key: int (rank), value: str (lab name)
        all_affs     = {} # key: str (author), value: str (lab name)
        get_labs(affiliations, laboratories) # update laboratories
        # we need to pre-process authors which are of the form "lastname~firstname <emails> (affiliation)"
        authors = row[PAPERINFO.index('AUTHORS')]
        auts    = ''
        rank    = 0
        for auth in authors.split(','):
            rank += 1
            aut = auth.strip().split('(')[0].split('<')[0]
            #print(article[xid_col], auth.strip())
            if '<' in auth:
                email = auth.strip().split('(')[0].split('<')[1].split('>')[0]
            else:
                email = ''
            lab = auth.strip().split('(')[1].split(')')[0] #only the main/first affiliation is stored
            #print(article[xid_col], lab)
            # we split names according to separator
            tokens = re.split('\xa0', aut) 
            if len(tokens) > 1:
                firstname = tokens[1].title().strip().replace(" ", "~")
                lastname  = tokens[0].strip().replace(" ", "~")
                newaut = firstname + ' ' + lastname
                #print("*",article[xid_col],newaut)
            else:
                newaut = aut
                #print("**",article[xid_col],newaut)         
            auts += newaut + ', ' #we compute the str representing the authors in the csv easychair input format
            #we prepare the dictionary of authors
            all_affs[rank] = { 'firstname': firstname, 'lastname': lastname, 'email': email, 'affiliation' : laboratories[lab] }
        # we update the tracks authors dict
        tracks_aut[trackname][article[xid_col]] = all_affs
        # we update article's metadata
        article[xauthors_col] = auts[:-2] # we remove the final ', '
        article[xtitle_col]   = row[PAPERINFO.index('TITLE')]
        #print("*", article[xtitle_col])
        article[xkeywords_col]= row[PAPERINFO.index('MOTCLE')]
        article[xidhal_col]   = '' # ignored at this stage
        if accept.startswith('Accept'):
            article[xaccept_col] = accept  
        elif accept.startswith('Initial'):
            article[xaccept_col] = 'Accept' 
        else:
            article[xaccept_col] = 'No'
        # we update the abstracts info
        tracks_abs[trackname][article[xid_col]] = { 'abstract' : row[PAPERINFO.index('ABSTRACT')].replace('\n',''), 'title' : article[xtitle_col] }
        #print("#", [article[xid_col]], row[PAPERINFO.index('ABSTRACT')].replace('\n',''))
        ## copy pdf file
        paperid = article[xid_col]
        p = re.compile("export/" + paperid + ".pdf")
        pdffile = list(filter(lambda x : p.match(x), zip_content))[0]
        newname = eventname + "_" + paperid + ".pdf"
        with zipfile.ZipFile(xzipfile, mode="r") as archive2:
            archive2.extract(pdffile, path=os.path.join(trackdir, 'pdf'))
        os.rename(os.path.join(trackdir, 'pdf', pdffile), \
                os.path.join(trackdir, 'pdf', newname))
        # we store the new filename                      
        article[xfile_col] =  newname
        # we convert current article into a csv entry 
        # and add it to the list of papers
        tracks_art[trackname].append('\t'.join(article))
    # finally we write down articles.csv, abstracts.csv and authors.json
    for tname in tracks_art:
        with open(os.path.join(indir, tname, 'articles.csv'), mode='w') as file_art:
            print('\n'.join(tracks_art[tname]), file=file_art)
            if verbose > 1:
                print('\n'.join(tracks_art[tname]), file=sys.stdout)
        with open(os.path.join(indir, tname, 'abstracts.json'), mode='w') as file_abs:
            print(json.dumps(tracks_abs[tname]), file=file_abs)
            if verbose > 1:
                print(json.dumps(tracks_abs[tname]), file=sys.stdout)
        with open(os.path.join(indir, tname, 'authors.json'), mode='w') as file_aut:
            print(json.dumps(tracks_aut[tname]), file=file_aut)
            if verbose > 1:
                print(json.dumps(tracks_aut[tname]), file=sys.stdout)
