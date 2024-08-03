import numpy as np

class MovingAverageFilter:
    """
    窗口平滑滤波器
    """
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.values = []

    def update(self, value):
        # 添加新值到列表
        self.values.append(value)
        # 如果超过窗口大小，移除最旧的值
        if len(self.values) > self.window_size:
            self.values.pop(0)
        # 返回当前窗口的平均值
        return np.mean(self.values)

class KalmanFilter:
    """
    卡尔曼滤波器类
    """
    def __init__(self, A, B, H, Q, R, P, x):
        self.A = A  # 状态转移矩阵
        self.B = B  # 控制矩阵
        self.H = H  # 观测矩阵
        self.Q = Q  # 过程噪声协方差
        self.R = R  # 观测噪声协方差
        self.P = P  # 估计误差协方差
        self.x = x  # 初始状态

    def predict(self, u=0):
        self.x = np.dot(self.A, self.x) + np.dot(self.B, u)
        self.P = np.dot(np.dot(self.A, self.P), self.A.T) + self.Q
        return self.x

    def update(self, z):
        y = z - np.dot(self.H, self.x)
        S = np.dot(self.H, np.dot(self.P, self.H.T)) + self.R
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        self.x = self.x + np.dot(K, y)
        self.P = self.P - np.dot(np.dot(K, self.H), self.P)
        return self.x

class ParticleFilter:
    """
    粒子滤波器 
    """
    def __init__(self, num_particles, state_dim, init_state, process_noise, measurement_noise):
        self.num_particles = num_particles
        self.state_dim = state_dim
        self.particles = np.tile(init_state, (num_particles, 1))
        self.weights = np.ones(num_particles) / num_particles
        self.process_noise = process_noise
        self.measurement_noise = measurement_noise

    def predict(self, control_input):
        self.particles += control_input + np.random.normal(0, self.process_noise, (self.num_particles, self.state_dim))

    def update(self, measurement):
        distances = np.linalg.norm(self.particles - measurement, axis=1)
        self.weights = np.exp(-distances**2 / (2 * self.measurement_noise**2))
        self.weights += 1.e-300  # 避免除零错误
        self.weights /= np.sum(self.weights)

    def resample(self):
        indices = np.random.choice(range(self.num_particles), size=self.num_particles, p=self.weights)
        self.particles = self.particles[indices]
        self.weights = np.ones(self.num_particles) / self.num_particles

    def estimate(self):
        return np.average(self.particles, weights=self.weights, axis=0)
    
   
class AdaptiveFilter: # aka 低通滤波
    """
    自适应滤波器, aka 低通滤波器
    """
    def __init__(self, initial_alpha=0.3):
        self.alpha = initial_alpha
        self.smoothed_value = None

    def update(self, value):
    
        if self.smoothed_value is None:
            self.smoothed_value = value
        else:
            self.smoothed_value = self.alpha * value + (1 - self.alpha) * self.smoothed_value
        return self.smoothed_value

# 示例使用
if __name__ == "__main__":
    ma_filter = MovingAverageFilter(window_size=10)
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    smoothed_data = []
    for value in data:
        smoothed_value = ma_filter.update(value)
        smoothed_data.append(smoothed_value)
    
    print("平滑后的数据:", smoothed_data)