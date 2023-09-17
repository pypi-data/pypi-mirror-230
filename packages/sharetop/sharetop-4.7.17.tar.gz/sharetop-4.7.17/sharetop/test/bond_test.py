from sharetop.core.prepare import BasicTop


if __name__ == '__main__':
    token = "9ada862fa17ce574"
    sharetop_obj = BasicTop(token)
    # print(sharetop_obj)
    d = sharetop_obj.common_exec_func("bond_yield", "kline_data", {"bond_name": "gcny10", "limit": 10})
    # d = sharetop_obj
    print(d)