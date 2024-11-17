from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--kiosk-printing')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

@app.route('/download-result', methods=['POST'])
def download_result():
    try:
        data = request.json
        roll_no = data['rollNo']
        
        wd = setup_driver()
        URL = "https://rguhs.karnataka.gov.in/rguresult/"
        
        try:
            wd.get(URL)
            registraction_button = wd.find_element(by=By.ID, value="ContentPlaceHolder1_txtReg")
            registraction_button.click()
            registraction_button.send_keys(roll_no)
            registraction_button.click()

            # Select exam
            select_element = wd.find_element(by=By.NAME, value='ctl00$ContentPlaceHolder1$ddlExam')
            dropdown = Select(select_element)
            dropdown.select_by_value('MBBS4D')

            # Click view button
            view_button = wd.find_element(by=By.ID, value="ContentPlaceHolder1_btnview")
            view_button.click()

            # Take screenshot and convert to base64
            screenshot = wd.get_screenshot_as_png()
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')

            wd.quit()
            return jsonify({
                'status': 'success',
                'message': f'Result downloaded for {roll_no}',
                'screenshot': screenshot_b64
            })

        except Exception as e:
            wd.quit()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
