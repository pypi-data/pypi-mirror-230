# Single-cell analysis workflow instructions tips
# category {rna,atac,tools}
# type {dnbc4,dnbc4tools}

def help_text(category,type):
    if category == 'rna':

        help_text = '''
        DNBelab C Series Single-Cell RNA analysis workflow:
        --------------------------------
        \033[0;32;40mFunction\033[0m:
        \033[0;32;40m%s run\033[0m      Using single-cell RNA cDNA and oligo library sequencing data for 
                                quality control, alignment, and annotation of functional region 
                                analysis. Identify droplets containing cells and merge beads in 
                                the same droplet to generate a filtered gene expression matrix. 
                                Use the filtered gene expression matrix for cell filtering, 
                                dimensionality reduction, clustering, and annotation analysis.
        \033[0;32;40m%s multi\033[0m    Generate shell scripts to run the "%s run" command on 
                                multiple samples.
        \033[0;32;40m%s mkref\033[0m    Build reference database.'''%(type,type,type,type)

    if category == 'atac':
        help_text = '''
        DNBelab C Series Single-Cell ATAC analysis workflow:
        --------------------------------
        \033[0;32;40mFunction\033[0m:
        \033[0;32;40m%s run\033[0m      Using the single-cell ATAC library sequencing data for quality 
                                 control and alignment analysis. Identify droplets containing 
                                 cells and merge beads in the same droplet to generate filtered 
                                 fragment files. Use the filtered fragment file for peak calling, 
                                 cell filtering, dimensionality reduction and cluster analysis
        \033[0;32;40m%s multi\033[0m    Generate shell scripts to run the "%s run" command on 
                                 multiple samples.
        \033[0;32;40m%s mkref\033[0m    Build reference database.'''%(type,type,type,type)


    if category == 'tools':
        help_text = '''
        DNBelab C Series Single-Cell tools:
        --------------------------------
        \033[0;32;40mFunction\033[0m:
        \033[0;32;40m%s mkgtf\033[0m      Perform gene type filtering on a GTF annotation file.
        \033[0;32;40m%s clean\033[0m      Delete intermediate files created during the analysis workflow.
        \033[0;32;40m%s changetag\033[0m  Exchange the tag information in bam in pairs.'''%(type,type,type)

    return help_text

    # atac


sum_help = '''
        DNBelab C Series Single-Cell Analysis Workflow Suite:
        --------------------------------
        \033[0;32;40mdnbctools rna\033[0m      Single-Cell RNA Analysis Workflow
        \033[0;32;40mdnbctools atac\033[0m     Single-Cell ATAC Analysis Workflow
        \033[0;32;40mdnbctools tools\033[0m    Collection of Analysis Tools'''


