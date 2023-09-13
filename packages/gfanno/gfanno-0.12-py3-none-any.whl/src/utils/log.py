import time
'''
   ______  ________    _     Gene Family Annotation Pipline                           
 .' ___  ||_   __  |  / \     Bioinformatics Lab of SCAU.            
/ .'   \_|  | |_ \_| / _ \     _ .--.   _ .--.   .--.   
| |   ____  |  _|   / ___ \   [ `.-. | [ `.-. |/ .'`\ \ 
\ `.___]  |_| |_  _/ /   \ \_  | | | |  | | | || \__. | 
 `._____.'|_____||____| |____|[___||__][___||__]'.__.'  
---------------------------------------------------------------------- 
'''
class log:
    def __init__(self):
        pass
    def welcome(self):
        msg = 'Hello'
        print(msg)
    def info(self,msg = '',workname='Default'):
        now = time.asctime( time.localtime(time.time()))
        print(f'{now} - {workname}: {msg}')

    def notice(self,msg = '',workname='Default'):
        now = time.asctime( time.localtime(time.time()))
        print(f'{now} - {workname}: [ {msg} ]')

    def record(self,log_file_path,args,result):
        with open(log_file_path,'a',encoding='utf8') as file:
            file.write(f'Activate Time: {time.asctime( time.localtime(time.time()))} \n')
            file.write(f'Command: {args} \n')
            file.write('--'*25 +'\n')
            file.write(result+'\n')
            file.write('==' * 25 +'\n')
        return True
