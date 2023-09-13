import os
import sys
import argparse
from typing import List, Dict
from dnbc4tools.tools.utils import str_mkdir,judgeFilexits,change_path,logging_call,read_json, get_formatted_time
from dnbc4tools.__init__ import __root_dir__

class Decon:
    def __init__(self, args: Dict):
        """
        Constructor for Decon class.

        Args:
        - args (Dict): A dictionary containing the arguments to configure the Decon object.
        """
        self.name: str = args.name
        self.outdir: str = os.path.abspath(os.path.join(args.outdir, args.name))
        self.threads: int = args.threads
        self.genomeDir: str = os.path.abspath(args.genomeDir)
        self.forcebeads: int = args.forcebeads
        self.forcefrags: int = args.forcefrags
        self.threshold: int = args.threshold

    def run(self) -> None:
        """
        Run the Decon algorithm.
        """
        # Check if genomeDir exists
        judgeFilexits(self.genomeDir,
                f'{self.outdir}/01.data/aln.bed'
                )
        
        # Create output and log directories
        str_mkdir(f"{self.outdir}/02.decon")
        str_mkdir(f"{self.outdir}/log")
        
        # Change to the output directory
        change_path()
        print(f'\n{get_formatted_time()}\n'
            f'Cell Calling, Deconvolution.')
        
        sys.stdout.flush()
        # Read the genome directory configuration from ref.json
        genomeDir = os.path.abspath(self.genomeDir)
        indexConfig: Dict = read_json(f"{genomeDir}/ref.json")
        blacklist: str = indexConfig['blacklist']
        tss: str = indexConfig['tss']
        chrmt: str = indexConfig['chrmt']
        chromeSize: str = indexConfig['chromeSize']

        # Construct the Decon command with the provided parameters
        d2c_cmd: List[str] = [
            f"{__root_dir__}/software/d2c/bin/d2c merge ",
            f"-i {self.outdir}/01.data/aln.bed ",
            f"--fb {self.threshold} ",
            f"-o {self.outdir}/02.decon ",
            f"-c {self.threads} ",
            f"-n {self.name} ",
            f"--bg {chromeSize} ",
            f"--ts {tss} ",
            f"--sat --bt1 CB ",
            f"--log {self.outdir}/02.decon"
        ]
        
        # Add optional parameters if they are not None
        if self.forcefrags:
            d2c_cmd.append(f"--bf {self.forcefrags}")
        if self.forcebeads:
            d2c_cmd.append(f"--bp {self.forcebeads}")
        if chrmt != 'None':
            d2c_cmd.append(f"--mc {chrmt}")
        if blacklist != 'None':
            d2c_cmd.append(f"--bl {blacklist}")
        
        # Join the command list into a single string and execute the command
        d2c_cmd = ' '.join(d2c_cmd)
        
        logging_call(d2c_cmd, 'decon', self.outdir)

def decon(args):
    Decon(args).run()

def helpInfo_decon(parser):
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
        help='Output diretory, [default: current directory].', 
        default=os.getcwd()
        )
    parser.add_argument(
        '--forcefrags', 
        type=int,
        metavar='INT',
        help='Minimum number of fragments to be thresholded.'
        )
    parser.add_argument(
        '--forcebeads', 
        type=int,
        metavar='INT',
        help='Top N number of beads to be thresholded.'
        )
    parser.add_argument(
        '--threshold', 
        type=int,
        metavar='INT',
        default=20000,
        help=argparse.SUPPRESS
        )
    parser.add_argument(
        '--threads',
        type=int, 
        metavar='INT',
        default=4,
        help='Number of threads used for the analysis, [default: 4].'
        )
    parser.add_argument(
        '--genomeDir',
        type=str, 
        metavar='PATH',
        help='Path of folder containing reference database.',
        required=True
        )
    return parser