import numpy as np
import os
def save_rmsd_data(file, X:np.ndarray,dir=None):
    # 如果dir不存在则创建
    if dir and not os.path.exists(dir):
        os.makedirs(dir)
    with open(dir+'/'+file, 'w') as f:
        for x in X:
            f.write('{:f} {:f} {:f} {:f}'.format(x[0], x[1], x[2],x[3]) + '\n')

# 定义保存xyz格式的函数,先写入原子数，再写入坐标，坐标前面加上原子类型
def save_xyz(file, X:np.ndarray, title:str, dir=None):
    # 如果dir不存在则创建
    if dir and not os.path.exists(dir):
        os.makedirs(dir)
    with open(dir+'/'+file, 'w') as f:
        f.write(str(X.shape[0]) + '\n')
        f.write(title + '\n')
        for x in X:
            f.write('1\t{:f} {:f} {:f}'.format(x[0], x[1], x[2]) + '\n')

def save_xyz_traj(file, X:np.ndarray, dir=None):
    # 如果dir不存在则创建
    if dir and not os.path.exists(dir):
        os.makedirs(dir)
    with open(dir+'/'+file, 'w') as f:
        for x in X:
            f.write(str(x.shape[0]) + '\n')
            f.write('\n')
            for p in x:
                f.write('1\t{:f} {:f} {:f}'.format(p[0], p[1], p[2]) + '\n')

# 定义绘制xyz格式文件为3d图像的函数
def draw_xyz(X:np.ndarray, title:str):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.scatter(X[:,0], X[:,1], X[:,2])
    ax.set_title(title)
    plt.show()


# 定义读取xyz格式的函数，返回迭代器
def read_xyz(file):
    with open(file) as f:
        while True:
            try:
                n_atoms = int(f.readline())
            except ValueError:
                break
            if not n_atoms:
                break
            f.readline()
            
            # 将坐标保存为narray
            coords = []
            for i in range(n_atoms):
                line = f.readline().split()
                coords.append([float(x) for x in line[1:]])
            yield coords
def my_print_helloworld():
    print('hello!')