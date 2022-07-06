import cv2
import mediapipe as mp
import time


class handDetector():
    def __init__(self, mode = False, maxHands = 2, modelcomplexity = 1, detectioncon = 0.5, trackcon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelcomplexity = modelcomplexity
        self.detectioncon = detectioncon
        self.trackcon = trackcon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelcomplexity,
                                        self.detectioncon, self.trackcon)
        self.mpDraw = mp.solutions.drawing_utils


    def findHands(self, img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(self.results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, 
                                                self.mpHands.HAND_CONNECTIONS)
        return img


    def findPosition(self, img, normalize = 0, draw = True):

        lmList = []

        if self.results.multi_hand_landmarks:
            myhand = self.results.multi_hand_landmarks[normalize]
            for id, Lm in enumerate(myhand.landmark):
                # print(id, Lm)
                h, w, c = img.shape
                cx, cy = int(Lm.x * w), int(Lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

        return lmList



def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)


        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == 27:
            break
    
    cv2.destroyAllWindows()
    exit()





if __name__ == "__main__":
    main()