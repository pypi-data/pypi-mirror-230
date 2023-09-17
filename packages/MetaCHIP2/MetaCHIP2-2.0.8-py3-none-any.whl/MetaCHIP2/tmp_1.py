import os
from Bio import SeqIO
import multiprocessing as mp


def select_seq(seq_file, seq_id_list, output_file):

    output_file_handle = open(output_file, 'w')
    for seq_record in SeqIO.parse(seq_file, 'fasta'):
        seq_id = seq_record.id
        if seq_id in seq_id_list:
            SeqIO.write(seq_record, output_file_handle, 'fasta-2line')
    output_file_handle.close()


def run_mmseqs_linclust(pwd_combined_ffn, num_threads, mmseqs_tsv):

    mmseqs_db  = '%s.db'            % pwd_combined_ffn
    mmseqs_clu = '%s.db.clu'        % pwd_combined_ffn
    mmseqs_tmp = '%s.db.clu.tmp'    % pwd_combined_ffn

    # run mmseqs
    mmseqs_createdb_cmd  = 'mmseqs createdb %s %s --dbtype 2 > /dev/null' % (pwd_combined_ffn, mmseqs_db)
    print(mmseqs_createdb_cmd)
    os.system(mmseqs_createdb_cmd)

    mmseqs_linclust_cmd  = 'mmseqs linclust %s %s %s --threads %s --min-seq-id 0.600 --seq-id-mode 0 --min-aln-len 200 --cov-mode 0 -c 0.75 --similarity-type 2 --remove-tmp-files > /dev/null' % (mmseqs_db, mmseqs_clu, mmseqs_tmp, num_threads)
    print(mmseqs_linclust_cmd)
    os.system(mmseqs_linclust_cmd)

    mmseqs_createtsv_cmd = 'mmseqs createtsv %s %s %s %s > /dev/null' % (mmseqs_db, mmseqs_db, mmseqs_clu, mmseqs_tsv)
    print(mmseqs_createtsv_cmd)
    os.system(mmseqs_createtsv_cmd)


