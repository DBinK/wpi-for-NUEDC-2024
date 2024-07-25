def _clamp(value, limits):
    """
    将值限制在指定的范围内。

    :param value: 需要限制的值
    :param limits: 一个元组，包含范围的下限和上限
    :return: 限制后的值
    """
    lower, upper = limits
    if value is None:
        return None
    elif (upper is not None) and (value > upper):
        return upper
    elif (lower is not None) and (value < lower):
        return lower
    return value


class PID(object):
    """
    PID（比例-积分-微分）控制器类。

    用于控制系统的自动调节，通过计算比例、积分和微分项的和来产生输出值。
    """

    def __init__(
        self,
        Kp=1.0,
        Ki=0.0,
        Kd=0.0,
        setpoint=0,
        sample_time=None,
        output_limits=(None, None),
        auto_mode=True,
        proportional_on_measurement=False,
        differential_on_measurement=True,
        error_map=None,
        time_fn=None,
        starting_output=0.0,
    ):
        """
        初始化PID控制器。

        :param Kp: 比例增益
        :param Ki: 积分增益
        :param Kd: 微分增益
        :param setpoint: 目标值
        :param sample_time: 控制器采样时间
        :param output_limits: 输出限制
        :param auto_mode: 是否自动控制
        :param proportional_on_measurement: 比例项是否基于测量值
        :param differential_on_measurement: 微分项是否基于测量值
        :param error_map: 错误值的转换函数
        :param time_fn: 获取当前时间的函数
        :param starting_output: 初始输出值
        """
        # 初始化控制器参数
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self.sample_time = sample_time

        # 输出限制
        self._min_output, self._max_output = output_limits
        self._auto_mode = auto_mode
        self.proportional_on_measurement = proportional_on_measurement
        self.differential_on_measurement = differential_on_measurement
        self.error_map = error_map

        # 初始化控制项值
        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        # 上次计算的时间、输出、误差和输入值
        self._last_time = None
        self._last_output = None
        self._last_error = None
        self._last_input = None

        # 设置时间函数
        if time_fn is not None:
            self.time_fn = time_fn
        else:
            import time

            try:
                self.time_fn = time.monotonic
            except AttributeError:
                self.time_fn = time.time

        # 重置控制器
        self.reset()
        # 初始化积分项为限制后的起始输出值
        self._integral = _clamp(starting_output, output_limits)

    def __call__(self, input_, dt=None):
        """
        调用控制器进行计算。

        :param input_: 当前输入值
        :param dt: 本次和上次计算的时间差
        :return: 控制器输出值
        """
        # 如果不在自动模式下，返回上次的输出值
        if not self.auto_mode:
            return self._last_output

        now = self.time_fn()
        if dt is None:
            # 计算时间差
            dt = now - self._last_time if (now - self._last_time) else 1e-16
        elif dt <= 0:
            # 时间差必须大于0
            raise ValueError('dt has negative value {}, must be positive'.format(dt))

        # 根据采样时间决定是否更新输出
        if self.sample_time is not None and dt < self.sample_time and self._last_output is not None:
            return self._last_output

        # 计算误差和其变化量
        error = self.setpoint - input_
        d_input = input_ - (self._last_input if (self._last_input is not None) else input_)
        d_error = error - (self._last_error if (self._last_error is not None) else error)

        # 如果有错误转换函数，应用之
        if self.error_map is not None:
            error = self.error_map(error)

        # 更新比例、积分和微分项
        if not self.proportional_on_measurement:
            self._proportional = self.Kp * error
        else:
            self._proportional -= self.Kp * d_input

        self._integral += self.Ki * error * dt
        self._integral = _clamp(self._integral, self.output_limits)  # 避免积分饱和

        if self.differential_on_measurement:
            self._derivative = -self.Kd * d_input / dt
        else:
            self._derivative = self.Kd * d_error / dt

        # 计算输出值，并限制在输出范围内
        output = self._proportional + self._integral + self._derivative
        output = _clamp(output, self.output_limits)

        # 更新上次计算的时间、输出、误差和输入值
        self._last_output = output
        self._last_input = input_
        self._last_error = error
        self._last_time = now

        return output

    def __repr__(self):
        """
        返回控制器的字符串表示。

        :return: 字符串表示
        """
        return (
            '{self.__class__.__name__}('
            'Kp={self.Kp!r}, Ki={self.Ki!r}, Kd={self.Kd!r}, '
            'setpoint={self.setpoint!r}, sample_time={self.sample_time!r}, '
            'output_limits={self.output_limits!r}, auto_mode={self.auto_mode!r}, '
            'proportional_on_measurement={self.proportional_on_measurement!r}, '
            'differential_on_measurement={self.differential_on_measurement!r}, '
            'error_map={self.error_map!r}'
            ')'
        ).format(self=self)

    @property
    def components(self):
        """
        获取最后一次计算的比例、积分和微分项。

        :return: 一个元组，包含比例、积分和微分项
        """
        return self._proportional, self._integral, self._derivative

    @property
    def tunings(self):
        """
        获取控制器的调谐参数。

        :return: 一个元组，包含比例增益、积分增益和微分增益
        """
        return self.Kp, self.Ki, self.Kd

    @tunings.setter
    def tunings(self, tunings):
        """
        设置控制器的调谐参数。

        :param tunings: 一个元组，包含比例增益、积分增益和微分增益
        """
        self.Kp, self.Ki, self.Kd = tunings

    @property
    def auto_mode(self):
        """
        获取控制器的自动模式状态。

        :return: 控制器是否处于自动模式
        """
        return self._auto_mode

    @auto_mode.setter
    def auto_mode(self, enabled):
        """
        设置控制器的自动模式状态。

        :param enabled: 控制器是否进入自动模式
        """
        self.set_auto_mode(enabled)

    def set_auto_mode(self, enabled, last_output=None):
        """
        设置控制器的自动模式状态，并可选地设置从手动模式切换到自动模式时的初始积分值。

        :param enabled: 控制器是否进入自动模式
        :param last_output: 从手动模式切换到自动模式时的初始输出值
        """
        if enabled and not self._auto_mode:
            # 切换到自动模式时重置并设置积分项初始值
            self.reset()
            self._integral = last_output if (last_output is not None) else 0
            self._integral = _clamp(self._integral, self.output_limits)

        self._auto_mode = enabled

    @property
    def output_limits(self):
        """
        获取输出限制。

        :return: 一个元组，包含输出的下限和上限
        """
        return self._min_output, self._max_output

    @output_limits.setter
    def output_limits(self, limits):
        """
        设置输出限制。

        :param limits: 一个元组，包含输出的下限和上限
        """
        if limits is None:
            self._min_output, self._max_output = None, None
            return

        min_output, max_output = limits
        if (None not in limits) and (max_output < min_output):
            raise ValueError('lower limit must be less than upper limit')

        self._min_output = min_output
        self._max_output = max_output

        # 限制当前的积分项和上次的输出值
        self._integral = _clamp(self._integral, self.output_limits)
        self._last_output = _clamp(self._last_output, self.output_limits)

    def reset(self):
        """
        重置控制器的状态。
        """
        # 重置控制项值
        self._proportional = 0
        self._integral = 0
        self._derivative = 0

        # 限制积分项在输出范围内
        self._integral = _clamp(self._integral, self.output_limits)

        # 更新上次计算时间为当前时间，上次输出和输入为None
        self._last_time = self.time_fn()
        self._last_output = None
        self._last_input = None