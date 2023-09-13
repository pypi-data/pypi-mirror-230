import os,argparse
import sys
from dnbc4tools.tools.utils import str_mkdir,judgeFilexits,change_path,logging_call,read_json,bin_path, get_formatted_time
from dnbc4tools.__init__ import __root_dir__

class Analysis:
    def __init__(self, args: argparse.Namespace) -> None:
        """
        Initialize the Analysis class.

        Args:
        - args (argparse.Namespace): parsed command-line arguments
        """
        self.name = args.name
        self.outdir = os.path.abspath(os.path.join(args.outdir, args.name))
        self.genomeDir = os.path.abspath(args.genomeDir)

    def run(self) -> None:
        """
        Run the analysis.
        """
        judgeFilexits(self.genomeDir,
                      f'{self.outdir}/02.decon/{self.name}.fragments.tsv.gz')
        str_mkdir('%s/03.analysis/peak'%self.outdir)
        # str_mkdir('%s/03.analysis/promoter'%self.outdir)
        str_mkdir('%s/03.analysis/images'%self.outdir)
        str_mkdir('%s/log'%self.outdir)
        change_path()
        bin_command = bin_path()

        genomeDir = os.path.abspath(self.genomeDir)
        indexConfig = read_json('%s/ref.json'%genomeDir)
        tss = indexConfig['tss']
        chrmt = indexConfig['chrmt']
        genomesize = indexConfig['genomesize']
        species = indexConfig['species']
        # promoter = indexConfig['promoter']

        macs2_cmd = (
            f"{bin_command}/macs2 callpeak "
            f"-t {self.outdir}/02.decon/{self.name}.fragments.tsv.gz "
            f"-f BED "
            f"-g {genomesize} "
            f"-n {self.name} "
            f"-B "
            f"-q 0.001 "
            f"--nomodel "
            f"--outdir {self.outdir}/03.analysis"
        )

        cluster_cmd = (
            f"{bin_command}/Rscript {__root_dir__}/atac/src/Cluster_Annotation.R "
            f"-I {self.outdir}/03.analysis/{self.name}_peaks.narrowPeak "
            f"-F {self.outdir}/02.decon/{self.name}.fragments.tsv.gz "
            f"-T {tss} -MT {chrmt} "
            f"-Q {self.outdir}/02.decon/{self.name}.Metadata.tsv "
            f"-O {self.outdir}/03.analysis "
            f"-S {species}"
        )
        
        print(f'\n{get_formatted_time()}\n'
            f'Peak Calling.')
        sys.stdout.flush()
        logging_call(macs2_cmd, 'analysis', self.outdir)

        print(f'\n{get_formatted_time()}\n'
            f'Dimensionality Reduction, Clustering.')
        sys.stdout.flush()
        logging_call(cluster_cmd, 'analysis', self.outdir)

def analysis(args: argparse.Namespace) -> None:
    """
    Run the analysis.

    Args:
    - args (argparse.Namespace): parsed command-line arguments
    """
    Analysis(args).run()


def helpInfo_analysis(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Add command-line arguments for the analysis subcommand.

    Args:
    - parser (argparse.ArgumentParser): argparse parser

    Returns:
    - argparse.ArgumentParser: argparse parser
    """
    parser.add_argument(
        '--name', 
        metavar='NAME',
        help='Sample name.', 
        type=str,
        required=True
    )
    parser.add_argument(
        '--outdir', 
        metavar='PATH',
        help='Output directory, [default: current directory].', 
        default=os.getcwd()
    )
    parser.add_argument(
        '--genomeDir',
        type=str, 
        metavar='PATH',
        help='Path of folder containing reference database.',
        required=True
    )
    return parser