def all_vs_all_blastn_by_mmseqs_clusters(mmseqs_tsv, ffn_dir, min_cluster_size, max_subset_seq_mum, num_threads, blast_parameters, ffn_dir_filtered, combined_blastn_op):

    mmseqs_cluster_dict = dict()
    for each_line in open(mmseqs_tsv):
        each_line_split = each_line.strip().split('\t')
        rep_id = each_line_split[0]
        mem_id = each_line_split[1]
        if rep_id not in mmseqs_cluster_dict:
            mmseqs_cluster_dict[rep_id] = set()
        mmseqs_cluster_dict[rep_id].add(mem_id)

    mmseqs_cluster_dict_filtered = dict()
    for each_cluster in mmseqs_cluster_dict:
        seq_set = mmseqs_cluster_dict[each_cluster]
        if len(seq_set) >= min_cluster_size:
            mmseqs_cluster_dict_filtered[each_cluster] = seq_set

    gnm_with_clustered_seq_set = set()
    gnm_to_clsutered_seq_dod = dict()
    subset_seq_num = 0
    for each_cluster in mmseqs_cluster_dict_filtered:
        clu_seq_set = mmseqs_cluster_dict_filtered[each_cluster]
        print('%s\t%s' % (each_cluster, clu_seq_set))
        subset_seq_num += len(clu_seq_set)
        subset_index = (subset_seq_num//max_subset_seq_mum) + 1

        if subset_index not in gnm_to_clsutered_seq_dod:
            gnm_to_clsutered_seq_dod[subset_index] = dict()

        for each_seq in clu_seq_set:
            gnm_id = '_'.join(each_seq.split('_')[:-1])
            gnm_with_clustered_seq_set.add(gnm_id)
            if gnm_id not in gnm_to_clsutered_seq_dod[subset_index]:
                gnm_to_clsutered_seq_dod[subset_index][gnm_id] = set()
            gnm_to_clsutered_seq_dod[subset_index][gnm_id].add(each_seq)

    #print('gnm_to_clsutered_seq_dod')
    #print(gnm_to_clsutered_seq_dod)

    for each_subset in gnm_to_clsutered_seq_dod:

        pwd_subset_dir       = '%s/%s'           % (ffn_dir_filtered, each_subset)
        pwd_subset_ffn       = '%s/%s.ffn'       % (ffn_dir_filtered, each_subset)
        pwd_subset_blastn_op = '%s/%s_blastn_op' % (ffn_dir_filtered, each_subset)

        os.mkdir(pwd_subset_dir)
        os.mkdir(pwd_subset_blastn_op)

        gnm_to_clsutered_seq_dict = gnm_to_clsutered_seq_dod[each_subset]
        for each_gnm in gnm_to_clsutered_seq_dict:
            clustered_seq_set     = gnm_to_clsutered_seq_dict[each_gnm]
            pwd_ffn_file          = '%s/%s.ffn' % (ffn_dir, each_gnm)
            pwd_ffn_file_filtered = '%s/%s.ffn' % (pwd_subset_dir, each_gnm)
            select_seq(pwd_ffn_file, clustered_seq_set, pwd_ffn_file_filtered)

        # makeblastdb
        cat_subset_seq_cmd = 'cat %s/*ffn > %s'  % (pwd_subset_dir, pwd_subset_ffn)
        os.system(cat_subset_seq_cmd)
        makeblastdb_cmd = 'makeblastdb -in %s -dbtype nucl -parse_seqids -logfile /dev/null' % pwd_subset_ffn
        os.system(makeblastdb_cmd)

        # run blastn
        blastn_cmd_list = []
        for each_gnm in gnm_to_clsutered_seq_dict:
            pwd_ffn         = '%s/%s.ffn'                           % (pwd_subset_dir, each_gnm)
            pwd_blatn_op    = '%s/%s_blastn.tab'                    % (pwd_subset_blastn_op, each_gnm)
            blastn_cmd      = 'blastn -query %s -db %s -out %s %s'  % (pwd_ffn, pwd_subset_ffn, pwd_blatn_op, blast_parameters)
            blastn_cmd_list.append(blastn_cmd)

        print('Running all-vs-all blastn with %s cores, subset %s/%s' % (num_threads, each_subset, len(gnm_to_clsutered_seq_dod)))
        pool = mp.Pool(processes=num_threads)
        pool.map(os.system, blastn_cmd_list)
        pool.close()
        pool.join()

    # combine blast results
    for each_gnm in gnm_with_clustered_seq_set:
        print(each_gnm)
        cat_cmd = 'cat %s/*_blastn_op/%s_blastn.tab > %s/%s_blastn.tab' % (ffn_dir_filtered, each_gnm, combined_blastn_op, each_gnm)
        os.system(cat_cmd)


# # file in
ffn_dir             = '/Users/songweizhi/Desktop/metachip_test/S2_sal_fde_pco_mmseqs_MetaCHIP_wd/tmp/ffn_faa_files'
pwd_combined_ffn    = '/Users/songweizhi/Desktop/metachip_test/S2_sal_fde_pco_mmseqs_MetaCHIP_wd/tmp/combined.ffn'
mmseqs_tsv          = '/Users/songweizhi/Desktop/metachip_test/S2_sal_fde_pco_mmseqs_MetaCHIP_wd/tmp/combined.ffn.db.clu.tsv'
min_cluster_size    = 5
max_subset_seq_mum  = 20000
num_threads         = 10
blast_parameters    = '-evalue 1e-5 -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen" -task blastn -num_threads 1'

# file out
ffn_dir_filtered    = '/Users/songweizhi/Desktop/metachip_test/S2_sal_fde_pco_mmseqs_MetaCHIP_wd/tmp/aaa'
combined_blastn_op  = '/Users/songweizhi/Desktop/metachip_test/S2_sal_fde_pco_mmseqs_MetaCHIP_wd/tmp/aaa_blastn_op'

if os.path.isdir(ffn_dir_filtered) is True:
    os.system('rm -r %s' % ffn_dir_filtered)
os.system('mkdir %s' % ffn_dir_filtered)

if os.path.isdir(combined_blastn_op) is True:
    os.system('rm -r %s' % combined_blastn_op)
os.system('mkdir %s' % combined_blastn_op)

print('running mmseqs')
run_mmseqs_linclust(pwd_combined_ffn, num_threads, mmseqs_tsv)
all_vs_all_blastn_by_mmseqs_clusters(mmseqs_tsv, ffn_dir, min_cluster_size, max_subset_seq_mum, num_threads, blast_parameters, ffn_dir_filtered, combined_blastn_op)


'''

S2_sal_fde_bin11_00493

'''
