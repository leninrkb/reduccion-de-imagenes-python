from PyQt5.QtWidgets import QFileDialog, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import uic
import cv2
import numpy as np
import time
import os

class VentanaPrincipal(QMainWindow): 
    def __init__(self): 
        super().__init__()
        uic.loadUi('gui_main.ui', self) 
        self.pushButton_ver_marco.clicked.connect(self.ver_marco_reduccion)
        self.pushButton_cargar_img.clicked.connect(self.seleccionar_archivo)
        self.pushButton_aplicar_reduccion.clicked.connect(self.aplicar_cambios)
        self.spinBox_ancho.valueChanged.connect(self.cambio_spin)
        self.spinBox_alto.valueChanged.connect(self.cambio_spin)
        self.label_procesando.setText('sin procesos')
        self.checkBox_ajustar_resultante.setEnabled(False)
        self.checkBox_ajustar_resultante.stateChanged.connect(self.ajustar_imagen_resultante)
        self.pushButton_descargar_nuevaimg.clicked.connect(self.descargar_img)

    def cambio_spin(self):
            self.label_marco.clear()
            self.label_img_resultante.clear()
            self.pushButton_aplicar_reduccion.setEnabled(False)
            self.pushButton_descargar_nuevaimg.setEnabled(False)
            self.label_procesando.setText('sin procesos')
            self.checkBox_ajustar_resultante.setEnabled(False)

    def extraer_marco(self, alto, ancho, maxancho, maxalto):
        print(alto, ancho, maxancho, maxalto)
        imagen = self.imgcv[0:alto,0:ancho]
        altoimg, anchoimg, channels = imagen.shape
        bytes_linea = channels * anchoimg
        q_image = QImage(imagen.data.tobytes(), anchoimg, altoimg, bytes_linea, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        if alto > ancho:
            pixmap = pixmap.scaledToHeight(maxalto - 2)
        else:
            pixmap = pixmap.scaledToWidth(maxancho - 2)
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

    def reducir_matriz(self,img, alto_original, ancho_original, alto, ancho):
        canalr, canalg, canalb = cv2.split(img)
        nuevo_canal_r = []
        nuevo_canal_g = []
        nuevo_canal_b = []
        t = 0
        pxs = (alto_original/alto) * (ancho_original/ancho)
        for i in range(0, alto_original - alto, alto):
            fila_r = []
            fila_g = []
            fila_b = []
            for j in range(0, ancho_original - ancho, ancho):
                t+=1
                print(f'{t} de {pxs}')
                pixels_r = canalr[i:i + alto, j:j + ancho]
                pixels_g = canalg[i:i + alto, j:j + ancho]
                pixels_b = canalb[i:i + alto, j:j + ancho]
                if self.radioButton_media.isChecked():
                    pixel_r = np.mean(pixels_r)
                    pixel_g = np.mean(pixels_g)
                    pixel_b = np.mean(pixels_b)
                else:
                    pixel_r = np.median(pixels_r)
                    pixel_g = np.median(pixels_g)
                    pixel_b = np.median(pixels_b)
                fila_r.append(pixel_r)
                fila_g.append(pixel_g)
                fila_b.append(pixel_b)
            t+=1
            print(f'{t} de {pxs}')
            nuevo_canal_r.append(fila_r)
            nuevo_canal_g.append(fila_g)
            nuevo_canal_b.append(fila_b)
        print('terminado')
        nuevo_canal_r = np.array(nuevo_canal_r)
        nuevo_canal_g = np.array(nuevo_canal_g)
        nuevo_canal_b = np.array(nuevo_canal_b)
        nuevo_canal_r = nuevo_canal_r.astype(np.uint8)
        nuevo_canal_g = nuevo_canal_g.astype(np.uint8)
        nuevo_canal_b = nuevo_canal_b.astype(np.uint8)
        return nuevo_canal_r, nuevo_canal_g, nuevo_canal_b
    
    def  descargar_img(self):
        directorio = QFileDialog.getExistingDirectory(ventana, 'Seleccionar directorio')
        if directorio:
            archivo = directorio+f'/{int(time.time())}_img.jpg'
            img = cv2.cvtColor(self.img_resultante, cv2.COLOR_BGR2RGB)
            cv2.imwrite(archivo,img)
            self.label_procesando.setText(f'imagen descargada en {directorio}')

    def ajustar_imagen_resultante(self):
        self.label_img_resultante.clear()
        pixmap_aux = self.pixmap_resultante
        if self.checkBox_ajustar_resultante.isChecked():
            if self.pixmap_resultante.height() > self.pixmap_resultante.width():
                pixmap_aux = self.pixmap_resultante.scaledToHeight(self.label_img_resultante.height()-2)
            else:
                pixmap_aux = self.pixmap_resultante.scaledToWidth(self.label_img_resultante.width()-2)
        self.label_img_resultante.setPixmap(pixmap_aux)

    def aplicar_media(self):
        # canalr, canalg, canalb = cv2.split(self.imgcv)
        # canalr = self.reducir_matriz(canalr, self.imgcv_alto, self.imgcv_ancho, self.alto, self.ancho)
        # canalg = self.reducir_matriz(canalg, self.imgcv_alto, self.imgcv_ancho, self.alto, self.ancho)
        # canalb = self.reducir_matriz(canalb, self.imgcv_alto, self.imgcv_ancho, self.alto, self.ancho)
        canalr, canalg, canalb = self.reducir_matriz(self.imgcv, self.imgcv_alto, self.imgcv_ancho, self.alto, self.ancho)
        
        self.img_resultante = cv2.merge([canalr, canalg, canalb])
        altoimg, anchoimg, channels = self.img_resultante.shape
        bytes_linea = channels * anchoimg
        q_image = QImage(self.img_resultante.data.tobytes(), anchoimg, altoimg, bytes_linea, QImage.Format_RGB888)
        self.pixmap_resultante = QPixmap.fromImage(q_image)
        self.ajustar_imagen_resultante()
        self.label_dimensiones_resultante.setText(f'Media - Ancho:{anchoimg} x Alto:{altoimg}')

    def aplicar_mediana(self):
        canalr, canalg, canalb = self.reducir_matriz(self.imgcv, self.imgcv_alto, self.imgcv_ancho, self.alto, self.ancho)
        self.img_resultante = cv2.merge([canalr, canalg, canalb])
        altoimg, anchoimg, channels = self.img_resultante.shape
        bytes_linea = channels * anchoimg
        q_image = QImage(self.img_resultante.data.tobytes(), anchoimg, altoimg, bytes_linea, QImage.Format_RGB888)
        self.pixmap_resultante = QPixmap.fromImage(q_image)
        self.ajustar_imagen_resultante()
        self.label_dimensiones_resultante.setText(f'Mediana - Ancho:{anchoimg} x Alto:{altoimg}')

    def aplicar_cambios(self):
        self.label_procesando.setText('procesando imagen...')
        QApplication.processEvents()
        if self.radioButton_media.isChecked():
            inicio = time.time()  
            self.aplicar_media()
            fin = time.time()
            self.label_procesando.setText(f'ejecutado en:{int(fin - inicio)} s')
        else:
            inicio = time.time()
            self.aplicar_mediana()
            fin = time.time()
            self.label_procesando.setText(f'ejecutado en:{int(fin - inicio)} s')
        self.pushButton_descargar_nuevaimg.setEnabled(True)
        self.checkBox_ajustar_resultante.setEnabled(True)

        
    def leer_img(self, ruta):
        ruta_absoluta = os.path.abspath(ruta)
        ruta_normalizada = os.path.normpath(ruta_absoluta)
        img = QPixmap(ruta_normalizada)
        self.imgcv = cv2.imread(ruta_normalizada)
        self.imgcv = cv2.cvtColor(self.imgcv, cv2.COLOR_BGR2RGB)
        self.imgcv_alto, self.imgcv_ancho, _ = self.imgcv.shape
        self.label_dimensiones_original.setText(f'Ancho:{self.imgcv_ancho} x Alto:{self.imgcv_alto}')
        self.label_img_original.setPixmap(img)
        label_width = self.label_img_original.width()
        label_height = self.label_img_original.height()
        if img.height() > img.width():
            img = img.scaledToHeight(label_height-2)
        else:
            img = img.scaledToWidth(label_width-2)
        self.label_img_original.setPixmap(img)
        self.label_marco.clear()
        self.label_img_resultante.clear()
        self.pushButton_ver_marco.setEnabled(True)
        self.pushButton_aplicar_reduccion.setEnabled(False)
        self.pushButton_descargar_nuevaimg.setEnabled(False)
        self.spinBox_ancho.setValue(2)
        self.spinBox_alto.setValue(2)
        self.label_dimensiones_resultante.setText(f'Ancho: x Alto:')
        self.label_procesando.setText('sin procesos')


    def seleccionar_archivo(self):
        archivo = QFileDialog()
        archivo.setWindowTitle("Seleccionar imagen")
        archivo.setFileMode(QFileDialog.ExistingFile)
        if archivo.exec_():
            ruta = archivo.selectedFiles()
            ruta = ruta[0]
            self.leer_img(ruta)

app = QApplication([])
ventana = VentanaPrincipal()
ventana.show()
app.exec()