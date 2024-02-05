import multiprocessing
from multiprocessing import JoinableQueue

import Singleton
from pygame_interface import PygameInterface
from ultralytics import YOLO

"""Video Tracker is a Singleton that manages the object detection"""


class VideoTracker(metaclass=Singleton.Singleton):

    def __init__(self):
        self._results = JoinableQueue()
        self._jobs = JoinableQueue()
        self._model = YOLO('yolov8n.pt')
        self._started = False

    def is_started(self):
        return self._started

    def start(self):
        self._started = True

    def stop(self):
        self._started = False


    def _process_results(self,frame):
        """detect a person box and put it in results if the tracking was started"""

        results_box = []
        model_results = self._model.predict(frame, True, verbose=False)
        for result in model_results:
            for box in result.boxes.data.tolist():
                x, y, w, h, score, class_id = box
                # class_id 0 is the person id, score is the accuracy of the prediction
                if class_id == 0 and score >= 0.5:
                    results_box.append((x, y, w, h))
        return (results_box)



    def object_detection(self, frame, interface: PygameInterface):
        """identifies the people that enters the frame, creates a box and
        put the center in the list """
        centers = []
        points =  self._process_results(frame)
        for point in points:
            # Each person detected is represented as a point that is the center of a box
            x, y, w, h = point
            center = ((x + w / 2), (y + h / 2))
            centers.append(center)
            interface.create_box(x, y, w, h)

        return centers
