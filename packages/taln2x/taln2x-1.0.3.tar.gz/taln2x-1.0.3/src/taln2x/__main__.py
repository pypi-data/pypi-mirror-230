#!/usr/bin/env python3
from . import __version__
from .utils              import readevent, easychair, archives as arin, searchid, sciencesconf
from .exports            import anthology, archives as arout, hal, dblp, pdf
from importlib.resources import files
from tomlkit             import dumps, parse
from zipfile             import ZipFile
import click, os, shutil, sys, subprocess, re, traceback

def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    version_str = 'Version ' + __version__
    click.echo(version_str)
    ctx.exit()

def remove_dir(outd):
    for the_file in os.listdir(outd):
        file_path = os.path.join(outd, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as exc:
            print(exc, file=sys.stderr)
    
def read_config():
    config_obj = None
    if not(os.path.exists('config.toml')):
        print('[Error] Configuration file config.toml not found, are you sure you are in a valid taln2x directory ?', file=sys.stderr)
        sys.exit(2)
    else:
        with open('config.toml', 'r') as config:
            config_text = config.read()
        config_obj = parse(config_text)
    return config_obj

@click.command()
@click.argument('action')
@click.argument('project_name', required=False)
@click.option('--in-format', default=None, \
              help='''input format''',
              type=click.Choice(['csv', 'xml', 'zip'], case_sensitive=False))
@click.option('--out-format', default=None, \
              help='''output format''',
              type=click.Choice(['pdf', 'acl', 'taln', 'hal', 'dblp'], \
                                case_sensitive=False))
@click.option('--verbose', '-v', default=None, type=int, \
              help='Define verbosity between 0 and 3.', show_default=True)
@click.option('--sessions', default=None, is_flag=True, \
              help='Do not ignore sessions defined in event.yml.')
@click.option('--tex-log', default=None, is_flag=True, \
              help='Do not remove logs of LaTeX compilation.')
@click.option('--stopwords', '-s', default=None, is_flag=True, \
              help='Ignore stopwords when sorting articles.')
@click.option('--ignore-pdf', default=None, is_flag=True, \
              help='Ignore metadata (abstract,keywords) from pdf ' + \
              'when these are available elsewhere.', show_default=True)
@click.option('--dump', default=None, is_flag=True, \
              help='Keep a copy of easy2acl\'s config file.')
@click.option('--xml', default=None, \
              help='''The name of the input XML file of the conference
              (TALN-archives input format).''')
@click.option('--zip-file', default=None, \
              help='''The name of the input ZIP file of the conference
              (sciencesconf input format).''')
@click.option('--anthology-id', default=None, \
              help='''The anthology ID of the conference.''')
@click.option('--bilingual', '-b', default=None, is_flag=True, \
              help='Generate bilingual article titles (cf anthology format).')
@click.option('--x-onbehalf', '-x', default=None, \
              help='''list of idHal_s (separated by ';') to be declared as co-owners
              during HAL ingestion (see https://aurehal.archives-ouvertes.fr/author).''')
@click.option('--stamp', default=None, \
              help='''Stamp (collection names, separated by ';') to be used during HAL
              export (see https://hal.science/browse/collection).''')
@click.option('--include-pdf', default=None, is_flag=True, \
              help='''During HAL ingestion, generate full exports made of references + pdf 
              files.''')
@click.option('--guess', '-g', default=None, is_flag=True, \
              help='''During HAL ingestion, activate the "guess affiliations".''')  
@click.option('--dry-run', '-d', default=None, is_flag=True, \
              help='''During HAL ingestion, use preprod server.''')  
@click.option('--halid', default=None, is_flag=True, \
              help='Include HAL id when compiling PDF proceedings.')
@click.option('--update', '-u', default=None, is_flag=True, \
              help='Update existing HAL reference/article.')
@click.option('--national', default=None, is_flag=True, \
              help='National event.', \
              show_default=True)
@click.option('--latex-encode', '-l', default=None, is_flag=True, \
              help='LaTeX-encode diacritics in output bibfiles.', \
              show_default=True)
@click.option('--no-meta', '-n', default=None, is_flag=True, \
              help='Do not miodify article metadata when updating HAL references.')
@click.option('--img', default=None, \
              help='Directory where to find user images.', \
              show_default=True)
@click.option('--lang', default=None, \
              help='Language used for pdf output.', \
              type=click.Choice(['fr', 'en'], case_sensitive=False), show_default=True)
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Display version number.')
def main(action, project_name, in_format, out_format, xml, zip_file, anthology_id, verbose, \
         bilingual, stopwords, ignore_pdf, dump, x_onbehalf, stamp, include_pdf, \
         guess, dry_run, halid, update, sessions, tex_log, no_meta, national, \
         latex_encode, img, lang):
    """Create proceedings (aka open archive) in various formats.

    ACTION should be one of : 'new' 'build' 'clean' 'list'

    In case of a *new* project, PROJECT_NAME is required (a directory of the corresponding name will be created)

    In case of a *build*, options are read from ./config.toml

    *list* is used to retrieve HAL identifiers of articles (if any)

    *clean* is used to remove output of previous conversions

    For more information, please consult https://talnarchives.gitlabpages.inria.fr/taln2x/
    """
    ############################
    ## INIT MODE
    ############################
    if action not in ['new', 'build', 'clean', 'list']:
        print("[Error] Unknown action (should be either new, convert, clean or list).", \
              file=sys.stderr)
        print("[Error] See also 'taln2x --help' for a full list of options.", \
              file=sys.stderr)        
        sys.exit(0)
    if action == 'new':
        if not(project_name):
            print("[Error] project name is missing\nPlease invoke taln2x init <project>", \
                  file=sys.stderr)
        else:
            in_dir= project_name
            if os.path.exists(in_dir):
                answer = input(f"Directory {in_dir} already exists, replace it ? [y/N]")
                if answer in ['yes', 'Yes', 'y', 'Y']:
                    shutil.rmtree(in_dir)                
                else:
                    click.echo("Abort.")
                    sys.exit(0)
            click.echo(f"\nCreating project directory {in_dir} ...")
            os.makedirs(in_dir)
            click.echo(f"Initializing project configuration in {in_dir}/config.toml ...")
            config_obj = parse(files('taln2x.templates').joinpath('config.toml').read_text())
            config_obj['project']['name'] = in_dir
            #print(dumps(config_obj))
            with open(os.path.join(in_dir, 'config.toml'), 'w') as configfile:
                print(dumps(config_obj), file=configfile)
            os.makedirs(os.path.join(in_dir, 'out'))            
            click.echo(f"Initializing event configuration file in {in_dir}/event.yml ...")
            shutil.copy(files('taln2x.templates').joinpath('event.yml'), in_dir)
            click.echo(f"Copying example logo and background pictures in {in_dir} ...")
            shutil.copy(files('taln2x.templates').joinpath('logo.png'), in_dir)
            shutil.copy(files('taln2x.templates').joinpath('background.png'), in_dir)
            shutil.copy(files('taln2x.templates').joinpath('by.eps'), in_dir)
            shutil.copy(files('taln2x.templates').joinpath('pre-proceedings.tex'), in_dir)
            shutil.copy(files('taln2x.templates').joinpath('pre-proceedings-en.tex'), in_dir)
            shutil.copy(files('taln2x.templates').joinpath('single_paper.tex'), in_dir)
            click.echo(f"Creating example track directory ({in_dir}/main) ...")
            os.makedirs(os.path.join(in_dir, 'main'))
            os.makedirs(os.path.join(in_dir, 'main', 'pdf'))
            shutil.copy(files('taln2x.templates').joinpath('articles.csv'), \
                        os.path.join(in_dir,'main'))
            shutil.copy(files('taln2x.templates').joinpath('articles.zip'), \
                        os.path.join(in_dir,'main', 'pdf'))
            with ZipFile(os.path.join(in_dir,'main', 'pdf', 'articles.zip'), mode='r') as zip_ref:
                zip_ref.extractall(path=os.path.join(in_dir,'main', 'pdf'))
            os.remove(os.path.join(in_dir,'main', 'pdf', 'articles.zip'))
            click.echo(f"Done.")
        sys.exit(0)
    elif action == 'clean':
        remove_dir('out')
        print('Cleaning output directory out/', file=sys.stderr)
        sys.exit(0)
    ############################
    ## DECLARATION (cf scope of variables)
    ############################
    ## Read config from command-line options
    # core options
    xin_format    = in_format
    xout_format   = out_format
    xverbose      = verbose
    xstopwords    = stopwords
    xignore_pdf   = ignore_pdf
    xsessions     = sessions
    xlatex_encode = latex_encode
    xdump         = dump 
    # csv options
    xid_col       = -1 #unset
    xauthors_col  = -1
    xtitle_col    = -1
    xidhal_col    = -1
    xfile_col     = -1
    xaccept_col   = -1
    xkeywords_col = -1
    # taln option
    xxml          = xml
    # sciencesconf option
    xzipfile      = zip_file
    # pdf options
    xtex_log      = tex_log
    ximg          = img
    xlang         = lang
    # acl options
    xanthology_id = anthology_id
    xbilingual    = bilingual
    # hal options
    xx_onbehalf   = x_onbehalf
    xstamp        = stamp
    xinclude_pdf  = include_pdf
    xguess        = guess
    xdry_run      = dry_run
    xhalid        = halid
    xupdate       = update
    xnational     = national
    xno_meta      = no_meta
    ## Update config from config file (note that CLI has priority over config file)
    if os.path.exists('config.toml'):
        config = read_config()
        # core options
        xin_format    = xin_format if xin_format else config['project']['core']['in_format']
        xout_format   = xout_format if xout_format else config['project']['core']['out_format']
        xverbose      = xverbose if xverbose else config['project']['core']['verbose']
        xstopwords    = xstopwords if xstopwords else config['project']['core']['stopwords']
        xignore_pdf   = xignore_pdf if xignore_pdf else config['project']['core']['ignore_pdf']
        xsessions     = xsessions if xsessions else config['project']['core']['sessions']
        xlatex_encode = xlatex_encode if xlatex_encode else config['project']['core']['latex_encode'] 
        xdump         = xdump if xdump else config['project']['core']['dump']
        # csv options
        xid_col       = config['project']['csv']['id_col']
        xauthors_col  = config['project']['csv']['authors_col']
        xtitle_col    = config['project']['csv']['title_col']
        xidhal_col    = config['project']['csv']['idhal_col']
        xfile_col     = config['project']['csv']['file_col']        
        xaccept_col   = config['project']['csv']['accept_col']
        xkeywords_col = config['project']['csv']['keywords_col']
        # taln option
        xxml          = xxml if xxml else config['project']['xml']['xml_file']
        # sciencesconf option
        xzipfile      = xzipfile if xzipfile else config['project']['zip']['zip_file']
        # pdf options
        xtex_log      = xtex_log if xtex_log else config['project']['pdf']['tex_log']
        ximg          = ximg if ximg else config['project']['pdf']['img']
        xlang         = xlang if xlang else config['project']['pdf']['language']
        # acl options
        xanthology_id = xanthology_id if xanthology_id else config['project']['acl']['anthology_id']
        xbilingual    = xbilingual if xbilingual else config['project']['acl']['bilingual']
        # hal options
        conf_on_behalf= config['project']['hal']['x_onbehalf'] if config['project']['hal']['x_onbehalf'] != '' else None
        xx_onbehalf   = xx_onbehalf if xx_onbehalf else conf_on_behalf 
        conf_stamp    = config['project']['hal']['stamp'] if config['project']['hal']['stamp'] != '' else None
        xstamp        = xstamp if xstamp else conf_stamp
        xinclude_pdf  = xinclude_pdf if xinclude_pdf else config['project']['hal']['include_pdf'] 
        xguess        = xguess if xguess else config['project']['hal']['guess'] 
        xdry_run      = xdry_run if xdry_run else config['project']['hal']['dry_run'] 
        xhalid        = xhalid if xhalid else config['project']['hal']['halid'] 
        xupdate       = xupdate if xupdate else config['project']['hal']['update'] 
        xnational     = xnational if xnational else config['project']['hal']['national']         
        xno_meta      = xno_meta if xno_meta else config['project']['hal']['no_meta'] 

    if not(os.path.exists('event.yml')):
        print("[Error] event.yml configuration file not found.", \
              file=sys.stderr)
        sys.exit(1)

    e      = readevent.get_meta('event.yml', xanthology_id)  #event
    indir  = os.getcwd()
    outdir = os.path.join(indir, 'out')

    ############################
    ## CASE: EASYCHAIR INPUT
    ############################
    if xin_format == 'csv':
        print('\nReading event information\n=========================', file=sys.stderr)
        easychair.get_data(e, indir, xverbose, xignore_pdf, xsessions, \
                           xid_col, xauthors_col, xtitle_col, xidhal_col, xfile_col, \
                           xaccept_col, xkeywords_col)
        if xverbose > 1:
            print(e)
    ############################
    ## CASE: TALN-ARCHIVES INPUT
    ############################lan
    elif xin_format == 'xml':
        if not(os.path.exists(xxml)) :
            print('\n[Error] Missing input XML file, exit.\n', file=sys.stderr)
            print_help_msg(main)
            exit(1)
        else:
            print('\nReading XML event file\n=========================', file=sys.stderr)
            try:
                arin.read_xml(e, xxml)
            except ValueError:
                print('[Error] Cannot read input XML file ' + xxml + ', abort.', file=sys.stderr)
                exit(20)
        if xverbose > 1:
            print(e)
    ############################
    ## CASE: SCIENCESCONF INPUT
    ############################
    elif xin_format == 'zip':
        if not(os.path.exists(xzipfile)) :
            print(f'\n[Error] {xzipfile} not found. Missing input ZIP file. Abort.\n', file=sys.stderr)
            print_help_msg(main)
            exit(1)
        else:
            print(f'\nReading ZIP file {xzipfile}\n=========================', file=sys.stderr)
            try:
                # a) convert sciencesconf's zip file into easychair format
                sciencesconf.get_data(e, xzipfile, indir, xverbose, xid_col, xauthors_col, xtitle_col, \
                                      xidhal_col, xfile_col, xaccept_col, xkeywords_col)
                # b) read easychair-like data
                easychair.get_data(e, indir, xverbose, xignore_pdf, xsessions, \
                           xid_col, xauthors_col, xtitle_col, xidhal_col, xfile_col, \
                           xaccept_col, xkeywords_col)
            except ValueError as ve:
                traceback.print_exc()
                print('[Error] Cannot read input ZIP file ' + xzipfile + ', abort.', file=sys.stderr)
                exit(20)
        if xverbose > 1:
            print(e)
    else:
        print('[Error] Unknown input format', file=sys.stderr)
        sys.exit(12)

    ############################
    ## ACTUAL ACTION
    ############################
    if action == 'build':
        if not(os.path.exists('event.yml')): #in case we call taln2x from a wrong dir
            print('\n[Error] Missing event yaml configuration file, exit.\n', \
                  file=sys.stderr)
            print_help_msg(main)
            sys.exit(12)
        else:
            click.echo("\nConverting directory ...")
    elif action == 'list' :
        # Listing existing HAL ids (for manual checking)
        print('\nExtracting HAL identifiers\n=========================', file=sys.stderr)
        if shutil.which('curl') is None:
            print('[Error] You need to install \"curl\" to use the --list-id option.', \
                  file=sys.stderr)
        else:
            searchid.get_id(e, os.getcwd(), xstopwords, xverbose, xsessions)
        sys.exit(0)
    else:
        click.echo("\nUnknown ACTION - please invoke 'taln2x --help' \n")
        sys.exit(1)

    ############################
    ## CASE: PDF EXPORT
    ############################
    if xout_format == 'pdf':
        if xhalid:
            if shutil.which('curl') is None:
                print('[Error] You need to install \"curl\" to use the --halid option.', \
                      file=sys.stderr)
                sys.exit(197)
        print('\nGenerating PDF proceedings\n=========================', file=sys.stderr)
        pdf.write_tex(e, xstopwords, xverbose, xhalid, xsessions, xtex_log, ximg, xlang)
    ############################
    ## CASE: EASY2ACL EXPORT
    ############################
    elif xout_format == 'acl':
        print('\nGenerating ACL anthology files\n=========================', file=sys.stderr)
        shutil.copy(files('taln2x.templates').joinpath('easy2acl.py'), outdir)
        shutil.copy(files('taln2x.templates').joinpath('blank.pdf'), outdir)
        ## actual compilation
        anthology.easy2acl_export(e, xbilingual, xstopwords, xverbose, xdump, xsessions, \
                                  xlatex_encode)
        ## cleaning
        shutil.rmtree(os.path.join(outdir, 'easy2acl'))
        os.unlink(os.path.join(outdir, 'easy2acl.py'))
        os.unlink(os.path.join(outdir, 'blank.pdf'))
    ############################
    # CASE: TALN ARCHIVES EXPORT
    ############################
    elif xout_format == 'taln':
        print('\nGenerating event XML file\n=========================', file=sys.stderr)
        arout.write_xml(e, xstopwords, xverbose, xdump, xsessions, xlatex_encode)
    ############################
    # CASE: HAL ARCHIVES EXPORT
    ############################
    elif xout_format == 'hal':
        shutil.copy(files('taln2x.templates').joinpath('aofr.xsd'), outdir)
        print('\nGenerating event HAL BIB and ZIP files\n=========================', \
              file=sys.stderr)
        hal.write_hal_xml(e, xstopwords, xverbose, xx_onbehalf, xstamp, xinclude_pdf, \
                          xguess, xdry_run, xupdate, xsessions, xno_meta, xnational)
        print('\nSWORD shell scripts created, to use them, please export LOGIN and ' + \
              'PASSWORD environment variables containing your HAL credentials.\n', \
              file=sys.stderr)
        os.unlink(os.path.join(outdir, 'aofr.xsd'))
    ############################
    # CASE: DBLP ARCHIVES EXPORT
    ############################
    elif xout_format == 'dblp':
        shutil.copy(files('taln2x.templates').joinpath('dblpsubmission.dtd'), outdir)
        print('\nGenerating event DBLP XML files\n=========================', file=sys.stderr)
        dblp.write_dblp_xml(e, xstopwords, xverbose, xsessions)
        os.unlink(os.path.join(outdir, 'dblpsubmission.dtd'))
    ############################
    else:
        print("[Error] Unknown output format", file=sys.stderr)
        sys.exit(8)

if __name__ == '__main__':
    main()
