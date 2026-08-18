from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

BASE_URL = "https://customer.hcgonline.co.in/Online/billpay"
POST_URL = "https://customer.hcgonline.co.in/Online/GetBillReceiptByConsumerNo"

COMMON_HEADERS = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36",
    'Accept-Language': "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
}

@app.route('/api/get-bill/<bp_number>', methods=['GET'])
def get_bill(bp_number):
    session = requests.Session()
    session.headers.update(COMMON_HEADERS)

    try:
        # Step 1: Page open karke fresh session aur CSRF Token nikalo
        get_response = session.get(BASE_URL, timeout=10)
        soup = BeautifulSoup(get_response.text, 'html.parser')

        token_input = soup.find('input', {'name': '__RequestVerificationToken'})
        if not token_input:
            return jsonify({"status": "error", "message": "Failed to extract Verification Token"}), 500
        
        csrf_token = token_input.get('value')

        # Step 2: Fresh Token ke sath POST request bhejo
        payload = {
            'consumerNumb': bp_number,
            'paymentCode': "1",
            '__RequestVerificationToken': csrf_token
        }

        post_headers = {
            'X-Requested-With': "XMLHttpRequest",
            'Origin': "https://customer.hcgonline.co.in",
            'Referer': BASE_URL
        }

        post_response = session.post(POST_URL, data=payload, headers=post_headers, timeout=10)

        # Step 3: Response return karo
        try:
            json_data = post_response.json()
            return jsonify({"status": "success", "data": json_data}), 200
        except ValueError:
            return jsonify({"status": "success", "raw_response": post_response.text}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Local test ke liye
if __name__ == '__main__':
    app.run(debug=True)
