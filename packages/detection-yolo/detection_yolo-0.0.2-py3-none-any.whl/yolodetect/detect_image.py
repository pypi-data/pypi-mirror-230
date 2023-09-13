import os
import json
import torch
from .utils.datasets import LoadImages
from .utils.general import check_img_size, scale_coords, get_xyxy_from_tensor
from yolo_detector import Detector, Utils

class ObjectDetector:
    def __init__(self, weights, indexer_version='v2', img_size=640, confidence=0.45, classes=[0]):
        self.weights = weights
        self.indexer_version = indexer_version
        self.img_size = img_size
        self.confidence = confidence
        self.classes = classes
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.detector = Detector()
        self.model = self._load_model()
        self.model.to(self.device).eval()

    def _load_model(self):
        return self.detector._load_model(self.weights[self.indexer_version], self.indexer_version)

    def detect_objects(self, source):
        dataset = LoadImages(source)
        frame_rate = dataset.get_video_frame_rate()
        frame_rate = Utils.check_frame_rate(frame_rate)

        data = {}
        objs = 0

        for path, im, im0s, vid_cap, s in dataset:
            (height, width, _) = im0s.shape
            im = torch.from_numpy(im).to(self.device)
            im = im.float() / 255.0  # Normalize pixel values

            if len(im.shape) == 3:
                im = im[None]  # Expand for batch dimension

            if im.ndimension() == 3:
                img = im.unsqueeze(0)

            pred = self.detector.detect_image(self.model, im, self.confidence, self.classes, self.indexer_version)

            for i, det in enumerate(pred):
                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size (im0 is image in source dimensions)
                    det[:, :4] = scale_coords(im.shape[2:], det[:, :4], (height, width)).round()

                    for *xyxy, conf, cls in reversed(det):
                        x1, y1, x2, y2 = get_xyxy_from_tensor(*xyxy)
                        class_label = int(cls)
                        objs += 1

                        # Minimum detected object's size is 32x32
                        data[f"object_{objs}"] = {
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2,
                            "confidence": conf.item()
                        }
        # Save the detection data to a JSON file
        json_filename = os.path.splitext(os.path.basename(source))[0] + "_detections.json"
        json_path = os.path.join("detection_results", json_filename)

        os.makedirs("detection_results", exist_ok=True)
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)    

        return json_path

if __name__ == "__main__":
    weights = {
        'v1': 'weights/FaceDetectionModel_Small_v1.pt',
        'v2': 'weights/FaceDetectionModel_Small_v2.pt'
    }
    indexer_version = 'v1'
    source_path = r'C:\Users\hasnain.ali\Desktop\videos\walking.jpg'

    detector = ObjectDetector(weights, indexer_version=indexer_version)
    data, objs_detected = detector.detect_objects(source_path)

    print(f"Detected {objs_detected} objects:")
    for item in data:
        print(item)
