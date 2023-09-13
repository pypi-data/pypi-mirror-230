import pandas as pd
'''
   ______  ________    _     Gene Family Annotation Pipline                           
 .' ___  ||_   __  |  / \     Bioinformatics Lab of SCAU.            
/ .'   \_|  | |_ \_| / _ \     _ .--.   _ .--.   .--.   
| |   ____  |  _|   / ___ \   [ `.-. | [ `.-. |/ .'`\ \ 
\ `.___]  |_| |_  _/ /   \ \_  | | | |  | | | || \__. | 
 `._____.'|_____||____| |____|[___||__][___||__]'.__.'  
---------------------------------------------------------------------- 
'''
class filter:
    def __init__(self):
        pass
    def extract_candidate_gene(self,hmmfile, blastpfile, domain, pfam_coverage, identity, blastp_qcovhsp, fileout):
        identity = int(identity)
        blastp_qcovhsp = int(blastp_qcovhsp)
        pfam_coverage = int(pfam_coverage)

        hmm_file = pd.read_csv(hmmfile,sep='\s+', comment='#', header=None)
        hmm_file[17] = ((hmm_file.iloc[:, 16] - hmm_file.iloc[:, 15]) / hmm_file.iloc[:, 5]) * 100
        hmm_evalue = hmm_file[hmm_file.iloc[:, 6] < 1E-10]
        hmm_subset = hmm_evalue.iloc[:, [0, 3, 17]]
        hmm_subset.columns = ['target_id', 'domain', 'pfam_coverage']
        # Split the data into two parts based on domain.
        domains = domain.split(',')
        df_list = []
        for d in domains:
            df_list.append(hmm_subset[hmm_subset['domain'] == d])
        if len(df_list) > 1:
            common_ids = set(df_list[0]['target_id']).intersection(set(df_list[1]['target_id']))
            for i in range(2, len(df_list)):
                common_ids = common_ids.intersection(set(df_list[i]['target_id']))
            hmm_domain = hmm_subset[hmm_subset['target_id'].isin(common_ids)]
        else:
            hmm_domain = df_list[0]
        hmm_coverage = hmm_domain[hmm_domain['pfam_coverage'] >= pfam_coverage]

        blastp_file = pd.read_csv(
            blastpfile,
            sep='\t', header=None, usecols=[0, 2, 10, 12],
            names=['target_id', 'blastp_identity', 'evalue', 'blastp_qcovhsp'])

        blastp_evalue = blastp_file[blastp_file['evalue'] < 1E-10]
        blastp_identity = blastp_evalue[blastp_evalue['blastp_identity'] >= identity]
        blastp_qcovhsp = blastp_identity[blastp_identity['blastp_qcovhsp'] >= blastp_qcovhsp]

        merged_hmm_blastp = pd.merge(hmm_coverage, blastp_qcovhsp, on='target_id')
        df = merged_hmm_blastp.sort_values(by=['blastp_identity', 'pfam_coverage'], ascending=[False, False])
        df2 = df.drop_duplicates(subset=['target_id'], keep='first')
        df_out = df2['target_id']
        df_out.to_csv(fileout, index=False)