import os, shutil, re, sys, tqdm
import xml.etree.cElementTree as ET
from xml.dom                import minidom
from pylatexenc.latexencode import UnicodeToLatexEncoder, \
    UnicodeToLatexConversionRule, RULE_DICT #unicode_to_latex
from unidecode              import unidecode
from pybtex.database        import BibliographyData, Entry
from ..utils.archives       import volumes
from ..exports.anthology    import order_papers, order_session

BASE_URL = 'http://talnarchives.atala.org'

def texify(string, encode=False):
    """Return a modified version of the argument string where non-ASCII symbols have
    been converted into LaTeX escape codes.
    """
    u = UnicodeToLatexEncoder(
        conversion_rules=[
            UnicodeToLatexConversionRule(rule_type=RULE_DICT, rule={
                0x0251:r'\textscripta',
                0x0254:r'\textopeno',
                0x0255:r'\textctc',
                0x026A:r'\textsci',
                0x0281:r'\textinvscr',
                0x0282:r'\textrtails',
                0x0283:r'\textesh',
                0x028A:r'\textupsilon',
                0x028F:r'\textscy',
                0x0292:r'\textyogh',
                0x02B0:r'\textsuperscript{h}',
                0x02C8:r'\textsuperscript{\textpipe}',
                0x0303:r'\textsuperscript{\textasciitilde}',
                0x201F:r'\textsuperscript{\textdoublegrave{}}'
            }),
            'defaults'
        ]
    )
    s = u.unicode_to_latex(string).replace(r'{\textquoteright}',"'")\
                                  .replace(r'{\textquoteleft}',"'")\
                                  .replace(r'{\oe}',"\oe ")\
                                  .replace(r'{\textquotedblleft}', '"')\
                                  .replace(r'{\textquotedblright}', '"')\
                                  .replace(r'{\textquotedblleft}', '"')\
                                  .replace(r'{\textquotedblright}', '"')\
                                  .replace(r'{\textendash}', '-')\
                                  .replace(r'\textquotesingle', "'")\
                                  .replace(r'{\textasciitilde}','~')\
                                  .replace(r'{\textasciicircum}', "^")\
                                  .replace(r'\{', "{")\
                                  .replace(r'\}', "}")\
                                  .replace(r'\$', "$")\
                                  .replace(r'{\textbackslash}', "\\")

    if encode:
        return string
    else:
        return s

