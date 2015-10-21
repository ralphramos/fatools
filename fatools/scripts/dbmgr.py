
import sys, argparse, yaml, csv, transaction
from fatools.lib.utils import cout, cerr, cexit, get_dbhandler, tokenize



def init_argparser( parser=None ):

    if parser is None:
        p = argparse.ArgumentParser('dbmgr')
    else:
        p = parser

    ## mandatory options

    p.add_argument('--sqldb', default=False,
            help = 'Sqlite3 database filename')

    p.add_argument('--fsdb', default=False,
            help = 'directory for filesystem-based database')

    ## commands
    ## all argument should store_true for consistency

    p.add_argument('--initdb', default=False, action='store_true',
            help = 'initialize database')

    p.add_argument('--importpanel', default=False, action='store_true',
            help = 'importing panel from YAML file')

    p.add_argument('--importmarker', default=False, action='store_true',
            help = 'importing marker from YAML file')

    p.add_argument('--updatebins', default=False, action='store_true',
            help = 'updating bins')

    p.add_argument('--uploadfsa', default=False, action='store_true',
            help = 'uploading FSA data')

    p.add_argument('--initsample', default=False, action='store_true',
            help = 'create new sample from sample file')

    p.add_argument('--clearfsa', default=False, action='store_true',
            help = 'clear FSA data')

    p.add_argument('--initbatch', default=False, action='store_true',
            help = 'create new batch')

    p.add_argument('--showbatches', default=False, action='store_true',
            help = 'show available batch(es)')

    p.add_argument('--initbin', default=False, action='store_true',
            help = 'create initial bin')

    p.add_argument('--viewbin', default=False, action='store_true',
            help = 'view bin')

    p.add_argument('--removebatch', default=False, action='store_true',
            help = 'remove batch from database')

    p.add_argument('--removesample', default=False, action='store_true',
            help = 'remove sample from database')

    p.add_argument('--removefsa', default=False, action='store_true',
            help = 'remove FSA from database')

    p.add_argument('--setbinbatch', default=False, action='store_true',
            help = 'set bins-related batch')

    p.add_argument('--exportmarker', default=False, action='store_true',
            help = 'export marker to YAML file')

    p.add_argument('--exportpanel', default=False, action='store_true',
            help = 'export panel to YAML file')

    p.add_argument('--exportfsa', default=False, action='store_true',
            help = 'export FSA (either or both metadata and FSA files')

    p.add_argument('--exportsample', default=False, action='store_true',
            help = 'export sample data to tab-delimited file')

    ## options

    p.add_argument('--infile', default=False,
            help = 'input file')

    p.add_argument('--outfile', default=False,
            help = 'output file')

    p.add_argument('--update', default=False,
            help = 'updating current data in the database')

    p.add_argument('--commit', default=False, action='store_true',
            help = 'commit to database')

    p.add_argument('-b', '--batch', default=False,
            help = 'batch code')

    p.add_argument('-m', '--marker', default='',
            help = 'marker list (comma separated)')

    p.add_argument('-s', '--sample', default='',
            help = 'sample code list (comma separated, no space)')

    p.add_argument('--fsa', default='',
            help = 'assay filename list (comma separated, no space)')

    p.add_argument('--assayprovider', default='',
            help = 'assay provider vendor/group')

    p.add_argument('--indir', default=False,
            help = 'input directory (eg. containing FSA files)')

    p.add_argument('--outdir', default=False,
            help = 'output directory')

    p.add_argument('--species', default='',
            help = 'species of markers')

    p.add_argument('--range', default=False,
            help = 'bin range, eg. 200-300')

    p.add_argument('--test', default=False, action='store_true',
            help = 'perform test, print error as warning')

    p.add_argument('--abort', default=False, action='store_true',
            help = 'abort for any warning')

    return p


def main(args):

    if not args.test and (args.commit or args.initdb):
        with transaction.manager:
            do_dbmgr(args)
            cerr('** COMMIT to database **')

    else:
        cerr('WARNING -- running without commiting to database!')
        if not args.test:
            keys = input('Do you want to continue [y/n]? ')
            if not keys.lower().strip().startswith('y'):
                sys.exit(1)
            
        do_dbmgr(args)



