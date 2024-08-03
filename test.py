import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体# 设置全局字体为Noto CJK系列字体
plt.rcParams['font.family'] = 'Noto Sans CJK JP'  # 或者 'Noto Serif CJK'
plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

# 生成模拟数据
np.random.seed(0)
num_steps = 100
true_position = np.linspace(0, 10, num_steps)  # 真实位置
observations = true_position + np.random.normal(0, 0.5, num_steps)  # 添加噪声的观测值

# 卡尔曼滤波器实现
class KalmanFilter:
    def __init__(self, A, H, Q, R, P, x):
        self.A = A  # 状态转移矩阵
        self.H = H  # 观测矩阵
        self.Q = Q  # 过程噪声协方差
        self.R = R  # 观测噪声协方差
        self.P = P  # 估计误差协方差
        self.x = x  # 初始状态

    def predict(self):
        self.x = np.dot(self.A, self.x)
        self.P = np.dot(np.dot(self.A, self.P), self.A.T) + self.Q
        return self.x

    def update(self, z):
        y = z - np.dot(self.H, self.x)
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        self.x = self.x + np.dot(K, y)
        self.P = self.P - np.dot(K, self.H) @ self.P
        return self.x

# 初始化卡尔曼滤波器参数
A = np.array([[1]])  # 状态转移矩阵
H = np.array([[1]])  # 观测矩阵
Q = np.array([[1e-5]])  # 过程噪声协方差
R = np.array([[1]])  # 观测噪声协方差
P = np.array([[1]])  # 估计误差协方差
x = np.array([[0]])  # 初始状态

kf = KalmanFilter(A, H, Q, R, P, x)

# 存储预测结果
predictions = []

# 对每个观测值应用卡尔曼滤波器
for z in observations:
    kf.predict()
    prediction = kf.update(z)
    predictions.append(prediction[0, 0])

# 可视化结果
plt.figure(figsize=(10, 6))
plt.plot(true_position, label='真实位置', color='g')
plt.scatter(range(num_steps), observations, label='观测值', color='r', s=10)
plt.plot(predictions, label='卡尔曼滤波预测', color='b')
plt.xlabel('时间步')
plt.ylabel('位置')
plt.title('卡尔曼滤波器结果可视化')
plt.legend()
plt.grid()
plt.show()