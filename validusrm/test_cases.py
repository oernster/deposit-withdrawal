from django.test import TestCase, Client
from validusrm.models import Commitment, Investment


class Main(TestCase):
    def setUp(self):
        self.url_prefix = 'http://127.0.0.1:8000/'

    def test_investments(self):
        url = self.url_prefix + 'investments'
        r = self.client.get(url)
        content = str(r.content)
        self.assertEqual(r.status_code, 200)
        self.assertIn('Deposit', content)
        self.assertIn('Investment Name', content)
        self.assertIn('Commitment Id', content)
        self.assertIn('Fund Id', content)
        self.assertIn('Date', content)
        self.assertIn('Amount', content)

    def test_withdraw_no_investment(self):
        url = self.url_prefix + 'investments'
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        data = {
            'investment_name': 'Investment I',
            'amount': 99999999999999999,
        }
        url = self.url_prefix + 'withdraw'
        r = self.client.post(url, data=data)
        self.assertEqual(r.status_code, 402)

        content = str(r.content)
        self.assertIn('Investment not found: no funds', content)

    def test_withdraw_not_enough_funds(self):
        url = self.url_prefix + 'investments'
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        data = {
            'investment_name': 'Investment I',
            'commitment_id': '1',
            'fund_id': 'Fund 1',
            'date': '2018-01-01',
            'amount': 10000000,
        }
        url = self.url_prefix + 'deposit'
        r = self.client.post(url, data=data)
        self.assertEqual(r.status_code, 302)

        data = {
            'investment_name': 'Investment I',
            'amount': 9999999999999999,
        }
        url = self.url_prefix + 'withdraw'
        r = self.client.post(url, data=data)
        self.assertEqual(r.status_code, 402)

        content = str(r.content)
        self.assertIn('Insufficient funds available', content)

    def test_valid_withdrawal(self):
        self.test_deposit(False)
        url = self.url_prefix + 'withdraw'
        data = {
            'investment_name': 'Investment I',
            'amount': 15000000,
        }
        r = self.client.post(url, data=data)
        self.assertEqual(r.status_code, 302)

        url = self.url_prefix + 'investments'
        r = self.client.get(url)
        content = str(r.content)
        self.withdrawal_checks(content)

    def test_deposit(self, deposit=True):
        url = self.url_prefix + 'investments'
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)

        data = {
            'investment_name': 'Investment I',
            'commitment_id': '1',
            'fund_id': 'Fund 1',
            'date': '2018-01-01',
            'amount': 10000000,
        }
        url = self.url_prefix + 'deposit'
        r = self.client.post(url, data=data)
        self.assertEqual(r.status_code, 302)

        data = {
            'investment_name': 'Investment I',
            'commitment_id': '2',
            'fund_id': 'Fund 2',
            'date': '2019-01-01',
            'amount': 20000000,
        }
        url = self.url_prefix + 'deposit'
        r = self.client.post(url, data=data)
        self.assertEqual(r.status_code, 302)

        data = {
            'investment_name': 'Investment I',
            'commitment_id': '3',
            'fund_id': 'Fund 1',
            'date': '2019-06-01',
            'amount': 50000000,
        }
        url = self.url_prefix + 'deposit'
        r = self.client.post(url, data=data)
        self.assertEqual(r.status_code, 302)

        # django test harness acts oddly with redirects so we need to do a get again
        url = self.url_prefix + 'investments'
        r = self.client.get(url)

        content = str(r.content)
        if deposit:
            self.deposit_checks(content)

    def withdrawal_checks(self, content):
        self.assertIn('Withdraw', content)
        self.assertIn('Summary', content)

        self.assertIn("""<h2>Summary</h2>""", content)
        self.assertIn("""<p>Investment I</p>""", content)
        self.assertIn("""<td>1</td>""", content)
        self.assertIn("""<td>Fund 1</td>""", content)
        self.assertIn("""<td>Jan. 1, 2018</td>""", content)
        self.assertIn("""<td>0.0</td>""", content)
        self.assertIn("""<td>2</td>""", content)
        self.assertIn("""<td>Fund 2</td>""", content)
        self.assertIn("""<td>Jan. 1, 2019</td>""", content)
        self.assertIn("""<td>0.0</td>""", content)
        self.assertIn("""<td>3</td>""", content)
        self.assertIn("""<td>Fund 1</td>""", content)
        self.assertIn("""<td>June 1, 2019</td>""", content)
        self.assertIn("""<td>50000000.0</td>""", content)

    def deposit_checks(self, content):
        self.assertIn('Withdraw', content)
        self.assertIn('Summary', content)

        self.assertIn("""<h2>Summary</h2>""", content)
        self.assertIn("""<p>Investment I</p>""", content)
        self.assertIn("""<td>1</td>""", content)
        self.assertIn("""<td>Fund 1</td>""", content)
        self.assertIn("""<td>Jan. 1, 2018</td>""", content)
        self.assertIn("""<td>10000000.0</td>""", content)
        self.assertIn("""<td>2</td>""", content)
        self.assertIn("""<td>Fund 2</td>""", content)
        self.assertIn("""<td>Jan. 1, 2019</td>""", content)
        self.assertIn("""<td>20000000.0</td>""", content)
        self.assertIn("""<td>3</td>""", content)
        self.assertIn("""<td>Fund 1</td>""", content)
        self.assertIn("""<td>June 1, 2019</td>""", content)
        self.assertIn("""<td>50000000.0</td>""", content)
