import cv2
def find_available_cameras(start_index=0, end_index=9):
    """
    返回在指定范围内所有可用摄像头的索引列表。
    @param start_index: 搜索范围的起始索引
    @param end_index: 搜索范围的结束索引
    @return: 找到的摄像头索引列表
    """
    available_cameras = []
    for index in range(start_index, end_index + 1):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            available_cameras.append(index)
            cap.release()
        else:
            continue  # 如果无法打开，则直接跳过，继续下一个索引
    return available_cameras


if __name__ == "__main__":
    # 调用函数并打印结果，例如搜索索引0到20之间的摄像头
    cameras = find_available_cameras(0, 20)

    print("Available cameras:", cameras)