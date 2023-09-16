import json
import logging
import ssl
import urllib.parse
from typing import NamedTuple

import requests
from requests.adapters import HTTPAdapter, DEFAULT_POOLBLOCK
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.wait import WebDriverWait
from urllib3 import PoolManager

CLIENT_ID = '20002'
CLIENT_SECRET = '3cjzNJmmQLnIUFDdjpt0CG9SiaWHB3gmnogGMC7d'
AUTH_URL = "https://cas.ust.hk/cas/oidc/authorize?client_id=20002&redirect_uri=hk.ust.staff%3A%2F%2Flogin&scope=&response_type=code&state=t1694573171584"


class Tokens(NamedTuple):
    access_token: str
    id_token: str
    student_id: str


def wait_for_protocol(driver):
    while True:
        for entry in driver.get_log('performance'):
            if '"Location":"hk.ust.staff://' in entry['message']:
                data = json.loads(entry['message'])
                return data['message']['params']['headers']['Location']


def auth(credentials: tuple[str, str] = None) -> tuple[str, str, str]:
    logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
    logger.setLevel(logging.INFO)

    options = Options()
    options.add_experimental_option("excludeSwitches", [
        "enable-logging",
        "enable-automation",
        "disable-popup-blocking"
    ])
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    options.set_capability('goog:loggingPrefs', {'performance': 'INFO'})

    if credentials is not None:
        options.add_argument('--headless')

    driver = webdriver.Chrome(options)

    driver.get(AUTH_URL)

    if credentials is not None:
        # Wait for the form to appear
        WebDriverWait(driver, 5 * 60).until(visibility_of_element_located((By.XPATH, '//*[@id="fm1"]')))
        # Input username
        driver.find_element(By.XPATH, '//*[@id="userNameInput"]').send_keys(credentials[0])
        # Input password
        driver.find_element(By.XPATH, '//*[@id="passwordInput"]').send_keys(credentials[1])
        # Submit
        driver.find_element(By.XPATH, '//*[@id="submitButton"]').click()
        # Wait for the allow button to appear
        WebDriverWait(driver, 5 * 60).until(visibility_of_element_located((By.XPATH, '//*[@id="allow"]')))
        driver.find_element(By.XPATH, '//*[@id="allow"]').click()

    url = urllib.parse.urlparse(wait_for_protocol(driver))
    queries = dict(urllib.parse.parse_qsl(url.query))
    driver.close()

    resp = requests.post(
        'https://cas.ust.hk/cas/oidc/accessToken',
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={'code': queries['code'], 'grant_type': 'authorization_code', 'redirect_uri': 'hk.ust.staff://login'},
    )
    resp.raise_for_status()
    token = resp.json()

    client = requests.session()
    client.mount("https://", TLSAdapter())
    resp = client.get(
        'https://w5.ab.ust.hk/msapi/sis/stdt_ecard/users/%7BstdtID%7D',
        headers={'authorization': f'Bearer {token["id_token"]}'}
    )
    resp.raise_for_status()
    student_id = resp.json()['stdtID']

    return Tokens(token['access_token'], token['id_token'], student_id)


class TLSAdapter(HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=DEFAULT_POOLBLOCK, **pool_kwargs):
        """Initializes an urllib3 PoolManager.

        This method should not be called from user code, and is only
        exposed for use when subclassing the
        :class:`HTTPAdapter <requests.adapters.HTTPAdapter>`.

        :param connections: The number of urllib3 connection pools to cache.
        :param maxsize: The maximum number of connections to save in the pool.
        :param block: Block when no free connections are available.
        :param pool_kwargs: Extra keyword arguments used to initialize the Pool Manager.
        """
        # save these values for pickling
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT')
        # noinspection PyAttributeOutsideInit
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_context=ctx,
            **pool_kwargs,
        )
