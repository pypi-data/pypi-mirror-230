import os
from dnbc4tools.__init__ import __root_dir__

def get_current_environment():
    if os.path.exists('/.dockerenv'):
        return 'Docker'
    elif 'SINGULARITY_CONTAINER' in os.environ:
        return 'Singularity'
    else:
        return 'Non-container'
    
def get_abspath(paths):
    relative_paths = paths.split(",")
    absolute_paths = [os.path.abspath(path) for path in relative_paths]
    result = ",".join(absolute_paths)
    return result

class Multi_list:
    def __init__(self, args):
        self.list = args.list
        self.genomeDir = os.path.abspath(args.genomeDir)
        self.outdir = args.outdir
        self.threads = args.threads
        self.calling_method = args.calling_method
        self.expectcells = args.expectcells
        self.no_introns = args.no_introns
    
    def run(self):
        with open(self.list) as samplelist:
            for line in samplelist:
                lst = line.strip().split('\t')
                name = lst[0]
                cDNAr1 = get_abspath(lst[1].split(';')[0])
                cDNAr2 = get_abspath(lst[1].split(';')[-1])
                oligor1 = get_abspath(lst[2].split(';')[0])
                oligor2 = get_abspath(lst[2].split(';')[-1])
                shelllist = open('%s.sh'%name,'w')

                current_environment = get_current_environment()
            
                cmd_line = []
                if current_environment == 'Singularity':
                    cDNAr1_dir = {os.path.dirname(os.path.realpath(item)) for item in cDNAr1.split(",")}
                    cDNAr2_dir = {os.path.dirname(os.path.realpath(item)) for item in cDNAr2.split(",")}
                    oligor1_dir = {os.path.dirname(os.path.realpath(item)) for item in oligor1.split(",")}
                    oligor2_dir = {os.path.dirname(os.path.realpath(item)) for item in oligor2.split(",")}
                    data_dir = ','.join(set.union(cDNAr1_dir, cDNAr2_dir, oligor1_dir, oligor2_dir))
                    genome_dir = os.path.dirname(os.path.realpath(self.genomeDir))
                    if self.outdir:
                        out_dir = os.path.dirname(os.path.realpath(self.outdir))
                    else:
                        out_dir = os.path.dirname(os.path.realpath(os.getcwd()))
                    cmd_line.append('export SINGULARITY_BIND=%s,%s,%s\n' % (data_dir, genome_dir, out_dir))
                    sif_or_sandbox_path = os.environ.get('SINGULARITY_CONTAINER')

                    cmd_line.append('singularity exec %s dnbc4rna run --name %s --cDNAfastq1 %s --cDNAfastq2 %s --oligofastq1 %s --oligofastq2 %s --genomeDir %s'
                                    % (sif_or_sandbox_path, name, cDNAr1, cDNAr2, oligor1, oligor2, self.genomeDir))

                elif current_environment == 'Docker':
                    path = '/'.join(str(__root_dir__).split('/')[0:-4]) + '/bin'
                    cmd_line.append('%s/dnbc4rna run --name %s --cDNAfastq1 %s --cDNAfastq2 %s --oligofastq1 %s --oligofastq2 %s --genomeDir %s'
                                    % (path, name, cDNAr1, cDNAr2, oligor1, oligor2, self.genomeDir))

                else:
                    path = '/'.join(str(__root_dir__).split('/')[0:-4]) + '/bin'
                    cmd_line.append('%s/dnbc4rna run --name %s --cDNAfastq1 %s --cDNAfastq2 %s --oligofastq1 %s --oligofastq2 %s --genomeDir %s'
                                    % (path, name, cDNAr1, cDNAr2, oligor1, oligor2, self.genomeDir))

                if self.threads:
                    cmd_line.append('--threads %s' % self.threads)
                if self.outdir:
                    self.outdir = os.path.abspath(self.outdir)
                    cmd_line.append('--outdir %s' % self.outdir)
                if self.calling_method:
                    cmd_line.append('--calling_method %s' % self.calling_method)
                if self.expectcells:
                    cmd_line.append('--expectcells %s' % self.expectcells)
                if self.no_introns:
                    cmd_line.append('--no_introns')

                cmd_str = ' '.join(cmd_line)
                shelllist.write(cmd_str + '\n')

                
def multi(args):
    Multi_list(args).run()

def helpInfo_multi(parser):
    parser.add_argument(
        '--list', 
        metavar='FILE',
        help='sample list.', 
        type=str,
        required=True
        )
    parser.add_argument(
        '--genomeDir',
        type=str, 
        metavar='PATH',
        help='Path to the directory where genome files are stored.',
        required=True
        )
    parser.add_argument(
        '--outdir', 
        metavar='PATH',
        help='Output directory, [default: current directory].'
        )
    parser.add_argument(
        '--threads',
        type=int, 
        metavar='INT',
        default=4,
        help='Number of threads used for analysis, [default: 4].'
        )
    parser.add_argument(
        '--calling_method',
        metavar='STR',
        choices=["barcoderanks","emptydrops"],
        help='Cell calling method, choose from barcoderanks and emptydrops, [default: emptydrops].'
        )
    parser.add_argument(
        '--expectcells',
        metavar='INT',
        help='Expected number of recovered beads, [default: 3000].'
        )
    parser.add_argument(
        '--no_introns', 
        action='store_true',
        help='Intron reads are not included in the expression matrix.'
        )
    return parser
    
