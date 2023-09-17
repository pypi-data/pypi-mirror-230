import os
import argparse


circos_usage = '''
======================== circos example commands ========================

MetaCHIP2 circos -i cir_plot_matrix.csv -o cir_plot_matrix.pdf

=========================================================================
'''


def circos(args):

    input_matrix = args['i']
    font_size    = args['s']
    output_plot  = args['o']

    current_file_path = '/'.join(os.path.realpath(__file__).split('/')[:-1])
    circos_HGT_R      = '%s/circos_HGT.R' % current_file_path

    os.system('Rscript %s -m %s -s %s -p %s' % (circos_HGT_R, input_matrix, font_size, output_plot))
    print('Done, plot exported to %s' % output_plot)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True,                        help='input matrix')
    parser.add_argument('-s', required=False, type=int, default=12, help='font size, default: 12')
    parser.add_argument('-o', required=True,                        help='output plot')
    args = vars(parser.parse_args())
    circos(args)


