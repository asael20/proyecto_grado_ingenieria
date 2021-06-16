import sys
from math import pi
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
import cv2 as cv
import numpy as np
from views.static.main import Ui_MainWindow
from model.util import Util
from model.hair_remover import HairRemover

class App(Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.master = QMainWindow()
        self.setupUi(self.master)
        self.util = Util()

        self.btn_select_img.clicked.connect(self.chooseImage)
        self.btn_segment_img.clicked.connect(self.segmentLesion)
        self.btn_remove_hair.clicked.connect(self.removeHairLesion)
        self.btn_calc_asymm_index.clicked.connect(self.calculateAsymmIndex)
        self.btn_asymmArea_ve.clicked.connect(self.showAsymmAreaVertical)
        self.btn_asymmArea_ho.clicked.connect(self.showAsymmAreaHorizontal)
        self.btn_circularidad.clicked.connect(self.calculateCircularity)


        self.image_cv = None
        self.image_edge = None
        self.image_binary = None
        self.image_roi = None

        self.length_border_roi = 0
        self.area_roi = 0
        self.box_roi = None
        self.edge_roi = None
        self.vertical_asymmArea = None
        self.horizontal_asymmArea = None

        self.coord_centroid = (0, 0)
        self.edge_pixels = []


    def chooseImage(self):

        image = self.util.getImage()

        if image is not None:
            self.image_cv = self.util.resizeImage(image.copy(), .5)
            image = self.util.setColorSpace(self.image_cv, 1)

            self.setImage(image, self.label_img_main, QImage.Format_RGB888)
            self.setImage(image, self.label_img_work, QImage.Format_RGB888)

            self.label_circularidad_indx.setText("")
            self.label_indxasym_lesion.setText("")
            self.label_indxasym_ve.setText("")
            self.label_indxasym_ho.setText("")

        else:
            message = QMessageBox()
            message.setText("Archivo no valido")
            message.exec_()


    def segmentLesion(self):

        if self.image_cv is None :
            message = QMessageBox()
            message.setText("Debe escoger una imagen para realizar esta acción ")
            message.exec_()

            return

        grayImage = self.util.setColorSpace(self.image_cv, 0)
        self.image_edge, self.image_binary = self.util.extractEdge(grayImage)   
        
        resp = self.util.findBox_roi(self.image_binary)
                
        if resp == None :
            message = QMessageBox()
            message.setText("La imagen no es adecuada, intente usar la remoción de cabello")
            message.exec_()

            return


        self.box_roi, start, end = resp

        mask = np.zeros(self.image_binary.shape, np.uint8)
        self.image_binary[:] = 0

        mask[start[0]-1:start[0]+end[0]+1, start[1]-1:start[1]+end[1]+1] = self.box_roi
        self.image_binary[start[0]-1:start[0]+end[0]+1, start[1]-1:start[1]+end[1]+1] = self.box_roi

        ret = cv.bitwise_and(self.image_cv, self.image_cv,mask=mask)
        self.edge_roi = self.util.findEdge_boxRoi(self.box_roi)

       
        self.area_roi = self.util.countPixelsROI(self.box_roi)
        self.length_border_roi = self.util.countPixelsROI(self.edge_roi)
   

        self.setImage(self.image_binary, self.label_img_binary, QImage.Format_Grayscale8)
        self.setImage(self.edge_roi, self.label_img_roi_edge, QImage.Format_Grayscale8)
        self.setImage(ret, self.label_img_segmented, QImage.Format_BGR888)


    def calculateAsymmIndex(self):

        if self.image_binary is None :
            message = QMessageBox()
            message.setText("Se requiere una imagen binaria ")
            message.exec_()

            return

        self.vertical_asymmArea, self.horizontal_asymmArea = self.util.findAssymmetric(self.image_binary)

        area_asymm_ve = self.util.countPixelsROI(self.vertical_asymmArea)
        area_asymm_ho = self.util.countPixelsROI(self.horizontal_asymmArea)
        
        vertical_asymm_index = area_asymm_ve / self.area_roi
        horizontal_asymm_index = area_asymm_ho / self.area_roi
        lesion_asymm_index = (vertical_asymm_index+horizontal_asymm_index)/2
   
        print(f"Area region asimetrica [Vertical] = {area_asymm_ve}")
        print(f"Area region asimetrica [Horizontal] = {area_asymm_ho}")

        print("")

        print(f"Indice de asimetría [Vertical] = {vertical_asymm_index} -> {vertical_asymm_index*100} %")
        print(f"Indice de asimetría [Horizontal] = {horizontal_asymm_index} -> {horizontal_asymm_index*100} %")
        
        self.label_indxasym_ve.setText(str(vertical_asymm_index))
        self.label_indxasym_ho.setText(str(horizontal_asymm_index))
        self.label_indxasym_lesion.setText(str(lesion_asymm_index))


    def showAsymmAreaVertical(self):

        if self.vertical_asymmArea is None :
            message = QMessageBox()
            message.setText("Debe calcular el índex de asimetría ")
            message.exec_()

            return

        self.util.showImageOpenCV(self.vertical_asymmArea, "Area asimetrica Eje Vertical")


    def showAsymmAreaHorizontal(self):
        if self.horizontal_asymmArea is None :
            message = QMessageBox()
            message.setText("Debe calcular el índex de asimetría ")
            message.exec_()

            return

        self.util.showImageOpenCV(self.horizontal_asymmArea, "Area asimetrica Eje Horizontal")
   

    def calculateCircularity(self):

        if self.image_binary is None :
            message = QMessageBox()
            message.setText("Se requiere una imagen binaria ")
            message.exec_()

            return

        circ = (4*self.area_roi*pi)/(self.length_border_roi**2)
        self.label_circularidad_indx.setText(str(circ))
        self.util.generateConvexHull(self.box_roi)


    def setImage(self, image, label_image, qImageFormat):
        rows, columns = image.shape[0:2]
        bytesPerLine = image.strides[0]
        qImage = QImage(image, columns, rows, bytesPerLine, qImageFormat)

        label_image.setPixmap(QPixmap.fromImage(qImage))


    def removeHairLesion(self):

        if self.image_cv is None :
            message = QMessageBox()
            message.setText("Debe escoger una imagen para realizar esta acción ")
            message.exec_()

            return

        remover = HairRemover(self.image_cv.copy())
        resp = remover.removeHair()

        self.image_cv = resp
        image = self.util.setColorSpace(self.image_cv, 1)
        self.setImage(image, self.label_img_main, QImage.Format_RGB888)
