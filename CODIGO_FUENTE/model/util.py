from PyQt5.QtWidgets import QFileDialog
import cv2 as cv
import numpy as np
from math import pi

class Util:

    def __init__(self):
        pass

    def getImage(self):
        patName = QFileDialog.getOpenFileName()[0]
        image = cv.imread(patName)
        return image
    

    def setColorSpace(self, image, color_format):
       
        if color_format == 0:
            space_color = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        elif color_format == 1:
            space_color = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        else:
            space_color = cv.cvtColor(image, cv.COLOR_RGB2BGR)

        return space_color


    def resizeImage(self, image, percent):
        return cv.resize(image, None, fx=percent, fy=percent, interpolation=cv.INTER_AREA)


    def extractEdge(self, grayImage):
        blurImage = cv.blur(grayImage, (5,5))
        
        thresh_val, image_thresh = cv.threshold(blurImage, 0, 255, cv.THRESH_OTSU + cv.THRESH_BINARY_INV)
        edgeImage = cv.Canny(image_thresh, 10, 50)

        dilated = cv.dilate(edgeImage, np.array([[255, 255, 255], [255, 255, 255], [255, 255, 255]]), iterations=1)

        return edgeImage, image_thresh


    def findCentroid(self, binaryImage_in):
        binaryImage = binaryImage_in.copy()
        moments = cv.moments(binaryImage)
        coord_x = int(moments["m10"] / moments["m00"])
        coord_y = int(moments["m01"] / moments["m00"])

        cv.circle(binaryImage, (coord_x, coord_y), 5, 255, -1)

        return binaryImage, (coord_x, coord_y)


    def selectForeground(self, image, binaryImage):

        image_out = np.array(image.copy())
        roi_edges = []
        rows, columns = binaryImage.shape
        row_index = 0

        while row_index < rows:
            column_index = 0
            while column_index < columns:
                pixel_val = binaryImage.item(row_index, column_index)
                if pixel_val == 255 and 20 <= row_index < rows - 20 and 20 <= column_index < columns - 20:
                    roi_edges.append((row_index, column_index))
                else:
                    image_out.itemset((row_index, column_index, 0), 0)
                    image_out.itemset((row_index, column_index, 1), 0)
                    image_out.itemset((row_index, column_index, 2), 0)
                column_index += 1
            row_index += 1

        return image_out, roi_edges


    def drawLineFromCenter(self, image, coordinate, orientation):
        image = image.copy()
        print(image.shape)
        x, y = coordinate
        if str(orientation).lower() == "vertical":
            image[:, x] = 255
        elif str(orientation).lower() == "horizontal":
            image[y, :] = 255
        else:
            image[:, x] = 255
            image[y, :] = 255

        mask = image[:, 0:x + 1]
        result_flip = cv.flip(mask, 1)
        cv.imshow('mask', mask)
        cv.imshow("image", image)


    def trackEdge(self, image, edge_pixels):
        image = np.array(image * 0)

        for row, column in edge_pixels:
            image.itemset((row, column, 0), 255)
            image.itemset((row, column, 1), 255)
            image.itemset((row, column, 2), 255)
        else:
            print("terminó el recorido de los piexeles del borde")

        cv.imshow('ventana', image)
        cv.waitKey(0)
        cv.destroyAllWindows()


    def showImageOpenCV(self, image, name):

        cv.imshow(name, image)

        cv.waitKey(0)
        cv.destroyAllWindows()


    def removeHair(self, image, mask):
        mask = cv.dilate(mask, (5, 5))
        dts = cv.inpaint(image, mask, 5, cv.INPAINT_TELEA)

        return dts


    def generateConvexHull(self, edge_roi):
        if(edge_roi is None): return

        contours, _ = cv.findContours(edge_roi, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        hull_list = []

        cnt = []
        index = 0

        for i in range(len(contours)):

            if len(contours[i]) > len(cnt) :
                cnt = contours[i]
                index = i
        
            hull = cv.convexHull(contours[i])
            hull_list.append(hull)


        blackBoard = edge_roi.copy()        
        cv.drawContours(blackBoard, hull_list, index, 255)
        
        cv.imshow("Convex Hull", blackBoard)
        cv.waitKey(0)
        cv.destroyAllWindows()


    def findBox_roi(self, img): 
        n = 0
        if(img is None ): 
            return None

        contours, _ = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnt = None

        if len(contours) == 2 : 
            cnt, n = (contours[0], 0) if len(contours[0]) > len(contours[1]) else (contours[1], 1)
           
        else:
            item =  [];
            u = 0
            for i in contours:
                if i[0, 0][0] != 0:
                    if len(i) > len(item) :
                        item = i
                        n = u
                u += 1
            cnt = item

        x,y, w,h = cv.boundingRect(cnt)

        if y-1 <= 0 or x-1 <= 0 or y+h+1 >= img.shape[0] or x+w+1 >= img.shape[1]:
            return None

        box_roi = img[y-1:y+h+1, x-1:x+w+1].copy()
        
        return box_roi, (y, x), (h, w)


    def findEdge_boxRoi(self, box_roi):
        edgeImage = cv.Canny(box_roi.copy(), 10, 50)
        
        return edgeImage


    def findAssymmetric(self, img): 
        n = 0
        if(img is None ): 
            return None

        contours, _ = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cnt = None

        if len(contours) == 2 : 
            cnt, n = (contours[0], 0) if len(contours[0]) > len(contours[1]) else (contours[1], 1)
           
        else:
            item =  [];
            u = 0
            for i in contours:

                if i[0, 0][0] != 0:
                    if len(i) > len(item) :
                        item = i
                        n = u
                u += 1
            cnt = item

       
        img_copy = img.copy()
        
        x,y, w,h = cv.boundingRect(cnt)
        box_roi = img[y-1:y+h+1, x-1:x+w+1].copy()       

       
        edgeImage = cv.Canny(box_roi.copy(), 10, 50)
        _, coord = self.findCentroid(edgeImage.copy())
        box_h, box_w = box_roi.shape[0:2]

        eje_v = box_roi[0: box_h, 0:coord[0]]
        eje_v_inv = cv.flip(eje_v, 1)

        asymmetric_plane_v = img_copy[y:y+box_h, x+eje_v.shape[1]:].copy()
        eje_v_2 = asymmetric_plane_v[:, 0: eje_v.shape[1]]
      
        xor_v = cv.bitwise_xor(eje_v_inv, eje_v_2)
        asymmetric_plane_v[:, 0: eje_v.shape[1] ] = xor_v


        eje_h = box_roi[0:coord[1], 0:]
        eje_h_inv = cv.flip(eje_h, 0)

        asymmetric_plane_h = img_copy[y+eje_h.shape[0]: , x:x+box_w].copy()
        eje_h_2 = asymmetric_plane_h[0:eje_h.shape[0], :]
        
        xor_h = cv.bitwise_xor(eje_h_inv, eje_h_2)
        asymmetric_plane_h[0:eje_h.shape[0], :] = xor_h

        box_roi[coord[1], coord[0]] = 0;


        return asymmetric_plane_v, asymmetric_plane_h 


    def countPixelsROI(self, image):
        count_pixels = 0

        for row in image :
            for column in row :
                if column == 255 :
                    count_pixels += 1

        return count_pixels