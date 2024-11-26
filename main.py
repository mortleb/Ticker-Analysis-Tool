from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PySide6 import QtCharts
from PySide6.QtCore import Qt, QDateTime
import fun
import sys
import numpy as np
from yahoo import Ui_MainWindow
from sauv import afficheur

class analyse(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(analyse, self).__init__()
        self.setupUi(self)
        self.bouton_confirm.clicked.connect(self.confirmation_ticker)
        self.bouton_confirm_comparaison.clicked.connect(self.confirmation_comparaison) 
        self.afficher_1.clicked.connect(self.afficher_one_ticker)
        self.afficher_2.clicked.connect(self.afficher_classeur)

        self.save_ticker = {}
        self.save_tickers = {}
    
    def afficher_one_ticker(self):
        if len(self.save_ticker) == 0:
            QMessageBox.critical(self, "Erreur", "Cliquez sur confirmer avant d'afficher le CSV !")
            return

        self.window_classeur = afficheur(text_1 = self.actif_a.text(), data_1 = self.save_ticker["data_1"])
        self.window_classeur.show()


    def afficher_classeur(self):
        if len(self.save_tickers) == 0:
            QMessageBox.critical(self, "Erreur", "Cliquez sur confirmer avant d'afficher le CSV !")
            return
        
        self.window_classeur = afficheur(text_1 = self.actif_a.text(), data_1 = self.save_tickers["data_1"], text_2 = self.actif_b.text(), data_2 = self.save_tickers["data_2"])
        self.window_classeur.show()

    def confirmation_ticker(self):
        infos = fun.obtenir_infos(self.ticker.text(), self.depart.text(), self.fin.text()) 

        if infos is None : 
            QMessageBox.critical(self, "Erreur", "Ticker inexistant ou dates incorrectes !")
            return
        
        self.save_ticker = {"data_1" : infos}
        
        self.linegraph(self.ticker.text(), data_1 = infos["data"])
        self.retours.setCurrentIndex(1)
        self.label_rendement.setText("Rendement")
        self.rendement.setText(str(infos["rendement"])+"%")
        self.label_vol.setText("Volatilité (en %)")
        self.vol.setText(str(infos["volatilite"])+"%")

    def confirmation_comparaison(self):
        actif_a = fun.obtenir_infos(self.actif_a.text(), self.depart_comparaison.text(), self.fin_comparaison.text()) 
        actif_b = fun.obtenir_infos(self.actif_b.text(), self.depart_comparaison.text(), self.fin_comparaison.text()) 

        
        if actif_a is None or actif_b is None: 
            QMessageBox.critical(self, "Erreur", "Ticker inexistant ou dates incorrectes !")
            return
        
        self.save_tickers = {"data_1" : actif_a, "data_2" : actif_b}

        self.linegraph(self.actif_a.text(), actif_a["data"], self.actif_b.text(), actif_b["data"])

        self.label_r_a.setText(f"Rendement de {self.actif_a.text()}")
        self.r_a.setText(str(actif_a["rendement"])+"%")
        self.label_r_b.setText(f"Rendement de {self.actif_b.text()}")
        self.r_b.setText(str(actif_b["rendement"])+"%")

        self.label_v_a.setText(f"Volatilité de {self.actif_a.text()} (en %)")
        self.v_a.setText(str(actif_a["volatilite"])+"%")
        self.label_v_b.setText(f"Volatilité de {self.actif_b.text()} (en %)")
        self.v_b.setText(str(actif_b["volatilite"])+"%")

        self.label_diff_r.setText(f"Spread Return")
        self.r_diff.setText(str(np.round(actif_a["rendement"] - actif_b["rendement"]))+"%")
        self.label_diff_v.setText(f"Spread Volatility")
        self.v_diff.setText(str(np.round(actif_a["volatilite"] - actif_b["volatilite"], 2))+"%")

        self.retours.setCurrentIndex(0)

    def linegraph(self, text_1, data_1, text_2 = None, data_2 = None):
        chart = QtCharts.QChart()
        if data_2 is not None:
            chart.setTitle(f"Comparaison de l'évolution du cours de {self.actif_a.text()} et de {self.actif_b.text()} entre le {self.depart_comparaison.text()} et le {self.fin_comparaison.text()} en base log")
        else : 
            chart.setTitle(f"Evolution du cours de {self.ticker.text()} entre le {self.depart.text()} et le {self.fin.text()}")

        series_data_1 = QtCharts.QLineSeries()
        series_data_1.setName(text_1)

        if data_2 is not None:
            series_data_2 = QtCharts.QLineSeries()
            series_data_2.setName(text_2)

            for i in range(len(data_2)):
                dates_2 = QDateTime.fromString(str(data_2["Date"].iloc[i]), "yyyy-MM-dd")
                series_data_2.append(float(dates_2.toMSecsSinceEpoch()), data_2["Close"].iloc[i])
            chart.addSeries(series_data_2)

        for i in range(len(data_1)):
            dates_1 = QDateTime.fromString(str(data_1["Date"].iloc[i]), "yyyy-MM-dd")
            series_data_1.append(float(dates_1.toMSecsSinceEpoch()), data_1["Close"].iloc[i])
        chart.addSeries(series_data_1)

        axis_x = QtCharts.QDateTimeAxis()
        if data_2 is not None:
            start_date_1 = QDateTime.fromString(str(data_1["Date"].iloc[0]), "yyyy-MM-dd").toMSecsSinceEpoch()
            start_date_2 = QDateTime.fromString(str(data_2["Date"].iloc[0]), "yyyy-MM-dd").toMSecsSinceEpoch()
            start_date = min(start_date_1, start_date_2)
            end_date_1 = QDateTime.fromString(str(data_1["Date"].iloc[-1]), "yyyy-MM-dd").toMSecsSinceEpoch()
            end_date_2 = QDateTime.fromString(str(data_2["Date"].iloc[-1]), "yyyy-MM-dd").toMSecsSinceEpoch()
            end_date = max(end_date_1, end_date_2)
        else:
            start_date = QDateTime.fromString(str(data_1["Date"].iloc[0]), "yyyy-MM-dd").toMSecsSinceEpoch()
            end_date = QDateTime.fromString(str(data_1["Date"].iloc[-1]), "yyyy-MM-dd").toMSecsSinceEpoch()
        axis_x.setRange(QDateTime.fromMSecsSinceEpoch(start_date), QDateTime.fromMSecsSinceEpoch(end_date))
        axis_x.setFormat("yyyy-MM-dd")
        axis_x.setTitleText("Date (in days from start date)")
        chart.addAxis(axis_x, Qt.AlignBottom)

        axis_y = QtCharts.QValueAxis() 
        marge_y = (max(data_1["Close"])- min(data_1["Close"])) * 0.05
        axis_y.setRange(min(data_1["Close"]) - marge_y, max(data_1["Close"]) + marge_y)
        axis_y.setTitleText(f"Close Value {self.actif_a.text()}")
        chart.addAxis(axis_y, Qt.AlignLeft)

        series_data_1.attachAxis(axis_x)
        series_data_1.attachAxis(axis_y)

        if data_2 is not None: 
            axis_z = QtCharts.QValueAxis()
            marge_z = (max(data_2["Close"])- min(data_2["Close"])) * 0.05
            axis_z.setRange(min(data_2["Close"]) - marge_z, max(data_2["Close"]) + marge_z)
            axis_z.setTitleText(f"Close Value {self.actif_b.text()}")
            chart.addAxis(axis_z, Qt.AlignRight)
            series_data_2.attachAxis(axis_x)
            series_data_2.attachAxis(axis_z)

        self.graph.setChart(chart)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = analyse()
    window.show()
    app.exec_()
