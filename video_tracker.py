import multiprocessing
from multiprocessing import JoinableQueue

import cv2

from pygame_interface import PygameInterface


class VideoTracker:
    started = False
    net = cv2.dnn.readNet("dnn_model/yolov4-tiny.weights", "dnn_model/yolov4-tiny.cfg")
    model = cv2.dnn.DetectionModel(net)
    model.setInputParams(size=(320, 320), scale=1/255)

    def __init__(self):
        self.results = JoinableQueue()


    @classmethod
    def start(cls):
        cls.started = True

    @classmethod
    def stop(cls):
        cls.started = False



    def object_detection(self, frame, interface:PygameInterface):
        """Indentifies the people that enters the frame and activates the smart lighting """
        classIds, scores, bboxes = VideoTracker.model.detect(frame)
        centers = []
        for score in scores:
            if score > 0.3:
                for classId in classIds:
                    #classId 0 is the person tag
                    if classId == 0:
                        for bbox in bboxes:
                            x, y, w, h = bbox
                            interface.create_box(x,y,w,h)
                            center = ((x + w/2), (y + h/2))
                            centers.append(center)
        return centers



