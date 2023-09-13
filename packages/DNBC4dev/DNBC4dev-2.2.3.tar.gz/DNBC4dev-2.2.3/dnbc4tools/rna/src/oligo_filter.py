import os
import pysam
import json
import multiprocessing
import re
from scipy import stats
import ahocorasick
import argparse
import heapq
import shutil
import pandas as pd
import numpy as np
import polars as pl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.interpolate import make_interp_spline
from collections import defaultdict
from subprocess import check_call


def calculate_hamming_distance(seq1, seq2):
    distance = sum(ch1 != ch2 for ch1, ch2 in zip(seq1, seq2))
    return distance

def process_fastq_file(fastq_file, whitelist1, whitelist2, whitelist1_distance, whitelist2_distance, output_file):
    ac = ahocorasick.Automaton()
    for idx, seq in enumerate(whitelist1):
        ac.add_word(seq, (1, idx))
    for idx, seq in enumerate(whitelist2):
        ac.add_word(seq, (2, idx))
    ac.make_automaton()
    
    with open(output_file, 'w') as out_file:
        for record in fastq_file:
            
            read_id = record.name
            regex = '(?<=CB:Z:).*$'
            str_select = re.findall(regex, read_id)[0]
            sequence = record.sequence
            umi = sequence[:10]
            barcode1 = sequence[10:20]
            barcode2 = sequence[20:30]

            matches = ac.iter(barcode1)
            corrected_barcode1 = None
            for _, (list_idx, match_idx) in matches:
                if list_idx == 1 and calculate_hamming_distance(barcode1, whitelist1[match_idx]) <= int(whitelist1_distance):
                    corrected_barcode1 = whitelist1[match_idx]
                    break
            matches = ac.iter(barcode2)
            corrected_barcode2 = None
            for _, (list_idx, match_idx) in matches:
                if list_idx == 2 and calculate_hamming_distance(barcode2, whitelist2[match_idx]) <= int(whitelist2_distance):
                    corrected_barcode2 = whitelist2[match_idx]
                    break
            
            if corrected_barcode1 != None and corrected_barcode2 != None:
                output_line = f"{str_select}\t{corrected_barcode1}{corrected_barcode2}\t{umi}\n"
                out_file.write(output_line)

def process_file(file_path, whitelist1, whitelist2, whitelist1_distance, whitelist2_distance, output_directory):
    file_name = os.path.basename(file_path)
    output_file = os.path.join(output_directory, f"{file_name}.processed")
    with pysam.FastxFile(file_path) as fastq_file:
        process_fastq_file(fastq_file, whitelist1, whitelist2, whitelist1_distance, whitelist2_distance, output_file)

