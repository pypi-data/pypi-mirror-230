from huhk.unit_apache_beam import ApacheFun


class TestFile:
    def test_file_001(self):
        path = r"C:\Users\hangkai.hu\Desktop\测试\雷达用例\活动发现页.xlsx"
        ApacheFun().read_excel(path, 0).print()

    def test_file_002(self):
        path = r"C:\Users\hangkai.hu\Desktop\测试\雷达用例\活动发现页.xlsx"
        path2 = r"C:\Users\hangkai.hu\Desktop\测试\雷达用例"
        ApacheFun().read_excel(path).write_excel(path2)