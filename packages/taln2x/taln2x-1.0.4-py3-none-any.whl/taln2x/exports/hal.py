import os, sys, shutil, re, zipfile, xmlschema, tqdm, subprocess, html
import xml.etree.cElementTree as ET
from xml.dom               import minidom
from unidecode             import unidecode
from pybtex.database       import BibliographyData, Entry
from pycountry             import countries
from urllib.parse          import quote
from nameparser            import HumanName
from pylatexenc.latex2text import LatexNodes2Text
from country_list          import countries_for_language
from ..exports.anthology   import order_papers, order_session
from ..exports.archives    import BASE_URL


def get_iso_code(name, verbose=0):
    code = None
    countries_en = {v:k for k,v in dict(countries_for_language('en')).items()}
    countries_fr = {v:k for k,v in dict(countries_for_language('fr')).items()}
    try: #Try 1: English country name
      code = countries_en[name]
    except KeyError:
        try: # Try 2: French country name
            code = countries_fr[name]
        except KeyError:
            print('[Warning] Unknown country name: ' + name, file=sys.stderr)
    return code


def write_hal_xml(event, stopwords, verbose, behalf, stamp, include_pdf, guess, dry, \
                  update, sessions, no_meta, national):
    indir    = os.getcwd()
    outdir   = os.path.join(indir, 'out')
    # Preparing output files
    eventname= 'hal_' + event.__dict__['abbrev'] + \
               '-' + str(event.__dict__['year'])
    if not os.path.exists(os.path.join(outdir, eventname)):
        os.mkdir(os.path.join(outdir, eventname))
    ## Process articles
    for t in event.__dict__['tracks']:
        print('Processing track:', t, file=sys.stderr)
        if not os.path.exists(os.path.join(outdir, eventname, t)):
            os.mkdir(os.path.join(outdir, eventname, t))
        # Get pdf url (default is TALN archives)
        pdf_url = os.path.join(BASE_URL, event.__dict__['abbrev'], \
                                event.__dict__['abbrev'] +'-'+ str(event.__dict__['year']))
        if event.__dict__['tracks'][t].base_url != '':
            if not(event.__dict__['tracks'][t].__dict__['base_url'].startswith('http')):
                pdf_url = os.path.join(BASE_URL, event.__dict__['tracks'][t].__dict__['base_url'])
            else:
                pdf_url = event.__dict__['tracks'][t].__dict__['base_url']
        else:
            if include_pdf:
                print('[Warning] Option --include-pdf used but no base_url '+\
                      'defined in track configuration (event.yml), ' +\
                      'default (TALN archives) URL is used for X2hal\'s bib import, ' +\
                      'please check output.', file=sys.stderr)
        # Check if the track's config includes a "onbehalf" field
        # to be used to set owner during HAL export
        onbehalf = behalf #default (may be None)
        if hasattr(event.__dict__['tracks'][t],'onbehalf'):
            onbehalf = event.__dict__['tracks'][t].__dict__['onbehalf']
        behalfof = [('x-onbehalfof', onbehalf)] if onbehalf is not None else []
        publisher= [('publisher',   event.__dict__['publisher'])] \
            if event.__dict__['publisher'] != '' else []
        # stamp (collection) definition
        x_stamp = stamp #default (may be None)
        if hasattr(event.__dict__['tracks'][t],'stamp'):
            x_stamp = event.__dict__['tracks'][t].__dict__['stamp']
        x_stamp_tag = [('x-stamp', x_stamp)] if x_stamp is not None else []
        # Compiling track bib content
        country=event.__dict__['location'].split('(')[0].split(',')[1].strip()
        bibfile  = os.path.join(outdir, eventname, \
                                eventname.lower() + '-' + t.lower() + '.bib')
        bibfileh = open(bibfile, 'wt')
        ttitle   = event.__dict__['booktitle'] + '. ' + \
                   event.__dict__['tracks'][t].__dict__['fullname'].replace('\\', '')
        tchairs  = event.__dict__['chairs']
        if event.__dict__['tracks'][t].chairs != '':
            tchairs = list(map(lambda y : HumanName(y.strip()).last+', '+\
                               HumanName(y.strip()).first,\
                               event.__dict__['tracks'][t].__dict__['chairs'].split(',')))
        #print(country, countries.get(name=country))
        bib_data = BibliographyData(
            { unidecode(event.__dict__['abbrev']) + \
              ':' + str(event.__dict__['year']) : \
              Entry('proceedings', [
                  ('editor',      ' and '.join(tchairs)),
                  ('title',       ttitle),
                  ('month',       str(event.__dict__['month'])),
                  ('year',        str(event.__dict__['year'])),
                  ('address',     event.__dict__['location']),
                  ('x-language',  'fr'),
                  ('x-audience',  'National' if national else 'International'),
                  ('x-popularlevel', 'No'),
                  ('x-city',      event.__dict__['location'].split(',')[0].strip()),
                  ('x-country',   get_iso_code(name=country) \
                   if get_iso_code(name=country) is not None \
                   else 'FR'),
                  ('x-conferencestartdate', event.__dict__['begin'].isoformat()),
                  ('url',         event.__dict__['url']),
              ] + behalfof + x_stamp_tag + publisher),
            })
        bibfileh.write(bib_data.to_string('bibtex'))
        bibfileh.write('\n\n')
        ## Process paper in right order (cf automatic numbering)
        papers  = event.__dict__['tracks'][t].__dict__['articles']
        # track's config overrides command line one
        start   = 1 #default
        if int(event.__dict__['tracks'][t].__dict__['startpage']) > 0:
            start = int(event.__dict__['tracks'][t].__dict__['startpage'])
        order   = 'input' #default
        if event.__dict__['tracks'][t].order != '':
            order = event.__dict__['tracks'][t].__dict__['order']
        current_pos = start
        ordered = papers
        if sessions and event.__dict__['tracks'][t].sessions != '':
            ordered = order_session(papers, order, stopwords, verbose, \
                                    event.__dict__['tracks'][t])
        else:
            ordered = order_papers(papers, order, stopwords, verbose, \
                                   event.__dict__['tracks'][t].__dict__['authors'])
        for art in tqdm.tqdm(ordered):
            if art:
                write_hal_article(event, t, indir, os.path.join(outdir, eventname), \
                                  art, current_pos, bibfileh, behalfof, x_stamp_tag, \
                                  include_pdf, guess, dry, update, no_meta, pdf_url, \
                                  national, verbose)
                current_pos += art.__dict__['numpages']
            else:
                current_pos += 1 #skip session's delimiter
        ## Close file handler and write down BIB content (cf X2Hal)
        bibfileh.close()
        ## Prepare shell script for upload to HAL via cURL
        shellfile = os.path.join(outdir, eventname, \
                                eventname.lower() + '-' + t.lower() + '.sh')
        shellfileh= open(shellfile, 'wt')
        logfile = os.path.join(eventname.lower() + '-' + t.lower() + '.log')
        curl = [f'#!/bin/bash\nrm -f {logfile}\ncd {t}\nfor i in $(ls *.sh)\ndo\n',
                f'\techo Processing article and file ${{i}} >> ../{logfile} ;\n'          
                f'\tbash ${{i}} >> ../{logfile} ;',
                f'\ndone\n']
        shellfileh.write(' '.join(curl))
        shellfileh.close()

