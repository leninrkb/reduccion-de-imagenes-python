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
        self.radioButton_media.toggled.connect(self.cambio_radio)
        self.radioButton_mediana.toggled.connect(self.cambio_radio)
        self.label_procesando.setText('sin procesos')
        self.checkBox_ajustar_resultante.setEnabled(False)
        self.checkBox_ajustar_resultante.stateChanged.connect(self.ajustar_imagen_resultante)
        self.pushButton_descargar_nuevaimg.clicked.connect(self.descargar_img)

    def modo_aplicar_cambios(self):
        self.label_img_resultante.clear()
        self.label_procesando.setText('procesando imagen...')
        self.label_dimensiones_resultante.setText('procesando imagen...')
        self.frame_radio_opciones.setEnabled(False)
        self.pushButton_cargar_img.setEnabled(False)
        self.spinBox_ancho.setEnabled(False)
        self.spinBox_alto.setEnabled(False)
        self.pushButton_ver_marco.setEnabled(False)
        self.pushButton_aplicar_reduccion.setEnabled(False)
        self.checkBox_ajustar_resultante.setEnabled(False)
        self.pushButton_descargar_nuevaimg.setEnabled(False)
        QApplication.processEvents()

    def fin_modo_aplicar_cambios(self):
        self.pushButton_cargar_img.setEnabled(True)
        self.spinBox_ancho.setEnabled(True)
        self.spinBox_alto.setEnabled(True)
        self.frame_radio_opciones.setEnabled(True)
        self.pushButton_ver_marco.setEnabled(True)
        self.pushButton_aplicar_reduccion.setEnabled(True)
        self.checkBox_ajustar_resultante.setEnabled(True)
        self.pushButton_descargar_nuevaimg.setEnabled(True)

    def cambio_radio(self):
        self.label_img_resultante.clear()
        self.pushButton_descargar_nuevaimg.setEnabled(False)
        self.label_procesando.setText('sin procesos')
        self.checkBox_ajustar_resultante.setEnabled(False)

    def cambio_spin(self):
        self.label_marco.clear()
        self.label_img_resultante.clear()
        self.pushButton_aplicar_reduccion.setEnabled(False)
        self.pushButton_descargar_nuevaimg.setEnabled(False)
        self.label_procesando.setText('sin procesos')
        self.label_dimensiones_resultante.setText('sin procesos')
        self.checkBox_ajustar_resultante.setEnabled(False)
    
    def imgcv2pixmap(self, img):
        altoimg, anchoimg, channels = img.shape
        bytes_linea = channels * anchoimg
        q_image = QImage(img.data.tobytes(), anchoimg, altoimg, bytes_linea, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        return pixmap
    
    def extraer_marco(self, alto, ancho, maxancho, maxalto):
        imagen = self.imgcv[0:alto,0:ancho]
        pixmap = self.imgcv2pixmap(imagen)
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
        for i in range(0, alto_original - alto + 1, alto):
            fila_r = []
            fila_g = []
            fila_b = []
            for j in range(0, ancho_original - ancho + 1, ancho):
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
            nuevo_canal_r.append(fila_r)
            nuevo_canal_g.append(fila_g)
            nuevo_canal_b.append(fila_b)

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
            idtiempo = int(time.time())
            titulo = f'/{idtiempo}_media_img.jpg' if self.radioButton_media.isChecked() else  f'/{idtiempo}_mediana_img.jpg'
            archivo = directorio + titulo
            img = cv2.cvtColor(self.img_resultante, cv2.COLOR_BGR2RGB)
            cv2.imwrite(archivo,img)
            self.label_procesando.setText(f'imagen descargada en {directorio}')

    def ajustar_imagen_resultante(self):
        pixmap_aux = self.pixmap_resultante
        if self.checkBox_ajustar_resultante.isChecked():
            if self.pixmap_resultante.height() > self.pixmap_resultante.width():
                pixmap_aux = self.pixmap_resultante.scaledToHeight(self.label_img_resultante.height()-2)
            else:
                pixmap_aux = self.pixmap_resultante.scaledToWidth(self.label_img_resultante.width()-2)
        self.label_img_resultante.setPixmap(pixmap_aux)

    def aplicar_media_mediana(self):
        canalr, canalg, canalb = self.reducir_matriz(self.imgcv, self.imgcv_alto, self.imgcv_ancho, self.alto, self.ancho)
        self.img_resultante = cv2.merge([canalr, canalg, canalb])
        self.pixmap_resultante = self.imgcv2pixmap(self.img_resultante)
        self.ajustar_imagen_resultante()
        opcion = 'Media' if self.radioButton_media.isChecked() else 'Mediana'
        self.label_dimensiones_resultante.setText(f'{opcion} - Ancho:{self.pixmap_resultante.width()} x Alto:{self.pixmap_resultante.height()}')

    def aplicar_cambios(self):
        self.modo_aplicar_cambios()
        inicio = time.time()  
        self.aplicar_media_mediana()
        fin = time.time()
        self.fin_modo_aplicar_cambios()
        self.label_procesando.setText(f'ejecutado en:{int(fin - inicio)} s')

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
        self.spinBox_ancho.setValue(1)
        self.spinBox_alto.setValue(1)
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