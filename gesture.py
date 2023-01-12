import cv2  
import mediapipe as mp
import numpy as np
import pyautogui

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("gesture-d7295-firebase-adminsdk-m4t20-5dc3cd1a5c.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://gesture-d7295-default-rtdb.firebaseio.com/' 
})

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles

temp = []
temp.append(0), temp.append(0), temp.append(0), temp.append(0)
t_x = t_y = -1
isOn = isPlay = False
volume = 0

dir = db.reference()
dir.update({'Kon':0})
dir.update({'Switch':0})
dir.update({'Volume':0})
dir.update({'Play':0})

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    while cap.isOpened():
        success, image = cap.read()

        h,w,c = image.shape

        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        image.flags.writeable = False
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_height, image_width, _ = image.shape

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                th_x = hand_landmarks.landmark[4].x*image_width
                th_y = hand_landmarks.landmark[4].y*image_height
                i_x = hand_landmarks.landmark[8].x*image_width
                i_y = hand_landmarks.landmark[8].y*image_height
                m_x = hand_landmarks.landmark[12].x*image_width
                m_y = hand_landmarks.landmark[12].y*image_height
                r_x = hand_landmarks.landmark[16].x*image_width
                r_y = hand_landmarks.landmark[16].y*image_height
                p_x = hand_landmarks.landmark[20].x*image_width
                p_y = hand_landmarks.landmark[20].y*image_height

                if int(i_x)+100 >= int(m_x) >= int(i_x)-100 and int(i_y)+50 >= int(m_y) >= int(i_y)-50:
                    if t_y-10 > i_y:
                        if isOn: temp[0]=0
                        else:
                            temp[0] += 1
                            if temp[0] > 9:
                                print('turn on\n')
                                temp[0] = 0
                                isOn = True
                                dir.update({'Switch':1})

                    elif t_y+10 < i_y:
                        if not isOn: temp[0]=0
                        else:
                            temp[0] -= 1
                            if temp[0] < -9:
                                print('turn off\n')
                                temp[0] = 0
                                isOn = False
                                dir.update({'Switch':0})
                    
                    elif t_x-10 > i_x:
                        temp[1] += 1
                        if temp[1] > 7:
                            temp[1] = 0
                            if volume: volume -= 1
                            print(f'volume down : {volume}\n')
                            dir.update({'Volume':volume})

                    elif t_x+10 < i_x:
                        temp[1] -= 1
                        if temp[1] < -7:
                            temp[1] = 0
                            if volume<10: volume += 1
                            print(f'volume up : {volume}\n')
                            dir.update({'Volume':volume})

                    elif int(th_y)+50 >= int(i_y) >= int(th_y)-50 and int(th_x)+10 >= int(i_x) >= int(th_x)-10:
                        temp[2] += 1
                        if isPlay and temp[2]>9:
                            print("pause\n")
                            isPlay = False
                            temp[2] = 0
                            dir.update({'Play':0})
                        elif not isPlay and temp[2]>9:
                            print("play\n")
                            isPlay = True
                            temp[2] = 0
                            dir.update({'Play':1})

                if int(th_y)+50 >= int(m_y) >= int(th_y)-50 and int(th_y)+50 >= int(r_y) >= int(th_y)-50 and not int(th_y)+100 >= int(i_y) >= int(th_y)-250 and not int(th_y)+100 >= int(p_y) >= int(th_y)-250:
                    print("콩.")
                    dir.update({'Kon':1})
                    import cv2
                    image = cv2.imread("Kon.jpg", cv2.IMREAD_ANYCOLOR)
                    cv2.imshow("Kon", image)
                    cv2.waitKey()
                    cv2.destroyAllWindows()
                    quit()

                t_x = i_x
                t_y = i_y

cap.release()