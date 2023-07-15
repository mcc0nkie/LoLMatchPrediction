import time
import requests
from datetime import datetime, timedelta
import requests
from tqdm import tqdm
import math

MAX_RETRIES = 10

class CustomTqdm(tqdm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('mininterval', 2)  # Set the default mininterval in seconds (how often the progress bar updates)
        # kwargs.setdefault('leave', False) # set the default leave (whether or not the progress bar stays in the terminal after closing)
        super().__init__(*args, **kwargs)

class RateLimitedAPI:
    
    def __init__(self):
        self.additional_time_limit_buffer = 10
        self.pull_limit = 100
        self.time_limit = 120 + self.additional_time_limit_buffer
        self.calls = []
        self.calls_in_time_limit = []
        self._time_since_last_reset = 0
        self.pbar = None
        self.parts_of_total = 0
        self.total = None
        self.retries = 0
        self.api_bar_format = '\033[32m{l_bar}{bar}{r_bar}\033[00m | {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}] [{percentage:3.0f}%] [{desc}]'
        self.limit_bar_format = '\033[34m{l_bar}{bar}{r_bar}\033[00m | {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        
    def __call__(self, endpoint, name, total=None, **kwargs):
        '''
        Used to:
        1. Make a request to an API endpoint
        2. Test that response to see if the response was not 200
        3. If it's not 200, repeat the process of getting the request until it's 200, increasing wait time until a successful request comes through
        '''
        
        self.endpoint = endpoint
        self.params = {**kwargs}
        self.name = name
        self.total = total
        if self.total is None:
            self.parts_of_total = 0

        self.response = None
  
        while self.response is None or self.response.status_code != 200 or self.retries != MAX_RETRIES:

            self.retries += 1
            try:
                self.pull_data()
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout, requests.exceptions.RequestException, requests.exceptions.Timeout):
                self.response = None
                self.delay_for_response_code()
            
            if self.response is None or self.response.status_code != 200:
                if self.retries == MAX_RETRIES:
                    self.response = 'MAX_RETRIES_REACHED'
                else:
                    self.delay_for_response_code()
                

        # if there is total provided, we need to save how many parts have been completed and update the pbar      
        if self.total is not None:
            self.parts_of_total += 1
        if self.pbar is not None:
            self.pbar.update(1)
        
        self.retries = 0 # reset retries
        return self.response
    
    def pull_data(self):
        if self.pbar is None:
            self.pbar = CustomTqdm(total=self.total, desc=self.name, unit=' calls', initial=self.parts_of_total, bar_format=self.api_bar_format)
        else:
            self.pbar.set_description_str(self.name)
      
        self.calls.append(datetime.now())
    
        self.response = requests.get(self.endpoint, params=self.params)

    def check_pull_limit(self):
        self.max_time = max(self.calls)
        self.min_time = min(t for t in self.calls if t >= self.max_time - timedelta(seconds=self.time_limit))
        self._time_since_last_reset = (self.max_time - self.min_time).total_seconds()
        self.calls_in_time_limit = sum(time >= self.max_time - timedelta(seconds=self.time_limit) for time in self.calls)
        if self.calls_in_time_limit >= self.pull_limit:
            self.pbar.close()
            try:
                wait_time = self.time_limit - self._time_since_last_reset
                wait_time = int(wait_time) + 1
            except (KeyError, ValueError):
                wait_time = 60
            with CustomTqdm(total=wait_time, desc=f'Rate limited, waiting {wait_time}s', bar_format=self.limit_bar_format, leave=False) as pbar:
                for _ in range(wait_time):
                    time.sleep(1)
                    pbar.update(1)
            self.pbar = CustomTqdm(total=self.total, desc=self.name, unit='calls', initial=self.parts_of_total, bar_format=self.api_bar_format)
        
        # only update if no total was provided
        if self.total is None:
            self.pbar.update(1)
    
    def delay_for_response_code(self):
        
        if self.pbar is not None:
            self.pbar.close()
        try:
            wait_time = self.response.headers['Retry-After']
            wait_time = int(wait_time)
            if wait_time < 10:
                wait_time = 10
            error_type = response.status_code
        except (KeyError,ValueError,AttributeError,NameError):
            wait_time = 60
            error_type = 'TIMEOUT'

        # dynamically increase wait time for the number of retries
        wait_time = math.ceil(wait_time * self.retries / 10)

        with CustomTqdm(total=wait_time, desc=f'Rate limited ({error_type} code), waiting {wait_time}s', bar_format=self.limit_bar_format, leave=False) as pbar:
            for _ in range(wait_time):
                time.sleep(1)
                pbar.update(1)

        # restart progress bar
        self.pbar = CustomTqdm(total=self.total, desc=self.name, unit='calls', initial=self.parts_of_total, bar_format=self.api_bar_format)


    def close(self):
        if self.pbar is not None:
            self.pbar.close()
        
        
