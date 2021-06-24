import cv2
import cvlib as cv 
from cvlib.object_detection import draw_bbox
import serial

ser = serial.Serial('/dev/serial0', 9600) # UART 통신을 위한 serial 연결
cam = cv2.VideoCapture(0) #  첫번째(0) 카메라를 VideoCapture 타입의 객체로 얻어옵니다.


while cam.isOpened(): # 캠이 열린 경우
	se, frame = cam.read()

	bbox, label, conf = cv.detect_common_objects(frame) # 물체 검출
	print(bbox, label, conf)
	
        # draw bounding box over detected objects (검출된 물체 가장자리에 바운딩 박스 그리기)
	out = draw_bbox(frame, bbox, label, conf, write_conf=True)

        # display 출력 
	cv2.imshow("test", out)

	# Q 눌렀을 경우 stop
	if cv2.waitKey(1) & 0xFF == ord('q'): 
		break

	# person 객체의 개수 count 
	person_count = str(label.count('person'))

	#UART serial 통신으로 person 수 송신
	ser.write((person_count).encode())
	
	print("person count: "+ person_count)
	
# release resources    
cv2.destroyAllWindows()
	
