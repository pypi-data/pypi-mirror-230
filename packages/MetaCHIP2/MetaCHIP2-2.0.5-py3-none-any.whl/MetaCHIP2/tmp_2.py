import os
import glob
from Bio import SeqIO
import matplotlib.pyplot as plt


def sep_path_basename_ext(file_in):

    # separate path and file name
    f_path, file_name = os.path.split(file_in)
    if f_path == '':
        f_path = '.'

    # separate file basename and extension
    f_base, f_ext = os.path.splitext(file_name)

    return f_path, f_base, f_ext


grouping_file    = '/Users/songweizhi/Desktop/MetaCHIP2/HGT_Shen/Bacilli_plus_78_clade.txt'
detected_hgt_txt = '/Users/songweizhi/Desktop/MetaCHIP2/HGT_Shen/Bacilli_plus_78_MetaCHIP2_wd_1_detected_HGTs.txt'


gnm_to_group_dict = dict()
for each_genome in open(grouping_file):
    each_genome_split = each_genome.strip().split(',')
    group_id = each_genome_split[0]
    genome_name = each_genome_split[1]
    gnm_to_group_dict[genome_name] = group_id
print(gnm_to_group_dict)


for each_hgt in open(detected_hgt_txt):
    if not each_hgt.startswith('Gene_1\tGene_2\tIdentity'):
        each_hgt_split = each_hgt.strip().split('\t')
        d_gnm = each_hgt_split[-1].split('-->')[0]
        r_gnm = each_hgt_split[-1].split('-->')[-1]
        d_grp = gnm_to_group_dict[d_gnm]
        r_grp = gnm_to_group_dict[r_gnm]

        if (d_grp not in ['A', 'B', 'C', 'D']) and (r_grp in ['A', 'B', 'C', 'D']) :
            print(each_hgt_split)
            print(d_grp)
            print(r_grp)






# gnm_to_hgt_num_dict = dict()
# grp_to_hgt_num_dict = dict()
# for each_hgt in open(detected_hgt_txt):
#     if not each_hgt.startswith('Gene_1\tGene_2\tIdentity'):
#
#         each_hgt_split = each_hgt.strip().split('\t')
#         recipient_gnm = each_hgt_split[-1].split('-->')[-1]
#         recipient_grp = gnm_to_group_dict[recipient_gnm]
#
#         if recipient_gnm not in gnm_to_hgt_num_dict:
#             gnm_to_hgt_num_dict[recipient_gnm] = 1
#         else:
#             gnm_to_hgt_num_dict[recipient_gnm] += 1
#
#         if recipient_grp not in grp_to_hgt_num_dict:
#             grp_to_hgt_num_dict[recipient_grp] = 1
#         else:
#             grp_to_hgt_num_dict[recipient_grp] += 1
#
# print(gnm_to_hgt_num_dict)
# print(grp_to_hgt_num_dict)
#
# grp_to_gc_content_dict = dict()
# grp_to_gc_num_dict = dict()
# grp_to_total_len_dict = dict()
# for each_seq in SeqIO.parse(recipient_ffn, 'fasta'):
#     recipient_gnm = '_'.join(each_seq.id.split('_')[:-1])
#     recipient_grp = gnm_to_group_dict[recipient_gnm]
#     gc_num = str(each_seq.seq).count('G') + str(each_seq.seq).count('C')
#     gc_content = gc_num*100/len(each_seq.seq)
#     gc_content = float("{0:.2f}".format(gc_content))
#     if recipient_grp not in grp_to_gc_content_dict:
#         grp_to_gc_content_dict[recipient_grp] = [gc_content]
#         grp_to_gc_num_dict[recipient_grp] = gc_num
#         grp_to_total_len_dict[recipient_grp] = len(each_seq.seq)
#     else:
#         grp_to_gc_content_dict[recipient_grp].append(gc_content)
#         grp_to_gc_num_dict[recipient_grp] += gc_num
#         grp_to_total_len_dict[recipient_grp] += len(each_seq.seq)
#
#
# print(grp_to_gc_content_dict)
#

#
# for each_grp in sorted(list(grp_to_gc_content_dict.keys())):
#     gc_list = grp_to_gc_content_dict[each_grp]
#     mean_gc = Average(gc_list)
#     print('%s\t%s\t%s' % (each_grp, mean_gc, gc_list))
#
# print()
# for each_grp in sorted(list(grp_to_gc_content_dict.keys())):
#     total_gc = grp_to_gc_num_dict[each_grp]/grp_to_total_len_dict[each_grp]
#     print('%s\t%s' % (each_grp,total_gc))







