import os, sys, csv, shutil, subprocess, re
import locale, threading
from contextlib  import contextmanager
from distutils   import dir_util
from unidecode   import unidecode
from .           import Event, Article, Author
from nameparser  import HumanName

def clean_easy2acl(where):
    tmpfiles = ['meta', 'submissions', 'submission.csv', 'accepted']
    tmpdir   = ['pdf', 'book-proceedings', 'proceedings']
    for f in tmpfiles: 
        try:
            os.remove(os.path.join(where, f))
        except FileNotFoundError as e:
            pass
    for d in tmpdir:
        try:
            shutil.rmtree(os.path.join(where, d))
        except FileNotFoundError as e:
            pass
    if not os.path.exists(os.path.join(where, 'book-proceedings')):
        os.mkdir(os.path.join(where, 'book-proceedings'))
    if not os.path.exists(os.path.join(where,'pdf')):
        os.mkdir(os.path.join(where,'pdf'))

def order_session(papers, order, stopwords, verbose, track):
    ordered = []
    for s in track.__dict__['sessions'].split(';'):
        #collect corresponding papers
        spapers = list(filter(lambda x: x.__dict__['paperid'] in track.__dict__['partition'][s.strip()], \
                              papers))
        ospapers= order_papers(spapers, order, stopwords, verbose, track.__dict__['authors'])
        ordered.extend([None] + ospapers) #None is used as a session delimiter
    return ordered

def order_papers(papers, order, stopwords, verbose, tauthors):
    ordered = papers
    if order == 'author':
        try:
            all_authors = []
            for paper in ordered:
                pid = paper.__dict__['paperid']
                pauthors = ''.join(list(map(lambda x: x.__name4ordering__(), tauthors[pid])))
                all_authors.append((pid, pauthors))
            #print(all_authors)
            opauth   = sorted(all_authors, key=lambda z : z[1:]) #sort according to authors (not paperid)
            pdict    = {n.__dict__['paperid'] : n for n in papers} #turn papers into a dictionary
            ordered  = list(map(lambda x : pdict[x[0]], opauth))   #actual ordering
        except KeyError as ke:
            print('[Warning] Paper ' + str(ke) + ' not found in track\'s authors, '+\
                  'falling back on track\'s articles for ordering authors.', file=sys.stderr)
            ordered = sorted(papers, key=lambda x : 
                             ''.join(list(map(lambda y : (unidecode(HumanName(y.strip()).middle)+\
                                                          unidecode(HumanName(y.strip()).last)+\
                                                          unidecode(HumanName(y.strip()).first)),\
                                              x.__dict__['authors'].replace(' and ', ', ')\
                                              .split(',')))))
        #to debug only:               
        #for x in ordered:
        #    print('*', x.__dict__['authors'])
    elif order == 'title':
        if stopwords:
            import nltk
            from nltk.corpus import stopwords as sw
            for x in papers:
                if x.__dict__['language'] == 'fr':
                    wordpos  = 0
                    sentence = re.split('\W+', x.__dict__['title'])
                    while wordpos in range(len(sentence)) \
                          and sentence[wordpos].lower() in \
                          [x for x in sw.words('french') if x not in ['nous']]:
                        # nous should not be considered a stopword
                        wordpos += 1
                    x.__dict__['titleTmp'] = unidecode((' '.join(sentence[wordpos:])).lower())
                else:
                    x.__dict__['titleTmp'] = unidecode(x.__dict__['title'].lower())
                if verbose > 2:
                    print(x.__dict__['title'])
                    print(x.__dict__['titleTmp'])
            ordered = sorted(papers, key=lambda x : x.__dict__['titleTmp'])
        else:
            ordered = sorted(papers, key=lambda x : unidecode(x.__dict__['title']))
    return ordered


def easy2acl_event(where, event, track):
    ACLINFO = ['anthology', 'title', 'month', 'year', \
               'location', 'publisher', 'chairs', 'shortbooktitle']
    # Turn e into easy2acl's expected config file
    with open(os.path.join(where,'meta'), 'w') as outfile:
        for k,v in event.__dict__.items():
            if k in ACLINFO:
                if k == 'anthology':
                    print('abbrev' + ' ' + v.lower(), file=outfile)
                elif k == 'chairs': 
                    # if track has specific chairs, override general settings
                    if event.__dict__['tracks'][track].chairs != '':
                        for y in event.__dict__['tracks'][track].chairs.split(','):
                            print(k + ' ' + y.split()[1].strip() + ', ' + \
                                  y.split()[0].strip(), file=outfile)
                    else: #recall list of chairs are split over lines
                        for x in v:
                            print(k + ' ' + x.split(',')[0].strip() + ', ' + \
                                  x.split(',')[1].strip(), file=outfile)
                elif type(v) == list: 
                    for x in v:
                        print(str(k) + ' ' + str(v), file=outfile)
                else:
                    print(str(k) + ' ' + str(v), file=outfile)
        print('booktitle' + ' ' + event.__dict__['booktitle'] + '. ' +  \
              event.__dict__['tracks'][track].__dict__['fullname'], file=outfile)
        print('volume' + ' ' + event.__dict__['tracks'][track].__dict__['volume'], \
              file=outfile)
    if event.__dict__['anthology'] == '':
        print('Missing anthology id, cannot export to anthology format', file=sys.stderr)
        sys.exit(1)


