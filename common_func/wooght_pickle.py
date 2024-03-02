# coding=utf-8
# @Explain  : 数据序列化
# @Author   : wooght
# @File     : linkmart apis
# @Time     : 2021/01/15 上午午09:40


import pickle


class wooght_pickle:
    def __init__(self, file_dir):
        self.file_dir = file_dir        # 文件路径
        self.exists = False             # 文件是否存在
        self.load_data = object         # load的文件内容
        self.file_exists()

    def file_exists(self, file_dir=None):
        if not file_dir:
            try:
                fr = open(self.file_dir, 'rb')
                fr.close()
                self.exists = True
            except:
                self.exists = False

    def load(self):
        fr = open(self.file_dir, 'rb')
        self.load_data = pickle.load(fr)
        fr.close()
        return self.load_data

    def dump(self, write_data):
        fw = open(self.file_dir, 'wb')
        pickle.dump(write_data, fw)
        fw.close()
        return True

