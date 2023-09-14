"""
这是nester.py模块，提供了一个名为print_lol()的函数，
这个函数的作用是打印列表，其中有可能包含，也可能不包含嵌套列表。
"""


def print_lol(the_list, indent=False, level=0):
    """
    第1个参数，名为"the_list"，这可以是任何python列表，也可以是包含嵌套列表的列表，
    所指定的列表中的每个数据项会递归地输出到屏幕上，各数据项各占一行。
    第2个参数，名为"indent"，用来打开缩进特性。
    第3个参数，名为"level"，用来在遇到嵌套列表时插入制表符。
    @param indent: False
    @param level: 0
    @param the_list: ["The", "Life", ["Of", "Brain", ["april", "max"]]]
    @return:
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent:
                for num in range(level):
                    print("\t", end='')
            print(each_item)
