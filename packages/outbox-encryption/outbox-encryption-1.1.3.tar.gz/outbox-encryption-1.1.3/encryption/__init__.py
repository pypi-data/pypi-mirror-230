# Ref : 
#   https://www.geeksforgeeks.org/fernet-symmetric-encryption-using-cryptography-module-in-python/
#   https://able.bio/rhett/how-to-set-and-get-environment-variables-in-python--274rgt5

import binascii
import os
# from io import StringIO
from pathlib import Path

from cryptography.fernet import Fernet              # pip install cryptography
from decouple import Config, Csv, RepositoryEnv     # pip install python-decouple
from django.conf import settings


class OutboxEncryption:
    '''
        Rules:
            Di semua linux yg aktif environmnetnya selalu ada variabel environment PS1
            Di windows variabel VENV


            UPDATE :
                8 Desember 2022
                # Ubah env_list dari string menjadi array []
                # Ubah env_local dari string menjadi array []
                # Ubah env_server dari string menjadi array []

                DI local 
                    iwan : django-outbox-dev
                    dony : outbox
                    
                Di server pythonanywhere 
                    env_outbox
                    
                Di server niaga hoster
                    ((outbox:3.10))

                Cari identifier sama persis data di atas


        Change Rules:
            1. library melakukan scan variabel environment
            2. pembeda antara developer satu dan lainnya ada di nama variabel environment
               LINUX :
                    LOGNAME + (WINDOWID | _ )   * masing2 di ambil 1 kata (bebas ambil kata pertama atau terakhir) 
                                                  sehingga menjadi 2 kata saja + .env di kata awalnya
                WINDOWS :
                    LOGONSERVER + (HOMEPATH | USERNAME )    * sama seperti di linux
            3. cek file dengan nama di atas, jika ada langsung execute
               Load From File ...
               Jika tidak ada maka tampilkan di interface "File Yang Di Cari Tidak Di Temukan"            

            4. keyword_local tidak di perlukan lagi
            5. cek semua kemungkinan variabel environment dari prioritas 1 sampai akhir, tampilkan di interface
            6. File ini yang harus di penuhi oleh programmer untuk dapat melanjutkan aplikasi
    '''

    keyword_local = []              # keyword must be only exist in local, if not assumtion script run in server
    # keyword_server = []             # agar bisa setting server 1 dan server 2 berbeda

    # PS1 for environmnet linux
    # VENV for environment windows
    # env_list = ['PS1', 'VENV', 'PYENV_VERSION'] # os.environ.get("PS1") --> list of environment
    env_list = ['VENV2'] # os.environ.get("PS1") --> list of environment

    # scan semua variable ini dan tampilkan semua hasilnya ke interface
    env_variable = ['LOGNAME', 'WINDOWID', '_', 'LOGONSERVER', 'HOMEPATH', 'USERNAME']

    # env_local = '.env.local'        # environment name local    (DELETE pending)
    # env_server = '.env.server'      # environment name server   (DELETE pending)
    env_name = '.env'               # + keyword_local (after string replace all symbol to _)
    BASE_DIR = ''
    DEBUG = True                    # get settings DEBUG Variable

    # constructor
    def __init__(self, base_dir=None):
        # self.keyword_local = ['env_opd'] # lets empty (for remainder user to insert keywordlocal)
        # self.keyword_server = ['env_opd', 'outbox', 'env_outbox']
        self.DEBUG = getattr(settings, "DEBUG", True)

        if not base_dir:
            self.BASE_DIR = Path(__file__).resolve().parent.parent
        else:
            self.BASE_DIR = base_dir
        # pass        
    
    def bytes2hex(self, bytes_text):
        res_hex = binascii.hexlify(bytes_text)
        return res_hex.decode()

    def hex2bytes(self, hex_text):
        res_bytes = binascii.unhexlify(hex_text)
        return res_bytes    # return in bytes format

    def generate_key(self):
        # save key to file
        return Fernet.generate_key()
    
    def encrypt(self, plain_text, key):
        # key created using generate_key()
        f = Fernet(key)

        # the plain_text is converted to ciphertext
        return f.encrypt(plain_text)

    def decrypt(self, cipher_text, key):
        # Load existing key
        f = Fernet(key)
        
        # the ciphertext converted to plain_text
        return f.decrypt(cipher_text)

    def clear_keyword_local(self):    # Untuk create env file lainnya
        self.keyword_local.clear()

    def set_keyword_local(self, keyword):
        '''
            Update keyword sesuai project, misal :
            env_opd
            env_outbox
        '''
        # keyword = keyword.replace('-','_') # pindah ke pada saat create file
        # keyword = keyword.replace(':','_')
        # keyword = keyword.replace('.','_')
        self.keyword_local.append(keyword)

    def create_env_file(self, file_path):
        if not Path(file_path).is_file():
            with open(file_path, "w") as f:
                f.write('\n') 
                f.close()

            if Path(file_path).is_file():
                print('File is created')
            else:
                raise Exception("Fail create directory!")
                # print('Fail create!')
        # else:
        #     print('Fail updated!')

    def string_replace(self, keyword):
        res = keyword.replace('-','_')
        res = res.replace(':','_')
        res = res.replace('.','_')
        res = res.replace('/','_') # baru untuk versi 3.8 Python
        return res

    def string_replace_env(self, keyword):
        res = keyword.replace('(','')
        res = res.replace(')','')        
        res = res.replace('/','_')        
        return res.strip()

    def encrypt_environ(self, plain_text):
        '''
            Write directly to environment file
            plain_text in dictionary format :
                # {db_password: 123},
                {secret_key: &#^@#&^$^}
                # {etc: etc..}
        '''
        if not self.keyword_local:
            # print("Please set keyword_local fisrt!")
            raise Exception("Please set keyword_local fisrt!")
        else:
            
            file_path  = []
            
            # 1. Read ALL data
            for i in range(len(self.keyword_local)):                
                tmp = self.env_name + '.' + self.string_replace(self.keyword_local[i])
                file_path.append(os.path.join(self.BASE_DIR, tmp))
                # print('file_path =', file_path, Path(file_path).is_file())
                print('file_path[i]=', file_path[i])
                # create file if not exists
                self.create_env_file(file_path[i])
                

                # # create file if not exists
                # if not Path(file_path).is_file():
                #     with open(file_path, "w") as f:
                #         f.write('\n') 
                #         f.close()

                #     if Path(file_path).is_file():
                #         print('File is created')
                #     else:
                #         print('Fail create!')
                # else:
                #     print('Fail updated!')

            # print(file_path)
            for j in range(len(file_path)):
                dict1 = {}                

                with open(file_path[j], "r") as f:
                    for line in f.readlines():                
                        values = line.split('=')
                        if len(values) > 1:                    
                            dict1[values[0]] = values[1]
                    f.close()
                        
                
                # 2. Encrypt data        
                key = self.generate_key()
                # print(key)
                key_in_hex = self.bytes2hex(key)
                # print(key_in_hex)

                # get key, value from parameter (plain_text)
                values = list(plain_text.values())        
                keys = list(plain_text.keys())

                # Khusus data yg di enkripsi aja (simpan di parameter plain_text)
                # data yg tidak di enkripsi seperti debug=True dll, di tulis manual
                enc = []
                enc_in_hex = []
                for i in range(len(keys)):
                    tmp = self.encrypt(values[i].encode(), key)
                    enc.append(tmp)
                    enc_in_hex.append(self.bytes2hex(tmp))

                # 3. Update Data        
                # dict1['DB_USER'] = '123\n'
                for i in range(len(keys)):
                    dict1[keys[i]] = enc_in_hex[i]

                dict1['DB_KEY'] = key_in_hex

                # 4. Write Back Data        
                values = list(dict1.values())        
                keys = list(dict1.keys())

                with open(file_path[j], "w") as f:
                    # tulis ulang DB_KEY (Penambahan ada di dict1)           
                    # f.write('DB_KEY' + '=' + key_in_hex + '\n')
                    
                    # tulis ulang DB_PASSWORD, SECRET_KEY
                    for i in range(len(keys)):
                        if '\n' in values[i]:
                            f.write(keys[i] + '=' + values[i])
                        else:
                            f.write(keys[i] + '=' + values[i] + '\n') 

                    f.close()

                print('File is create on :', file_path[j])
                    
    def decrypt_environ(self, mplaint_key, mplaint_list=[], mplaint_tuple=[]): #, env_name, cipher_text, key_hex):
        '''        
            Read directly from environment file
            cipher_text and key_hex, in hexadecimal format            
        '''
        # text = self.hex2bytes(cipher_text)
        # key = self.hex2bytes(key_hex)
        # BASE_DIR = Path(__file__).resolve().parent.parent

        # env_list = os.environ.get(self.env_list)
        if not self.keyword_local:
            # print("Please set keyword_local fisrt!")
            raise Exception("Please set keyword_local fisrt!")
            # Fail create!
        else:
            
            file_path  = []
            find_env_name = [] 

            # 1. Read ALL data
            for i in range(len(self.keyword_local)):                
                find_env_name.append(self.string_replace(self.keyword_local[i]))
                tmp = self.env_name + '.' + find_env_name[i]
                
                print('find_env_name = ' , tmp)
                print('path lengkap=', os.path.join(self.BASE_DIR, tmp))

                file_path.append(os.path.join(self.BASE_DIR, tmp))
                # print('file_path =', file_path, Path(file_path).is_file())
                
                print('create file if not exists', file_path[i])
                # create file if not exists
                self.create_env_file(file_path[i])

            # print('file_path = ',file_path)

            # Baca data dari variable ENV, jika ketemu data dari list (keyword_local) maka load data dari file itu
            print('self.env_list=',self.env_list)
            for j in range(len(self.env_list)):   
                env_list_split = []
                env_list_split2 = [] # karena ada tag pembuka dan penutup, maka split 2 kali

                print('proses ', self.env_list[j])
                env_list = os.getenv(self.env_list[j]) # PS1 atau VENV
                print('env_list=',env_list)
                # env_list = os.environ.get(self.env_list[j]) # PS1 atau VENV
                # print('env_list=',env_list)
                is_found = False
                file_path_idx = 0

                # test
                # env_list = 'outbox'
                # env_list = "(\[\033[0;34m\]django-outbox-dev\[\033[0;0m\]) \[\033[0;31m\]✘-127\[\033[0;0m\] \[\033[0;33m\]\w\[\033[0;0m\] [\[\033[0;35m\]${GIT_BRANCH}\[\033[0;0m\]|\[\033[0;34m\]✚ 44\[\033[0;0m\]\[\033[0;36m\]…7\[\033[0;0m\]\[\033[0;0m\]] \n\[\033[0;37m\]$(date +%H:%M)\[\033[0;0m\] $"
                # env_list = '((outbox:3.10)) '
                # env_list = "(env_outbox) \[\033[0;37m\]$(date +%H:%M) \w\[\033[0;33m\] $(parse_git_branch)\[\033[1;32m\]$ \[\033[0;37m\]"
                if env_list:
                    env_list_split = env_list.split('\[')
                    for i in env_list_split:
                        for k in i.split('\]'):
                            env_list_split2.append(self.string_replace_env(k))  # clear tanda (()) di dalam env


                # env_list_split2 jadi kunci
                #  akan di komprare dengan data env real di server dengan karekter (()) replace menjadi spasi kosong
                # dan karakter / di replace menjadi _
                # print('env_list_split2',env_list_split2)

                # create file if not exists        
                # create sebelum dibaca oleh RepositoryEnv di path tersebut jika tidak ada file maka akan muncul error
                # file_path = self.BASE_DIR / self.env_local
                # if not Path(file_path).is_file():
                #     with open(file_path, "w") as f:
                #         f.write('\n') 
                #         f.close()               

                #     if Path(file_path).is_file(): 
                #         print('File is created')
                #     else:
                #         print('Fail create!')
                # # else:
                # #     print('Fail updated!')

                # file_path = self.BASE_DIR / self.env_server
                # if not Path(file_path).is_file():
                #     with open(file_path, "w") as f:
                #         f.write('\n') 
                #         f.close()

                #     if Path(file_path).is_file(): 
                #         print('File is created')
                #     else:
                #         print('Fail create!')

                    # print('File is created')

                # print('self.keyword_local = ' , self.keyword_local)
                # print('env_list = ', env_list)
                if env_list:
                    file_path_idx = -1
                    for i in self.keyword_local:
                        print('keyword_local=',i)
                        print('data=', env_list_split2)
                        file_path_idx += 1
                        if i in env_list_split2:
                            # env_config = Config(RepositoryEnv(self.BASE_DIR / self.env_local))
                            # print('file_path[i] = ', file_path_idx, file_path[file_path_idx])

                            env_config = Config(RepositoryEnv(file_path[file_path_idx]))
                            # file_path = os.path.join(self.BASE_DIR, self.env_local)
                            print('Load setting from ' + self.keyword_local[file_path_idx])
                            
                            is_found = True
                            # print('FOUND!!!!')
                            break

                # if is_run_from_server:
                #     env_config = Config(RepositoryEnv(file_path[i]))
                #     # file_path = os.path.join(self.BASE_DIR, self.env_server)
                #     print('Load setting from ' + self.keyword_local[i])
                

                # print('File is load from :', file_path)
                # Get ALL env_config data

                if is_found:
                    dict1 = {}        
                    with open(file_path[file_path_idx], "r") as f:
                        for line in f.readlines():                
                            values = line.split('=')
                            if len(values) > 1:                    
                                dict1[values[0]] = values[1].replace('\n','')
                        f.close()

                    # print(dict1)
                    keys = list(dict1.keys())
                    values = list(dict1.values())
                    # print(keys)

                    # decrypt DB_KEY
                    # dapatkan key dulu untuk proses decrypt yg lain
                    tmp_keys = ''
                    for i in range (len(keys)):        
                        if keys[i]=='DB_KEY':                
                            tmp_keys = self.hex2bytes(values[i])                
                            # dict1[keys[i]] = tmp_keys # key tetap rahasia, jangan disimpan di dict
                            break

                    for i in range (len(keys)):        
                        if keys[i] in mplaint_key:  # khusus tipe data enkripsi
                            tmp = self.hex2bytes(values[i])
                            tmp = self.decrypt(tmp, tmp_keys).decode()
                            # print(keys[i], tmp)                
                            dict1[keys[i]] = tmp

                        elif keys[i] in mplaint_list:   # khusus tipe data list
                            # dict1[keys[i]] = env_config(keys[i], cast=lambda v: [s.strip() for s in v.split(',')])
                            dict1[keys[i]] = env_config(keys[i], cast=Csv())

                        elif keys[i] in mplaint_tuple:   # khusus tipe data tuple
                            # contoh di environment : os.environ['SECURE_PROXY_SSL_HEADER'] = 'HTTP_X_FORWARDED_PROTO, https'
                            # proses casting : config('SECURE_PROXY_SSL_HEADER', cast=Csv(post_process=tuple))  <--
                            # ('HTTP_X_FORWARDED_PROTO', 'https')
                            
                            dict1[keys[i]] = env_config(keys[i], cast=Csv(post_process=tuple))

                        else:                           # konversi sesuai tipe data python standart
                            # print(keys[i], values[i])
                            #dict1[keys[i]] = values[i]
                            # Ambil sesuai tipe data
                            if values[i] in ['True', 'False']:
                                dict1[keys[i]] = env_config(keys[i], default=True, cast=bool)
                            elif values[i].isnumeric():
                                dict1[keys[i]] = env_config(keys[i], default=0, cast=int)

                        # selain kondisi di atas, biarkan apa adanya (default = string)

                    # print('hasilnya = ', dict1)
                    return dict1
                else:
                    print('Activate environment first!')
                    # raise Exception("Please set keyword_local fisrt!")
    
    # ----- UPDATE NEW RULE -----

    def remove_empty_data_array(self, data_array):
        i=0
        while i<len(data_array):
            if data_array[i].strip() == '':
                data_array.pop(i)
            else:
                i+=1                
        return data_array
    

    def remove_duplicate_data_array(self, data_array):                
        i=0 
        while i<len(data_array)-1:
            j=i+1
            while j<len(data_array):
                if data_array[i].lower() == data_array[j].lower():
                    data_array.pop(j)

                j+=1
            i+=1

        return data_array


    def split_from_multiple_word(self, data, split_word):
        '''
            split char, in array
        '''
        # replace dulu semua karakter di split_word dengan karakter _, kemudian split karakter _ tersebut
        #         
        for i in enumerate(split_word):
            data = data.replace(i[1], '_') # i[0] = index; i[1] = data

        # result
        tmp = data.split('_')       
        if self.DEBUG:
            print('Split', tmp)

        # remove empty data
        tmp = self.remove_empty_data_array(tmp)
        if self.DEBUG:
            print('Remove empty array', tmp)

        # remove duplicate word
        tmp = self.remove_duplicate_data_array(tmp)
        if self.DEBUG:
            print('Remove duplicate array', tmp)

        return tmp


    def scan_environment_variable(self):
        res = '.env'                                        # jika semua kosong, maka paling tidak file .env harus ada
        for i in range(len(self.env_variable)):   
            if self.DEBUG:
                print('Proses env_variable -', str(i+1), self.env_variable[i])

            split_char = ['/', ' ', ':', '\\', '.']
            tmp = os.getenv(self.env_variable[i]) 

            tmp_arr = None
            if tmp:                                
                tmp_arr = self.split_from_multiple_word(tmp, split_char)
            
            if tmp_arr:                
                if len(tmp_arr)>=3:
                    res += '-' + tmp_arr[2]               # ambil index ke tiga biasanya /home/iwan/.virtualenv (index ke tiga ini biasanya uniq)
                else:
                    res += '-' + tmp_arr[len(tmp_arr)-1]  # ambil index terakhir

        if self.DEBUG:
            print('result:', res)

        return res     

    def enc_environ(self, plain_text):
        # # mplaint_text = {
        # #     'DB_PASSWORD': 'password untuk koneksi ke database',
        # #     'SECRET_KEY': 'secret key yg ada di setting.py'
        # # }

        # Result akan bernama filename sesuai environment yg aktif
        # segera rename dengan filename yg di butuhkan oleh komputer target
        file_name = self.scan_environment_variable()
        file_path = os.path.join(self.BASE_DIR, file_name)
        if self.DEBUG:
            print('file_path', file_path)

        dict1 = {}      
        # open file, create if not exists          
        with open(file_path, "w+") as f:
            # for line in f.readlines():                
            #     values = line.split('=')
            #     if len(values) > 1:                    
            #         dict1[values[0]] = values[1]
            f.close()

        # if self.DEBUG:
        #     print('file_path value', dict1)
            
        
        # 2. Encrypt data        
        key = self.generate_key()        
        # if self.DEBUG:
        #     print('Enc - Key ', key)

        key_in_hex = self.bytes2hex(key)
        if self.DEBUG:
            print('Enc - Key in hex ', key_in_hex)

        # get key, value from parameter (plain_text)
        values = list(plain_text.values())        
        if self.DEBUG:
            print('Plain text value ', values)

        keys = list(plain_text.keys())
        if self.DEBUG:
            print('Plain text keys ', keys)

        # Khusus data yg di enkripsi aja (simpan di parameter plain_text)
        # data yg tidak di enkripsi seperti debug=True dll, di tulis manual
        enc = []
        enc_in_hex = []
        for i in range(len(values)):
            tmp = self.encrypt(values[i].encode(), key)
            enc.append(tmp)
            enc_in_hex.append(self.bytes2hex(tmp))

        # 3. Update Data        
        # dict1['DB_USER'] = '123\n'
        for i in range(len(keys)):
            dict1[keys[i]] = enc_in_hex[i]

        dict1['DB_KEY'] = key_in_hex
        if self.DEBUG:
            print('dict1', dict1)

        # 4. Write Back Data        
        values = list(dict1.values())        
        keys = list(dict1.keys())

        with open(file_path, "w+") as f:
            # tulis ulang DB_KEY (Penambahan ada di dict1)           
            # f.write('DB_KEY' + '=' + key_in_hex + '\n')
            f.write('# Environment file, create using outbox-encryption library \n')
            f.write('# > pip install outbox-encryption \n')
            f.write('\n')
            f.write('# Setting section (change manually) :\n')
            f.write('# -----------------------------------\n')                    
            f.write('DEBUG=True \n')
            f.write('UNDER_CONSTRUCTION=False \n')

            f.write('\n')
            f.write('# Change between mysql or sqlite3 \n')
            f.write('DB_ENGINE=django.db.backends.mysql \n')
            f.write('#DB_ENGINE=django.db.backends.sqlite3 \n')
            
            f.write('\n')
            f.write('# Change to full path, if using sqlite3 \n')
            f.write('DB_NAME=db_outbox \n')
            f.write('#DB_NAME=/home/db_outbox.sqlite3 \n')

            f.write('\n')
            f.write('# This setting, ignored when use sqlite3 \n')
            f.write('DB_USER=root \n')
            f.write('DB_HOST=127.0.0.1 \n')
            f.write('DB_PORT=3306 \n')

            f.write('\n')
            f.write('# All allowed host, separate with comma \n')
            f.write('ALLOWED_HOSTS=127.0.0.1, localhost \n')
            
            f.write('\n')
            f.write('# Optional Static and media (change on vhost too) \n')
            f.write('STATIC_ROOT=/home/u10xxx/public_html/static/ \n')
            f.write('MEDIA_ROOT=/home/u1578244/public_html/media/ \n')
        
            f.write('\n')
            f.write('# Optional for django >4.0 separate with comma \n')
            f.write('CSRF_TRUSTED_ORIGINS=https://domain-example.com, https://*.subdomain.com  \n')


            f.write('\n')
            f.write('# Encrypt section :\n')
            f.write('# -----------------\n')

            # tulis ulang DB_PASSWORD, SECRET_KEY
            for i in range(len(keys)):
                if '\n' in values[i]:
                    f.write(keys[i] + '=' + values[i])
                else:
                    f.write(keys[i] + '=' + values[i] + '\n') 

            f.write('\n')
            f.write('# End of file \n')
            f.close()

        print('File is create on :', file_path)

    def dec_environ(self, mplaint_key, mplaint_list=[], mplaint_tuple=[]): #, env_name, cipher_text, key_hex):
        '''        
            Cari file sesuai hasil scan_environment_variable()
            Jika tidak maka tidak dapat melanjutkan aplikasi
        '''

        file_name = self.scan_environment_variable()
        file_path = os.path.join(self.BASE_DIR, file_name)
        if self.DEBUG:
            print('file_path', file_path)

        if not Path(file_path).is_file():
            # mode non DEBUG juga munculin pesan ini
            print('File is not exists', file_path)
        else:

            env_config = Config(RepositoryEnv(file_path))            
            print('Load setting from ' + file_name)
            
            dict1 = {}        
            with open(file_path, "r") as f:
                for line in f.readlines():                
                    values = line.split('=')
                    if len(values) > 1:                    
                        if values[0][:1] != '#':
                            dict1[values[0]] = values[1].replace('\n','').strip()
                f.close()
            
            keys = list(dict1.keys())
            values = list(dict1.values())

            if self.DEBUG:
                print('keys', keys)
                print('values', values)


            # decrypt DB_KEY
            # dapatkan key dulu untuk proses decrypt yg lain
            tmp_keys = ''
            for i in range (len(keys)):        
                if keys[i]=='DB_KEY':                
                    tmp_keys = self.hex2bytes(values[i])                                    
                    break

            for i in range (len(keys)):        
                if keys[i] in mplaint_key:  # khusus tipe data enkripsi
                    tmp = self.hex2bytes(values[i])
                    tmp = self.decrypt(tmp, tmp_keys).decode()                    
                    dict1[keys[i]] = tmp

                elif keys[i] in mplaint_list:   # khusus tipe data list
                    # dict1[keys[i]] = env_config(keys[i], cast=lambda v: [s.strip() for s in v.split(',')])
                    dict1[keys[i]] = env_config(keys[i], cast=Csv())

                elif keys[i] in mplaint_tuple:   # khusus tipe data tuple
                    # contoh di environment : os.environ['SECURE_PROXY_SSL_HEADER'] = 'HTTP_X_FORWARDED_PROTO, https'
                    # proses casting : config('SECURE_PROXY_SSL_HEADER', cast=Csv(post_process=tuple))  <--
                    # ('HTTP_X_FORWARDED_PROTO', 'https')
                    
                    dict1[keys[i]] = env_config(keys[i], cast=Csv(post_process=tuple))

                else:                           # konversi sesuai tipe data python standart
                    # print(keys[i], values[i])
                    #dict1[keys[i]] = values[i]
                    # Ambil sesuai tipe data
                    if values[i] in ['True', 'False']:
                        dict1[keys[i]] = env_config(keys[i], default=True, cast=bool)
                    elif values[i].isnumeric():
                        dict1[keys[i]] = env_config(keys[i], default=0, cast=int)

                # selain kondisi di atas, biarkan apa adanya (default = string)

            if self.DEBUG:
                print('result', dict1)

            return dict1
               

