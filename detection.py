from ultralytics import YOLO
from PIL import ImageGrab
import numpy as np
from variables import MOB_TYPES, MODEL_NAME
from functions import get_distance



class Detection:

    def __init__(self):
        self.model = YOLO(MODEL_NAME + '/weights/best.pt')
        self.model.fuse()

    def process_image(self, image):
        results = self.model(image)[0]

        classes_names = results.names
        classes = results.boxes.cls.cpu().numpy()
        boxes = results.boxes.xyxy.cpu().numpy().astype(np.int32)

        grouped_objects = {'aggressive': [], 'neutral': []}

        for class_id, box in zip(classes, boxes):
            x1, y1, x2, y2 = box
            click_cords = [(x1 + x2) // 2, (y1 + y2) // 2]
            distance = get_distance((x1 + x2) // 2, y2)
            class_name = classes_names[int(class_id)]

            if class_name in MOB_TYPES['neutral']:
                grouped_objects['neutral'].append(
                    {'type': class_name, 'cords': box, 'click': click_cords, 'distance': distance})
            else:
                grouped_objects['aggressive'].append(
                    {'type': class_name, 'cords': box, 'click': click_cords, 'distance': distance})

        for key in grouped_objects:
            grouped_objects[key] = sorted(grouped_objects[key], key=lambda d: d['distance'])
        return grouped_objects
