# -*-coding:utf-8-*-
import solcx

if __name__ == '__main__':
    list1 = []
    # data = list1[0] if len(list1) else None
    ret = solcx.get_compilable_solc_versions()
    print(ret)
    # solcx.install_solc("0.4.25")
    # print(data)
