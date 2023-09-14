from itertools import accumulate as _accumulate, repeat as _repeat
from bisect import bisect as _bisect
import random
import traceback
from functools import wraps
import datetime
import pytz
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from .version import __version__

def random_choices(population, weights=None, *, cum_weights=None, k=1):
    """Return a k sized list of population elements chosen with replacement.
    If the relative weights or cumulative weights are not specified,
    the selections are made with equal probability.
    """
    n = len(population)
    if cum_weights is None:
        if weights is None:
            _int = int
            n += 0.0    # convert to float for a small speed improvement
            return [population[_int(random.random() * n)] for i in _repeat(None, k)]
        cum_weights = list(_accumulate(weights))
    elif weights is not None:
        raise TypeError('Cannot specify both weights and cumulative weights')
    if len(cum_weights) != n:
        raise ValueError('The number of weights does not match the population')
    bisect = _bisect
    total = cum_weights[-1] + 0.0   # convert to float
    hi = n - 1
    return [population[bisect(cum_weights, random.random() * total, 0, hi)]
            for i in _repeat(None, k)]


def monitor_func(logger,
                 func_name=None,
                 set_execution_id=True,
                 execution_id=None,
                 start_done=True,
                 except_level='error'):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            fname = func_name or func.__name__

            try:
                if set_execution_id:
                    logger.setExecutionId(execution_id)

                if start_done:
                    logger.start(f'Starting {fname}')

                result = func(*args, **kwargs)

                if start_done:
                    logger.done(f'Done with {fname}')

                return result

            except Exception as e:

                getattr(logger, except_level.lower())(
                    str(e), data={'traceback': traceback.format_exc()}
                )
                if hasattr(logger, 'return_when_exception'):
                    return logger.return_when_exception

        return wrapper

    return decorator


def send_alert(logger,
               alert_token,
               name,
               lead,
               body='',
               details='',
               priority=False,
               dev=None,
               min_time=None,
               max_time=None,
               search_time=None,
               link_text=None,
               link_url=None,
               docs_text=None,
               docs_url=None,
               alert_update_url=None,
               retry_count=5,
               backoff_factor=1,
               timeout=10):

    alert_body = None

    try:

        dev = dev if isinstance(dev, bool) else logger.dev
        assert isinstance(alert_token, str) and len(alert_token) > 10, 'Invalid alert token'

        if search_time is None:
            search_time = pytz.utc.localize(datetime.datetime.utcnow())
        assert isinstance(search_time, datetime.datetime), 'search_time needs to be a datetime instance'

        alert_body = {
            'name': name,
            'lead': lead,
            'body': body,
            'details': details,
            'level': 'alert',
            'priority': priority,
            'dev': dev,
            'info_search_time': search_time.timestamp()
        }

        if not min_time is None:
            assert isinstance(min_time, datetime.datetime), 'min_time needs to be a datetime instance'
            alert_body['info_min_time'] = min_time.timestamp()

        if not max_time is None:
            assert isinstance(max_time, datetime.datetime), 'max_time needs to be a datetime instance'
            alert_body['info_max_time'] = max_time.timestamp()

        if not link_url is None:
            link = {'url': link_url}
            if not link_text is None:
                link['text'] = link_text
            alert_body['link'] = link

        if not docs_url is None:
            docs = {'url': docs_url}
            if not docs_text is None:
                docs['text'] = docs_text
            alert_body['docs'] = docs

        if not alert_update_url is None:
            alert_body['alert_update_url'] = alert_update_url

        url = 'https://alerts.' + logger.host
        headers = {'Authorization': alert_token,
                   'User-Agent': 'watchtower-logging-python/{version}'.format(version=__version__)}

        session = requests.Session()
        retry = Retry(total=retry_count,
                      backoff_factor=backoff_factor,
                      status_forcelist=[500, 502, 503, 504])

        session.mount(url, HTTPAdapter(max_retries=retry))
        r = session.post(url,
                     json=alert_body,
                     headers=headers,
                     timeout=timeout)
        r.raise_for_status()

    except Exception as e:

        logger.critical('Failed to send alert',
                        data={
                            'alert_body': alert_body,
                            'error': str(e),
                            'traceback': traceback.format_exc()})