def easy2acl_articles(where, e, papers, order, pdfdir, bilingual, stopwords, verbose, \
                      keep, sessions):
    # Start page (useful only in case of TALN import)
    taln_start= None
    # Ordered fields used in easy2acl
    SUBMISSIONS_PATTERN     = ['paperid', 'authors', 'title', 'url', 'keywords']
    SUBMISSIONS_CSV_PATTERN = ['paperid', 'title']
    trackname = os.path.basename(os.path.dirname(pdfdir))
    indir     = os.path.dirname(os.path.join(where, '..'))
    # Logging
    if keep:
        logfile = open(os.path.join(indir, trackname, 'submissions-'+ trackname +'.in.csv'),'w')
    with open(os.path.join(where,'submissions'), 'w') as outfile1:
        with open(os.path.join(where,'accepted'), 'w') as outfile2:
            with open(os.path.join(where,'submission.csv'), 'w') as abs_csv:
                writer = csv.writer(abs_csv)
                writer.writerow(['#', 'abstract'])
                ordered = papers
                if sessions and e.__dict__['tracks'][trackname].sessions != '':
                    ordered = order_session(papers, order, stopwords, verbose, \
                                            e.__dict__['tracks'][trackname])
                else:
                    ordered = order_papers(papers, order, stopwords, verbose, \
                                           e.__dict__['tracks'][trackname].__dict__['authors'])
                for article in ordered:
                    if article:
                        #print('***',article.__dict__['title'])
                        if taln_start is None and 'pages' in article.__dict__ \
                           and article.__dict__['pages'] != '':
                            taln_start = article.__dict__['pages'].split('-')[0]
                        if bilingual:
                            article.update_title()
                        writer.writerow([article.__dict__['paperid'],\
                                         article.__dict__['abstract']])
                        #for submissions, only the first 3 columns are read by easy2acl:
                        print('\t'.join(article.__dict__[x] \
                                        if type(article.__dict__[x]) == str \
                                        else ', '.join(article.__dict__[x]) \
                                        for x in SUBMISSIONS_PATTERN), \
                              file=outfile1) 
                        #for accepted, we need the status
                        # print ID TITLE [...] STATUS => outfile2
                        print('\t'.join(article.__dict__[x] for x in SUBMISSIONS_CSV_PATTERN)+\
                              '\t'+'ACCEPT', file=outfile2)
                        #copy pdf file
                        if os.path.exists(os.path.join(pdfdir, \
                                                       os.path.basename(article.__dict__['url']))):
                            if verbose > 1:
                                print('Copying pdf file ' + os.path.basename(article.__dict__['url']),\
                                      file=sys.stderr)
                            shutil.copy(os.path.join(pdfdir, \
                                                     os.path.basename(article.__dict__['url'])), \
                                        os.path.join(where,'pdf', \
                                                     e.__dict__['anthology'] + '_' + \
                                                     str(e.__dict__['year']) + '_paper_' + \
                                                     article.__dict__['paperid'] + '.pdf'))
                        #update log
                        if keep:
                            LOG_PATTERN=SUBMISSIONS_PATTERN[:3] +['track']+\
                                         [SUBMISSIONS_PATTERN[3]]+['title2','language','accept']+\
                                         [SUBMISSIONS_PATTERN[4]]
                            s = []
                            for y in LOG_PATTERN:
                                if y == 'url':
                                    s.append(os.path.basename(article.__dict__[y]))
                                elif y == 'accept':
                                    s.append('ACCEPT')
                                else:                            
                                    if type(article.__dict__[y]) == str :
                                        s.append(article.__dict__[y])
                                    else: 
                                        s.append(', '.join(article.__dict__[y]))
                            print('\t'.join(s),file=logfile) 
                    else: #session's delimiter
                        # we add an accepted article whose id is 0
                        # print ID TITLE [...] STATUS => outfile2
                        print('\t'.join(['-1', 'session delimiter'])+ \
                              '\t'+'ACCEPT', file=outfile2)
    #close log
    if keep:
        logfile.close()
    return taln_start


