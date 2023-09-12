import os,subprocess
from . import log

'''
   _____                 ______      
  / ____|               |  ____/\    
 | |  __  ___ _ __   ___| |__ /  \   GeneFamilyAnno Pipline
 | | |_ |/ _ \ '_ \ / _ \  __/ /\ \   Bioinformatics Lab of SCAU.
 | |__| |  __/ | | |  __/ | / ____ \    
  \_____|\___|_| |_|\___|_|/_/    \_\   Version:0.1
---------------------------------------------------------------------- 
'''
class commander:
    def __init__(self,log_path):
        if log_path == None:
            self.log_path = os.path.join(os.getcwd(),'Command.log')
        else:
            self.log_path = log_path

    def run(self,command):
        res = self.cmd(command,)
        l = log.log()
        l.record(log_file_path=self.log_path,args=res.args,result=res.stdout)
        # 如果状态码不为了则Error
        res.check_returncode()
        return res

    # 执行命令
    def cmd(self,command):
        subp = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
        return subp