def do_dbmgr(args, dbh = None, warning=True):

    if not dbh:
        dbh = get_dbhandler(args, initial = args.initdb)

    if args.uploadfsa is not False:
        do_uploadfsa(args, dbh)
    elif args.initbatch is not False:
        do_initbatch(args, dbh)
    elif args.showbatches is not False:
        do_showbatches(args, dbh)
    elif args.initsample is not False:
        do_initsample(args, dbh)
    elif args.importpanel is not False:
        do_importpanel(args, dbh)
    elif args.importmarker is not False:
        do_importmarker(args, dbh)
    elif args.initdb is not False:
        do_initdb(args, dbh)
    elif args.clearfsa is not False:
        do_clearfsa(args, dbh)
    elif args.initbin is not False:
        do_initbin(args, dbh)
    elif args.viewbin is not False:
        do_viewbin(args, dbh)
    elif args.updatebins is not False:
        do_updatebins(args, dbh)
    elif args.removebatch is not False:
        do_removebatch(args, dbh)
    elif args.removefsa is not False:
        do_removefsa(args, dbh)
    elif args.setbinbatch is not False:
        do_setbinbatch(args, dbh)
    elif args.exportfsa is not False:
        do_exportfsa(args, dbh)
    else:
        if warning:
            cerr('Unknown command, nothing to do!')
        return False

    return True



def do_initdb(args, dbh):

    dbh.initdb()



def do_importpanel(args, dbh):

    panels = yaml.load( open(args.infile) )

    for code, panel in panels.items():
        if panel['code'] != code:
            cerr('ERR: code for panel %s is not consistent!' % code)
            sys.exit(1)
        p = dbh.new_panel()
        p.update( panel )
        if args.update:
            db_p = p.sync(dbh.session)
            cout("INFO: panel %s sync'd." % db_p.code)
        else:
            dbh.session.add(p)
            cout("INFO: panel %s added." % p.code)



def do_importmarker(args, dbh):

    markers = yaml.load(open(args.infile))
    # markers is a dict of dict, so need a new instance for updating

    for code, marker in markers.items():
        if marker['code'] != code:
            cerr('ERR: code for marker %s is not consistent!' % code)
            sys.exit(1)
        m = dbh.new_marker()
        m.update(marker)
        if args.update:
            db_m = m.sync(dbh.session)
            cerr("INFO: marker: %s sync'd." % db_m.code)
        else:
            dbh.session.add(m)
            cerr('INFO: marker %s added.' % m.code)
            db_m = m

        if 'bins_range' in marker:
            batch = dbh.get_batch('default')
            db_m.initbins( marker['bins_range'][0], marker['bins_range'][1], batch)
            cerr('INFO: bins for marker %s has been created in batch %s'
                % (db_m.code, batch.code))



def do_initbatch(args, dbh):

    b = dbh.Batch()
    b.code = args.initbatch
    b.species = args.species
    b.assay_provider = args.assayprovider
    # set default bin_batch to batch default
    def_batch = dbh.get_batch('default')
    b.bin_batch = def_batch
    dbh.session.add(b)
    cout('INFO: batch %s added.' % b.code)



def do_showbatches(args, dbh):

    cout('Available batch(es):')
    batches = dbh.get_batches()
    for batch in batches:
        cout('  %s' % batch.code)



def do_initsample(args, dbh):

    if not args.batch:
        cerr('ERR: batch code must be supplied!')
        sys.exit(1)

    b = dbh.Batch.search(args.batch, dbh.session)
    cout('INFO - using batch code: %s' % b.code)

    inrows = csv.reader( open(args.infile),
                delimiter = ',' if args.infile.endswith('.csv') else '\t' )

    next(inrows)    # discard the 1st line

    counter = 0
    for row in inrows:
        s = b.add_sample( row[0] )
        counter += 1
        cout('INFO - sample: %s added.' % s.code)

    cout('INFO - number of new sample(s): %d' % counter)



def do_upload(args, dbh):

    cout('Uploading FSA files from input file: %s' % args.upload)

    b = dbh.get_batch(args.batch)

    inrows = csv.reader( open(args.infile),
                delimiter = ',' if args.infile.endswith('.csv') else '\t' )
    next(inrows)

    total_fsa = 0
    line_counter = 1
    for row in inrows:

        line_counter += 1

        if not row[0] or row[0].startswith('#'):
            continue

        if len(row) < 3:
            cerr('ERR - line %d only has %d item(s)' % (line_counter, len(row)))

        sample_code, fsa_filename, fsa_panel = row[0], row[1], row[2]
        if len(row) >= 4:
            options = tokenize( row[3] )
        else:
            options = None

        try:

            s = b.search_sample(row[0])
            if not s:
                cerr('ERR - sample %s does not exist' % row[0])
                sys.exit(1)

            with open( args.indir + '/' + row[1], 'rb') as f:
                trace = f.read()

            a = s.add_fsa( trace, filename=fsa_filename, panel_code = fsa_panel,
                        options = options, species = args.species, dbhandler = dbh)
            cerr('INFO - sample: %s assay: %s panel: %s has been uploaded' % 
                        (s.code, a.filename, fsa_panel))

        except Exception as exc:

            if not args.test:
                raise
            cerr('ERR - line %d' % line_counter)
            cerr(' => %s' % str(exc))



