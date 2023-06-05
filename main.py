from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import uic
import cv2
import numpy as np
from statistics import mean

class VentanaPrincipal(QMainWindow): 
    def __init__(self): 
        super().__init__()
        uic.loadUi('gui_main.ui', self) 
        self.pushButton_ver_marco.clicked.connect(self.ver_marco_reduccion)
        self.pushButton_cargar_img.clicked.connect(self.seleccionar_archivo)
        self.pushButton_aplicar_reduccion.clicked.connect(self.aplicar_cambios)
    
    def extraer_marco(self, alto, ancho, maxancho, maxalto):
        print(alto, ancho, maxancho, maxalto)
        imagen = self.imgcv[0:alto,0:ancho]
        altoimg, anchoimg, channels = imagen.shape
        bytes_linea = channels * anchoimg
        q_image = QImage(imagen.data.tobytes(), anchoimg, altoimg, bytes_linea, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        if alto > ancho:
            pixmap = pixmap.scaledToHeight(maxalto)
        else:
            pixmap = pixmap.scaledToWidth(maxancho)
        return pixmap
    
    def ver_marco_reduccion(self):
        self.alto = self.spinBox_alto.value()
        self.ancho = self.spinBox_ancho.value()
        if self.alto > self.imgcv_alto:
            self.alto = self.imgcv_alto
            self.spinBox_alto.setValue(self.imgcv_alto)
        if self.ancho > self.imgcv_ancho:
            self.ancho = self.imgcv_ancho
            self.spinBox_ancho.setValue(self.imgcv_ancho)
        pixmap = self.extraer_marco(self.alto, self.ancho, self.label_marco.width(), self.label_marco.height())
        self.label_marco.setPixmap(pixmap)
        self.pushButton_aplicar_reduccion.setEnabled(True)

    def reducir_matriz(self,canal, alto_original, ancho_original, alto, ancho):
        nuevaimg = []
        for i in range(0, alto_original - alto, alto):
            fila = []
            for j in range(0, ancho_original - ancho, ancho):
                pixels = canal[i:i + alto, j:j + ancho]
                pixel = np.mean(pixels)
                fila.append(pixel)
            nuevaimg.append(fila)
        nuevaimg = np.array(nuevaimg)
        nuevaimg = nuevaimg.astype(np.uint8)
        return nuevaimg
    
    def aplicar_media(self):
        canalr, canalg, canalb = cv2.split(self.imgcv)
        canalr = self.reducir_matriz(canalr, self.imgcv_alto, self.imgcv_ancho, self.alto, self.ancho)
        canalg = self.reducir_matriz(canalg, self.imgcv_alto, self.imgcv_ancho, self.alto, self.ancho)
        canalb = self.reducir_matriz(canalb, self.imgcv_alto, self.imgcv_ancho, self.alto, self.ancho)
        nuevaimg = cv2.merge([canalr, canalg, canalb])
        altoimg, anchoimg, channels = nuevaimg.shape
        bytes_linea = channels * anchoimg
        q_image = QImage(nuevaimg.data.tobytes(), anchoimg, altoimg, bytes_linea, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        if pixmap.height() > pixmap.width():
            pixmap = pixmap.scaledToHeight(self.label_img_resultante.height())
        else:
            pixmap = pixmap.scaledToWidth(self.label_img_resultante.width())
        self.label_img_resultante.setPixmap(pixmap)
        self.label_dimensiones_resultante.setText(f'Ancho:{anchoimg} x Alto:{altoimg}')

    def aplicar_cambios(self):
        if self.radioButton_media.isChecked():
            print('haciendo la media')
            self.aplicar_media()
        else:
            print('haciendo la mediana')
        self.pushButton_descargar_nuevaimg.setEnabled(True)
        
    def leer_img(self, ruta):
        img = QPixmap(ruta)
        self.imgcv = cv2.imread(ruta)
        self.imgcv = cv2.cvtColor(self.imgcv, cv2.COLOR_BGR2RGB)
        self.imgcv_alto, self.imgcv_ancho, _ = self.imgcv.shape
        self.label_dimensiones_original.setText(f'Ancho:{self.imgcv_ancho} x Alto:{self.imgcv_alto}')
        self.label_img_original.setPixmap(img)
        label_width = self.label_img_original.width()
        label_height = self.label_img_original.height()
        if img.height() > img.width():
            img = img.scaledToHeight(label_height)
        else:
            img = img.scaledToWidth(label_width)
        self.label_img_original.setPixmap(img)
        self.label_marco.clear()
        self.label_img_resultante.clear()
        self.pushButton_ver_marco.setEnabled(True)
        self.pushButton_aplicar_reduccion.setEnabled(False)
        self.pushButton_descargar_nuevaimg.setEnabled(False)
        self.spinBox_ancho.setValue(2)
        self.spinBox_alto.setValue(2)
        self.label_dimensiones_resultante.setText(f'Ancho: x Alto:')


    def seleccionar_archivo(self):
        archivo = QFileDialog()
        archivo.setWindowTitle("Seleccionar imagen")
        archivo.setFileMode(QFileDialog.ExistingFile)
        if archivo.exec_():
            ruta = archivo.selectedFiles()
            self.leer_img(ruta[0])

app = QApplication([])
ventana = VentanaPrincipal()
ventana.show()
app.exec()