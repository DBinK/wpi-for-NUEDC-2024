import numpy as np
import matplotlib.pyplot as plt

def find_valid_average(data):
    # 转换为numpy数组并排序
    data = np.array(data)
    data.sort()

    # 定义窗口大小和密度阈值
    window_size = 5
    density_threshold = 2  # 选择密度大于2的区域

    # 计算每个数据点的密度
    valid_data = []
    for point in data:
        # 计算在窗口内的数据数量
        count = np.sum((data >= point - window_size / 2) & (data <= point + window_size / 2))
        if count > density_threshold:
            valid_data.append(point)

    # 计算有效数据的平均值
    if valid_data:
        print("有效数据为:", valid_data)
        average = np.mean(valid_data)
        print(f"有效数据的平均值为: {average:.2f}")
        return average
    else:
        print("没有有效数据可计算平均值。")
        return None

# 定义角度数据

angles = [61.19995, 71.99997, 117.9, 110.7, 62.09995, 72.89996, 117.9, 111.6, 62.09995, 71.99996, 117.9, 110.7, 62.09995, 71.99996, 117.0, 111.6, 61.19994, 71.99996, 108.9, 62.09995, 71.99996, 62.09995, 71.99996, 62.09995, 71.99996, 62.09995, 71.09996, 62.09995, 71.99996, 62.09995, 71.99996, 62.09995, 71.99996, 62.09995, 71.09996, 62.09995, 71.99996, 61.19994]


# 计算平均值
average_value = np.mean(angles)
# 计算平均值
average_value = find_valid_average(angles)

# 将角度转换为弧度
angles = np.radians(angles)

# 计算对应的x和y坐标
x = np.cos(angles)
y = np.sin(angles)

# 绘制点云图
plt.figure(figsize=(6, 6))
plt.scatter(x, y, color='blue', marker='o', label='angles',s=10)

# 添加表示平均值的红色点
average_x = np.cos(np.radians(average_value))
average_y = np.sin(np.radians(average_value))
plt.scatter(average_x, average_y, color='red', marker='o', s=10, label='average')

# 设置图形属性
plt.xlim(-1.5, 1.5)
plt.ylim(-1.5, 1.5)
plt.axhline(0, color='gray', lw=0.5, ls='--')
plt.axvline(0, color='gray', lw=0.5, ls='--')
plt.title('Point clouds and averages')
plt.xlabel('X')
plt.ylabel('Y')
plt.gca().set_aspect('equal', adjustable='box')  # 设置坐标轴比例相等
plt.grid()
plt.legend()
plt.show()