from numpy import load
from os.path import join
from torch import device
from torch.cuda import is_available
from numpy import min, max as min_, max_
from numpy import mean, std as mean_, std_


def min_max(data):
    min_data, max_data = min_(data),max_(data)
    return (data - min_data)/(max_data-min_data)
def standardization(data):
    mu = mean_(data, axis=0)
    sigma = std_(data, axis=0)
    return (data - mu) / sigma

def get_device(gpu_index=0):
    d = str( device("cuda:"+str(gpu_index) if is_available() else "cpu"))
    if ('cpu' == d):
        print("CPU MODE")
    return device("cuda:"+str(gpu_index) if is_available() else "cpu")

print(type(str(get_device())))

from os.path import dirname

def get_vol6(nums: int, type = 64):
    '''
    获得一个64个序列长度的电池电压第6阶段放电数据
    '''
    # import sys
    # dir_path = abspath('tool.py')
    # print(sys.path[0])
    # chdir(dir_path[0])
    dir_name = dirname(__file__)
    # real_path = join(dir_name,'vol6_64.py')
    real_path = None
    real_path = join(dir_name, 'vol6_64.py')
    if type == 75:
        real_path = join(dir_name,'vol50000.py')

    # abs_path = abspath('tool.py')
    # print(abs_path)
    data = load(real_path)
    if nums > data.shape[0]:
        print('Warning: max size is ', data.shape[0])
    return data[0:nums]


# x = np.zeros((100, 100))

# print(x.shape)
# print(x[0:1010].shape)

# get_vol6_64(10221)