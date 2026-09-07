from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")


def detect_objects():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        return "Camera open nahi ho saka."

    success, frame = camera.read()

    camera.release()

    if not success:
        return "Camera se image nahi mil saki."

    results = model(frame, verbose=False)

    detected_objects = []

    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if confidence >= 0.5:

                object_name = model.names[class_id]

                detected_objects.append(object_name)

    unique_objects = sorted(set(detected_objects))

    if not unique_objects:
        return "Mujhe camera mein koi object clearly nazar nahi aa raha."

    return "Mujhe yeh objects nazar aa rahe hain: " + ", ".join(unique_objects)


if __name__ == "__main__":

    print("JARVIS Vision Test")

    result = detect_objects()

    print("\nJARVIS:", result)