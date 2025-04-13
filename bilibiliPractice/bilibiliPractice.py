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
# #2025/4/12/106
'''
1类属性：直接定义在类中，方法外的变量
2实例属性：定义在__init__方法中，使用self打点的变量，实例属性可以在整个类中去使用
3实例方法：定义在类中的的函数，而且自带参数self（就是类中定义的普通方法）
4静态方法：使用装饰器@staticmethod修饰的方法，不与类或实例绑定，只是在类的命名空间内。同样通过类名或类的实例使用打点操作符来调用静态方法
5类方法：使用装饰器@classmethod修饰的方法，第一个参数通常是cls，代表类本身
每个对象的属性名称相同，但属性值不同
可以为某个对象绑定独有的属性或方法
'''
#类的实例方法和类方法通常是通过(.)调用的

class Car:#汽车制造的蓝图，规定汽车具有哪些属性和功能
    brand = '宝马'#1类属性，代表汽车品牌，所有宝马车实例都共享这个品牌名 

    def __init__(self,color,horsepower):#3实例方法，__init__方法是初始构造方法
        self.color = color #2左侧是实例属性，xm是局部变量，将局部变量的值赋值给self.name
        self.horsepower = horsepower #实例属性的名称和局部变量的名称可能相同

    def show(self):#第一个参数必须是self用于访问实例属性和调用其他实例方法，通过实例来调用
        print(f"颜色是{self.color},{self.horsepower}匹马力")
        # print(Car.brand)

    @staticmethod
    def sm():
        print("这是一个静态方法，静态方法不能调用实例属性，也不能调用实例方法")

#创建四个车辆对象
car  = Car("绿色","100")
car2 = Car("红色","200")
# car3 = Car("蓝色","300")
# car4 = Car("黑色","400")

# # Car.brand = "奔驰"
# # print(Car.brand)
# lst = [car,car2,car3,car4] #列表中的元素是Car类型的对象
# for item in lst:#item是列表中的元素，是Car类型的对象
#     item.show()
print(car.color,car.horsepower)
print(car2.color,car2.horsepower)

#动态绑定一个实例属性
car2.gender='男'
print(car2.color,car2.horsepower,car2.gender)

#动态绑定方法
def introduce():
    print('我是一个普通的函数，我被动态绑定成car2的方法')
car2.fun= introduce
#fun就是car2对象的方法
#调用
car2.fun()#此处的fun是随便写的，其他单词也可以
