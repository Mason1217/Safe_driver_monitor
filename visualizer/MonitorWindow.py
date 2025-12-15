from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QProgressBar,
)

from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
import pyqtgraph as pg

from data_preprocessor.DataAnalyzer import DATA_DICT_KEY, ALCOHOL_ST, FATIGUE_ST, MAX_HR, MIN_HR

pg.setConfigOption("background", 'w')
pg.setConfigOption("foreground", 'k')

class MonitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.graph_data_limit = 100
        self.x_data = list(range(self.graph_data_limit))
        self.y_data = [0] * self.graph_data_limit

        self.setup_ui()

    def setup_ui(self):
        '''
        Setup window appearance and widget layouts

        '''
        self.setWindowTitle("Fatigue & Alcohol Monitor")
        self.resize(1000, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.lbl_title = QLabel("Driver Status Dashboard")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        main_layout.addWidget(self.lbl_title)

        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_layout = QGridLayout(info_frame)
        info_layout.setVerticalSpacing(15)
        info_layout.setHorizontalSpacing(30)

        value_font = QFont("Arial", 30, QFont.Weight.Bold)
        label_font = QFont("Arial", 14)
        sub_label_font = QFont("Arial", 12)

        self.lbl_alcohol_title = QLabel("Alcohol")
        self.lbl_alcohol_title.setFont(label_font)

        self.lbl_alcohol_val = QLabel("0.00")
        self.lbl_alcohol_val.setFont(value_font)

        self.lbl_alcohol_status = QLabel(ALCOHOL_ST['N'])
        self.lbl_alcohol_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_hrv_title = QLabel("HRV")
        self.lbl_hrv_title.setFont(label_font)
        self.lbl_hrv_val = QLabel("--")
        self.lbl_hrv_val.setFont(value_font)

        self.lbl_fatigue_status = QLabel(FATIGUE_ST['A'])
        self.lbl_fatigue_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_baseline = QLabel("7-Day Avg: --")
        self.lbl_baseline.setFont(sub_label_font)
        self.lbl_baseline.setStyleSheet("color: gray;")

        self.lbl_fatigue_idx_title = QLabel("Fatigue Index (0-100)")
        self.lbl_fatigue_idx_title.setFont(sub_label_font)

        self.pbar_fatigue = QProgressBar()
        self.pbar_fatigue.setRange(0, 100)
        self.pbar_fatigue.setValue(0)
        self.pbar_fatigue.setTextVisible(True)
        self.pbar_fatigue.setFixedHeight(30)

        info_layout.addWidget(self.lbl_alcohol_title, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.lbl_alcohol_val, 1, 0, alignment=Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.lbl_alcohol_status, 2, 0)

        info_layout.addWidget(self.lbl_hrv_title, 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.lbl_hrv_val, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.lbl_baseline, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.lbl_fatigue_status, 3, 1)
        main_layout.addWidget(info_frame)

        info_layout.addWidget(self.lbl_fatigue_idx_title, 4, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignBottom)
        info_layout.addWidget(self.pbar_fatigue, 5, 0, 1, 2)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setTitle("Heart Rate", color='k')
        self.graphWidget.setLabel("left", "BPM", color='k')
        self.graphWidget.setLabel("bottom", "Samples", color='k')
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setYRange(MIN_HR, MAX_HR)

        self.data_line = self.graphWidget.plot(
            self.x_data,
            self.y_data,
            pen=pg.mkPen(color='b', width=2)
        )

        main_layout.addWidget(self.graphWidget)

    def update_display(self, data_dict: dict):
        '''
        Update UI based on data received from server.

        '''
        if data_dict is None:
            return
        
        alcohol = data_dict.get(DATA_DICT_KEY["al"], 0.0)
        hrv     = data_dict.get(DATA_DICT_KEY["hrv"], 0.0)
        hr      = data_dict.get(DATA_DICT_KEY["hr"], -1)
        al_st   = data_dict.get(DATA_DICT_KEY["al_st"])
        f_st    = data_dict.get(DATA_DICT_KEY["f_st"], FATIGUE_ST['A'])
        f_idx   = data_dict.get(DATA_DICT_KEY["f_idx"], 0)
        base    = data_dict.get(DATA_DICT_KEY["base"], 0.0)


        self.lbl_alcohol_val.setText(f"{alcohol:.2f}")
        self.lbl_alcohol_status.setText(al_st)

        if al_st == ALCOHOL_ST['D']:
            self.lbl_alcohol_val.setStyleSheet("color: red")
            self.lbl_alcohol_status.setStyleSheet("background-color: red; color: white; padding: 5px;")
        else:
            self.lbl_alcohol_val.setStyleSheet("color: black")
            self.lbl_alcohol_status.setStyleSheet("background-color: green; color: white; padding: 5px;")

        self.lbl_hrv_val.setText(f"{hrv:.2f}")
        self.lbl_baseline.setText(f"7-Day Avg: {base:.1f} ms")
        self.lbl_fatigue_status.setText(f_st)
        
        if f_st == FATIGUE_ST['N'] or f_st == FATIGUE_ST['B']:
            status_style = "background-color: green; color: white; padding: 5px;"
            text_color = "color: black"
        elif f_st == FATIGUE_ST['U']:
            status_style = "background-color: orange; color: white; padding: 5px;"
            text_color = "color: orange"
        elif f_st == FATIGUE_ST['L'] or f_st == FATIGUE_ST['F']:
            status_style = "background-color: red; color: white; padding: 5px;"
            text_color = "color: red"
        else:
            status_style = "background-color: gray; color: white; padding: 5px;"
            text_color = "color: gray"

        self.lbl_hrv_val.setStyleSheet(text_color)
        self.lbl_fatigue_status.setStyleSheet(status_style)

        self.pbar_fatigue.setValue(f_idx)
        
        if f_idx < 40:
            chunk_color = "#2ecc71"
        elif f_idx < 75:
            chunk_color = "#f39c12"
        else:
            chunk_color = "#e74c3c"

        self.pbar_fatigue.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid grey;
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {chunk_color};
                width: 20px;
            }}
        """)

        self.update_plot(hr)

    def update_plot(self, hr):
        '''
        Update heart rate plot

        '''
        if hr < MIN_HR: return

        self.y_data = self.y_data[1:]
        self.y_data.append(hr)

        self.data_line.setData(self.x_data, self.y_data)