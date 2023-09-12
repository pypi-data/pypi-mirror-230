import os
import sys


class FileUtil:

    # 获取工程root地址
    @staticmethod
    def getProjectRootPath():
        rootPath = None
        # 判断调试模式
        debug_vars = dict((a, b) for a, b in os.environ.items()
                          if a.find('IPYTHONENABLE') >= 0)
        # 根据不同场景获取根目录
        if len(debug_vars) > 0:
            """当前为debug运行时"""
            rootPath = sys.path[2]
        elif getattr(sys, 'frozen', False):
            """当前为exe运行时"""
            rootPath = os.getcwd()
        else:
            """正常执行"""
            rootPath = sys.path[1]

        return  rootPath

    # 获取文件中的单行数据
    @staticmethod
    def readLines(fileName):
        lineDatas = []

        if os.path.exists(fileName):
            f = open(fileName, "r")
            line = f.readline()
            while line:
                line = line.replace('\n', '').replace('\r', '')
                lineDatas.append(line)
                line = f.readline()

            f.close()

        return lineDatas

    # 按行写入excel数据
    @staticmethod
    def writeLines(fileName,lineDatas):
        with open(fileName, "a") as file:
            for lineData in lineDatas:
                file.write(lineData + "\n")
