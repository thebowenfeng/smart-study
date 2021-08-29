import cv2
import mediapipe as mp
import time
import math
import requests
import threading
import sys

ACCESS = sys.argv[1]
REFRESH = sys.argv[2]
USERNAME = sys.argv[3]


def movement_sigmoid(x: float):
    return 1 / (1 + math.e ** -(15.2*x - 6))


def yawn_exp(x:float):
    result = (0.99 * (x + 0.15) + 0.56) ** 14.5
    return 0.6 if result > 0.6 else result


def send_requests(action, time_diff):
    global ACCESS, REFRESH

    print(f"Action: {action} Time_diff: {time_diff}")
    headers = {
        'Content-Type': "application/json",
        'Authorization': ACCESS
    }
    resp = requests.post("https://resource-smartstudy.herokuapp.com/post_face_data",
                         json={"Username": USERNAME, "Action": action, "Length": time_diff},
                         headers=headers)

    if resp.status_code == 403 and resp.json()["message"] == 'Invalid access token':
        headers = {
            'Content-Type': "application/json",
        }
        resp = requests.post("https://auth-smartstudy.herokuapp.com/refresh_access_token",
                             json={"ClientID": "react", "ClientSecret": "my secret", "RefreshToken": REFRESH},
                             headers=headers)

        ACCESS = resp.json()["access_token"]
        REFRESH = resp.json()["refresh_token"]
        send_requests(action, time_diff)


def main():
    cap = cv2.VideoCapture(1)

    prev_time = time.time()
    mp_draw = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=3)
    draw_spec = mp_draw.DrawingSpec(thickness=1, circle_radius=1)

    left = None
    right = None
    nose = None
    top = None
    bottom = None
    mouth_mid = None
    mouth_left = None
    mouth_open_top = None
    mouth_open_bottom = None
    nose_bottom = None

    LEFT_RIGHT_RATIO = 0.2
    BOTTOM_RATIO = 0.4
    TOP_RATIO = 0.5

    while True:
        temp, img = cap.read()
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(img_rgb)

        curr_time = time.time()
        time_diff = curr_time - prev_time
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(img, f"FPS: {int(fps)}", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        if results.multi_face_landmarks:
            for face_lms in results.multi_face_landmarks:
                mp_draw.draw_landmarks(img, face_lms, mp_face_mesh.FACE_CONNECTIONS, draw_spec, draw_spec)

                for id, lm in enumerate(face_lms.landmark):
                    height, width, channel = img.shape
                    x, y = int(lm.x * width), int(lm.y * height)

                    if id == 234:
                        left = x, y
                    elif id == 323:
                        right = x, y
                    elif id == 4:
                        nose = x, y
                    elif id == 10:
                        top = x, y
                    elif id == 152:
                        bottom = x, y
                    elif id == 61:
                        mouth_left = x, y
                    elif id == 0:
                        mouth_mid = x, y
                    elif id == 13:
                        mouth_open_top = x, y
                    elif id == 14:
                        mouth_open_bottom = x, y
                    elif id == 2:
                        nose_bottom = x, y

                movement_flag = False
                action_flag = False

                if left and right and nose and top and bottom and mouth_left:
                    n_to_left = nose[0] - left[0]
                    n_to_right = right[0] - nose[0]
                    total_horiz = right[0] - left[0]
                    n_to_bottom = bottom[1] - nose[1]
                    n_to_top = nose[1] - top[1]
                    total_vert = bottom[1] - top[1]
                    mouth_side_vert_dist = mouth_left[1] - mouth_mid[1]
                    mouth_vert_dist = mouth_open_bottom[1] - mouth_open_top[1]
                    nose_mouth_gap = mouth_open_top[1] - nose_bottom[1]

                    if n_to_right < total_horiz * LEFT_RIGHT_RATIO:
                        print(f"Turning right! Time: {time_diff}s")
                        movement_flag = True
                        action_flag = True

                        thr = threading.Thread(target=send_requests, args=("right", time_diff,))
                        thr.start()
                    elif n_to_left < total_horiz * LEFT_RIGHT_RATIO:
                        print(f"Turning left! Time: {time_diff}s")
                        movement_flag = True
                        action_flag = True

                        thr = threading.Thread(target=send_requests, args=("left", time_diff,))
                        thr.start()
                    if n_to_bottom < total_vert * BOTTOM_RATIO:
                        print(f"Turning down! Time: {time_diff}s")
                        movement_flag = True
                        action_flag = True

                        thr = threading.Thread(target=send_requests, args=("down", time_diff,))
                        thr.start()
                    elif n_to_top < total_vert * TOP_RATIO and not (mouth_vert_dist / nose_mouth_gap > 0.7):
                        print(f"Turning up! Time: {time_diff}s")
                        movement_flag = True
                        action_flag = True

                        thr = threading.Thread(target=send_requests, args=("up", time_diff,))
                        thr.start()
                    if not movement_flag:
                        if mouth_side_vert_dist < 1:
                            print(f"Smiling! Time: {time_diff}s")
                            action_flag = True

                            thr = threading.Thread(target=send_requests, args=("smile", time_diff,))
                            thr.start()
                    if mouth_vert_dist / nose_mouth_gap > 0.7 and not (mouth_side_vert_dist < 2):
                        print(f"Yawning Time: {time_diff}s")
                        action_flag = True

                        thr = threading.Thread(target=send_requests, args=("yawn", time_diff,))
                        thr.start()
                if not action_flag:
                    print("No actions!")

        #print(i)
        #cv2.imshow("Image", img)
        #char = cv2.waitKey(1)


if __name__ == '__main__':
    main()