def help_sub_text(category,type,pipe):
    
    if category == 'rna':

        if pipe == 'mkref':
            help_text = '''

            '--species',  
                Specify the species name for constructing the reference database. 
                For cell annotation analysis, only "Homo_sapiens", "Human", "Mus_musculus", and "Mouse" are valid options.

            '--chrM', 
                Definition of mitochondrial chromosomes, 'auto' will recognize in 'chrM,MT,chrMT,mt,Mt'.
                Genes located on mitochondria will be automatically identified.

            '--noindex', 
                When the database has already been constructed using scSTAR, 
                using the '--noindex' parameter will skip the indexing step.

            Example:
                %s mkref --fasta /database/genome.fasta --ingtf /database/genes.gtf --species Homo_sapiens --chrM MT --genomeDir /database --threads 10
            '''%type

        elif pipe == 'run':
            help_text = '''

            '--cDNAfastq1', '--cDNAfastq2', '--oligofastq1', '--oligofastq2',
                Multiple raw FASTQ sequences, separated by commas, 
                should have consistent ordering of the cDNA or oligo R1/R2 FASTQ files.

            '--chemistry', '--darkreaction', 
                Recommend automatic detection for settings.
                When multiple FASTQ files are used, ensure that the cDNA or oligo libraries have consistent dark cycles. 
                If manual configuration of the reagent version and dark cycles is necessary, both parameters should be set together.
                The reagent versions available are "scRNAv1HT" and "scRNAv2HT".
                Dark cycles for cDNA and oligo libraries should be separated by commas, for example, "R1,R1R2", "R1,R1", "unset,unset", etc.

            '''
        elif pipe == 'multi':
            help_text = '''
            All samples should be from the same species or the same reference database.
            
            '--list', 
                Generates a three-column list with tab (\\t) as the separator. 
                The first column contains the sample name, the second column contains the cDNA library sequencing data, 
                and the third column contains the oligo library sequencing data. 
                Multiple fastq files should be separated by commas, and R1 and R2 files should be separated by semicolons. 
                Here's an example of how the input list should be formatted:
                sample1  cDNA1_R1.fq.gz;cDNA1_R2.fq.gz  oligo1_R1.fq.gz,oligo4_R1.fq.gz;oligo1_R2.fq.gz,oligo4_R2.fq.gz
                sample2  cDNA2_R1.fq.gz;cDNA2_R2.fq.gz  oligo2_R1.fq.gz;oligo2_R2.fq.gz
                sample3  cDNA3_R1.fq.gz;cDNA3_R2.fq.gz  oligo3_R1.fq.gz;oligo3_R2.fq.gz
            '''

        else:
            help_text = '''
        '''

    if category == 'atac':
        if pipe == 'mkref':
            help_text = '''

            '--chrM', 
                Definition of mitochondrial chromosomes, 'auto' will recognize in 'chrM,MT,chrMT,mt,Mt'.

            '--blacklist', 
                The software offers blacklists for hg38, hg19, and mm10. 
                You can simply input "--blacklist hg38" to utilize the hg38 blacklist. 
                For other species, you will need to provide the corresponding BED file. 
                In case you do not possess a blacklist file, you can proceed without including this parameter.

            '--prefix', 
                A string or a list of strings representing the prefix(es) or full name(s) of the chromosome(s) to keep.

            '--noindex', 
                When the database has been built using chromap, add this parameter will skip this step and only generate the ref.json file.

            Example:
                %s mkref --fasta /database/genome.fasta --ingtf /database/genes.gtf --species Homo_sapiens --chrM MT --genomeDir /database --blacklist blacklist.bed 
            '''%type
            
        elif pipe == 'run':
            help_text = '''

            '--fastq1', '--fastq2',
                Multiple raw FASTQ files should be separated by commas and belong to the same sequencing library.
                The order of the R1/R2 fastq files must be consistent.

            '--darkreaction', 
                Recommend using automatic detection for settings.
                Multiple FASTQ data for sequencing need to have consistent sequencing lengths and dark cycles. 
                The dark cycles mode can be "R1R2", "R1", "R2", "unset", etc.

            '--customize', 
                The value is a comma-separated string, [r1|r2|bc]:start:end:strand.
                The start and end are inclusive and -1 means the end of the read.
                For example, 'bc:6:15,bc:22:31,r1:65:-1,r2:19:-1': 
                'bc' indicates the cell barcode information, '6:15' denotes positions 7 to 16 in the sequence.
            '''
        elif pipe == 'multi':
            help_text = '''
            All samples should be from the same species or the same reference database.

            '--list', 
                Generates a two-column list with tab (\\t) as the separator.
                The first column contains the sample name, and the second column contains the sequencing data. 
                R1 and R2 reads should be separated using semicolons, and multiple FASTQ files should be separated with commas. 
                Here's an example of how the input list should be formatted:
                sample1  test1_R1.fq.gz,test4_R1.fq.gz;test1_R2.fq.gz,test4_R2.fq.gz
                sample2  test2_R1.fq.gz;test2_R2.fq.gz
                sample3  test3_R1.fq.gz;test3_R2.fq.gz
            '''
        
        else:
            help_text = '''
            '''

    if category == 'tools':
        if pipe == 'mkgtf':
            help_text = '''
            Filter Gene Types in a GTF Annotation File.           
            For Single-Cell RNA analysis, the GTF file must include at least "gene" or "transcript" types and "exon" type annotations. 
            Additionally, the attributes should have at least one of "gene_id" or "gene_name" and one of "transcript_id" or "transcript_name".
                
            
            '--include', 
                Choose specific gene types to retain through filtering. By default, 
                the following gene types are included:
                    protein_coding, lncRNA, lincRNA, antisense, IG_C_gene, IG_D_gene, 
                    IG_J_gene, IG_LV_gene, IG_V_gene, IG_V_pseudogene, IG_J_pseudogene, 
                    IG_C_pseudogene,TR_C_gene, TR_D_gene, TR_J_gene, TR_V_gene 
            
            The 'action' parameter can be set to 'mkgtf' or 'stat':
            '--action stat', 
                Calculate the number of genes for each gene type.
                Example:
                    %s mkgtf --action stat --ingtf genes.gtf --output gtfstat.txt --type gene_biotype

            '--action mkgtf', 
                Filter gene types in the GTF file.
                Example:
                    %s mkgtf --ingtf genes.gtf --output genes.filter.gtf --type gene_biotype 
            '''%(type,type)

        elif pipe == 'clean':
            help_text = '''
            Perform cleanup of intermediate files generated during the analysis to save storage space.

            Example:
                %s clean --name sample1,sample2
            '''%type

        elif pipe == 'changetag':
            help_text = '''
            Exchange the tag information in bam in pairs.

            Example:
                %s changetag --inbam anno_decon_sorted.bam --outbam out.velocyto.bam
            '''%type

        else:
            help_text = '''
        '''
    return help_text
