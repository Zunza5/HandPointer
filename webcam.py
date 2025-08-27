import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2 as cv 
from utilies import draw_landmarks_on_image
import time
import globals


model_path = 'model/hand_landmarker.task'

def init_mediapipe():
    BaseOptions = mp.tasks.BaseOptions
    HandLandmarker = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
    VisionRunningMode = mp.tasks.vision.RunningMode


    # Create a hand landmarker instance with the live stream mode:
    def print_result(result, output_image: mp.Image, timestamp_ms: int):
        globals.detection_result = result


    options = HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result,
        num_hands=1)
    with HandLandmarker.create_from_options(options) as landmarker:
        # The landmarker is initialized. Use it here.
        # ...
        print("tracking...")
        cap = cv.VideoCapture(1)
        old_timestamp = -1
        if not cap.isOpened():
                print("Cannot open camera")
                exit()
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            frame_timestamp_ms = int(time.time_ns() / 1_000_000)
            if(frame_timestamp_ms == old_timestamp):
                continue

            # if frame is read correctly ret is True
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break
            # Our operations on the frame come here
            # Display the resulting frame
            frame_mirror = cv.flip(frame, 1)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_mirror)
            landmarker.detect_async(mp_image, frame_timestamp_ms)
            old_timestamp = frame_timestamp_ms
            #show_image_landmarks(mp_image, frame_mirror)
            #if cv.waitKey(1) & 0xFF == ord('q'):
            #    break

            



            
        # When everything done, release the capture
        cap.release()
        cv.destroyAllWindows()

def show_image_landmarks(mp_image, frame_mirror):
    if globals.detection_result is not None and len(globals.detection_result.hand_landmarks) > 0:
        annotated_image = draw_landmarks_on_image(mp_image.numpy_view(), globals.detection_result)
        cv.imshow("Hand Landmarks", cv.cvtColor(annotated_image, cv.COLOR_RGB2BGR))
    else:
        cv.imshow("Hand Landmarks", frame_mirror)