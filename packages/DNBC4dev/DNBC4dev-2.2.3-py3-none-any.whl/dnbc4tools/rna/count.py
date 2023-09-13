import os
from dnbc4tools.tools.utils import str_mkdir,logging_call,judgeFilexits,change_path,bin_path, get_formatted_time,rm_temp
from dnbc4tools.__init__ import __root_dir__

def matrix_summary(matrixpath,outdir,cellreport):
    from dnbc4tools.tools.utils import read_anndata
    import scanpy as sc
    adata = read_anndata(matrixpath)
    adata.write("%s/filter_feature.h5ad"%outdir)
    sc.pp.calculate_qc_metrics(
        adata, 
        percent_top=None, 
        log1p=False, 
        inplace=True
        )
    total_gene = str(adata.var.shape[0])
    mean_gene = str(round(adata.obs['n_genes_by_counts'].mean()))
    median_gene = str(round(adata.obs['n_genes_by_counts'].median()))
    mean_umi = str(round(adata.obs['total_counts'].mean()))
    median_umi = str(round(adata.obs['total_counts'].median()))
    
    with open(cellreport,'a') as reportfile:
        reportfile.write('Mean UMI counts per cell,%s'%mean_umi+'\n')
        reportfile.write('Median UMI Counts per Cell,%s'%median_umi+'\n')
        reportfile.write('Total Genes Detected,%s'%total_gene+'\n')
        reportfile.write('Mean Genes per Cell,%s'%mean_gene+'\n')
        reportfile.write('Median Genes per Cell,%s'%median_gene+'\n')


