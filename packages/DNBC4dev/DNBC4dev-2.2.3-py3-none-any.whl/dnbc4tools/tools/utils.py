import os
import sys
import gzip
import json
import time
import logging
import sys
import warnings
from datetime import datetime
import subprocess
from dnbc4tools.__init__ import __root_dir__

def str_mkdir(arg):
    if not os.path.exists(arg):
        os.system('mkdir -p %s'%arg)

def change_path():
    os.environ['PATH'] += ':'+'/'.join(str(__root_dir__).split('/')[0:-4])+ '/bin'
    os.environ['LD_LIBRARY_PATH'] = '/'.join(str(__root_dir__).split('/')[0:-4]) + '/lib'

def bin_path():
    bin_command = '/'.join(str(__root_dir__).split('/')[0:-4])+ '/bin'
    return bin_command
    
def rm_temp(*args):
    for filename in args:
        if os.path.exists(filename):
            os.remove(filename)
        else:
            pass

def start_print_cmd(arg, log_dir):
    today = time.strftime('%Y%m%d', time.localtime(time.time()))
    logfile = f'{log_dir}/log/{today}.txt'
    logging.basicConfig(filename=logfile,level=logging.INFO, format='%(message)s')
    logger = logging.getLogger()
    logger.info(arg)
    subprocess.check_call(arg, shell=True)

def get_formatted_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

def setup_logging(name, log_dir):
    today = time.strftime('%Y%m%d', time.localtime(time.time()))
    logfile = f'{log_dir}/log/{today}.txt'
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s \n%(message)s')
        
        file_handler = logging.FileHandler(logfile, encoding="utf8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def logging_call(popenargs, name, log_dir):
    logger = setup_logging(name, log_dir)

    try:
        output = subprocess.check_output(popenargs, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        logger.info('%s', output)
    except subprocess.CalledProcessError as e:
        logger.error('Command failed with exit code %d', e.returncode)
        logger.error('%s', e.output)
    

def judgeFilexits(*args):
    for input_files in args:
        for input_file in input_files.split(','):
            if not os.path.exists(input_file): 
                print(" ------------------------------------------------") 
                print("Error: Cannot find input file or dir %s"%(str(input_file))) 
                print(" ------------------------------------------------") 
                sys.exit()
            else:
                pass

def hamming_distance(chain1, chain2):
    return len(list(filter(lambda x : ord(x[0])^ord(x[1]), zip(chain1, chain2))))


def read_json(file):
    with open(file,'r',encoding='utf8')as fp:
        json_data = json.load(fp)
    return json_data

def seq_comp(seq):
    nt_comp = {'A':'0', 'C':'1', 'G':'2', 'T':'3'}
    length = len(seq)-1
    sum = 0
    for k,v in enumerate(seq.upper()):
        sum += int(nt_comp[v])*(4**(length-k))
    return str('%010x'%sum).upper()

def read_anndata(path):
    import scipy.io
    from scipy.sparse import csr_matrix
    import anndata
    import pandas as pd
    mat = scipy.io.mmread(path+"/"+"matrix.mtx.gz").astype("float32")
    mat = mat.transpose()
    mat = csr_matrix(mat)
    adata = anndata.AnnData(mat,dtype="float32")
    genes = pd.read_csv(path+'/'+'features.tsv.gz', header=None, sep='\t')
    var_names = genes[0].values
    var_names = anndata.utils.make_index_unique(pd.Index(var_names))
    adata.var_names = var_names
    adata.var['gene_symbols'] = genes[0].values
    adata.obs_names = pd.read_csv(path+'/'+'barcodes.tsv.gz', header=None)[0].values
    adata.var_names_make_unique()
    return adata

def png_to_base64(file,filename,outdir):
    import base64
    base64_path = outdir +'/'+filename+'.base64'
    if os.path.isfile(file):
        with open(file, "rb") as f:
            base64_data = base64.b64encode(f.read())
            s = base64_data.decode()
            base64_path_f = open(base64_path, 'w')
            base64_path_f.write('<img src=data:image/'+'png'+';base64,'+s+">")
            base64_path_f.close()

def csv_datatable(file,outfile):
    import pandas as pd
    if os.path.exists(file):
        df= pd.read_csv(open(file),encoding="utf-8",dtype=str,)
        fw = open(outfile,'w')
        for index, row in df.iterrows():
            fw.write('<tr><td>'+row['gene']+'</td>'\
                +'<td>'+row['cluster']+'</td>'\
                +'<td>'+row['p_val_adj']+'</td>'\
                +'<td>'+row['p_val']+'</td>'\
                +'<td>'+row['avg_log2FC']+'</td>'\
                +'<td>'+row['pct.1']+'</td>'\
                +'<td>'+row['pct.2']+'</td>'\
            )
        fw.close()

def write_matrix(adata,outdir):
    import scipy.io
    import scipy.sparse
    import shutil
    import gzip
    adata.X = scipy.sparse.csr_matrix(adata.X.astype('int32'))
    scipy.io.mmwrite(
        "%s/matrix.mtx"%outdir, 
        adata.X.transpose()
        )
    adata.var.to_csv(
        '%s/features.tsv.gz'%outdir, 
        sep='\t', index=True, header=False,
        compression='gzip'
        )
    adata.obs.to_csv(
        '%s/barcodes.tsv.gz'%outdir, 
        sep='\t', index=True, header=False,
        compression='gzip'
        )
    with open("%s/matrix.mtx"%outdir,'rb') as mtx_in:
        with gzip.open("%s/matrix.mtx"%outdir + '.gz','wb') as mtx_gz:
            shutil.copyfileobj(mtx_in, mtx_gz)
    os.remove("%s/matrix.mtx"%outdir)


def verify_file(fastqfile):
    """
    Ensure that file can both be read and exists
    """
    try:
        fp = open_file(fastqfile)
        readlinefile = fp.readline()
        fp.close()
    except IOError as err:
        raise ValueError("Error reading the file {0}: {1}".format(fastqfile, err))
    return fastqfile

def open_file(fastqfile):
    if fastqfile.endswith('.gz'):
        return gzip.open(fastqfile, 'rt')
    else:
        return open(fastqfile, 'r')

def verify_paired_end(file1, file2, max_lines:int =1000):
    """
    Verify if paired-end files match
    """
    with open_file(file1) as f1, open_file(file2) as f2:
        mismatch_found = False
        for i, (line1, line2) in enumerate(zip(f1, f2)):
            if i >= max_lines * 4:
                break
            if i % 4 == 0:  # Read ID line
                if not line1.split('/')[0] == line2.split('/')[0] or line1.strip().split('/')[-1] != '1' or line2.strip().split('/')[-1] != '2':
                    mismatch_found = True
                    break
        if mismatch_found:
            warnings.warn("\033[0;33;40m Paired-end reads do not match at [%s,%s] \033[0m"%(file1, file2))


def verify_fastq_files(file1_list, file2_list):
    """
    Verify if the provided fastq files are valid and match as paired-end files
    """
    file1_list = file1_list.split(",")
    file2_list = file2_list.split(",")
    if len(file1_list) != len(file2_list):
        raise ValueError("Number of fastq1 files does not match number of fastq2 files")
    for file1, file2 in zip(file1_list, file2_list):
        file1 = verify_file(file1)
        file2 = verify_file(file2)
        verify_paired_end(file1, file2)