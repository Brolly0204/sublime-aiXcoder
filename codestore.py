instance = None

CHECK_LENGTH = 800  # 最多检查的字符数量
REDUNDANCY_LENGTH = 10


class CodeStore:
    "保存上一次给服务器发送的代码，服务器会维护一份一样的数据。 通过比较保存的数据和即将发送的数据，CodeStore避免发送相同的代码前缀部分，减少网络传输"

    @staticmethod
    def getInstance():
        global instance
        if instance is None:
            instance = CodeStore()
        return instance

    def __init__(self):
        self.project = ""  # 上次的项目，每次打开新项目的时候清空
        self.store = {}  # 当前项目各个文件的缓存情况

    def getDiffPosition(self, fileID, content):
        """获得即将发送内容和上次发送内容开始不同的下标，只发送下标往后的部分，下标本身作为offset参数发送
        fileID  文件id
        content 文件内容
        内容开始不同的下标"""
        i = 0
        if fileID in self.store:
            lastSent = self.store[fileID]
            # lastSent: 1000 -> [201: 1000]
            # content: 1010 -> [201: 1010]
            initialI = min(len(lastSent) - CHECK_LENGTH,
                           len(content) - CHECK_LENGTH)
            i = max(0, initialI)
            while i < len(content) and i < len(lastSent):
                if lastSent[i] != content[i]:
                    break
                i += 1
            if i - initialI < 3:
                # 只匹配了两个或更少的字符
                i = 0
        return max(0, i - REDUNDANCY_LENGTH)

    def saveLastSent(self, project, fileID, content):
        """发送成功之后，保存
        project 当前项目
        fileID  文件id
        content 文件内容"""
        if self.project is None or self.project != project:
            self.project = project
            self.store = {}
        self.store[fileID] = content

    def invalidateFile(self, project, fileID):
        """删除一个文件的缓存
        @param project 当前项
        @param fileID  文件id"""
        if self.project is not None and self.project == project:
            del self.store[fileID]
