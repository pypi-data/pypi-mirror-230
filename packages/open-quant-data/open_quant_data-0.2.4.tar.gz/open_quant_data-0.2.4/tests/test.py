from open_quant_data.dataset.thirdparty.akshare.AkshareDataset import AkshareDataset as ak, ReportPeriod
from datetime import datetime

if __name__ == '__main__':
    ak.fund_timed("161716", "20230101", "20230901").to_csv('../assets/output/fund-161716.csv')
