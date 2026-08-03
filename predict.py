from ultralytics import YOLO
import cv2

# Load a custom model
model = YOLO("/Users/jensen/Desktop/python_final/runs/detect/train3/weights/best.pt")

# Predict with the model
results = model("/Users/jensen/Desktop/python_final/test.bmp")

# Loop through results and process
for i, result in enumerate(results):
    # 複製原始圖像以便自訂標註
    img = result.orig_img.copy()

    # 處理每個框
    for box, cls_id, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
        x1, y1, x2, y2 = map(int, box.tolist())
        width = x2 - x1
        height = y2 - y1
        area = width * height

        # 面積分級
        if area > 10000:
            level = "重大瑕疵"
            color = (0, 0, 255)  # Red
        elif area > 3000:
            level = "中等瑕疵"
            color = (0, 255, 255)  # Yellow
        else:
            level = "輕微瑕疵"
            color = (0, 255, 0)  # Green

        class_name = result.names[int(cls_id)]

        # 繪製框與等級標籤
        label = f"{class_name}"
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, label, (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # 印出文字資訊
        print(f"Class: {class_name}, Confidence: {conf:.2f}, Area: {area}, Level: {level}")

    # 儲存圖片
    output_path = f"/Users/jensen/Desktop/python_final/output_result_{i}.jpg"
    cv2.imwrite(output_path, img)