def process_directory(input_directory, whitelist1, whitelist2, whitelist1_distance, whitelist2_distance, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    input_files = []
    for file_name in os.listdir(input_directory):
        if file_name.endswith(".fq.gz"):
            file_path = os.path.join(input_directory, file_name)
            input_files.append(file_path)

    pool = multiprocessing.Pool()

    for file_path in input_files:
        pool.apply_async(process_file, args=(file_path, whitelist1, whitelist2, whitelist1_distance, whitelist2_distance, output_directory))

    pool.close()
    pool.join()

def combine_txt(indir: str):
    if os.path.exists(f"{indir}/total_reads.xls"):
        os.remove(f"{indir}/total_reads.xls")
    os.system("find %s/temp/ -name \"*.processed\" | xargs cat  >> %s/total_reads.xls" % (indir, indir))

def external_sort(indir, buffer_size=10000000):
    sorted_files = []
    with open('%s/total_reads.xls'%indir, 'r') as f_in:
        chunk = []
        chunk_size = 0
        while True:
            line = f_in.readline()
            if not line:
                break

            chunk.append(line)
            chunk_size += 1

            if chunk_size >= buffer_size:
                sorted_file = os.path.join('%s/temp'%indir, f'{len(sorted_files)}.tmp')
                sorted_files.append(sorted_file)

                with open(sorted_file, 'w') as f_out:
                    f_out.writelines(sorted(chunk))
                
                chunk = []
                chunk_size = 0

    if chunk:
        sorted_file = os.path.join('%s/temp'%indir, f'{len(sorted_files)}.tmp')
        sorted_files.append(sorted_file)

        with open(sorted_file, 'w') as f_out:
            f_out.writelines(sorted(chunk))

    counts = defaultdict(int)
    with open('%s/unique_total_reads.xls'%indir, 'w') as f_out:
        for line in open_heapq(sorted_files):
            line = line.rstrip('\n')
            counts[line] += 1

        for line, count in counts.items():
            count_line = f"{count}\t{line}"
            f_out.write(count_line + '\n')

    for sorted_file in sorted_files:
        os.remove(sorted_file)
    shutil.rmtree('%s/temp'%indir)

def open_heapq(sorted_files):
    heap = []
    files = [open(file, 'r') for file in sorted_files]
    for i, file in enumerate(files):
        line = file.readline()
        if line:
            heapq.heappush(heap, (line, i, file))

    try:
        while heap:
            line, file_index, file = heapq.heappop(heap)
            yield line
            line = file.readline()
            if line:
                heapq.heappush(heap, (line, file_index, file))
            else:
                file.close()
    finally:
        for file in files:
            file.close()

def split_fastq(indexfastq,outdir,seqkitpath,threads):
    if os.path.exists("{outdir}/temp"):
        os.system("rm -rf {outdir}/temp")
    cmd = '%s/seqkit split2 --quiet --force --by-part %s %s -O %s/temp'%(seqkitpath,threads,indexfastq,outdir)
    check_call(cmd,shell=True)

def read_json(whitelist):
    with open(whitelist,'r') as load_f:
        load_dict = json.load(load_f)
        whitelist1_distance = load_dict["index carrier"][0]['distance']
        whitelist2_distance = load_dict["index carrier"][1]['distance']
        whitelist1 = load_dict["index carrier"][0]['white list']
        whitelist2 = load_dict["index carrier"][1]['white list']
        return whitelist1_distance,whitelist1,whitelist2_distance,whitelist2

def correct_umi(umi_dict, percent=0.1):
    umi_arr = sorted(
        umi_dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
    while len(umi_arr) > 1:
        umi_low = umi_arr.pop()
        low_seq = umi_low[0]
        low_count = umi_low[1]

        for umi_kv in umi_arr:
            high_seq = umi_kv[0]
            high_count = umi_kv[1]
            if float(low_count / high_count) > percent:
                break
            if calculate_hamming_distance(low_seq, high_seq) == 1:
                n_low = umi_dict[low_seq]
                umi_dict[high_seq] += n_low
                del umi_dict[low_seq]
                break
    return umi_dict

def process_group(grouped, group):
    group_df = grouped.get_group(group)
    data_dict = group_df.set_index('umi')['count'].to_dict()
    umi_dict = correct_umi(data_dict, percent=0.3)
    cellbarcode = group_df['cellbarcode'].iloc[0]
    indexcarrier = group_df['indexcarrier'].iloc[0]
    result_df = pd.DataFrame({"count": list(umi_dict.values()), "cellbarcode": cellbarcode, "indexcarrier": indexcarrier, "umi": list(umi_dict.keys())})
    return result_df

def process_worker(grouped, groups):
    result_dfs = []
    for group in groups:
        result_df = process_group(grouped, group)
        result_dfs.append(result_df)
    return pd.concat(result_dfs)

def processUmiAdjust(indir, n_processes):
    df = pd.read_table('%s/unique_total_reads.xls'%indir, header=None, sep='\t')
    df.columns = ["count", "cellbarcode", "indexcarrier", "umi"]

    grouped = df.groupby(['cellbarcode', 'indexcarrier'], sort=False)
    groups = list(grouped.groups.keys())

    groups_per_process = len(groups) // n_processes
    group_chunks = [groups[i:i+groups_per_process] for i in range(0, len(groups), groups_per_process)]

    with multiprocessing.Pool(processes=n_processes) as pool:
        results = pool.starmap(process_worker, [(grouped, group_chunk) for group_chunk in group_chunks])

    final_result_df = pd.concat(results)
    final_result_df["count"] = final_result_df["count"].astype(str).astype(int)
    final_result_df.to_csv('%s/adjust_unique_total_reads.xls'%indir, sep='\t', index=False, header=False)

def filter_outliers(df, column_name, z_threshold):
    value_counts = df[column_name].value_counts()
    z_scores = stats.zscore(value_counts)
    outlier_indices = value_counts[z_scores > z_threshold].index
    filtered_df = df[~df[column_name].isin(outlier_indices)]
    return filtered_df


def CB_UB_xls(indir,z_threshold):
    df = pd.read_table('%s/unique_total_reads.xls'%indir, sep='\t',header=None)
    df.columns = ['count','cDNA','oligo','umi']
    filtered_df = df[(df["count"] != 1) | (df[["cDNA", "oligo"]].duplicated(keep=False))]
    # filtered_df.to_csv("%s/unique_total_reads_filter1.xls"%indir, sep="\t", header=False, index=False)
    comb_count = filtered_df.groupby(["cDNA", "oligo"]).size().reset_index(name="count")
    comb_count_order = comb_count[["count","oligo","cDNA"]]
    filtered_df_index = filter_outliers(comb_count_order, 'oligo', z_threshold)
    comb_count_filter = filter_outliers(filtered_df_index, 'cDNA', z_threshold)
    comb_count_filter.to_csv("%s/CB_UB_count.txt"%indir, sep="\t", header=False, index=False)


def fraction_reads(outdir:str, threads:int = 4):
    cellcount_df = pl.read_csv(
        os.path.join(outdir, "unique_total_reads.xls"),
        has_headers=False,
        sep='\t',
        use_pyarrow=False,
        n_threads=threads,
        columns=["column_1", "column_2", "column_3", "column_4"],
        new_columns=["Count", "Cell", "oligo", "UMI"]
    ).with_columns([
        pl.col("Cell").cast(pl.Categorical),
        pl.col("oligo"),
        pl.col("UMI").cast(pl.Categorical),
        pl.col("Count").cast(pl.UInt32)
    ])

    sampling_fractions = [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    sampling_fractions_length = len(sampling_fractions)
    stats_df = pd.DataFrame(
        {
            "Total oligo": np.zeros(sampling_fractions_length, np.uint32),
            "Sequencing Saturation": np.zeros(sampling_fractions_length, np.float64),
            "UMI Saturation": np.zeros(sampling_fractions_length, np.float64)
        },
        index=pd.Index(data=np.array(sampling_fractions), name="sampling_fraction")
    )

    cellcount_all_df = cellcount_df.with_column(pl.col("Count").repeat_by(pl.col("Count"))).explode("Count")
    stats_df.loc[1.0, "UMI Saturation"] = round((1- (cellcount_df.filter(pl.col("Count") == 1).height)/(cellcount_df.height))*100,2)
    stats_df.loc[1.0, "Sequencing Saturation"] = round((1- cellcount_df.height/cellcount_df.filter(pl.col('Cell')!='None').select([pl.col("Count").sum()])[0,0])*100,2)
    cellcount_df = cellcount_df.with_column(pl.col("oligo").str.split(";")).explode("oligo")
    stats_df.loc[1.0, "Total oligo"] = pl.n_unique(cellcount_df['oligo'])
    del cellcount_df

    for sampling_fraction in sampling_fractions:
        if sampling_fraction == 0.0:
            continue
        elif sampling_fraction == 1.0:
            continue
        else:
            cellcount_sampled=cellcount_all_df.sample(frac=sampling_fraction)
            cellcount_sampled=cellcount_sampled.groupby(["Cell", "oligo","UMI"]).agg([pl.col("UMI").count().alias("Count")])
            stats_df.loc[sampling_fraction, "UMI Saturation"] = round((1- (cellcount_sampled.filter(pl.col("Count") == 1).height)/cellcount_sampled.height)*100,2)
            stats_df.loc[sampling_fraction, "Sequencing Saturation"] = round((1- (cellcount_sampled.height-1)/cellcount_sampled.filter(pl.col('Cell')!='None').select([pl.col("Count").sum()])[0,0])*100,2)
            cellcount_sampled = cellcount_sampled.with_column(pl.col("oligo").str.split(";")).explode("oligo")
            stats_df.loc[sampling_fraction, "Total oligo"] = pl.n_unique(cellcount_sampled['oligo'])
            del cellcount_sampled
    del cellcount_all_df
    stats_df.to_csv(os.path.join(outdir,"saturation_oligo.xls"),sep='\t')

def umi_saturation(ax: plt.axes, table: pd.DataFrame):
    xnew = np.linspace(table['sampling_fraction'].min(),table['sampling_fraction'].max(),20)
    smooth = make_interp_spline(table['sampling_fraction'],table['Sequencing Saturation']/100)(xnew)
    ax.set_xlim([0, table['sampling_fraction'].max()])
    ax.set_ylim([0, 0.9999])
    ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.spines['right'].set_visible(False) 
    ax.spines['top'].set_visible(False)
    ax.grid(linestyle='--')
    ax.plot(xnew,smooth,linewidth=3.0)
    ax.axhline(y=0.9,ls="--",c="black",linewidth=2.0)
    ax.set(xlabel='sampling_fraction', ylabel='Sequencing Saturation',title='Sequencing Saturation')

def gene_saturation(ax: plt.axes, table: pd.DataFrame):
    xnew = np.linspace(table['sampling_fraction'].min(),table['sampling_fraction'].max(),20)
    smooth = make_interp_spline(table['sampling_fraction'],table['UMI Saturation']/100)(xnew)
    ax.set_xlim([0, table['sampling_fraction'].max()])
    ax.set_ylim([0, 0.9999])
    ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.xaxis.set_major_locator(MaxNLocator(5))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.grid(linestyle='--')
    ax.plot(xnew,smooth,linewidth=3.0)
    ax.axhline(y=0.9,ls="--",c="black",linewidth=2.0)
    ax.set(xlabel='sampling_fraction', ylabel='UMI Saturation',title='UMI Saturation')

def plot_saturation(outdir):
    for_plot = pd.read_table(os.path.join(outdir,'saturation_oligo.xls'),sep='\t')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), tight_layout=True)
    arts = umi_saturation(ax1,for_plot)
    arts = gene_saturation(ax2,for_plot)
    fig.savefig(os.path.join(outdir,'saturation_oligo.png'),facecolor='white',transparent=False,dpi=400)
    plt.close(fig)

def oligo_combine(whitelistfile,oligofq,outdir,seqkitpath,threads):
    whitelist1_distance,whitelist1,whitelist2_distance,whitelist2 = read_json(whitelistfile)
    split_fastq(oligofq,outdir,seqkitpath,threads)
    process_directory('%s/temp'%outdir, whitelist1, whitelist2, whitelist1_distance, whitelist2_distance, '%s/temp'%outdir)
    combine_txt(outdir)
    external_sort(outdir)
    # processUmiAdjust(outdir,threads)
    CB_UB_xls(outdir,10)
    fraction_reads(outdir,int(threads))
    plot_saturation(outdir)

    if os.path.exists(f"{outdir}/total_reads.xls"):
        os.remove(f"{outdir}/total_reads.xls")


def cut_umi(beads_stat,condition):
    beadsStatDf = pd.read_table(beads_stat,header=0,sep='\t')
    filtered_beadsStat = beadsStatDf[beadsStatDf['UB'] >= condition]
    if len(filtered_beadsStat) > 100000:
        filtered_beadsStat = filtered_beadsStat.nlargest(100000, 'UB')
    return filtered_beadsStat


def parse_args():
    parser = argparse.ArgumentParser(description="filter whitelist")
    parser.add_argument(
        "--oligofq",
        type=str,
        help="input Index_reads.fq.gz"
        )
    parser.add_argument(
        "--whitelist",
        type=str,
        help="whitelist file"
        )
    parser.add_argument(
        "--outdir",
        type=str,
        help="outdir",
        default=os.getcwd()
        )
    parser.add_argument(
        "--seqkit",
        type=str,
        help="seqkit path"
        )
    parser.add_argument(
        "--threads",
        type=int,
        help="threads"
        )
    args = parser.parse_args()
    return args


if __name__=='__main__':
    args = parse_args()
    oligofq = args.oligofq
    outdir = args.outdir
    whitelistfile = args.whitelist
    seqkitpath = args.seqkit
    threads = args.threads

    oligo_combine(whitelistfile,oligofq,outdir,seqkitpath,threads)