class Count:
    def __init__(self,args):
        self.name = args.name
        self.threads = args.threads
        self.calling_method = args.calling_method
        self.expectcells = args.expectcells
        self.forcecells = args.forcecells
        self.minumi = args.minumi
        self.outdir = os.path.abspath(os.path.join(args.outdir,args.name))
    
    def run(self):
        judgeFilexits(
            '%s/01.data/final_sorted.bam'%self.outdir,
            '%s/01.data/cDNA_barcode_counts_raw.txt'%self.outdir,
            '%s/01.data/Index_reads.fq.gz'%self.outdir,
            '%s/01.data/beads_stat.txt'%self.outdir
            )
        str_mkdir('%s/02.count'%self.outdir)
        str_mkdir('%s/log'%self.outdir)
        str_mkdir('%s/log/.temp'%self.outdir)
        os.environ[ 'MPLCONFIGDIR' ] = '%s/log/.temp'%self.outdir
        os.environ[ 'NUMBA_CACHE_DIR' ] = '%s/log/.temp'%self.outdir
        change_path()
        bin_command = bin_path()

        ## filter oligo
        print(f'\n{get_formatted_time()}\n'
            f'Calculating bead similarity and merging beads.')
        from dnbc4tools.rna.src.oligo_filter import oligo_combine,cut_umi
        oligo_combine(f"{__root_dir__}/config/oligo_type.json",
                      f"{self.outdir}/01.data/Index_reads.fq.gz",
                      f"{self.outdir}/02.count",
                      f"{__root_dir__}/software",
                      f"{self.threads}"
                      )
        
        filtered_beadsStat = cut_umi(
            f"{self.outdir}/01.data/beads_stat.txt",100
            )
        
        filtered_beadsStat['BARCODE'].to_csv(
            f"{self.outdir}/02.count/beads_barcodes_umi100.txt", 
            index=False, 
            header=False
            )
        
        similiarBeads_cmd = [
            f"{__root_dir__}/software/similarity",
            f"-n {self.threads}",
            f"{self.name}",
            f"{self.outdir}/02.count/CB_UB_count.txt",
            f"{self.outdir}/02.count/beads_barcodes_umi100.txt",
            f"{__root_dir__}/config/oligo_type.txt",
            f"{self.outdir}/02.count/similarity_all.csv",
            f"{self.outdir}/02.count/similarity_droplet.csv",
            f"{self.outdir}/02.count/similarity_dropletfiltered.csv"
        ]
        similiarBeads_cmd_str = " ".join(similiarBeads_cmd)  
        logging_call(similiarBeads_cmd_str,'count',self.outdir)

        ### merge beads list

        from dnbc4tools.rna.src.combinedListOfBeads import similarity_droplet_file
        similarity_droplet_file('%s/02.count/similarity_droplet.csv'%self.outdir,
                                '%s/02.count/beads_barcodes_umi100.txt'%self.outdir,
                                '%s/02.count/combined_list.txt'%self.outdir,
                                0.4,1)

        from dnbc4tools.rna.src.cellMerge import barcodeTranslatefile
        barcodeTranslatefile(
            f"{self.outdir}/02.count/combined_list.txt", 
            f"{self.outdir}/01.data/beads_stat.txt", 
            f"{self.outdir}/02.count/barcodeTranslate.txt",
            f"{self.outdir}/02.count/barcodeTranslate_hex.txt",
            f"{self.outdir}/02.count/cell.id"
            )
    
        ### add DB tag for bam
        # print(f'\n{get_formatted_time()}\t'
        #     f'Generating anno decon sorted bam.')
        tagAdd_cmd = [
            f"{__root_dir__}/software/tagAdd",
            f"-n {self.threads}",
            f"-bam {self.outdir}/01.data/final_sorted.bam",
            f"-file {self.outdir}/02.count/barcodeTranslate_hex.txt",
            f"-out {self.outdir}/02.count/anno_decon_sorted.bam",
            "-tag_check CB:Z:",
            "-tag_add DB:Z:"
        ]
        tagAdd_cmd_str = " ".join(tagAdd_cmd)
        logging_call(tagAdd_cmd_str,'count',self.outdir)

        ### get bam index
        def create_index(threads,bam):
            try:
                bam_index_cmd = '%s/samtools index -@ %s %s'%(bin_command,threads,bam)
                logging_call(bam_index_cmd,'count',self.outdir)
            except Exception as e:
                print('build csi index for bam')
                bam_index_cmd = '%s/samtools index -c -@ %s %s'%(bin_command,threads,bam)
                logging_call(bam_index_cmd,'count',self.outdir)
        create_index(self.threads,'%s/02.count/anno_decon_sorted.bam'%self.outdir)

        print(f'\n{get_formatted_time()}\n'
            f'Generating the raw expression matrix.')
        str_mkdir('%s/02.count/raw_matrix'%self.outdir)
        PISA_countRaw_cmd = [
            f"{__root_dir__}/software/PISA",
            "count",
            "-one-hit",
            f"-@ {self.threads}",
            "-cb DB",
            "-anno-tag GN",
            "-umi UB",
            f"-list {self.outdir}/02.count/cell.id",
            f"-outdir {self.outdir}/02.count/raw_matrix",
            f"{self.outdir}/02.count/anno_decon_sorted.bam"
        ]
        PISA_countRaw_cmd_str = " ".join(PISA_countRaw_cmd)
        logging_call(PISA_countRaw_cmd_str,'count',self.outdir)


        ## cell calling using DropletUtils
        cellCalling_cmd = [
            f"{bin_command}/Rscript",
            f"{__root_dir__}/rna/src/cell_calling.R",
            f"--matrix {self.outdir}/02.count/raw_matrix",
            f"--outdir {self.outdir}/02.count/",
            f"--method {self.calling_method}",
            f"--expectcells {self.expectcells}",
            f"--forcecells {self.forcecells}",
            f"--minumi {self.minumi}"
        ]

        cellCalling_cmd_str = " ".join(cellCalling_cmd)
        logging_call(
            cellCalling_cmd_str,'count',self.outdir
            )

        print(f'\n{get_formatted_time()}\n'
            f'Generating the filtered expression matrix.')
        str_mkdir('%s/02.count/filter_matrix'%self.outdir)
        PISA_countFilter_cmd = [
            f"{__root_dir__}/software/PISA",
            "count",
            "-one-hit",
            f"-@ {self.threads}",
            "-cb DB",
            "-anno-tag GN",
            "-umi UB",
            f"-list {self.outdir}/02.count/beads_barcodes.txt",
            f"-outdir {self.outdir}/02.count/filter_matrix",
            f"{self.outdir}/02.count/anno_decon_sorted.bam"
        ]
        PISA_countFilter_cmd_str = " ".join(PISA_countFilter_cmd)
        logging_call(PISA_countFilter_cmd_str,'count',self.outdir)       
        
        ### summary beads merge 
        from dnbc4tools.rna.src.cellMerge import summary_count
        summary_count('%s/02.count/barcodeTranslate.txt'%self.outdir,
                      '%s/01.data/beads_stat.txt'%self.outdir,
                      '%s/02.count/beads_barcodes.txt'%self.outdir,
                      '%s/02.count/cellCount_report.csv'%self.outdir,
                      '%s/02.count'%self.outdir
                      )
        
        ### get cell report
        matrix_summary('%s/02.count/filter_matrix'%self.outdir,
                        '%s/02.count'%self.outdir,
                        '%s/02.count/cellCount_report.csv'%self.outdir)

        from dnbc4tools.rna.src.saturation import count_saturation
        # print(f'\n{get_formatted_time()}\t'
        #     f'Calculate saturation.')
        count_saturation('%s/02.count/anno_decon_sorted.bam'%self.outdir,
                         '%s/02.count/cellCount_report.csv'%self.outdir,
                         '%s/02.count/beads_barcodes.txt'%self.outdir,
                         '%s/02.count'%self.outdir,
                         threads = self.threads,
                         quality=20
                         )
        
        rm_temp('%s/02.count/unique_total_reads.xls'%self.outdir)
        rm_temp('%s/02.count/cell.id'%self.outdir)
        rm_temp('%s/02.count/cell_count_detail.xls'%self.outdir)
        rm_temp('%s/02.count/similarity_dropletfiltered.csv'%self.outdir)
        rm_temp('%s/02.count/beads_barcodes_umi100.txt'%self.outdir)
        rm_temp('%s/02.count/combined_list.txt'%self.outdir)

def count(args):
    Count(args).run()

def helpInfo_count(parser):
    parser.add_argument(
        '--name',
        metavar='NAME',
        help='sample name.'
        )
    parser.add_argument(
        '--threads',
        metavar='INT',
        help='Analysis threads. [default: 4].',
        type=int,default=4
        )
    parser.add_argument(
        '--outdir',
        metavar='DIR',
        help='output dir, [default: current directory].',
        default=os.getcwd()
        )
    parser.add_argument(
        '--calling_method',
        metavar='STR',
        help='Cell calling method, Choose from barcoderanks and emptydrops, [default: emptydrops].', 
        default='emptydrops'
        )
    parser.add_argument(
        '--expectcells',
        metavar='INT',
        help='Expected number of recovered beads, used as input to cell calling algorithm, [default: 3000].', 
        default=3000
        )
    parser.add_argument(
        '--forcecells',
        metavar='INT',
        help='Force pipeline to use this number of beads, bypassing cell calling algorithm.',
        default=0
        )
    parser.add_argument(
        '--minumi',
        metavar='INT',
        help='The min umi for use emptydrops, [default: 1000].', 
        default=1000
        )
    return parser
