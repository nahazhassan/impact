import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QScrollArea)

from PyQt5.QtCore import Qt

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ",self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.forecast_label = QLabel("Forecast:", self)
        self.forecast_area = QScrollArea(self)
        self.forecast_content = QWidget()
        self.forecast_layout = QVBoxLayout()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather app")

        vbox = QVBoxLayout()

        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        vbox.addWidget(self.forecast_label)
        vbox.addWidget(self.forecast_area)

        self.forecast_content.setLayout(self.forecast_layout)
        self.forecast_area.setWidget(self.forecast_content)
        self.forecast_area.setWidgetResizable(True)
        self.forecast_area.setFixedHeight(200)

        self.forecast_label.setAlignment(Qt.AlignCenter)
        self.forecast_label.setObjectName("forecast_label")


        self.setStyleSheet("""
            QLabel, QPushButton{
                           font-family:calibri;
                           }
                           QLabel#city_label{
                           font-size: 40px;
                           font-style: italic;
                           }
                           QLineEdit#city_input{
                           font-size: 40px;
                           }
                           QPushButton#get_weather_button{
                           font-size: 80px;
                           font-weight: bold;
                           }
                           QLabel#temperature_label{
                           font-size: 80px;
                           }
                           QLabel#emoji_label{
                           font-size: 100px;
                           font-family: segoe UI emoji;
                           }
                           QLabel#description_label{
                           font-size: 50px;
                           }
                           QLabel#forecast_label{
                           font-size: 30px;
                           font-weight: bold;
                           margin-top: 10px;
                           }
                           """)
        self.get_weather_button.clicked.connect(self.get_weather)
    

    def get_weather(self):
        api_key = "38faccae9911ee7dc394e895a9a49943"
        city = self.city_input.text()
        current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}"
        
        try:
            # Get current weather
            response = requests.get(current_url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)
            else:
                self.display_error("Error fetching current weather data")

            # Get forecast weather
            forecast_response = requests.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            if forecast_data["cod"] == "200":
                self.display_forecast(forecast_data)
            else:
                self.display_error("Error fetching forecast data")

        except requests.exceptions.HTTPError as http_error:
            status_code = None
            if http_error.response is not None:
                status_code = http_error.response.status_code
            if status_code == 400:
                self.display_error("Bad request\n please check your input")
            elif status_code == 401:
                self.display_error("unauthorized \n invalid api")
            elif status_code == 403:
                self.display_error("forbidden\n access denied")
            elif status_code == 404:
                self.display_error("city not found \n please check your input")
            elif status_code == 500:
                self.display_error("internal server error \n please try again later")
            elif status_code == 502:
                self.display_error("Bad gateway\n invalid response from server")
            elif status_code == 503:
                self.display_error("service unavailable\n server is down")
            elif status_code == 504:
                self.display_error("gateway timed out\n no response from the server")
            else:
                self.display_error(f"HTTP error occurred\n{http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("connection error\n check your internet connection")
        except requests.exceptions.Timeout:
            self.display_error("timeout error\n the request timed out")
        except requests.exceptions.TooManyRedirects:
            self.display_error("too many redirects\n request timed out\check the url")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"request error\n {req_error}")


    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px")
        self.temperature_label.setText(message)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, weather_data):
        self.temperature_label.setStyleSheet("font-size: 80px")
        temperature_k= weather_data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        weather_id= weather_data["weather"][0]["id"]
        weather_description= weather_data["weather"][0]["description"]
        self.description_label.setStyleSheet("font-size: 40px")

        self.temperature_label.setText(f"{temperature_c:.2f}°C")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(weather_description)
    
    def display_forecast(self, forecast_data):
        self.clear_forecast()
        # Display forecast for the next 5 days, every 3 hours
        for forecast in forecast_data["list"]:
            dt_txt = forecast["dt_txt"]
            temp_k = forecast["main"]["temp"]
            temp_c = temp_k - 273.15
            weather_id = forecast["weather"][0]["id"]
            description = forecast["weather"][0]["description"]

            forecast_label = QLabel(f"{dt_txt}: {temp_c:.2f}°C, {description} {self.get_weather_emoji(weather_id)}")
            forecast_label.setStyleSheet("font-size: 20px; margin: 2px;")
            self.forecast_layout.addWidget(forecast_label)

    def clear_forecast(self):
        while self.forecast_layout.count():
            child = self.forecast_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    @staticmethod
    def get_weather_emoji(weather_id):
        
        if 200<= weather_id <= 232:
            return "☁️"
        elif 300<= weather_id <=  321:
            return "⛅"
        elif 500<= weather_id <= 531:
            return "🌧️"
        elif 600<= weather_id <= 622:
            return "❄️"
        elif 700<= weather_id <= 741:
            return "🌁"
        elif weather_id == 762:
            return "🌋"
        elif weather_id == 771:
            return "💨"
        elif weather_id == 781:
            return "🌪️"
        elif weather_id == 800:
            return "☀️"
        elif 801 <= weather_id <= 804:
            return "☁️"
        else:
            return ""
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
