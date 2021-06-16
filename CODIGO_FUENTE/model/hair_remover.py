import numpy as np
import cv2 as cv

class HairRemover :

    __img = None
    __mask = None
    __active = False
    __img_result = None

    def __init__(self, image_input) :
        self.__img = image_input
        self.__img_result = self.__img.copy()
        self.__mask = np.zeros(self.__img.shape[:2], np.uint8)
            

    def __RemoveLines(self, img, mask):
            
        dst = cv.inpaint(img, mask, 3, cv.INPAINT_TELEA)
        return dst


    def __drawLine(self, event, x, y, flags, param) :
        
        if event == cv.EVENT_LBUTTONDOWN :
            self.__active = True

        elif event == cv.EVENT_MOUSEMOVE:
            if self.__active :
                    
                self.__img[y,x] = 255
                cv.circle(self.__img, (x, y), 5, [0, 0, 255], -1)

                self.__mask[y,x] = 255
                cv.circle(self.__mask, (x, y), 5, 255, -1)

        elif event == cv.EVENT_LBUTTONUP:
            self.__active = False
            self.__img_result[:] = self.__RemoveLines(self.__img_result, self.__mask)


    def removeHair(self): 
        
        cv.namedWindow("Imagen")
        cv.setMouseCallback("Imagen", self.__drawLine)

        while True :
            cv.imshow("Imagen", self.__img)
            cv.imshow("resultado", self.__img_result)
            
            if cv.waitKey(20) & 0xFF == 113:
                break

        cv.destroyAllWindows()

        return self.__img_result
