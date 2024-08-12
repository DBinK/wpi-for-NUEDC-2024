class PID:
    def __init__(self, kp=1, ki=0, kd=0, setpoint=0, output_limits=(None, None)):
        self.kp = kp  # 比例增益
        self.ki = ki  # 积分增益
        self.kd = kd  # 微分增益
        self.setpoint = setpoint  # 目标值
        self.prev_error = 0  # 上一个误差
        self.integral = 0  # 积分值
        self.output_limits = output_limits  # 输出限制

    def update(self, measured_value):
        # 计算误差
        error = self.setpoint - measured_value
        # 积分
        self.integral += error
        # 微分
        derivative = error - self.prev_error
        # 计算控制输出
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        
        # 应用输出限制
        if self.output_limits[0] is not None and output < self.output_limits[0]:
            output = self.output_limits[0]
        if self.output_limits[1] is not None and output > self.output_limits[1]:
            output = self.output_limits[1]

        # 保存当前误差以便下次计算
        self.prev_error = error
        return output

# 示例使用
if __name__ == "__main__":
    pid = PID(1.2, 1.0, 0.001, setpoint=1.0, output_limits=(-10, 10))
    measured_value = 0.0  # 初始测量值

    for _ in range(100):  # 模拟100次控制循环
        control = pid.update(measured_value)
        # 在这里可以将控制输出应用于系统，并更新测量值
        measured_value += control * 0.1  # 假设系统响应
        print(f"控制输出: {control}, 当前值: {measured_value}")