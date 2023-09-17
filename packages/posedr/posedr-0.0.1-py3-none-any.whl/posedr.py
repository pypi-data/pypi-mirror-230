import cv2
import mediapipe as mp
import math

def run_pose_detection(mode=False, smooth=True, detectionCon=0.5, trackCon=0.5):
    mpDraw = mp.solutions.drawing_utils
    mpPose = mp.solutions.pose
    pose = mpPose.Pose(static_image_mode=mode,
                       smooth_landmarks=smooth,
                       min_detection_confidence=detectionCon,
                       min_tracking_confidence=trackCon)

    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        if results.pose_landmarks:
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy, cz = int(lm.x * w), int(lm.y * h), int(lm.z * w)

            ad = abs(cx - cx) // 2
            x1, x2 = cx - ad, cx + ad
            y1, y2 = cy - ad, cy + ad
            bbox = (x1, y1, x2 - x1, y2 - y1)
            cx, cy = bbox[0] + (bbox[2] // 2), bbox[1] + bbox[3] // 2
            bboxInfo = {"bbox": bbox, "center": (cx, cy)}

            cv2.rectangle(img, bbox, (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            h="Thing"
            print("the King:",h)

        cv2.imshow("Image", img)
        cv2.waitKey(1)

    cap.release()
#
# if __name__ == "__main__":
#     run_pose_detection()
