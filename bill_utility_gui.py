import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QDateEdit, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon
from seleniumbase import SB
from get_token import extract_token
from simplified_uploader import main

class LibertyBillUploader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.token = None
        self.file_path = None
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle('Liberty Bill Uploader')
        self.setMinimumSize(500, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title label
        title_label = QLabel('Liberty Bill Uploader')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Add separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # File selection section
        file_layout = QHBoxLayout()
        file_label = QLabel('Excel File:')
        self.file_path_label = QLabel('No file selected')
        select_file_button = QPushButton('Select File')
        select_file_button.clicked.connect(self.select_excel_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path_label, 1)
        file_layout.addWidget(select_file_button)
        main_layout.addLayout(file_layout)
        
        # Date selection section
        date_layout = QHBoxLayout()
        date_label = QLabel('Select Date:')
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit, 1)
        main_layout.addLayout(date_layout)
        
        # Button section
        button_layout = QHBoxLayout()
        
        # Login button
        self.login_button = QPushButton('Step 1: Login to Liberty')
        self.login_button.setToolTip('Opens Chrome for login to Liberty')
        self.login_button.clicked.connect(self.login_to_liberty)
        
        # Upload button
        self.upload_button = QPushButton('Step 2: Upload Bill Data')
        self.upload_button.setToolTip('Uploads bill data to the system')
        self.upload_button.clicked.connect(self.upload_bill_data)
        self.upload_button.setEnabled(False)  # Disabled until login is complete
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.upload_button)
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel('Ready. Please select a file and date, then login.')
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Show the window
        self.center_on_screen()
        self.show()
    
    def center_on_screen(self):
        # Center the window on the screen
        screen_geometry = QApplication.desktop().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def select_excel_file(self):
        # Open file dialog to select Excel file
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select Excel File', '', 'Excel Files (*.xlsx *.xls *.xlsm)'
        )
        if file_path:
            self.file_path = file_path
            # Display just the filename, not the full path
            filename = os.path.basename(file_path)
            self.file_path_label.setText(filename)
            self.status_label.setText(f'File selected: {filename}')
    
    def login_to_liberty(self):
        # Check if file is selected
        if not self.file_path:
            QMessageBox.warning(self, 'Warning', 'Please select an Excel file first.')
            return
        
        self.status_label.setText('Opening Chrome for login. Please wait...')
        self.setEnabled(False)  # Disable the entire UI during login
        
        try:
            # Setup Chrome data directory
            full_path = os.path.abspath("chromedatabills")
            
            # Open browser for login
            with SB(uc=True, headless=False, user_data_dir=full_path, log_cdp_events=True) as sb:
                # Open the target website
                sb.open("https://myaccount.libertyenergyandwater.com/portal/#/login?LUCA")
                
                # Show message to user
                QMessageBox.information(
                    self, 
                    'Login Instructions', 
                    'Please log in to your Liberty account in the browser window.\n\n'
                    'Once logged in, close this message box to continue.'
                )
                
                # Capture CDP logs after login
                cdp_logs = sb.driver.get_log("performance")
                logs_file_path = os.path.abspath("cdp_logs.json")
                with open(logs_file_path, 'w') as f:
                    json.dump(cdp_logs, f, indent=4)
                
                # Extract token from logs
                self.token = extract_token(logs_file_path)
                
                if self.token:
                    self.status_label.setText('Login successful! Token acquired.')
                    self.upload_button.setEnabled(True)
                else:
                    self.status_label.setText('Login failed or token not found. Please try again.')
        
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred during login: {str(e)}')
            self.status_label.setText('Login error. Please try again.')
        
        self.setEnabled(True)  # Re-enable the UI
    
    def upload_bill_data(self):
        if not self.token:
            QMessageBox.warning(self, 'Warning', 'Please login first to obtain a token.')
            return
        
        try:
            # Get the selected date
            selected_date = self.date_edit.date().toString('yyyy-MM-dd')
            
            # Set environment variables for the main function to use
            os.environ['SELECTED_DATE'] = selected_date
            os.environ['EXCEL_FILE'] = self.file_path
            
            # Call the main function with the token
            self.status_label.setText(f'Processing data for date: {selected_date}...')
            
            # Call the main function with the token
            main(self.token)
            
            self.status_label.setText('Bill data uploaded successfully!')
            QMessageBox.information(self, 'Success', 'Bill data has been processed and uploaded successfully.')
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred during upload: {str(e)}')
            self.status_label.setText('Upload error. Please check log for details.')

def run():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for a modern look
    window = LibertyBillUploader()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run() 