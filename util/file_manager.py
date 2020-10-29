import os
class FileManager:
    def __init__(self,directory=None):
        if directory is None:
            self.dir = os.path.join(os.getcwd(),"graph_store")
        else:
            self.dir = directory


    def read(self,filename):
        with open(filename, 'r') as file:
            contents = file.read().replace('\n', '')
        return contents

    def write(self,filename,content):
        filename = os.path.join(self.dir,filename)
        f = open(filename,"a+")
        if isinstance(content,list):
            for l in content:
                f.write(l + "\n")
        else:
            f.write(content)
        f.close()

    def delete(self):
        pass
    
    def generate_filename(self,fn):
        filename = os.path.join(self.dir,fn)
        fn,ft = filename.split(".")
        if fn[-1].isdigit():
            count = int(fn[-1]) + 1
            fn = "".join(fn[:-2])
        else:
            count = 1
        
        while os.path.isfile(filename):
            filename = fn + "_" + str(count) + "." + ft 
            count = count + 1
        return filename