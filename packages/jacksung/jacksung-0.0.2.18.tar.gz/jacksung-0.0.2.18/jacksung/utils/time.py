import time
from datetime import datetime
import pytz


class RemainTime:
    def __init__(self, epoch):
        self.start_time = time.time()
        self.epoch = epoch

    def update(self, now_epoch, log_temp='[ Epochs Remaining:{}\tFinished in {} ]', print_log=True):
        epoch_time = time.time() - self.start_time
        epoch_remaining = self.epoch - now_epoch
        time_remaining = epoch_time * epoch_remaining
        pytz.timezone('Asia/Shanghai')  # 东八区
        t = datetime.fromtimestamp(int(time.time()) + time_remaining,
                                   pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
        log = log_temp.format(epoch_remaining, t)
        if print_log:
            print(log)
        self.start_time = time.time()
        return epoch_remaining, t
