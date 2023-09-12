class GeneFamilyAnno:
    def __init__(self, ctl=dict()):

        if type(ctl) != type(dict):
            assert 'Parameter configuration error!'

        self.u_fasta_file_path = ctl.get('u_fasta_file_path')
        self.u_seed_file_path = ctl.get('u_seed_file_path')
        self.u_hmm_file_path = ctl.get('u_hmm_file_path')
        self.u_domain = ctl.get('u_domain', 'Peptidase_S10')
        self.u_identity = ctl.get('u_identity', 90)
        self.u_pfam_coverage = ctl.get('u_pfam_coverage', 50)
        self.u_blastp_gcovhsp = ctl.get('u_blastp_gcovhsp', 80)
        self.u_output = ctl.get('output.txt', 'Result.txt')

    def welcome(self):
        m = '''
   ______  ________    _     Gene Family Annotation Pipline
 .' ___  ||_   __  |  / \     Bioinformatics Lab of SCAU.
/ .'   \_|  | |_ \_| / _ \     _ .--.   _ .--.   .--.   
| |   ____  |  _|   / ___ \   [ `.-. | [ `.-. |/ .'`\ \ 
\ `.___]  |_| |_  _/ /   \ \_  | | | |  | | | || \__. | 
 `._____.'|_____||____| |____|[___||__][___||__]'.__.'  
---------------------------------------------------------------------- 
            '''
        print(m)

    def run(self):
        import time, os
        from .utils.commander import commander
        from .utils.filter import filter
        from .utils.log import log

        # Define Directory
        BASE_DIR = os.getcwd()
        PROJECT_DIR = os.path.join(BASE_DIR, 'Project_' + str(int(time.time())))
        LOG_PATH = os.path.join(PROJECT_DIR, 'log.txt')
        CPU_COUNT = os.cpu_count()

        if not os.path.exists(PROJECT_DIR):
            os.mkdir(PROJECT_DIR)

        # 文件路径定义
        BLASTDB_PATH = os.path.join(PROJECT_DIR, "blastdb", os.path.basename(self.u_seed_file_path))
        BLASTP_PATH = os.path.join(PROJECT_DIR, 'blastp.out')
        HMMSEARCH_PATH = os.path.join(PROJECT_DIR, 'hmm.out')

        # 实例化
        cmd = commander(LOG_PATH)
        log = log()

        # makeblastdb
        log.info(msg='Start Makeblastdb...')
        res = cmd.run(f'makeblastdb -in {self.u_seed_file_path} -dbtype prot -out {BLASTDB_PATH}')

        # BLASTP
        log.info(msg='Start Blastp...')
        res = cmd.run(
            f'blastp -num_threads {CPU_COUNT} -db {BLASTDB_PATH} -query {self.u_fasta_file_path} -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qcovhsp" -seg yes')
        with open(BLASTP_PATH, 'w', encoding='utf8') as f:
            f.write(res.stdout)

        # hmmsearch
        log.info(msg='Start hmmsearch...')
        res = cmd.run(
            f'hmmsearch --cpu {CPU_COUNT} --domtblout {HMMSEARCH_PATH} {self.u_hmm_file_path} {self.u_fasta_file_path}')

        log.info(msg='Start Filter...')
        filter = filter()
        filter.extract_candidate_gene(
            hmmfile=HMMSEARCH_PATH,
            blastpfile=BLASTP_PATH,
            domain=self.u_domain,
            pfam_coverage=self.u_pfam_coverage,
            identity=self.u_identity,
            blastp_qcovhsp=self.u_blastp_gcovhsp,
            fileout=self.u_output)
        log.info(msg='Success!')