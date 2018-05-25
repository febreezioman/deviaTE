#! /usr/local/bin/python3
import argparse
import glob
import sys
from bin import deviaTE_IO as IO

deviaTE = '/'.join(sys.argv[0].split('/')[:-1])

parser = argparse.ArgumentParser()
# args for prepping
parser.add_argument('--library', dest='lib', type=str, help='path to reference library')
parser.add_argument('--read_type', type=str, default='sanger')
parser.add_argument('--min_read_len', type=str, default='1')
parser.add_argument('--quality_threshold', type=str, default='15')
parser.add_argument('--min_alignment_len', type=str, default='1')
parser.add_argument('--threads', type=str, default='1')
# args for analysis
parser.add_argument('--family', type=str, required=True, dest='fam', default=None)
parser.add_argument('--annotation', type=str, default=None, help='annotation in gff-format')
# args for plotting
parser.add_argument('--free_yaxis', action='store_true', help='flag to free the y-axis; for highly differential coverage')
parser.add_argument('--color_reference', action='store_true', help='color ref in snps')
# input arguments - mutually exclusive
inp_group = parser.add_mutually_exclusive_group(required=True)
inp_group.add_argument('--input_fq', type=str, default=None, help='fastq file for prepping and analysis')
inp_group.add_argument('--input_bam', type=str, default=None, help='alignment file to be analyzed')
inp_group.add_argument('--input_fq_dir', action='store_true', help='directory of fastq-files as input')
inp_group.add_argument('--input_bam_dir', action='store_true', help='directory of sam-files as input')
args = parser.parse_args()


def process_fq(file):
    sample_id = file
    output_table = sample_id + '.' + args.fam
    output_plot = output_table + '.pdf'
    
    fq = IO.fq_file(inp=file)
    fq.prep(script_loc=deviaTE, lib=args.lib, qual_tr=args.quality_threshold, min_rl=args.min_read_len,
            min_al=args.min_alignment_len, read_ty=args.read_type, thr=args.threads)
    
    prep_bam = IO.bam_file(inp=fq.path + '.fused.sort.bam', from_fq=True)    
    prep_bam.analyze(script_loc=deviaTE, lib=args.lib, fam=args.fam, sid=sample_id,
                     out=output_table, anno=args.annotation)
    
    table = IO.analysis_table(inp=output_table)
    table.plot(script_loc=deviaTE, out=output_plot, free_y=args.free_yaxis, col_ref=args.color_reference)
    
def process_bam(bam):
    sample_id = bam
    output_table = sample_id + '.' + args.fam
    output_plot = output_table + '.pdf'
    
    prep_bam = IO.bam_file(inp=bam, from_fq=False)
    prep_bam.fuse(script_loc=deviaTE)
    fused_bam = IO.bam_file(inp=bam + '.fused.sort.bam', from_fq=False)
    fused_bam.analyze(script_loc=deviaTE, lib=args.lib, fam=args.fam, sid=sample_id,
                      out=output_table, anno=args.annotation)
        
    table = IO.analysis_table(inp=output_table)
    table.plot(script_loc=deviaTE, out=output_plot, free_y=args.free_yaxis, col_ref=args.color_reference)
    

if args.input_fq:
    print('Fastq provided: preparing for alignment')
    process_fq(file=args.input_fq)
    
elif args.input_bam:
    print('Alignment file provided: skipping preparation')
    process_bam(bam=args.input_bam)
    
elif args.input_fq_dir:
    print('Directory of fastq files provided: preparing for alignment')
    fq_list = glob.glob('*.fastq') #+ glob.glob('*.fq') fq not yet implemented
    print(fq_list)
    
    for f in fq_list:
        process_fq(file=f)
        
elif args.input_bam_dir:
    print('Directory of bam-files provided: skipping preparation')    
    bam_list = glob.glob('*.bam')
    print(bam_list)
    
    for b in bam_list:
        process_bam(bam=b)
        
else:
    sys.exit('No input provided')
    
print('done')