def do_reassign(args, dbh):

    cerr("Reassign FSA assays")

    assay_list = get_assay_list( args, dbh)

    b = dbh.get_batch(args.batch)

    if args.excludedmarker:
        excludedmarkers = args.excludedmarker.upper().split(',')
    else:
        excludedmarkers = None

    if args.reassign.strip() == '-':
        # use the one already in the db for each assay (ie. only reaffirm)
        for (assay, sample_code) in assay_list:
            if excludedmarkers is None:
                try:
                    exclusion_data = assay.exclude
                    excludedmarkers = exclusion_data.upper().split(',')
                except KeyError:
                    excluded_markers = None
            assay.assign_channels(excludedmarkers)

    else:
        pass



def do_initbin(args, dbh):

    if not args.marker:
        cexit('ERR - please provide marker code')

    if '-' not in args.range:
        cexit('ERR - please provide range for bin')

    if not args.batch:
        args.batch = 'default'
    batch = dbh.get_batch( args.batch )

    markers = [ dbh.get_marker(code) for code in args.marker.split(',') ]
    ranges = args.range.split('-')
    start_range = int(ranges[0])
    end_range = int(ranges[1])

    print(markers)
    for m in markers:
        m.initbins(start_range, end_range, batch)
        cerr('INFO  - bin for marker %s with batch %s has been created.' % (m.label, batch.code))



def do_viewbin(args, dbh):

    if not args.marker:
        cexit('ERR - please provide marker code')

    markers = [ dbh.get_marker(code) for code in args.marker.split(',') ]

    for m in markers:
        cout('Marker: %s' % m.label)
        cout('    Bin   Mean   25%P   75%P   Width')
        cout('  ====================================')
        for binset in m.bins:
            cout('   %3d  %5.2f  %5.2f  %5.2f  %4.2f' %
                    (binset[0], binset[1], binset[2], binset[3], binset[3] - binset[2]))



def do_updatebins(args, dbh):
    
    with open(args.updatebins) as f:
        updated_bins = yaml.load( f )

    for (marker_label, marker_data) in updated_bins.items():
        if marker_data['label'] != marker_label:
            raise RuntimeError()
        marker = dbh.get_marker( marker_label )
        marker.bins = marker_data['bins']
        cerr('I: Updating bins for marker: %s' % marker.label)



def do_removebatch(args, dbh):

    batch = dbh.get_batch(args.batch)
    batch_code = batch.code
    dbh.session().delete(batch)
    cerr('INFO - batch %s has been removed' % batch_code)



def do_removeassay(args, dbh):

    assay_list = get_assay_list( args, dbh )

    batch = dbh.get_batch(args.batch)
    if batch and not (args.sample or args.assay):
        # remove all assay in this batch
        batch.remove_assays()
        cerr('INFO - removing all assays from batch %s' % batch.code)
    else:
        sess = dbh.session()
        for (assay, sample_code) in assay_list:
            assay_filename = assay.filename
            sess.delete(assay)
            cerr('INFO - removing assay %s | %s' % (sample_code, assay_filename))



def do_clearassay(args, dbh):

    cout('Clearing assay...')



def do_setbinbatch(args, dbh):

    batch = dbh.get_batch(args.batch)
    bin_batch = dbh.get_batch(args.setbinbatch)
    batch.bin_batch = bin_batch
    cerr('INFO - bins for batch %s has been set to batch %s'
            % (batch.code, bin_batch.code))



def do_exportfsa(args, dbh):

    assay_list = get_assay_list( args, dbh )

    outdir = None
    if args.outdir:
        os.mkdirs(args.outdir)
        outdir = args.outdir + '/'

    if args.outfile:
        outfile = open(args.outfile, 'w')
    else:
        outfile = sys.stdout
    outfile.write('FILENAME\tSAMPLE\tPANEL\tOPTIONS\n')

    for (assay, sample_code) in assay_list:
        if outdir:
            with open(outdir + assay.filename, 'wb') as f:
                f.write(assay.raw_data)
        exclude = 'exclude=%s' % assay.exclude if assay.exclude else ''
        outfile.write('%s\t%s\t%s\t%s\n' % (assay.filename, sample_code,
                            assay.panel.code, exclude))

    outfile.close()



# helpers

def get_assay_list( args, dbh ):
    
    if not args.batch:
        cerr('ERR - need --batch argument!')
        sys.exit(1)

    batch = dbh.get_batch( args.batch )
    if not batch:
        cerr('ERR - batch %s not found!' % args.batch)
        sys.exit(1)

    samples = []
    if args.sample:
        samples = args.sample.split(',')

    assays = []
    if args.fsa:
        assays = args.assay.split(',')

    assay_list = []
    for sample in batch.samples:
        if samples and sample.code not in samples: continue
        for assay in sample.assays:
            if assays and assay.filename not in assays: continue
            assay_list.append( (assay, sample.code) )

    cerr('INFO - number of assays to be processed: %d' % len(assay_list))
    return assay_list

