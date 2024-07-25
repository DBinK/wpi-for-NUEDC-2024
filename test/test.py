import subprocess

# 正确的调用方式
result = subprocess.run(["v4l2-ctl", "--device=/dev/video0", "--all"], capture_output=True, text=True)
print(result.stdout)