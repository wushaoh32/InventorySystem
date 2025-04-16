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
#2025/4/12/106
print('-'*40)
'''
类名要求首字母大写，类相当于图纸，是抽象的模版,类里面要求包括：
1类属性:直接定义在类中,方法外的变量
2类方法、
3实例属性:定义在__init__方法中,使用self大点的的变量
4实例方法、
5静态方法

'''

class Student():
    #对象名=类名()
    #类属性:直接定义在类中,方法外的变量
    school = '北京大学'
    
    def __init__(self,name,age):#name和age是方法的参数，是局部变量
        pass

