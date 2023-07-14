import time
import requests
from tqdm import tqdm
from datetime import datetime, timedelta
import requests

class RateLimitedAPI:
    
    def __init__(self):
        self.pull_limit = 100
        self.time_limit = 120
        self.calls = []
        self.calls_in_time_limit = []
        self._time_since_last_reset = 0
        
    def __call__(self, endpoint, params, headers, name):
        self.endpoint = endpoint
        self.params = params 
        self.headers = headers
        self.name = name
        response = requests.get(self.endpoint, params=self.params, headers=self.headers)
        self.pbar = tqdm(total=None, desc=self.name, unit=' calls')
      
        self.calls.append(datetime.now())
        min_time = min(self.calls)
        max_time = max(self.calls)
        self._time_since_last_reset = (max_time - min_time).total_seconds()
        
        if response.status_code == 429:
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
            self.pbar = tqdm(total=None, desc=self.name, unit='calls')
            
        self.pbar.update(1)
        
        self.calls_in_time_limit = sum(time >= max_time - timedelta(seconds=self.time_limit) for time in self.calls)
        if self.calls_in_time_limit >= self.pull_limit:
            self.pbar.close()
            wait_time = self.time_limit - self._time_since_last_reset
            with tqdm(total=wait_time, desc=f'Rate limited, waiting {wait_time}s') as pbar:
                for _ in range(wait_time):
                    time.sleep(1)
                    pbar.update(1)
            self.pbar = tqdm(total=None, desc=self.name, unit='calls')
        
        return response
        
        
