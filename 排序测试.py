lst = [54,64,77,87,12,14]
#sort直接修改列表的值
lst.sort()
print(lst)
#sorted开辟新内存
lst2 = [54,64,77,87,12,14]
asc_lst2 = sorted(lst2,reverse=True)
print(lst)
print(lst2)
print(asc_lst2)

