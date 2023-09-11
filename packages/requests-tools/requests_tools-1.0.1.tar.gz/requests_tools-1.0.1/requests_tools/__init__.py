import os
import sys
import time
import pickle
import platform
import requests
import colorama
import threading
import subprocess
from tqdm import tqdm
colorama.init()

_HOST = ""
download_list = {}

class Downloader(object):
    def __init__(self,url,zips):
        self.url = url
        self.zips = zips
        self.path = "storage/emulated/0/Download/RayServer/"
    def sizeof_fmt(self,num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.2f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.2f%s%s" % (num, 'Yi', suffix)
    def make_session(self,new=False):
        global _HOST
        dir = self.path
        if new:
            sp = open(dir+'.s.pkl','wb')
            try:
                r = requests.get("http://apiserver.alwaysdata.net/new")
            except:
                r = requests.get("http://apiserver.alwaysdata.net/new")
            for i in r.iter_content(1024*1024):
                sp.write(i)
            sp.close()
        if not os.path.exists(dir+'.s.pkl'):
            self.make_session(new=True)
        with open(dir+'.s.pkl','rb') as f:
            s = pickle.load(f)
            _HOST = "https://"+str(s.cookies).split("ielax=true for ",1)[1].split("/>")[0]+"/"
            return s
    def update_download(self,filename,part,total):
        m = f"> Descargado {self.sizeof_fmt(part)} de {self.sizeof_fmt(total)}"
        print(m, end="\r")
    def download_part(self,start_byte, end_byte, part_num,session,url,filename,filesize):
        try:
            headers = {'Range': f'bytes={start_byte}-{end_byte}'}
            resp = session.get(url, headers=headers, stream=True)
            with open(f'{self.path}.{filename}_part{part_num}', 'wb') as f:
                for chunk in resp.iter_content(1024*512):
                    f.write(chunk)
                    download_list[filename]+=len(chunk)
                    self.update_download(filename, download_list[filename], filesize)
        except Exception as ex:
            print(str(ex))
    def _download_file(self):
        global _HOST
        num_parts = self.zips
        dat = str(self.url).split(".dl/")[1].split("/")
        filename = dat[2]
        uid = dat[2]
        filesize = int(dat[0])
        download_list[filename] = 0
        print("> "+filename)
        session = self.make_session()
        furl = f"{_HOST}remote.php/dav/uploads/A875BE09-18E1-4C95-9B84-DD924D2781B7/web-file-upload-{uid}/.file"
        part_size = filesize // num_parts
        ranges = [(i * part_size, (i + 1) * part_size - 1) for i in range(num_parts)]
        threads = []
        for i, (start, end) in enumerate(ranges):
            thread = threading.Thread(target=self.download_part, args=(start, end, i+1,session,furl,filename,filesize))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        with open(self.path+filename, 'wb') as f:
            download_list.pop(filename)
            print("Contruyendo archivo", end="\r")
            for i in range(num_parts):
                n = f'{self.path}.{filename}_part{i+1}'
                with open(n, 'rb') as part_file:
                    f.write(part_file.read())
                os.unlink(n)
        print(colorama.Fore.GREEN+"[SUCCESS] -- Completed|Completado")
        print(colorama.Style.RESET_ALL+"")
        main()
    def vdownload(self):
        if platform.system() == 'Windows':
            self.path = "RayServer/"
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        if "rayserver.dl/" in self.url:
            if platform.system()=="Linux":
                subprocess.call("clear", shell=True)
            if platform.system()=="Windows":
                subprocess.call("cls", shell=True)
            thread = threading.Thread(target=self._download_file)
            thread.start()

def input_download():
    if platform.system()=="Linux":
        subprocess.call("clear", shell=True)
    if platform.system()=="Windows":
        subprocess.call("cls", shell=True)
    url = input("Ingrese un enlace: ")
    zips = input("Ingrese el número de hilos (1-5) ")
    if int(zips)<1 or int(zips)>5:
        print(colorama.Fore.RED+"El valor de los hilos debe ser entre 1 y 5")
        zips = input("Ingrese el número de hilos (1-5) ")
        if int(zips)<1 or int(zips)>5:
            print(colorama.Fore.RED+"[ERROR] El valor de los hilos debe ser entre 1 y 5")
            sys.exit()
    else:
        cli = Downloader(url,int(zips))
        cli.vdownload()
def main():
    print(colorama.Fore.YELLOW+"Bienvenido a RayServer.CLI")
    print(colorama.Style.RESET_ALL+"")
    print("> 1 Descargar un enlace")
    print("> 2 Reiniciar Servidor")
    print("> 3 Obtener Información")
    print("> 4 Exit|Salir")
    value = input("Seleccione una obción (1-3) ")
    if value=="1":
        input_download()
    elif value=="2":
        if platform.system()=="Linux":
            subprocess.call("clear", shell=True)
        if platform.system()=="Windows":
            subprocess.call("cls", shell=True)
        print("Reiniciando...", end="\r")
        path = "storage/emulated/0/Download/RayServer/"
        if platform.system() == 'Windows':
            path = "RayServer/"
        if not os.path.exists(path):
            os.mkdir(path)
        try:
            r=requests.get("http://apiserver.alwaysdata.net/new")
        except:
            r=requests.get("http://apiserver.alwaysdata.net/new")
        sp=open(path+'.s.pkl','wb')
        for i in r.iter_content(1024*1024):
            sp.write(i)
        sp.close()
        print(colorama.Fore.GREEN+"[SUCCESS] Reiniciando")
        print(colorama.Style.RESET_ALL+"")
        main()
    elif value=="3":
        if platform.system()=="Linux":
            subprocess.call("clear", shell=True)
        if platform.system()=="Windows":
            subprocess.call("cls", shell=True)
        print(colorama.Fore.YELLOW+"Este es un servicio complementario de la cadena RayServer DL mediante el cual podrá descargar los enlaces proveniente de nuestros servicios")
        print("")
        print("Propietario https://t.me/raydel0307")
        print(colorama.Style.RESET_ALL+"")
        main()
    elif value=="4":
        if platform.system()=="Linux":
            subprocess.call("clear", shell=True)
        if platform.system()=="Windows":
            subprocess.call("cls", shell=True)
        print(colorama.Fore.YELLOW+"GRACIAS POR USAR RAYSERL.CLI")
        sys.exit()
main()