from argparse import ArgumentParser
from .GeneFamilyAnno import GeneFamilyAnno

'''
   ______  ________    _     Gene Family Annotation Pipline                           
 .' ___  ||_   __  |  / \     Bioinformatics Lab of SCAU.            
/ .'   \_|  | |_ \_| / _ \     _ .--.   _ .--.   .--.   
| |   ____  |  _|   / ___ \   [ `.-. | [ `.-. |/ .'`\ \ 
\ `.___]  |_| |_  _/ /   \ \_  | | | |  | | | || \__. | 
 `._____.'|_____||____| |____|[___||__][___||__]'.__.'  
'''

arg = ArgumentParser(description='GeneFamilyAnno - BLOSCAU')

arg.add_argument("-f",
                 "--fasta",
                 required=True,
                 help="input fasta file path")
arg.add_argument("-s",
                 "--seed",
                 required=True,
                 help="input seed file path")
arg.add_argument("--hmm",
                 required=True,
                 help="Input files required the hmmsearch results file")

arg.add_argument("-o",
                 "--output",
                 default='Result.txt',
                 help="output file path (Default:Result.txt)")

arg.add_argument('--domain',
                 type=str,
                 default='Peptidase_S10',
                 help="The name(s) of the matching structural domain(s) should be entered;(Default:Peptidase_S10)"
                 )

arg.add_argument('--identity',
                 type=int,
                 default=90,
                 help='Entering the threshold value for blastp identity'
                      'function: Filter out sequences that are smaller than the identity threshold. (Default:90)'
                 )

arg.add_argument('--blastp_qcovhsp',
                 type=int,
                 default=80,
                 help='Entering the threshold value for the Query Coverage Per Subject of Blastp.(Default:80)'
                 )

# Add pfam_coverage parameter.
arg.add_argument('--pfam_coverage',
                 type=int,
                 default=80,
                 help='Entering the threshold value for the Coverage of Hmmsearch. (Default:50)'
                 )

args = arg.parse_args()
ctl = {
    'u_fasta_file_path': args.fasta,
    'u_seed_file_path': args.seed,
    'u_hmm_file_path': args.hmm,
    'u_domain': args.domain,
    'u_identity': args.identity,
    'u_pfam_coverage': args.pfam_coverage,
    'u_blastp_gcovhsp': args.blastp_qcovhsp,
    'u_output': args.output,
}


def main():
    s = GeneFamilyAnno(ctl)
    s.welcome()
    s.run()

if __name__ == '__main__':
    main()
