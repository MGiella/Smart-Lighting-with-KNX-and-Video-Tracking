import multiprocessing
from multiprocessing import JoinableQueue
from pygame_interface import PygameInterface
from ultralytics import YOLO



class VideoTracker:
    started = False
    yolo_model = YOLO('yolov8n.pt')
    yolo_model.info(False, False)



    def __init__(self):
        self.results = JoinableQueue()
        self.jobs = JoinableQueue()
        self.create_processes()

    def create_processes(self):
        for _ in range(5):
            p = multiprocessing.Process(target=self.process_results)
            p.daemon=True
            p.start()

    def process_results(self):
        """detect a person box and put it in results"""
        while True:
            results_box = []
            frame  = self.jobs.get()
            results = VideoTracker.yolo_model.predict(frame, True, verbose=False)
            for result in results:
                for box in result.boxes.data.tolist():
                    x, y, w, h, score, class_id = box
                    if class_id == 0 and score >= 0.5:
                        results_box.append((x,y,w,h))

            self.results.put(results_box)

    @classmethod
    def start(cls):
        cls.started = True

    @classmethod
    def stop(cls):
        cls.started = False


    def object_detection(self, frame, interface:PygameInterface):
        """Indentifies the people that enters the frame, creates a box and
        put the center in the list """
        self.jobs.put(frame)
        centers = []
        if not self.results.empty():
            points = self.results.get()
            for point in points:
                x, y, w, h = point
                center = ((x + w / 2), (y + h / 2))
                centers.append(center)
                interface.create_box(x, y, w, h)

        return centers



