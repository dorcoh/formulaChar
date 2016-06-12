import os, shutil
folder = os.getcwd() + 'output'
files = os.listdir(folder)
for the_file in files:
    file_path = os.path.join(folder, the_file)
    try:
        if os.path.isfile(file_path):
            os.unlink(file_path)
        #elif os.path.isdir(file_path): shutil.rmtree(file_path)
    except Exception, e:
        print e