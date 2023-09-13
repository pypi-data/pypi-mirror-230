import os
from typing import Optional
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

class MultiList:
    def __init__(self, args):
        """
        Initialize the MultiList class.

        :param list_file: str, the path to the sample list file.
        :param genome_dir: str, the path to the genome directory.
        :param outdir: Optional[str], the path to the output directory.
        :param threads: Optional[int], the number of threads to use.
        """
        self.list = args.list
        self.genomeDir = os.path.abspath(args.genomeDir)
        self.outdir = args.outdir
        self.threads = args.threads
    
    def run(self) -> None:
        """
        Run the dnbc4atac pipeline for all samples listed in the sample list file.
        """
        with open(self.list) as samplelist:
            for line in samplelist:
                lst = line.strip().split('\t')
                name = lst[0]
                fastqr1 = get_abspath(lst[1].split(';')[0])
                fastqr2 = get_abspath(lst[1].split(';')[-1])
                shelllist = open('%s.sh'%name,'w')

                current_environment = get_current_environment()
            
                cmd_line = []
                if current_environment == 'Singularity':
                    fastqr1_dir = {os.path.dirname(os.path.realpath(item)) for item in fastqr1.split(",")}
                    fastqr2_dir = {os.path.dirname(os.path.realpath(item)) for item in fastqr2.split(",")}

                    data_dir = ','.join(set.union(fastqr1_dir, fastqr2_dir))
                    genome_dir = os.path.dirname(os.path.realpath(self.genomeDir))
                    if self.outdir:
                        out_dir = os.path.dirname(os.path.realpath(self.outdir))
                    else:
                        out_dir = os.path.dirname(os.path.realpath(os.getcwd()))

                    cmd_line.append('export SINGULARITY_BIND=%s,%s,%s\n' % (data_dir, genome_dir, out_dir))
                    sif_or_sandbox_path = os.environ.get('SINGULARITY_CONTAINER')

                    cmd_line.append('singularity exec %s dnbc4atac run --name %s --fastq1 %s --fastq2 %s --genomeDir %s'
                                    % (sif_or_sandbox_path, name, fastqr1,fastqr2,self.genomeDir))
                    
                elif current_environment == 'Docker':
                    path = '/'.join(str(__root_dir__).split('/')[0:-4])+ '/bin'
                    cmd_line.append('%s/dnbc4atac run --name %s --fastq1 %s --fastq2 %s --genomeDir %s'
                                    %(path,name,fastqr1,fastqr2,self.genomeDir))
                    
                else:
                    path = '/'.join(str(__root_dir__).split('/')[0:-4])+ '/bin'
                    cmd_line.append('%s/dnbc4atac run --name %s --fastq1 %s --fastq2 %s --genomeDir %s'
                                    %(path,name,fastqr1,fastqr2,self.genomeDir))
                    

                if self.threads:
                    cmd_line.append('--threads %s'%self.threads)
                if self.outdir:
                    self.outdir = os.path.abspath(self.outdir)
                    cmd_line.append('--outdir %s'%self.outdir)
                    
                cmd_line = ' '.join(cmd_line)
                shelllist.write(cmd_line + '\n')
                
def multi(args):
    MultiList(args).run()

def helpInfo_multi(parser):
    parser.add_argument(
        '--list', 
        metavar='FILE',
        help='sample list.', 
        type=str,
        required=True
        )
    parser.add_argument(
        '--outdir', 
        metavar='PATH',
        help='Output diretory, [default: current directory].', 
        )
    parser.add_argument(
        '--threads',
        type=int, 
        metavar='INT',
        default=4,
        help='Number of threads used for analysis, [default: 4].'
        )
    parser.add_argument(
        '--genomeDir',
        type=str, 
        metavar='PATH',
        help='Path to the directory where genome files are stored.',
        required=True
        )
    return parser