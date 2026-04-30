import cv2 as cv
import numpy as np

def nothing(x): pass

cap = cv.VideoCapture(0)

cv.namedWindow("Tuner", cv.WINDOW_NORMAL)
for name, val in [("H_lo",0),("H_hi",179),("S_lo",0),("S_hi",255),("V_lo",0),("V_hi",255)]:
    cv.createTrackbar(name, "Tuner", val, 179 if "H" in name else 255, nothing)

while True:
    ret, frame = cap.read()
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    lo = np.array([cv.getTrackbarPos(n, "Tuner") for n in ["H_lo","S_lo","V_lo"]])
    hi = np.array([cv.getTrackbarPos(n, "Tuner") for n in ["H_hi","S_hi","V_hi"]])
    mask = cv.inRange(hsv, lo, hi)
    result = cv.bitwise_and(frame, frame, mask=mask)
    cv.imshow("Tuner", result)
    cv.imshow("Camera", frame)
    
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()