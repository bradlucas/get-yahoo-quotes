import sys, os, re, io, tempfile, time, logging, pycurl
from datetime import datetime, timedelta

logging.basicConfig(filename="log.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='w') 

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG) 

class download_stock_data:

    def validate_ticker_symbol(self, ticker):
        if ticker is None:
            log.exception("Informe um ticker valido, por ex. B3SA3")
        
        return ticker

    def convert_date_to_unixtimestamp(self, date_to_convert):
        unixtime = '{0:.0f}'.format(time.mktime(
                                datetime.strptime(
                                date_to_convert, "%d/%m/%Y").timetuple() ))
        return unixtime

    def set_date_interval(self, interval=int):
        if interval:
            start_date = (datetime.today() - timedelta(days=interval)).strftime("%d/%m/%Y")
        else:
            start_date = (datetime.today() - timedelta(days=60)).strftime("%d/%m/%Y")

        start_date = self.convert_date_to_unixtimestamp(start_date)
        end_date   = self.convert_date_to_unixtimestamp(datetime.now().strftime("%d/%m/%Y"))

        log.info("start_date: {0} end_date: {1}".format(start_date, end_date))

        return start_date, end_date
        
    def get_crumb(self, ticker):
        log.info('function: {0} ticker: {1}'.format('get_crumb', ticker))

        url = 'https://finance.yahoo.com/quote/{0}/?p={0}'.format(ticker.upper())

        cookie_file = tempfile.mkstemp()[1]
        buffer = io.BytesIO()

        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(pycurl.TIMEOUT, 30)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.COOKIEJAR, cookie_file)
        c.setopt(c.VERBOSE, False)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform() 
        html = str(buffer.getvalue())

        if "CrumbStore" in html:
            pattern = r'CrumbStore\":{\"crumb\":\"(.*?)\"}'
            crumb = re.search(pattern, html).group(1).encode('utf-8').decode('unicode-escape')

        log.info('function: {0}, crumb: {1} cookie_file: {2}'.format('get_crumb', crumb, cookie_file))

        return crumb, cookie_file

    def download_csv(self, url, cookie_file):
        log.info('base_url: {0} cookie_file: {1}'.format(url, cookie_file))

        buffer = io.BytesIO()

        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(pycurl.TIMEOUT, 30)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.COOKIEFILE, cookie_file)
        c.setopt(c.VERBOSE, False)
        c.setopt(pycurl.SSL_VERIFYPEER, 0)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()

        csv_content = str(buffer.getvalue(), 'utf-8')

        return csv_content

    def write_into_csv(self, csv_content, ticker):

        path_to_file = '{0}.csv'.format(ticker)

        f = open(path_to_file, 'w')
        f.write(csv_content)
        f.close()

        return path_to_file


    def get_data(self, ticker, days, write_output):

        ticker = self.validate_ticker_symbol(ticker)
        start_date, end_date = self.set_date_interval(days)
        interval = '1wk'
        crumb, cookie_file = self.get_crumb(ticker)

        url = 'https://query1.finance.yahoo.com/v7/finance/download/{0}?period1={1}&period2={2}&interval={3}&events=history&crumb={4}'.format(ticker, start_date, end_date, interval, crumb)

        log.info('base_url: {0}'.format(url))

        csv_content = self.download_csv(url, cookie_file)

        if write_output is True:
            return self.write_into_csv(csv_content, ticker)

        return csv_content

# Calling the method
ticker = 'B3SA3.SA'
write_output = True

d = download_stock_data()
csv = d.get_data(ticker, 240, write_output)
print(csv)