# test module level
if __name__=='__main__':
    # print('Begin Test ENCRYPTION')
    # print('---------------------')
    # secret_text = input("Input Secret Text: ")    

    lib = OutboxEncryption()
    # key = lib.generate_key()    

    # # Out key in hexadecimal format
    # key = lib.bytes2hex(key)
    # print('Key:', key)
    
    # res_enc = lib.encrypt(secret_text.encode(), lib.hex2bytes(key))

    # # Out in hexadecimal
    # res_enc = lib.bytes2hex(res_enc)
    # print('Encrypt result:', res_enc)

    # print('')
    # print('Begin Test DECRYPTION')
    # print('---------------------')
    
    # res_dec = lib.decrypt(lib.hex2bytes(res_enc), lib.hex2bytes(key))
    # print('Decrypt result:', res_dec.decode())
    # print('')
    
    ## versi 1
    # print('')
    # print('Encrypt to Environment')
    # print('----------------------')
    # # BASE_DIR = Path(__file__).resolve().parent.parent
    # # print(BASE_DIR)

    # # mplaint_text = {
    # #     'DB_PASSWORD': 'password untuk koneksi ke database',
    # #     'SECRET_KEY': 'secret key yg ada di setting.py'
    # # }

    # mplaint_text = {
    #     'DB_PASSWORD': '',
    #     'SECRET_KEY': 'xxg_7me8rl2m#a_h2oresgt2#ni=3_4*!ai*=rtsq)yi!g7_5-51xx'
    # }
    # lib.set_keyword_local('django-outbox-dev')      # iwan
    # lib.set_keyword_local('outbox')                 # dony
    # lib.set_keyword_local('env_outbox')             # python anywhere
    # lib.set_keyword_local('outbox:3.10')            # niaga hoster


    # lib.encrypt_environ(mplaint_text)
    # print('Show Hidden File to Show .env.local')


    # # print('')
    # # print('Decrypt From Environment')
    # # print('----------------------')
    # # # agar bisa mendeteksi environment local
    # # lib.set_keyword_local('django-outbox-dev')

    # # kunci yg di buka khusus, karena ada proses enkripsi
    # # selain kunci ini, langsung ambil datanya, tipe data string

    # # mplaint_key = list(mplaint_text.keys())
    # mplaint_list = ['localhost:8000', '127.0.0.1:8000']    # daftar tipe data list (cara konversinya khsusus)
    # # mplaint_tuple = ['SECURE_PROXY_SSL_HEADER']

    # # mplaint_key = [
    # #     'DB_PASSWORD', 'SECRET_KEY'
    # # ]

    # lib.decrypt_environ(mplaint_text, mplaint_list)
    # print('Decrypt Finish')

    # versi 2
    # -------
    # data = 'c:/var/lib/www data/testing/contoh \\var lib'
    # split_char = ['/', ' ', ':', '\\']
    # lib.split_from_multiple_word(data, split_char)

    # file_name = lib.scan_environment_variable()
    # print ('This file must be exists', file_name)

    # UPDATE HELP file with this example
    # 1. test enc:
    # mplaint_text = {
    #     'DB_PASSWORD': '',
    #     'SECRET_KEY': 'xxg_7me8rl2m#a_h2oresgt2#ni=3_4*!ai*=rtsq)yi!g7_5-51xx'
    # }
    # lib.enc_environ(mplaint_text)

    # 2. test dec:
    mplaint_key = {
        'DB_PASSWORD',
        'SECRET_KEY'
    }
    mplaint_list = {
        'ALLOWED_HOSTS',
        'CSRF_TRUSTED_ORIGINS'
    }
    key = lib.dec_environ(mplaint_key, mplaint_list)

    # 3. settings.py
    # SECRET_KEY = key['SECRET_KEY']
    # DEBUG = key['DEBUG']
    # UNDER_CONSTRUCTION = key['UNDER_CONSTRUCTION']
    # ALLOWED_HOSTS = key['ALLOWED_HOSTS']
    
    # Optional:
    # tmp = key.get('CSRF_TRUSTED_ORIGINS') 
    # if tmp:
    #   CSRF_TRUSTED_ORIGINS=key['CSRF_TRUSTED_ORIGINS']

    # tmp_engine = key['DB_ENGINE']
    # if 'sqlite3' in tmp_engine:
    #     DATABASES = {
    #         'default': {
    #             'ENGINE': tmp_engine,                
    #             'NAME': key['DB_NAME'],   # Path lengkap
    #         }
    #     }
    # else: # default 
    #     DATABASES = {
    #         'default': {
    #             'ENGINE'    : key['DB_ENGINE'],
    #             'NAME'      : key['DB_NAME'],
    #             'USER'      : key['DB_USER'],
    #             'PASSWORD'  : key['DB_PASSWORD'],
    #             'HOST'      : key['DB_HOST'],
    #             'PORT'      : key['DB_PORT'],
    #         }
    #     }

    # # use default value if setting not exists
    # tmp = key.get('STATIC_ROOT')  # True if exists, None if not exists
    # STATIC_ROOT = key['STATIC_ROOT'] if tmp else os.path.join(BASE_DIR, 'staticfiles')

    # tmp = key.get('MEDIA_ROOT')
    # MEDIA_ROOT = key['MEDIA_ROOT'] if tmp else os.path.join(BASE_DIR, 'media')
