import os
import pickle

if __name__ == "__main__":
	module_path = os.path.abspath(os.curdir)
	id_dict = {}
	txt_file = open(module_path + "/doc/stockid_name.txt", "r", encoding='UTF-8')
	while(True):
		file_line = txt_file.readline()
		file_line = file_line.replace('\n', '')
		file_line = file_line.replace('\r', '')
		file_line = file_line.replace('*', '')

		if (len(file_line) == 0):
			break
		line = file_line.split("\t")
		id_dict[line[0]] = line[1]

	pickle.dump(id_dict, open(module_path+"/bin/dict.bin", "wb"))