def easy2acl_export(e, bilingual, stopwords, verbose, keep, sessions, latex_encode):
    indir      = os.getcwd()
    outdir     = os.path.join(indir, 'out')
    where      = os.path.join(outdir, 'easy2acl')
    if not(os.path.exists(where)):
        os.makedirs(where)
        os.makedirs(os.path.join(where, 'pdf'))
        os.makedirs(os.path.join(where, 'pdf', 'book-proceedings'))
        os.makedirs(os.path.join(where, 'pdf', 'proceedings'))
        
    eventname  = e.__dict__['abbrev'] + '-' + str(e.__dict__['year'])            
    outdirname = os.path.join(outdir, 'acl_' + eventname)
    
    for track in e.__dict__['tracks'].keys():
        order = 'input' #default
        start = 1       #default
        clean_easy2acl(where)
        print('Exporting event information', file=sys.stderr)
        easy2acl_event(where, e, track)
        #print(track, e.__dict__['tracks'][track].keys())
        print('Processing track ' + e.__dict__['tracks'][track].__dict__['fullname'], file=sys.stderr)
        print('Exporting articles information', file=sys.stderr)
        # track's config overrides command line one
        if e.__dict__['tracks'][track].order != '':
            order = e.__dict__['tracks'][track].__dict__['order']
        pdf_indir = os.path.join(indir, track, 'pdf')
        if os.path.exists(os.path.join(indir, 'out', 'pdf_'+eventname, track, 'pdf_out')):
            pdf_indir = os.path.join(indir, 'out', 'pdf_'+eventname, track, 'pdf_out')
        tstart = easy2acl_articles(where, e, e.__dict__['tracks'][track].__dict__['articles'], order, \
                                   pdf_indir, bilingual, stopwords, \
                                   verbose, keep, sessions)
        # prepare tmp pdf file for frontmatter and full volume 
        # since these won't be compiled by easy2acl itself 
        if os.path.exists(os.path.join(indir, 'out', 'pdf_'+eventname, track, 'proceedings.pdf')):
            shutil.copy(os.path.join(indir, 'out', 'pdf_'+eventname, track, 'proceedings.pdf'), \
                        os.path.join(where, 'pdf', \
                                     e.__dict__['anthology'] + '_' + \
                                     str(e.__dict__['year']) + '.pdf'))
        else:
            shutil.copy(os.path.join(outdir,'blank.pdf'), \
                        os.path.join(where, 'pdf', \
                                     e.__dict__['anthology'] + '_' + \
                                     str(e.__dict__['year']) + '.pdf'))
        if os.path.exists(os.path.join(indir, 'out', 'pdf_'+eventname, track, 'frontmatter.pdf')):
            shutil.copy(os.path.join(indir, 'out', 'pdf_'+eventname, track, 'frontmatter.pdf'), \
                        os.path.join(where, 'pdf', \
                                     e.__dict__['anthology'] + '_' + \
                                     str(e.__dict__['year']) + \
                                     '_frontmatter.pdf'))
        else:
            shutil.copy(os.path.join(outdir,'blank.pdf'), \
                        os.path.join(where, 'pdf', \
                                     e.__dict__['anthology'] + '_' + \
                                     str(e.__dict__['year']) + \
                                     '_frontmatter.pdf'))

        print('Generating bibtex for articles using easy2acl', file=sys.stderr)
        # First call of easy2acl.py
        if tstart is not None: #read from input data (case of a TALN import)
            start = tstart
        curdir = os.getcwd()
        shutil.copy(os.path.join(outdir, 'easy2acl.py'), where)
        os.chdir(where)
        # Track configuration overwrite cli start option
        if int(e.__dict__['tracks'][track].startpage) > 0:
            start = int(e.__dict__['tracks'][track].startpage)
        try:
            returncode = subprocess.call([os.path.join('.','easy2acl.py'), str(start), \
                                          str(latex_encode)], timeout=10) 
            ## Copy easy2acl's proceedings dir
            dirname = e.__dict__['abbrev'] + str(e.__dict__['year']) + \
                      '-' + track
            if os.path.exists(os.path.join(curdir, outdirname + '_data', dirname)):
                shutil.rmtree(os.path.join(curdir, outdirname + '_data', dirname))
            if returncode == 0:
                shutil.copytree('proceedings', \
                                os.path.join(curdir, outdirname + '_data', dirname, \
                                             'proceedings'))
            else:
                print('''\nCreation of proceedings in ACL format failed, 
                please check easy2acl's above message\n''', file=sys.stderr)
        except subprocess.TimeoutExpired as toe:
            print('''Creation of proceedings in ACL format failed, 
            please check the input files''', file=sys.stderr)
        os.chdir(curdir)
