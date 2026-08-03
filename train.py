from ultralytics import YOLO

# 使用 YOLOv11 模型
model = YOLO("yolo11n.pt")  # 可改成 yolo11s.pt / yolo11m.pt

# 訓練模型
model.train(
    data="datasets/metal-surface-defect.v1i.yolov11/data.yaml", 
    epochs=100,
    imgsz=640,
    batch=16,
    device=0  # 0 = GPU；如果有多張卡也可寫 0,1
)
