import time
import requests
from datetime import datetime, timedelta
import requests
from tqdm import tqdm
from functools import lru_cache

class RateLimitedAPI:
    
    def __init__(self):
        self.pull_limit = 100
        self.time_limit = 120
        self.calls = []
        self.calls_in_time_limit = []
        self._time_since_last_reset = 0
        self.pbar = None
        self.parts_of_total = 0
        self.total = None
        
    @lru_cache(maxsize=500)
    def __call__(self, endpoint, params, name, total=None):
        self.endpoint = endpoint
        self.params = params
        self.name = name
        self.total = total
        if self.total is None:
            self.parts_of_total = 0

        response = None
  
        while response is None or response.status_code == 429:

            response = self.pull_data()
            
            if response.status_code == 429:
                self.test_if_429(response)

        # if there is total provided, we need to save how many parts have been completed and update the pbar      
        if self.total is not None:
            self.parts_of_total += 1
        if self.pbar is not None:
            self.pbar.update(1)
        return self.pull_data()
        # response = requests.get(self.endpoint, params=self.params)
        
        # if self.pbar is None:
        #     self.pbar = tqdm(total=None, desc=self.name, unit=' calls')
        # else:
        #     self.pbar.set_description_str(self.name)
      
        # self.calls.append(datetime.now())
        # min_time = min(self.calls)
        # max_time = max(self.calls)
        # self._time_since_last_reset = (max_time - min_time).total_seconds()
        
        # if response.status_code == 429:
        #     self.pbar.close()
        #     try:
        #         wait_time = response.headers['Retry-After']
        #         wait_time = int(wait_time) + 1
        #     except KeyError or ValueError:
        #         wait_time = 60
        #     with tqdm(total=wait_time, desc=f'Rate limited, waiting {wait_time}s') as pbar:
        #         for _ in range(wait_time):
        #             time.sleep(1)
        #             pbar.update(1)

        #     # restart progress bar
        #     self.pbar = tqdm(total=None, desc=self.name, unit='calls')
        
        # self.calls_in_time_limit = sum(time >= max_time - timedelta(seconds=self.time_limit) for time in self.calls)
        # if self.calls_in_time_limit >= self.pull_limit:
        #     self.pbar.close()
        #     wait_time = self.time_limit - self._time_since_last_reset
        #     with tqdm(total=wait_time, desc=f'Rate limited, waiting {wait_time}s') as pbar:
        #         for _ in range(wait_time):
        #             time.sleep(1)
        #             pbar.update(1)
        #     self.pbar = tqdm(total=None, desc=self.name, unit='calls')
        
        # self.pbar.update(1)
        
        # return response
    
    def pull_data(self):
        if self.pbar is None:
            self.pbar = tqdm(total=self.total, desc=self.name, unit=' calls')
        else:
            self.pbar.set_description_str(self.name)
      
        self.calls.append(datetime.now())
        max_time = max(self.calls)
        min_time = min(time >= max_time - timedelta(seconds=self.time_limit) for time in self.calls)
        self._time_since_last_reset = (max_time - min_time).total_seconds()
        response = requests.get(self.endpoint, params=self.params)
        
        self.test_if_429(response)

        self.calls_in_time_limit = sum(time >= max_time - timedelta(seconds=self.time_limit) for time in self.calls)
        if self.calls_in_time_limit >= self.pull_limit:
            self.pbar.close()
            try:
                wait_time = self.time_limit - self._time_since_last_reset
                wait_time = int(wait_time) + 1
            except KeyError or ValueError:
                wait_time = 60
            with tqdm(total=wait_time, desc=f'Rate limited, waiting {wait_time}s') as pbar:
                for _ in range(wait_time):
                    time.sleep(1)
                    pbar.update(1)
            self.pbar = tqdm(total=self.total, desc=self.name, unit='calls')
        
        # only update if no total was provided
        if self.total is None:
            self.pbar.update(1)
        
        return response
    
    def test_if_429(self, response):
        if response.status_code == 429:
            if self.pbar is not None:
                self.pbar.close()
            try:
                wait_time = response.headers['Retry-After']
                wait_time = int(wait_time) + 1
            except KeyError or ValueError:
                wait_time = 60
            with tqdm(total=wait_time, desc=f'Rate limited, waiting {wait_time}s') as pbar:
                for _ in range(wait_time):
                    time.sleep(1)
                    pbar.update(1)

            # restart progress bar
            self.pbar = tqdm(total=self.total, desc=self.name, unit='calls')


    def close(self):
        if self.pbar is not None:
            self.pbar.close()
        
        