def write_hal_article(event, track, indir, outdir, art, current_pos, bibfileh, behalf, \
                      stamptag, include_pdf, guess, dry, update, no_meta, base_url, national, verbose):
    paperid    = art.__dict__['paperid']
    xmlfile    = os.path.join(outdir, track, paperid + '.xml')
    #print('*', art)
    #print('**', list(map(lambda x: event.__dict__['tracks'][track].__dict__['authors'][paperid][x].__str__(), range(len(event.__dict__['tracks'][track].__dict__['authors'][paperid])))))
    # Preparing XML content (DOM)
    root       = ET.Element('TEI', xmlns="http://www.tei-c.org/ns/1.0")
    root.set("xmlns:hal","http://hal.archives-ouvertes.fr/")
    text       = ET.SubElement(root, 'text')
    body       = ET.SubElement(text, 'body')
    lbibl      = ET.SubElement(body, 'listBibl')
    bfull      = ET.SubElement(lbibl,'biblFull')
    # Processing paper
    ## Updating XML file
    ## Title Statement
    tstmt      = ET.SubElement(bfull, 'titleStmt')
    title      = ET.SubElement(tstmt, 'title')
    title.set('xml:lang', html.unescape(art.__dict__['language']))
    title.text = art.__dict__['title']
    title2     = ET.SubElement(tstmt, 'title')
    title2.set('xml:lang', html.unescape(art.__dict__['language2']))
    title2.text= art.__dict__['title2']
    affilia    = [] #name, country
    autbib     = [] #authors as bibtex strings
    try:
        for au in event.__dict__['tracks'][track].__dict__['authors'][paperid]:
            auteur  = ET.SubElement(tstmt, 'author', role="aut")
            autbib.append((re.sub(r'([^\\])~', r'\1 ', au.__dict__['firstname']), \
                           re.sub(r'([^\\])~', r'\1 ', au.__dict__['lastname'])))
            pers    = ET.SubElement(auteur, 'persName')
            ET.SubElement(pers, 'forename', type='first').text = au.__dict__['firstname'].replace('~', ' ')
            ET.SubElement(pers, 'surname').text                = au.__dict__['lastname'].replace('~', ' ')
            ET.SubElement(auteur,'affiliation',ref="#localStruct-"+str(au.__dict__['rank']))
            affilia.append(au.__dict__['affiliation'])
    except KeyError: #paperid not found in track's authors (cf author_list.xlsx)
        if verbose > 0 :
            print(f'[Warning] author unknown for paper {paperid}', file=sys.stderr)
        #fall back to default authoring (w/o affiliations):
        for aut2 in art.__dict__['authors'].replace(' and ', ', ').split(', '):
            aut     = re.sub(r'([^\\])~', r'\1 ', aut2) #replace unsplittable spaces
            auteur  = ET.SubElement(tstmt, 'author', role="aut")
            #fname  = aut.split(' ')[0]
            #lname  = ' '.join(aut.split(' ')[1:])
            fname   = HumanName(aut.strip()).first + ' ' + HumanName(aut.strip()).middle
            lname   = HumanName(aut.strip()).last
            autbib.append((fname, lname))
            pers    = ET.SubElement(auteur, 'persName')
            ET.SubElement(pers, 'forename', type="first").text = fname
            ET.SubElement(pers, 'surname').text                = lname
    ## Edition Statement
    estmt  = ET.SubElement(bfull, 'editionStmt')
    edition= ET.SubElement(estmt, 'edition')
    if include_pdf:
        ET.SubElement(edition, 'ref', type='file', subtype='greenPublisher', n='1', \
                      target=paperid + '.pdf')
    ## Publication Statement
    pstmt = ET.SubElement(bfull, 'publicationStmt')
    avail = ET.SubElement(pstmt, 'availability')
    ET.SubElement(avail, 'licence', target="https://creativecommons.org/licenses/by/")
    ## Series Statement
    sstmt = ET.SubElement(bfull, 'seriesStmt')
    if stamptag != []:
        for x in stamptag[0][1].split(';'):
            ET.SubElement(sstmt, 'idno', type="stamp", n=x)
    ## Notes Statement
    audience_code = "3" if national else "2"
    nstmt = ET.SubElement(bfull, 'notesStmt')
    ET.SubElement(nstmt, 'note', type="audience",   n=audience_code) 
    #1 => unspecified, 2 => international, 3 => national
    ET.SubElement(nstmt, 'note', type="invited",    n="0")
    ET.SubElement(nstmt, 'note', type="popular",    n="0")
    ET.SubElement(nstmt, 'note', type="peer",       n="1")
    ET.SubElement(nstmt, 'note', type="proceedings",n="1")
    ## Source Desc
    sdesc   = ET.SubElement(bfull, 'sourceDesc')
    bstruct = ET.SubElement(sdesc, 'biblStruct')
    analytic= ET.SubElement(bstruct, 'analytic')
    titleA  = ET.SubElement(analytic, 'title')
    titleA.set('xml:lang', art.__dict__['language'])
    titleA.text = art.__dict__['title']
    try:
        #print(paperid, sorted(event.__dict__['tracks'][track].__dict__['authors']))
        for au in event.__dict__['tracks'][track].__dict__['authors'][paperid]:
            auteurA  = ET.SubElement(analytic, 'author', role="aut")
            persA    = ET.SubElement(auteurA, 'persName')
            ET.SubElement(persA, 'forename', type='first').text = au.__dict__['firstname'].replace('~', ' ')
            ET.SubElement(persA, 'surname').text                = au.__dict__['lastname'].replace('~', ' ')
            ET.SubElement(auteurA, 'email').text = au.__dict__['email']
            ET.SubElement(auteurA, 'affiliation',ref="#localStruct-"+str(au.__dict__['rank']))
    except KeyError as ke:
        if verbose > 0:
            print(f'[Warning] author unknown for paper {paperid}', file=sys.stderr)
        for aut2 in art.__dict__['authors'].replace(' and ', ', ').split(', '):
            aut      = re.sub(r'([^\\])~', r'\1 ', aut2)
            auteurA  = ET.SubElement(analytic, 'author', role="aut")
            #fname   = aut.split(' ')[0]
            #lname   = ' '.join(aut.split(' ')[1:])
            fname    = HumanName(aut.strip()).first + ' ' + HumanName(aut.strip()).middle
            lname    = HumanName(aut.strip()).last
            persA    = ET.SubElement(auteurA, 'persName')
            ET.SubElement(persA, 'forename', type="first").text = fname
            ET.SubElement(persA, 'surname').text                = lname
    monog = ET.SubElement(bstruct, 'monogr')
    ET.SubElement(monog, 'title', level="m").text = event.__dict__['booktitle'] + '. ' + \
                                                    event.__dict__['tracks'][track].__dict__['fullname']
    meetin= ET.SubElement(monog, 'meeting')
    ET.SubElement(meetin, 'title').text = event.__dict__['title'].replace('\\', '-')
    ET.SubElement(meetin, 'date', type="start").text = str(event.__dict__['year'])
    ET.SubElement(meetin, 'settlement').text = event.__dict__['location'].split(',')[0]
    country = event.__dict__['location'].split('(')[0].split(',')[1].strip()
    #print(country,  countries.get(name=country))
    ET.SubElement(meetin, 'country', key=get_iso_code(name=country))
    tchairs = event.__dict__['chairs']
    if event.__dict__['tracks'][track].chairs != '':
        tchairs = list(map(lambda y : HumanName(y.strip()).last+', '+\
                            HumanName(y.strip()).first,\
                            event.__dict__['tracks'][track].__dict__['chairs'].split(',')))
    for c in tchairs:
        ET.SubElement(monog, 'editor').text = c
    imprint = ET.SubElement(monog, 'imprint')
    ET.SubElement(imprint, 'publisher').text = event.__dict__['publisher']
    pages = art.__dict__['pages']
    if pages == '':
        pages = str(current_pos) + '-' + str(current_pos + art.__dict__['numpages'] - 1)
    ET.SubElement(imprint, 'biblScope', unit="pp").text = pages
    ET.SubElement(imprint, 'date', type="datePub").text = str(event.__dict__['year'])
    ## profileDesc
    pdesc = ET.SubElement(bfull, 'profileDesc')
    lusage= ET.SubElement(pdesc, 'langUsage')
    lang  = art.__dict__['language'] if art.__dict__['language'] == 'fr' else 'en' 
    #lang defined via an if expression due to (rare) wrong lang detect
    ET.SubElement(lusage, 'language', ident=lang)
    tclass= ET.SubElement(pdesc, 'textClass')
    kwords= ET.SubElement(tclass, 'keywords', scheme="author")
    for k in art.__dict__['keywords'].split(','):
        kw = ET.SubElement(kwords, 'term')
        kw.text = k.strip()
        kw.set('xml:lang', lang)
    ET.SubElement(tclass, 'classCode', scheme="halDomain", n="info.info-cl")
    ET.SubElement(tclass, 'classCode', scheme="halTypology", n="COMM")
    abstract = ET.SubElement(pdesc, 'abstract')
    abstract.text = art.__dict__['abstract']
    abstract.set('xml:lang', lang)
    ## Back
    back = ET.SubElement(text, 'back')
    lorg = ET.SubElement(back, 'listOrg', type="structures")
    #print('**',affilia)
    if len(affilia) > 0:
        for aff in range(len(affilia)):
            affname   = ', '.join(affilia[aff].split(',')[:-1]).strip()
            affcountry= affilia[aff].split(',')[-1].strip()
            org       = ET.SubElement(lorg, 'org', type="institution")
            org.set('xml:id', "localStruct-" + str(aff+1))
            ET.SubElement(org, 'orgName').text = affname
            desc      = ET.SubElement(org, 'desc')
            address   = ET.SubElement(desc, 'address')
            #print('**',affcountry, art.__dict__['paperid'], get_iso_code(affcountry))
            real_affcountry = affcountry.replace('South Korea','Korea, Republic of').replace('République tchèque', 'Tchéquie')
            ET.SubElement(address, 'country', key=get_iso_code(real_affcountry))
    else:
        print(f'[Warning] affiliations not found for paper {paperid}', file=sys.stderr)
        ET.SubElement(lorg, 'org', type="institution")
    ## Generate article bib file (and populating event bib file)
    #  Get title Language
    title2label = 'x-title_en' if lang == 'fr' else 'x-title_fr'
    #  Include pdf if required
    pdf_info = []
    if include_pdf:
        pdf_info = [('pdf', os.path.join(base_url, paperid +'.pdf')),
                    ('x-filesource', 'greenPublisher')]
    bib_key = '-'.join(list(map(lambda x: unidecode(x[1].replace(' ', '-')), autbib[:3]))) + \
              '-p' + pages.split('-')[0] + \
              ':' + unidecode(event.__dict__['abbrev']) + ':' + \
              str(event.__dict__['year'])
    tchairs  = event.__dict__['chairs']
    publisher= [('publisher',   event.__dict__['publisher'])] \
        if event.__dict__['publisher'] != '' else []
    if event.__dict__['tracks'][track].chairs != '':
        tchairs = list(map(lambda y : HumanName(y.strip()).last+', '+\
                           HumanName(y.strip()).first,\
                           event.__dict__['tracks'][track].__dict__['chairs'].split(',')))
    bib_art = BibliographyData({
        bib_key : Entry('inproceedings', [
            ('author',    ' and '.join(list(map(lambda x: x[1]+', '+x[0],autbib)))),
            ('title',     art.__dict__['title']),
            ('booktitle', event.__dict__['booktitle'] + '. ' + \
             event.__dict__['tracks'][track].__dict__['fullname'].replace('\\', '')),
            ('editor',    ' and '.join(tchairs)),
            ('month',     str(event.__dict__['month'])),
            ('year',      str(event.__dict__['year'])),
            ('address',   event.__dict__['location']),
            ('pages',     pages),
            (title2label, art.__dict__['title2']), 
            ('abstract',  art.__dict__['abstract']),
            ('keywords',  art.__dict__['keywords'].replace(',', ';')),
            ('x-language',lang),
            ('x-audience','National' if national else 'International'),
            ('x-peerreviewing','Yes'),
            ('x-popularlevel', 'No'),
            ('x-invitedcommunication', 'No'),
            ('x-proceedings',  'Yes'),
            ('x-city',    event.__dict__['location'].split(',')[0].strip()),
            ('x-country', get_iso_code(name=country)),
            ('x-conferencestartdate', event.__dict__['begin'].isoformat()),
        ] + behalf + publisher + stamptag + pdf_info),
    })
    bibfileh.write(bib_art.to_string('bibtex'))
    bibfileh.write('\n\n')
    #debug only
    #print(bib_art.to_string('bibtex'))
    xmlstr=''
    if update and no_meta:
        cmd   = ["curl", "-s", \
                 'https://api.archives-ouvertes.fr/search/?q=title_s:\"'\
                 + quote(LatexNodes2Text().latex_to_text(art.__dict__['title']))\
                 .replace('%C2%A0', '%20').replace('%20%20%20', '%26')\
                 + '\"&wt=xml-tei&fl=*']
        #print(' '.join(cmd))
        out   = subprocess.check_output(cmd)
        root2 = ET.fromstring(out.decode())
        ns    = {'ns0':"http://www.tei-c.org/ns/1.0"}
        root2.remove(root2.find('ns0:teiHeader', ns))
        # In case the search is sucessful:
        bibf  = root2.find('.//ns0:biblFull', ns)
        if bibf is not None: #there is a result (should be unique cf search by exact title)
            # Clear tags to be ignored
            dep = root2.find (".//ns0:editor[@role='depositor']", ns)
            if dep is not None:
                dep.clear()
            edi = root2.find('.//ns0:editionStmt', ns)
            if edi is not None:
                edi.clear()
                ed = ET.SubElement(edi, 'edition')
                # Attach new pdf version
                if include_pdf:
                    ET.SubElement(ed, 'ns0:ref', type='file', subtype='greenPublisher', n='1', \
                                  target=paperid + '.pdf')
            # Update licence (mandatory to fix previous exports)
            licen = root2.find('.//ns0:licence', ns)
            if licen is not None :
                licen.clear()
                root2.find('.//ns0:licence', ns).set('target',"https://creativecommons.org/licenses/by/")
            else:
                pubs = root2.find('.//ns0:publicationStmt', ns)
                avai = ET.SubElement(pubs, 'ns0:availability')
                ET.SubElement(avai, 'ns0:licence', target="https://creativecommons.org/licenses/by/")
            # Fix idno for authors
            auth = root2.findall('.//ns0:author', ns)
            for au in auth:
                keep      = True
                to_remove = []
                for child in au:
                    if child.tag == '{http://www.tei-c.org/ns/1.0}affiliation':
                        keep = False
                    elif child.tag == '{http://www.tei-c.org/ns/1.0}idno':
                        if not keep:
                            to_remove.append(child)
                    elif child.tag == '{http://www.tei-c.org/ns/1.0}email':
                        to_remove.append(child) #email received by HAL search are ill-formed
                for i in range(len(to_remove)):
                    x = to_remove.pop()
                    au.remove(x)
        else:
            print('\n[Warning] No reference found in HAL for paper ' + art.__dict__['paperid'] + \
                  ' (article skipped)\n', file=sys.stderr) 
            return #move to next article
        # Write XML to string (while removing ns0 namespace prefix)
        root2.set("xmlns:hal","http://hal.archives-ouvertes.fr/")
        xmlstr= minidom.parseString(ET.tostring(root2, encoding='utf-8', 
                                                short_empty_elements=False)).\
                                                toprettyxml(indent='   ').\
                                                replace(':ns0', '').replace('ns0:', '')
        #print(xmlstr)
    else:
        ## Write down XML file
        #xmls   = ET.tostring(root, encoding='utf-8', short_empty_elements=False).decode()
        #print(xmls)
        xmlstr = minidom.parseString(ET.tostring(root, encoding='utf-8', 
                                                 short_empty_elements=False)).\
                                                 toprettyxml(indent='   ')
    with open(xmlfile, 'w') as f:
        f.write(xmlstr)
    ## Validate XML file
    schema = xmlschema.XMLSchema(os.path.join(indir, 'out', 'aofr.xsd'))
    try:
        schema.validate(xmlfile)
    except xmlschema.validators.exceptions.XMLSchemaChildrenValidationError as xe:
        print('XML schema validation error', file=sys.stderr)
        print(xe, file=sys.stderr)
        sys.exit(1)
    ## Copy pdf file and zip it together with XML 
    if include_pdf:
        if os.path.exists(os.path.join(outdir, track, paperid + '.pdf')):
            os.remove(os.path.join(outdir, track, paperid + '.pdf'))
        pdf_indir = os.path.join(indir, track, 'pdf')
        evtname   = event.__dict__['abbrev'] + '-' + str(event.__dict__['year'])
        #print('**', os.path.join(indir, 'out', 'pdf_'+evtname, track, 'pdf_out'))
        if os.path.exists(os.path.join(indir, 'out', 'pdf_'+evtname, track, 'pdf_out')):
            pdf_indir = os.path.join(indir, 'out', 'pdf_'+evtname, track, 'pdf_out')
        st = os.stat(os.path.join(pdf_indir, os.path.basename(art.__dict__['url'])))
        shutil.copy(os.path.join(pdf_indir, os.path.basename(art.__dict__['url'])), \
                    os.path.join(outdir, track, paperid + '.pdf'))
        os.chmod(os.path.join(outdir, track, paperid + '.pdf'), st.st_mode)

        # Zip file cf 
        # https://stackoverflow.com/questions/1855095/
        # how-to-create-a-zip-archive-of-a-directory-in-python
        zipf = zipfile.ZipFile(os.path.join(outdir, track, paperid + '.zip'), \
                               'w', zipfile.ZIP_DEFLATED)
        xmlfile = os.path.join(outdir, track, paperid + '.xml')
        pdffile = os.path.join(outdir, track, paperid + '.pdf')
        zipf.write(xmlfile, os.path.basename(xmlfile))
        zipf.write(pdffile, os.path.basename(pdffile))
    ## Write down shell script for upload via cURL
    shellfile = os.path.join(outdir, track, paperid + '.sh')
    shellfileh= open(shellfile, 'wt')
    serv = 'https://api.archives-ouvertes.fr'
    opt  = '-H "X-test:1"' if dry else ''
    beh  = '-H "On-Behalf-Of: ' + \
           ';'.join(list(map(lambda x: 'idhal|' + x, behalf[0][1].split(';')))) \
           + '"' if len(behalf) > 0 else ''
    getid= f'ID=$(curl -s \'{serv}/search/?q=title_s:\"' \
                 + quote(LatexNodes2Text().latex_to_text(art.__dict__['title']))\
                 .replace('%C2%A0', '%20').replace('%20%20%20', '%26') \
                 + '\"&fl=halId_s\' | jq .response.docs[0].halId_s' \
                 + '| sed -e \'s/\"//g\'' + ')' \
                 if update else ''
    pid  = f'\necho Found ID: "${{ID}}"\n' if update else ''
    rtype= '-X PUT' if update else '-X POST'
    curl = []
    if include_pdf:
        gue  = '-H "X-Allow-Completion: grobid,affiliation"' if guess else '-H "LoadFilter: noaffiliation"'
        suf  = f'${{ID}}' if update else 'hal/'
        curl = [f'#!/bin/bash\n\n{getid}\n{pid}\n',
                f'\ncurl {rtype} -v -u $LOGIN:$PASSWORD',
                f'{serv}/sword/{suf} {beh} {gue} {opt}',
                f'-H "Packaging:http://purl.org/net/sword-types/AOfr"',
                f'-H "Content-Type:application/zip"',
                f'-H "ForceDoublonByTitle: 1"', #we solve duplicates a posteriori (merging of deposits)
                f'-H "Content-Disposition: attachment; filename={paperid}.xml"', 
                f'--data-binary @{paperid}.zip\n']        
    else:
        gue  = '-H "X-Allow-Completion: affiliation"' if guess else '-H "LoadFilter: noaffiliation"'
        vers = f'VERSION=$(curl -s \'{serv}/search/?q=title_s:\"' \
                 + quote(LatexNodes2Text().latex_to_text(art.__dict__['title']))\
                 .replace('%C2%A0', '%20').replace('%20%20%20', '%26') \
                 + '\"&fl=version_i\' | jq .response.docs[0].version_i' \
                 + ' )' \
                 if update else ''
        suf  = f'${{ID}}v${{VERSION}}' if update else 'hal/'
        curl = [f'#!/bin/bash\n\n{getid}\n{vers}\n{pid}\n',
                f'\ncurl {rtype} -v -u $LOGIN:$PASSWORD',
                f'{serv}/sword/{suf} {beh} {gue} {opt}',
                f'-H "Packaging:http://purl.org/net/sword-types/AOfr"',
                f'-H "Content-Type:text/xml"',
                f'-H "ForceDoublonByTitle: 1"', #we solve duplicates a posteriori (merging of deposits)
                f'-d @{paperid}.xml\n']
    shellfileh.write(' '.join(curl))
    shellfileh.close()