def write_xml(event, stopwords, verbose, keep, sessions, latex_encode):
    # Preparing XML content (DOM)
    root     = ET.Element('conference')
    edition  = ET.SubElement(root, 'edition')
    articles = ET.SubElement(root, 'articles')
    # Preparing output files
    eventname= event.__dict__['abbrev'] + \
               '-' + str(event.__dict__['year'])
    indir    = os.getcwd()
    xmldir   = os.path.join(indir, "out")
    xmlfile  = os.path.join(xmldir, eventname, \
                            eventname.lower() + '.xml')
    bibfile  = os.path.join(xmldir, eventname, \
                            eventname.lower() + '.bib')
    bibdir   = os.path.join(xmldir, eventname, 'bib')
    pdfdir   = os.path.join(xmldir, eventname, 'actes')
    if not os.path.exists(os.path.join(xmldir, eventname)):
        os.mkdir(os.path.join(xmldir, eventname))
    if not os.path.exists(bibdir):
        os.mkdir(bibdir)
    if not os.path.exists(pdfdir):
        os.mkdir(pdfdir)
    # Compiling conference bib content
    bibfileh = open(bibfile, 'wt')
    urlpref  = os.path.join(BASE_URL, event.__dict__['abbrev'], eventname) #default value
    if 'base_url' in event.__dict__ :
        urlpref = event.__dict__['base_url'] #the base_url is specified at the event level
    bib_data = BibliographyData(
        { event.__dict__['abbrev'] + \
          ':' + str(event.__dict__['year']) : \
          Entry('proceedings', [
              ('editor', texify(' and '.join(event.__dict__['chairs']), latex_encode)),
              ('title',  texify(event.__dict__['booktitle'], latex_encode)),
              ('month',  str(event.__dict__['month'])),
              ('year',   str(event.__dict__['year'])),
              ('address',texify(event.__dict__['location'], latex_encode)),
              ('publisher', 'Association pour le Traitement Automatique des Langues'),
              ('url',    urlpref),
          ]),
        })
    bibfileh.write(bib_data.to_string('bibtex'))
    bibfileh.write('\n\n')
    ## Process edition
    ET.SubElement(edition, 'acronyme').text = event.__dict__['abbrev'] +\
                                              "'"+str(event.__dict__['year'])
    ET.SubElement(edition, 'titre').text    = event.__dict__['title']
    ET.SubElement(edition, 'ville').text    = event.__dict__['location'].split(', ')[0]
    ET.SubElement(edition, 'pays').text     = event.__dict__['location'].split(', ')[1]
    ET.SubElement(edition, 'dateDebut').text= event.__dict__['begin'].strftime('%Y-%m-%d')
    ET.SubElement(edition, 'dateFin').text  = event.__dict__['end'].strftime('%Y-%m-%d')
    ET.SubElement(edition, 'siteWeb').text  = event.__dict__['url'] 
    presidents= ET.SubElement(edition, 'presidents')
    for c in event.__dict__['chairs']:
        president = ET.SubElement(presidents, 'president')
        ET.SubElement(president, 'prenom').text = (' '.join(c.split(' ')[:-1])).strip()
        ET.SubElement(president, 'nom').text    = c.split(' ')[-1] 
    types     = ET.SubElement(edition, 'typeArticles')
    for t in event.__dict__['tracks']:
        ET.SubElement(types, 'type', id=t).text = dict(volumes)[t] if t in dict(volumes) else event.__dict__['tracks'][t].__dict__['fullname']
    ## Process articles
    for t in event.__dict__['tracks']:
        print('Processing track:', t, file=sys.stderr)
        order = 'input' #default
        start = 1       #default
        ## Logging (keep submissions info)
        if keep:
            logfile = open(os.path.join(indir,'submissions-'+eventname+'-'+t+'.in.csv'),'w') 
        papers  = event.__dict__['tracks'][t].articles
        # track's config overrides command line one
        if event.__dict__['tracks'][t].order != '':
            order = event.__dict__['tracks'][t].order
        ordered = papers
        if sessions and event.__dict__['tracks'][t].sessions != '':
            ordered = order_session(papers, order, stopwords, verbose, \
                                    event.__dict__['tracks'][t])
        else:
            ordered = order_papers(papers, order, stopwords, verbose, \
                                   event.__dict__['tracks'][t].authors)
        # Track settings overwrite cli start option
        if int(event.__dict__['tracks'][t].startpage) > 0:
            start = int(event.__dict__['tracks'][t].startpage)
        current_pos = start
        for art in tqdm.tqdm(ordered):
            if art:
                if keep:
                    LOG_PATTERN = ['paperid', 'authors', 'title', 'track', 'url', \
                               'title2', 'language', 'accept', 'keywords']
                    s = []
                    for y in LOG_PATTERN:
                        if y == 'url':
                            s.append(os.path.basename(art.__dict__[y]))
                        elif y == 'accept':
                            s.append('ACCEPT')
                        else:                            
                            if type(art.__dict__[y]) == str :
                                s.append(art.__dict__[y])
                            else: 
                                s.append(', '.join(art.__dict__[y]))
                    print('\t'.join(s),file=logfile) 
                ## Updating XML file
                article = ET.SubElement(articles, 'article', id=art.__dict__['paperid'])
                auteurs = ET.SubElement(article, 'auteurs')
                affilia = []
                autbib  = [] #authors as bibtex strings
                try:
                    for au in event.__dict__['tracks'][t].authors[int(art.__dict__['paperid'])]:
                        auteur  = ET.SubElement(auteurs, 'auteur')
                        autbib.append((au.__dict__['firstname'], \
                                       au.__dict__['lastname']))
                        ET.SubElement(auteur, 'prenom').text       = au.__dict__['firstname']
                        ET.SubElement(auteur, 'nom').text          = au.__dict__['lastname']
                        ET.SubElement(auteur, 'email').text        = au.__dict__['email']
                        ET.SubElement(auteur, 'affiliationId').text= str(au.__dict__['rank'])
                        affilia.append(au.__dict__['affiliation'])
                except KeyError:
                    for aut2 in art.__dict__['authors'].replace(' and ', ', ').split(', '):
                        aut     = re.sub(r'([^\\])~', r'\1 ', aut2)
                        auteur  = ET.SubElement(auteurs, 'auteur')
                        fname   = aut.split(' ')[0]
                        lname   = ' '.join(aut.split(' ')[1:])
                        autbib.append((fname, lname))
                        ET.SubElement(auteur, 'prenom').text       = fname
                        ET.SubElement(auteur, 'nom').text          = lname
                affiliations = ET.SubElement(article, 'affiliations')
                for aff in range(len(affilia)):
                    ET.SubElement(affiliations, 'affiliation', \
                                  affiliationId=str(aff+1)).text = affilia[aff]
                if art.__dict__['language'] == 'fr':
                    ET.SubElement(article, 'titre').text    = art.__dict__['title']
                    ET.SubElement(article, 'resume').text   = art.__dict__['abstract']
                    ET.SubElement(article, 'mots_cles').text= art.__dict__['keywords']
                    ET.SubElement(article, 'title').text    = ''
                    ET.SubElement(article, 'abstract').text = ''
                    ET.SubElement(article, 'keywords').text = ''
                    ET.SubElement(article, 'language').text = 'french' 
                else:
                    ET.SubElement(article, 'titre').text    = ''
                    ET.SubElement(article, 'resume').text   = ''
                    ET.SubElement(article, 'mots_cles').text= ''
                    ET.SubElement(article, 'title').text    = art.__dict__['title']
                    ET.SubElement(article, 'abstract').text = art.__dict__['abstract']
                    ET.SubElement(article, 'keywords').text = art.__dict__['keywords']
                    ET.SubElement(article, 'language').text = 'english' 
                ET.SubElement(article, 'type').text         = art.__dict__['track']
                pages = str(current_pos) + '-' + str(current_pos + art.__dict__['numpages']-1)
                current_pos += art.__dict__['numpages']
                ET.SubElement(article, 'pages').text        = pages
                ## Generate article bib file (and populating event bib file)
                if 'base_url' in event.__dict__['tracks'][t].__dict__: #urlpref is defined at the track level
                    urlpref = event.__dict__['tracks'][t].__dict__['base_url']
                bib_art = BibliographyData({
                    '-'.join(list(map(lambda x: unidecode(x[1].replace(' ', '-')), autbib)))+':'+\
                    event.__dict__['abbrev'] + ':' + str(event.__dict__['year']) \
                    : Entry('inproceedings', [
                        ('author',    texify(' and '.join(list(map(lambda x: x[1] + ', ' + x[0], \
                                                                   autbib))), latex_encode)),
                        ('title',     texify(art.__dict__['title'], latex_encode)),
                        ('booktitle', texify(event.__dict__['booktitle'] + '. ' + \
                                             event.__dict__['tracks'][t].fullname, latex_encode)),
                        ('month',     str(event.__dict__['month'])),
                        ('year',      str(event.__dict__['year'])),
                        ('address',   texify(event.__dict__['location'], latex_encode)),
                        ('publisher', 'Association pour le Traitement Automatique des Langues'),
                        ('pages',     pages),
                        ('note',      texify(art.__dict__['title2'], latex_encode)), 
                        ('abstract',  texify(art.__dict__['abstract'], latex_encode)),
                        ('keywords',  texify(art.__dict__['keywords'], latex_encode)),
                        ('url',       os.path.join(urlpref, art.__dict__['paperid']+'.pdf')),
                    ]),
                })
                bibfileh.write(bib_art.to_string('bibtex'))
                bibfileh.write('\n\n')
                bib_art.to_file(os.path.join(bibdir, art.__dict__['paperid'] + '.bib'), 'bibtex')
                ## Copy pdf file
                if os.path.exists(os.path.join(pdfdir, art.__dict__['paperid'] + '.pdf')):
                    os.remove(os.path.join(pdfdir, art.__dict__['paperid'] + '.pdf'))
                pdf_indir = os.path.join(indir, t, 'pdf')
                if os.path.exists(os.path.join(indir, 'out', 'pdf_'+eventname, t, 'pdf_out')):
                    pdf_indir = os.path.join(indir, 'out', 'pdf_'+eventname, t, 'pdf_out')
                st = os.stat(os.path.join(pdf_indir, os.path.basename(art.__dict__['url'])))
                shutil.copy(os.path.join(pdf_indir, os.path.basename(art.__dict__['url'])), \
                            os.path.join(pdfdir, art.__dict__['paperid'] + '.pdf'))
                os.chmod(os.path.join(pdfdir, art.__dict__['paperid'] + '.pdf'), st.st_mode)
            else:
                current_pos += 1
        ## Close logging if needed
        if keep:
            logfile.close()
    ## Close file handler and write down XML content
    bibfileh.close()
    if verbose > 2:
        xmls   = ET.tostring(root, encoding='utf-8', short_empty_elements=False).decode()
        print(xmls)
    xmlstr = minidom.parseString(ET.tostring(root, encoding='utf-8', 
                                             short_empty_elements=False)).\
                                             toprettyxml(indent='   ')
    with open(xmlfile, 'w') as f:
        f.write(xmlstr)
