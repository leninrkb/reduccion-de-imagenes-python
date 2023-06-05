from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import uic
import cv2

class VentanaPrincipal(QMainWindow): 
    def __init__(self): 
        super().__init__()
        uic.loadUi('gui_main.ui', self) 
        self.pushButton_ver_marco.clicked.connect(self.ver_marco_reduccion)
        self.pushButton_cargar_img.clicked.connect(self.seleccionar_archivo)
    
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
        alto = self.spinBox_alto.value()
        ancho = self.spinBox_ancho.value()
        if alto > self.imgcv_alto:
            alto = self.imgcv_alto
            self.spinBox_alto.setValue(self.imgcv_alto)
        if ancho > self.imgcv_ancho:
            ancho = self.imgcv_ancho
            self.spinBox_ancho.setValue(self.imgcv_ancho)
        pixmap = self.extraer_marco(alto, ancho, self.label_marco.width(), self.label_marco.height())
        self.label_marco.clear()
        self.label_marco.setPixmap(pixmap)

    def leer_img(self, ruta):
        img = QPixmap(ruta)
        self.imgcv = cv2.imread(ruta)
        self.imgcv = cv2.cvtColor(self.imgcv, cv2.COLOR_BGR2RGB)
        self.imgcv_alto, self.imgcv_ancho, _ = self.imgcv.shape
        self.label_dimensiones_original.setText(f'Alto:{self.imgcv_alto} x Ancho:{self.imgcv_ancho}')
        self.label_img_original.setPixmap(img)
        label_width = self.label_img_original.width()
        label_height = self.label_img_original.height()
        if img.height() > img.width():
            img = img.scaledToHeight(label_height)
        else:
            img = img.scaledToWidth(label_width)
        self.label_img_original.setPixmap(img)
        self.pushButton_ver_marco.setEnabled(True)
        self.spinBox_ancho.setValue(2)
        self.spinBox_alto.setValue(2)

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