#import requests
import logging, re, json, base64, quickjs, queue, threading, uuid, random, struct, os, string, browser_cookie3, playsound
from curl_cffi import requests
from langdetect import detect
from deep_translator import GoogleTranslator
from google.cloud import translate_v2 as translate
from colorama import Fore, Back, Style
from urllib.parse import quote
from time         import time
from datetime     import datetime
from queue        import Queue, Empty
from threading    import Thread
from re           import findall
from curl_cffi.requests import post

#Ask

logging.basicConfig()
logger = logging.getLogger()

class Client:
  base_url = "https://sdk.vercel.ai"
  token_url = base_url + "/openai.jpeg" #nice try vercel
  generate_url = base_url + "/api/prompt"
  chat_url = base_url + "/api/generate"

  def __init__(self, proxy=None):
    self.session = requests.Session(impersonate="chrome107")
    self.headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.{rand1}.{rand2} Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "en-US,en;q=0.5",
      "Te": "trailers",
      "Upgrade-Insecure-Requests": "1"
    }
    self.session.headers.update(self.headers)

    self.proxy = proxy
    if self.proxy:       
      self.session.proxies = {
        "http": self.proxy,
        "https": self.proxy
      }

    self.models = self.get_models()
    self.model_ids = list(self.models.keys())
    self.model_defaults = {}
    for model_id in self.models:
      self.model_defaults[model_id] = self.get_default_params(model_id)
  
  def get_models(self):
    logger.info("Downloading homepage...")
    html = self.session.get(self.base_url).text
    paths_regex = r'static\/chunks.+?\.js'
    separator_regex = r'"\]\)<\/script><script>self\.__next_f\.push\(\[.,"'

    paths = re.findall(paths_regex, html)
    for i in range(len(paths)):
      paths[i] = re.sub(separator_regex, "", paths[i])
    paths = list(set(paths))

    scripts = []
    threads = []

    logger.info(f"Downloading and parsing scripts...")
    def download_thread(path):
      script_url = f"{self.base_url}/_next/{path}"
      script = self.session.get(script_url).text
      scripts.append(script)
      
    for path in paths:
      thread = threading.Thread(target=download_thread, args=(path,), daemon=True)
      thread.start()
      threads.append(thread)
    
    for thread in threads:
      thread.join()
    
    for script in scripts:
      models_regex = r'let .="\\n\\nHuman:\",.=(.+?),.='
      matches = re.findall(models_regex, script)

      if matches:
        models_str = matches[0]
        stop_sequences_regex = r'(?<=stopSequences:{value:\[)\D(?<!\])'
        models_str = re.sub(stop_sequences_regex, re.escape('"\\n\\nHuman:"'), models_str)

        context = quickjs.Context()
        json_str = context.eval(f"({models_str})").json()
        return json.loads(json_str)

    return []

  def get_token(self):
    logger.info("Fetching token from "+self.token_url)
    b64 = self.session.get(self.token_url).text
    data = json.loads(base64.b64decode(b64, validate=True))

    script = """
      String.prototype.fontcolor = function() {{
        return `<font>${{this}}</font>`
      }}
      var globalThis = {{marker: "mark"}};
      ({script})({key})
    """.format(script=data["c"], key=data["a"])
    context = quickjs.Context()
    token_data = json.loads(context.eval(script).json())
    token_data[2] = "mark"
    token = {
      "r": token_data,
      "t": data["t"]
    }
    token_str = json.dumps(token, separators=(',', ':')).encode("utf-16le")
    return base64.b64encode(token_str).decode()

  def get_default_params(self, model_id):
    model = self.models[model_id]
    defaults = {}
    for key, param in model["parameters"].items():
      defaults[key] = param["value"]
    return defaults

  #bad streaming workaround cause the tls library doesn't support it
  def stream_request(self, method, *args, **kwargs):
    chunks_queue = queue.Queue()
    error = None
    response = None

    def callback(data):
      chunks_queue.put(data.decode())
    def request_thread():
      nonlocal response, error
      try:
        response = self.session.post(*args, **kwargs, content_callback=callback)
        response.raise_for_status()
      except Exception as e:
        error = e
    
    thread = threading.Thread(target=request_thread, daemon=True)
    thread.start()
    
    while True:
      try:
        chunk = chunks_queue.get(block=True, timeout=0.01)
      except queue.Empty:
        if error:
          raise error
        elif response:
          break
        else:
          continue
      
      yield chunk
  
  def get_headers(self):
    token = self.get_token()

    headers = {**self.headers, **{
      "User-Agent": self.headers["User-Agent"].format(
        rand1=random.randint(0,9999),
        rand2=random.randint(0,9999)
      ),
      "Accept-Encoding": "gzip, deflate, br",
      "Custom-Encoding": token,
      "Host": "sdk.vercel.ai",
      "Origin": "https://sdk.vercel.ai",
      "Referrer": "https://sdk.vercel.ai",
      "Sec-Fetch-Dest": "empty",
      "Sec-Fetch-Mode": "cors",
      "Sec-Fetch-Site": "same-origin",
    }}

    return headers

  def generate(self, model_id, prompt, params={}):
    logger.info(f"Sending to {model_id}: {prompt}")

    defaults = self.get_default_params(model_id)
    payload = {**defaults, **params, **{
      "prompt": prompt,
      "model": model_id,
    }}
    headers = self.get_headers()

    logger.info("Waiting for response")
    text = ""
    index = 0
    for chunk in self.stream_request(self.session.post, self.generate_url, headers=headers, json=payload):
      text += chunk
      lines = text.split("\n")

      if len(lines) - 1 > index:
        new = lines[index:-1]
        for word in new:
          yield json.loads(word)
        index = len(lines) - 1
  
  def chat(self, model_id, messages, params={}):
    logger.info(f"Sending to {model_id}: {len(messages)} messages")

    defaults = self.get_default_params(model_id)
    payload = {**defaults, **params, **{
      "chatIndex": 0, 
      "messages": messages,
      "model": model_id,
      "playgroundId": str(uuid.uuid4())
    }}
    headers = self.get_headers()
    
    logger.info("Waiting for response")
    return self.stream_request(self.session.post, self.chat_url, headers=headers, json=payload)
  

#Ask Internet

def extract_links(data: list) -> list:
    """
    Extract links from the given data.

    Args:
        data: Data to extract links from.

    Returns:
        list: Extracted links.
    """
    links = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, list):
                # recursive
                links.extend(extract_links(item))
            elif (
                isinstance(item, str)
                and item.startswith("http")
                and "favicon" not in item
            ):
                links.append(item)
    return links


def upload_image(image: bytes, filename="Photo.jpg"):
    """
    Upload image into bard bucket on Google API, do not need session.

    Returns:
        str: relative URL of image.
    """
    resp = requests.options("https://content-push.googleapis.com/upload/")
    resp.raise_for_status()
    size = len(image)

    headers = IMG_UPLOAD_HEADERS
    headers["size"] = str(size)
    headers["x-goog-upload-command"] = "start"

    data = f"File name: {filename}"
    resp = requests.post(
        "https://content-push.googleapis.com/upload/", headers=headers, data=data
    )
    resp.raise_for_status()
    upload_url = resp.headers["X-Goog-Upload-Url"]
    resp = requests.options(upload_url, headers=headers)
    resp.raise_for_status()
    headers["x-goog-upload-command"] = "upload, finalize"

    # It can be that we need to check returned offset
    headers["X-Goog-Upload-Offset"] = "0"
    resp = requests.post(upload_url, headers=headers, data=image)
    resp.raise_for_status()
    return resp.text


def extract_bard_cookie(cookies: bool = False) -> dict:
    """
    Extracts the specified Bard cookie(s) from the browser's cookies.

    This function searches for the specified Bard cookies in various web browsers
    installed on the system. It supports modern web browsers and operating systems.

    Args:
        cookies (bool, optional): If True, extracts only '__Secure-1PSID' cookie.
            If False, extracts '__Secure-1PSID', '__Secure-1PSIDTS', and '__Secure-1PSIDCC' cookies.
            Defaults to False.

    Returns:
        dict: A dictionary containing the extracted Bard cookies.

    Raises:
        Exception: If no supported browser is found or if there's an issue with cookie extraction.
    """
    supported_browsers = [
        browser_cookie3.chrome,
        browser_cookie3.chromium,
        browser_cookie3.opera,
        browser_cookie3.opera_gx,
        browser_cookie3.brave,
        browser_cookie3.edge,
        browser_cookie3.vivaldi,
        browser_cookie3.firefox,
        browser_cookie3.librewolf,
        browser_cookie3.safari,
    ]

    cookie_dict = {}

    for browser_fn in supported_browsers:
        try:
            cj = browser_fn(domain_name=".google.com")

            for cookie in cj:
                if cookie.name == "__Secure-1PSID" and cookie.value.endswith("."):
                    cookie_dict["__Secure-1PSID"] = cookie.value
                    if not cookies:
                        cookie_dict["__Secure-1PSIDTS"] = cookie.value
                        cookie_dict["__Secure-1PSIDCC"] = cookie.value
                    if cookies or not cookies:
                        return cookie_dict

        except Exception as e:
            # Ignore exceptions and try the next browser function
            continue

    if not cookie_dict:
        raise Exception("No supported browser found or issue with cookie extraction")

    return cookie_dict


def max_token(text: str, n: int):
    """
    Print the first 'n' tokens (words) of the given text.

    Args:
        text (str): The input text to be processed.
        n (int): The number of tokens (words) to be printed from the beginning.

    Returns:
        None
    """
    word_count = 0
    word_start = 0
    for i, char in enumerate(text):
        if char.isspace():
            word_count += 1
            if word_count == n:
                print(text[:i])
                break
    else:
        print(text)


def max_sentence(text: str, n: int):
    """
    Print the first 'n' sentences of the given text.

    Args:
        text (str): The input text to be processed.
        n (int): The number of sentences to be printed from the beginning.

    Returns:
        None
    """
    punctuations = set("?!.")

    sentences = []
    sentence_count = 0
    for char in text:
        sentences.append(char)
        if char in punctuations:
            sentence_count += 1
            if sentence_count == n:
                print("".join(sentences).strip())
                return
    print("".join(sentences).strip())

ALLOWED_LANGUAGES = {"en", "ko", "ja", "english", "korean", "japanese"}
DEFAULT_LANGUAGE = "en"
SEPARATOR_LINE = "=" * 36
USER_PROMPT = Fore.BLUE + "You: " + Fore.RESET

SESSION_HEADERS = {
    "Host": "bard.google.com",
    "X-Same-Domain": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Origin": "https://bard.google.com",
    "Referer": "https://bard.google.com/",
}

IMG_UPLOAD_HEADERS = {
    "authority": "content-push.googleapis.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.7",
    "authorization": "Basic c2F2ZXM6cyNMdGhlNmxzd2F2b0RsN3J1d1U=",  # Constant Authorization Key
    "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    "origin": "https://bard.google.com",
    "push-id": "feeds/mcudyrk2a4khkz",  # Constant
    "referer": "https://bard.google.com/",
    "x-goog-upload-command": "start",
    "x-goog-upload-header-content-length": "",
    "x-goog-upload-protocol": "resumable",
    "x-tenant-id": "bard-storage",
}



class Ask_Internet:
    """
    Bard class for interacting with the Bard API.
    """

    def __init__(
        self,
        token: str = None,
        timeout: int = 20,
        proxies: dict = None,
        session: requests.Session = None,
        conversation_id: str = None,
        google_translator_api_key: str = None,
        language: str = None,
        run_code: bool = False,
        token_from_browser=False,
    ):
        """
        Initialize the Bard instance.

        Args:
            token (str): Bard API token.
            timeout (int): Request timeout in seconds.
            proxies (dict): Proxy configuration for requests.
            session (requests.Session): Requests session object.
            conversation_id: ID to fetch conversational context
            google_translator_api_key (str): Google cloud translation API key.
            language (str): Natural language code for translation (e.g., "en", "ko", "ja").
            run_code (bool): Whether to directly execute the code included in the answer (Python only)
            token_from_browser (bool): Gets a token from the browser
        """
        self.token = self._get_token(token, token_from_browser)
        self.proxies = proxies
        self.timeout = timeout
        self._reqid = int("".join(random.choices(string.digits, k=4)))
        self.conversation_id = conversation_id or ""
        self.response_id = ""
        self.choice_id = ""
        self.session = self._get_session(session)
        self.SNlM0e = self._get_snim0e()
        self.language = language or os.getenv("_BARD_API_LANG")
        self.run_code = run_code
        self.google_translator_api_key = google_translator_api_key

    def _get_token(self, token, token_from_browser):
        """
        Get the Bard API token either from the provided token or from the browser cookie.

        Args:
            token (str): Bard API token.
            token_from_browser (bool): Whether to extract the token from the browser cookie.

        Returns:
            str: The Bard API token.
        Raises:
            Exception: If the token is not provided and can't be extracted from the browser.
        """
        if token:
            return token
        elif os.getenv("_BARD_API_KEY"):
            return os.getenv("_BARD_API_KEY")
        elif token_from_browser:
            extracted_cookie_dict = extract_bard_cookie(cookies=False)
            if not extracted_cookie_dict:
                raise Exception("Failed to extract cookie from browsers.")
            return extracted_cookie_dict["__Secure-1PSID"]
        else:
            raise Exception(
                "Bard API Key must be provided as token argument or extracted from browser."
            )

    def _get_session(self, session):
        """
        Get the requests Session object.

        Args:
            session (requests.Session): Requests session object.

        Returns:
            requests.Session: The Session object.
        """
        if session is None:
            new_session = requests.Session()
            new_session.headers = SESSION_HEADERS
            new_session.cookies.set("__Secure-1PSID", self.token)
            new_session.proxies = self.proxies
            return new_session
        else:
            return session

    def _get_snim0e(self) -> str:
        """
        Get the SNlM0e value from the Bard API response.

        Returns:
            str: SNlM0e value.
        Raises:
            Exception: If the __Secure-1PSID value is invalid or SNlM0e value is not found in the response.
        """
        if not self.token or self.token[-1] != ".":
            raise Exception(
                "__Secure-1PSID value must end with a single dot. Enter correct __Secure-1PSID value."
            )
        resp = self.session.get(
            "https://bard.google.com/", timeout=self.timeout, proxies=self.proxies
        )
        if resp.status_code != 200:
            raise Exception(
                f"Response status code is not 200. Response Status is {resp.status_code}"
            )
        snim0e = re.search(r"SNlM0e\":\"(.*?)\"", resp.text)
        if not snim0e:
            raise Exception(
                "SNlM0e value not found. Double-check __Secure-1PSID value or pass it as token='xxxxx'."
            )
        return snim0e.group(1)

    def get_answer(self, input_text: str) -> dict:
        """
                Get an answer from the Bard API for the given input text.

                Example:
                >>> token = 'xxxxxx'
                >>> bard = Bard(token=token)
                >>> response = bard.get_answer("나와 내 동년배들이 좋아하는 뉴진스에 대해서 알려줘")
                >>> print(response['content'])

                Args:
                    input_text (str): Input text for the query.
        blac
                Returns:
                    dict: Answer from the Bard API in the following format:
                        {
                            "content": str,
                            "conversation_id": str,
                            "response_id": str,
                            "factuality_queries": list,
                            "text_query": str,
                            "choices": list,
                            "links": list,
                            "images": set,
                            "program_lang": str,
                            "code": str,
                            "status_code": int
                        }
        """
        params = {
            "bl": "boq_assistant-bard-web-server_20230713.13_p0",
            "_reqid": str(self._reqid),
            "rt": "c",
        }
        if self.google_translator_api_key is not None:
            google_official_translator = translate.Client(
                api_key=self.google_translator_api_key
            )

        # [Optional] Set language
        if (
            self.language is not None
            and self.language not in ALLOWED_LANGUAGES
            and self.google_translator_api_key is None
        ):
            translator_to_eng = GoogleTranslator(source="auto", target="en")
            input_text = translator_to_eng.translate(input_text)
        elif (
            self.language is not None
            and self.language not in ALLOWED_LANGUAGES
            and self.google_translator_api_key is not None
        ):
            input_text = google_official_translator.translate(
                input_text, target_language="en"
            )

        # Make post data structure and insert prompt
        input_text_struct = [
            [input_text],
            None,
            [self.conversation_id, self.response_id, self.choice_id],
        ]
        data = {
            "f.req": json.dumps([None, json.dumps(input_text_struct)]),
            "at": self.SNlM0e,
        }

        # Get response
        resp = self.session.post(
            "https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
            params=params,
            data=data,
            timeout=self.timeout,
        )

        # Post-processing of response
        resp_dict = json.loads(resp.content.splitlines()[3])[0][2]

        if not resp_dict:
            return {
                "content": f"Response Error: {resp.content}. "
                f"\nUnable to get response."
                f"\nPlease double-check the cookie values and verify your network environment or google account."
            }
        resp_json = json.loads(resp_dict)

        # [Optional] gather image links
        images = set()
        try:
            if len(resp_json) >= 3:
                nested_list = resp_json[4][0][4]
                for img in nested_list:
                    images.add(img[0][0][0])
        except (IndexError, TypeError, KeyError):
            pass

        # Parsed Answer Object
        parsed_answer = json.loads(resp_dict)

        # [Optional] translated by google translator
        # Unofficial
        if (
            self.language is not None
            and self.language not in ALLOWED_LANGUAGES
            and self.google_translator_api_key is None
        ):
            translator_to_lang = GoogleTranslator(source="auto", target=self.language)
            parsed_answer[4] = [
                [x[0], [translator_to_lang.translate(x[1][0])] + x[1][1:], x[2]]
                for x in parsed_answer[4]
            ]

        # Official google cloud translation API
        elif (
            self.language is not None
            and self.language not in ALLOWED_LANGUAGES
            and self.google_translator_api_key is not None
        ):
            parsed_answer[4] = [
                [
                    x[0],
                    [google_official_translator(x[1][0], target_language=self.language)]
                    + x[1][1:],
                    x[2],
                ]
                for x in parsed_answer[4]
            ]

        # [Optional] get program_lang & code
        try:
            program_lang = (
                parsed_answer[4][0][1][0].split("```")[1].split("\n")[0].strip()
            )
            code = parsed_answer[4][0][1][0].split("```")[1][len(program_lang) :]
        except Exception:
            program_lang, code = None, None

        # Returnd dictionary object
        bard_answer = {
            "content": parsed_answer[4][0][1][0],
            "conversation_id": parsed_answer[1][0],
            "response_id": parsed_answer[1][1],
            "factuality_queries": parsed_answer[3],
            "text_query": parsed_answer[2][0] if parsed_answer[2] else "",
            "choices": [{"id": x[0], "content": x[1]} for x in parsed_answer[4]],
            "links": extract_links(parsed_answer[4]),
            "images": images,
            "program_lang": program_lang,
            "code": code,
            "status_code": resp.status_code,
        }
        self.conversation_id, self.response_id, self.choice_id = (
            bard_answer["conversation_id"],
            bard_answer["response_id"],
            bard_answer["choices"][0]["id"],
        )
        self._reqid += 100000

        # Execute code
        if self.run_code and bard_answer["code"] is not None:
            try:
                print(bard_answer["code"])
                exec(bard_answer["code"])
            except Exception:
                pass

        return bard_answer

    def speech(self, input_text: str, lang="en-US") -> dict:
        """
        Get speech audio from Bard API for the given input text.

        Example:
        >>> token = 'xxxxxx'
        >>> bard = Bard(token=token)
        >>> audio = bard.speech("hello!")
        >>> with open("bard.ogg", "wb") as f:
        >>>     f.write(bytes(audio['audio']))

        Args:
            input_text (str): Input text for the query.
            lang (str): Input language for the query.

        Returns:
            dict: Answer from the Bard API in the following format:
            {
                "audio": bytes,
                "status_code": int
            }
        """
        params = {
            "bl": "boq_assistant-bard-web-server_20230713.13_p0",
            "_reqid": str(self._reqid),
            "rt": "c",
        }

        input_text_struct = [
            [["XqA3Ic", json.dumps([None, input_text, lang, None, 2])]]
        ]

        data = {
            "f.req": json.dumps(input_text_struct),
            "at": self.SNlM0e,
        }

        # Get response
        resp = self.session.post(
            "https://bard.google.com/_/BardChatUi/data/batchexecute",
            params=params,
            data=data,
            timeout=self.timeout,
            proxies=self.proxies,
        )

        # Post-processing of response
        resp_dict = json.loads(resp.content.splitlines()[3])[0][2]
        if not resp_dict:
            return {
                "content": f"Response Error: {resp.content}. "
                f"\nUnable to get response."
                f"\nPlease double-check the cookie values and verify your network environment or google account."
            }
        resp_json = json.loads(resp_dict)
        audio_b64 = resp_json[0]
        audio_bytes = base64.b64decode(audio_b64)
        return {"audio": audio_bytes, "status_code": resp.status_code}

    def export_conversation(self, bard_answer, title: str = ""):
        """
        Get Share URL for specific answer from bard

        Example:
        >>> token = 'xxxxxx'
        >>> bard = Bard(token=token)
        >>> bard_answer = bard.get_answer("hello!")
        >>> url = bard.export_conversation(bard_answer, title="Export Conversation")
        >>> print(url['url'])

        Args:
            bard_answer (dict): bard_answer returned from get_answer
            title (str): Title for URL
        Returns:
            dict: Answer from the Bard API in the following format:
            {
                "url": str,
                "status_code": int
            }
        """
        conv_id = bard_answer["conversation_id"]
        resp_id = bard_answer["response_id"]
        choice_id = bard_answer["choices"][0]["id"]
        params = {
            "rpcids": "fuVx7",
            "source-path": "/",
            "bl": "boq_assistant-bard-web-server_20230713.13_p0",
            # '_reqid': str(self._reqid),
            "rt": "c",
        }
        input_data_struct = [
            [
                [
                    "fuVx7",
                    json.dumps(
                        [
                            [
                                None,
                                [
                                    [
                                        [conv_id, resp_id],
                                        None,
                                        None,
                                        [[], [], [], choice_id, []],
                                    ]
                                ],
                                [0, title],
                            ]
                        ]
                    ),
                    None,
                    "generic",
                ]
            ]
        ]
        data = {
            "f.req": json.dumps(input_data_struct),
            "at": self.SNlM0e,
        }
        resp = self.session.post(
            "https://bard.google.com/_/BardChatUi/data/batchexecute",
            params=params,
            data=data,
            timeout=self.timeout,
        )
        # Post-processing of response
        resp_dict = json.loads(resp.content.splitlines()[3])
        url_id = json.loads(resp_dict[0][2])[2]
        url = f"https://g.co/bard/share/{url_id}"
        # Increment request ID
        self._reqid += 100000
        return {"url": url, "status_code": resp.status_code}

    def ask_about_image(self, input_text: str, image: bytes, lang: str = None) -> dict:
        """
        Send Bard image along with question and get answer

        Example:
        >>> token = 'xxxxxx'
        >>> bard = Bard(token=token)
        >>> image = open('image.jpg', 'rb').read()
        >>> bard_answer = bard.ask_about_image("what is in the image?", image)['content']

        Args:
            input_text (str): Input text for the query.
            image (bytes): Input image bytes for the query, support image types: jpeg, png, webp
            lang (str): Language to use.

        Returns:
            dict: Answer from the Bard API in the following format:
                {
                    "content": str,
                    "conversation_id": str,
                    "response_id": str,
                    "factuality_queries": list,
                    "text_query": str,
                    "choices": list,
                    "links": list,
                    "images": set,
                    "program_lang": str,
                    "code": str,
                    "status_code": int
                }
        """
        if self.google_translator_api_key is not None:
            google_official_translator = translate.Client(
                api_key=self.google_translator_api_key
            )
        else:
            translator_to_eng = GoogleTranslator(source="auto", target="en")

        # [Optional] Set language
        if (
            (self.language is not None or lang is not None)
            and self.language not in ALLOWED_LANGUAGES
            and self.google_translator_api_key is None
        ):
            translator_to_eng = GoogleTranslator(source="auto", target="en")
            transl_text = translator_to_eng.translate(input_text)
        elif (
            (self.language is not None or lang is not None)
            and self.language not in ALLOWED_LANGUAGES
            and self.google_translator_api_key is not None
        ):
            transl_text = google_official_translator.translate(
                input_text, target_language="en"
            )
        elif (
            (self.language is None or lang is None)
            and self.language not in ALLOWED_LANGUAGES
            and self.google_translator_api_key is None
        ):
            translator_to_eng = GoogleTranslator(source="auto", target="en")
            transl_text = translator_to_eng.translate(input_text)

        # Supported format: jpeg, png, webp
        image_url = upload_image(image)

        input_data_struct = [
            None,
            [
                [transl_text, 0, None, [[[image_url, 1], "uploaded_photo.jpg"]]],
                [lang if lang is not None else self.language],
                ["", "", ""],
                "",  # Unknown random string value (1000 characters +)
                uuid.uuid4().hex,  # Should be random uuidv4 (32 characters)
                None,
                [1],
                0,
                [],
                [],
            ],
        ]
        params = {
            "bl": "boq_assistant-bard-web-server_20230716.16_p2",
            "_reqid": str(self._reqid),
            "rt": "c",
        }
        input_data_struct[1] = json.dumps(input_data_struct[1])
        data = {
            "f.req": json.dumps(input_data_struct),
            "at": self.SNlM0e,
        }

        resp = self.session.post(
            "https://bard.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate",
            params=params,
            data=data,
            timeout=self.timeout,
        )

        # Post-processing of response
        resp_dict = json.loads(resp.content.splitlines()[3])[0][2]
        if not resp_dict:
            return {
                "content": f"Response Error: {resp.content}. "
                f"\nUnable to get response."
                f"\nPlease double-check the cookie values and verify your network environment or google account."
            }
        parsed_answer = json.loads(resp_dict)
        content = parsed_answer[4][0][1][0]
        try:
            if self.language is not None and self.google_translator_api_key is None:
                translator = GoogleTranslator(source="en", target=self.language)
                translated_content = translator.translate(content)

            elif lang is not None and self.google_translator_api_key is None:
                translator = GoogleTranslator(source="en", target=lang)
                translated_content = translator.translate(content)

            elif (
                lang is None and self.language is None
            ) and self.google_translator_api_key is None:
                us_lang = detect(input_text)
                translator = GoogleTranslator(source="en", target=us_lang)
                translated_content = translator.translate(content)

            elif (
                self.language is not None and self.google_translator_api_key is not None
            ):
                translated_content = google_official_translator.translate(
                    content, target_language=self.language
                )
            elif lang is not None and self.google_translator_api_key is not None:
                translated_content = google_official_translator.translate(
                    content, target_language=lang
                )
            elif (
                self.language is None and lang is None
            ) and self.google_translator_api_key is not None:
                us_lang = detect(input_text)
                translated_content = google_official_translator.translate(
                    content, target_language=us_lang
                )
        except Exception as e:
            print(f"Translation failed, and the original text has been returned. \n{e}")
            translated_content = content

        # Returned dictionary object
        bard_answer = {
            "content": translated_content,
            "conversation_id": parsed_answer[1][0],
            "response_id": parsed_answer[1][1],
            "factuality_queries": parsed_answer[3],
            "text_query": parsed_answer[2][0] if parsed_answer[2] else "",
            "choices": [{"id": x[0], "content": x[1]} for x in parsed_answer[4]],
            "links": extract_links(parsed_answer[4]),
            "images": [""],
            "program_lang": "",
            "code": "",
            "status_code": resp.status_code,
        }
        self.conversation_id, self.response_id, self.choice_id = (
            bard_answer["conversation_id"],
            bard_answer["response_id"],
            bard_answer["choices"][0]["id"],
        )
        self._reqid += 100000
        return bard_answer

    def export_replit(
        self, code: str, program_lang: str = None, filename: str = None, **kwargs
    ):
        """
        Get export URL to repl.it from code

        Example:
        >>> token = 'xxxxxx'
        >>> bard = Bard(token=token)
        >>> bard_answer = bard.get_answer("Give me python code to print hello world")
        >>> url = bard.export_replit(bard_answer['code'], bard_answer['program_lang'])
        >>> print(url['url'])

        Args:
            code (str): source code
            program_lang (str): programming language
            filename (str): filename
            **kwargs: instructions, source_path
        Returns:
        dict: Answer from the Bard API in the following format:
            {
                "url": str,
                "status_code": int
            }
        """
        params = {
            "rpcids": "qACoKe",
            "source-path": kwargs.get("source_path", "/"),
            "bl": "boq_assistant-bard-web-server_20230718.13_p2",
            "_reqid": str(self._reqid),
            "rt": "c",
        }
        support_langs = {
            "python": "main.py",
            "javascript": "index.js",
            "go": "main.go",
            "java": "Main.java",
            "kotlin": "Main.kt",
            "php": "index.php",
            "c#": "main.cs",
            "swift": "main.swift",
            "r": "main.r",
            "ruby": "main.rb",
            "c": "main.c",
            "c++": "main.cpp",
            "matlab": "main.m",
            "typescript": "main.ts",
            "scala": "main.scala",
            "sql": "main.sql",
            "html": "index.html",
            "css": "style.css",
            "nosql": "main.nosql",
            "rust": "main.rs",
            "perl": "main.pl",
        }

        # Reference: https://github.com/jincheng9/markdown_supported_languages
        if program_lang not in support_langs and filename is None:
            raise Exception(
                f"Language {program_lang} not supported, please set filename manually."
            )

        filename = (
            support_langs.get(program_lang, filename) if filename is None else filename
        )
        input_data_struct = [
            [
                [
                    "qACoKe",
                    json.dumps(
                        [kwargs.get("instructions", ""), 5, code, [[filename, code]]]
                    ),
                    None,
                    "generic",
                ]
            ]
        ]
        data = {
            "f.req": json.dumps(input_data_struct),
            "at": self.SNlM0e,
        }

        resp = self.session.post(
            "https://bard.google.com/_/BardChatUi/data/batchexecute",
            params=params,
            data=data,
            timeout=self.timeout,
            proxies=self.proxies,
        )
        resp_dict = json.loads(resp.content.splitlines()[3])
        print(resp_dict)
        url = json.loads(resp_dict[0][2])[0]
        # Increment request ID
        self._reqid += 100000

        return {"url": url, "status_code": resp.status_code}

class Chat_Internet(Ask_Internet):
    """
    A class representing a chatbot powered by the Bard API.

    Usage:
        chat = ChatBard()
        chat.start()

    Example:
        from bardapi import ChatBard

        chat = ChatBard()
        chat.start()
    """

    USER_PROMPT = ">>> "

    def __init__(
        self,
        token: str = None,
        timeout: int = 20,
        proxies: dict = None,
        session: requests.Session = None,
        google_translator_api_key: str = None,
        language: str = None,
        token_from_browser=False,
    ):
        self.session = session or self._init_session(token)
        self.language = language or os.getenv("_BARD_API_LANG") or "english"
        self.timeout = int(timeout or os.getenv("_BARD_API_TIMEOUT") or 30)
        self.token = token or os.getenv("_BARD_API_KEY") or self._get_api_key()
        self.token_from_browser = token_from_browser
        self.proxies = proxies
        self.google_translator_api_key = google_translator_api_key

        self.bard = self._init_bard()

        # Chat history
        self.chat_history = []

    def _init_session(self, token):
        session = requests.Session()
        session.headers = SESSION_HEADERS
        session.cookies.set("__Secure-1PSID", token)
        return session

    def _get_api_key(self):
        key = input("Enter the Bard API Key(__Secure-1PSID): ")
        if not key:
            print("Bard API(__Secure-1PSID) Key must be entered.")
            exit(1)
        return key

    def _init_bard(self):
        return Ask_Internet(
            token=self.token,
            session=self.session,
            google_translator_api_key=self.google_translator_api_key,
            timeout=self.timeout,
            language=self.language,
            proxies=self.proxies,
            token_from_browser=self.token_from_browser,
        )

    def start(self, prompt: str = None) -> None:
        """
        Starts the chatbot interaction.

        Takes user input and retrieves responses from the Bard API until the user enters "quit", "q", or "stop".
        Prints the chatbot's response, including image links if available.

        Parameters:
            prompt (str): Custom prompt message for user input. If not provided, defaults to the class constant USER_PROMPT.

        Returns:
            None
        """

        prompt = prompt or self.USER_PROMPT
        print(
            f"{SEPARATOR_LINE}\n{Back.BLUE}          Welcome to Chatbot        {Back.RESET}\n{SEPARATOR_LINE}"
        )
        print("If you enter quit, q, or stop, the chat will end.")

        # Start chat
        while True:
            user_input = input(prompt).lower()
            if user_input in ["quit", "q", "stop"]:
                break

            # Validate user input
            if not self._is_valid_input(user_input):
                print(f"{Fore.RED}Invalid input! Please try again.{Fore.RESET}")
                continue

            # Get response from Bard API
            try:
                response = self.bard.get_answer(user_input)
                if response.get("error"):
                    print(f"{Fore.RED}Error: {response['error']}{Fore.RESET}")
                else:
                    self._display_response(response)
                    # Add user input and chatbot response to chat history
                    self._add_to_chat_history(user_input, response["content"])
            except requests.exceptions.RequestException as e:
                print(f"{Fore.RED}Error occurred: {str(e)}{Fore.RESET}")

        print(
            f"{SEPARATOR_LINE}\n{Fore.RED}Chat Ended.{Fore.RESET}\n\nDanielPark's Chat Template\n{SEPARATOR_LINE}"
        )

    def display_chat_history(self) -> None:
        """
        Displays the chat history.

        Prints the user input and chatbot responses from the chat history.

        Returns:
            None
        """
        print(
            f"{SEPARATOR_LINE}\n{Back.YELLOW}          Chat History        {Back.RESET}\n{SEPARATOR_LINE}"
        )

        for entry in self.chat_history:
            print(f"{Fore.GREEN}User: {entry['User']}{Fore.RESET}")
            print(f"{Fore.BLUE}Chatbot: {entry['Chatbot']}{Fore.RESET}")

        print(SEPARATOR_LINE)

    def _is_valid_input(self, user_input: str) -> bool:
        """
        Checks if the user input is valid.

        Validates the user input by checking if it is empty or exceeds a certain length.

        Parameters:
            user_input (str): The user input.

        Returns:
            bool: True if the user input is valid, False otherwise.
        """
        if not user_input:
            return False
        if len(user_input) > 1000:
            return False
        return True

    def _display_response(self, response: dict) -> None:
        """
        Displays the chatbot's response.

        Prints the chatbot's response, including image links if available.

        Parameters:
            response (dict): The response from the Bard API.

        Returns:
            None
        """
        if response.get("images"):
            print(
                f"{Fore.BLUE}{Style.BRIGHT}Chatbot: {response['content']} \n\n Image links: {response['images']}{Fore.RESET}{Style.RESET_ALL}"
            )
        else:
            print(
                f"{Fore.BLUE}{Style.BRIGHT}Chatbot: {response['content']} {Fore.RESET}{Style.RESET_ALL}"
            )

    def _add_to_chat_history(self, user_input: str, chatbot_response: str) -> None:
        """
        Adds the user input and chatbot response to the chat history.

        Parameters:
            user_input (str): The user input.
            chatbot_response (str): The chatbot's response.

        Returns:
            None
        """
        self.chat_history.append({"User": user_input, "Chatbot": chatbot_response})

#Ask Internet(New)

cf_clearance = 'MDzwnr3ZWk_ap8u.iwwMR5F3WccfOkhUy_zGNDpcF3s-1682497341-0-160'
user_agent   = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'

class PhindResponse:
    
    class Completion:
        
        class Choices:
            def __init__(self, choice: dict) -> None:
                self.text           = choice['text']
                self.content        = self.text.encode()
                self.index          = choice['index']
                self.logprobs       = choice['logprobs']
                self.finish_reason  = choice['finish_reason']
                
            def __repr__(self) -> str:
                return f'''<__main__.APIResponse.Completion.Choices(\n    text           = {self.text.encode()},\n    index          = {self.index},\n    logprobs       = {self.logprobs},\n    finish_reason  = {self.finish_reason})object at 0x1337>'''

        def __init__(self, choices: dict) -> None:
            self.choices = list(map(self.Choices, choices))

    class Usage:
        def __init__(self, usage_dict: dict) -> None:
            self.prompt_tokens      = usage_dict['prompt_tokens']
            self.completion_tokens  = usage_dict['completion_tokens']
            self.total_tokens       = usage_dict['total_tokens']

        def __repr__(self):
            return f'''<__main__.APIResponse.Usage(\n    prompt_tokens      = {self.prompt_tokens},\n    completion_tokens  = {self.completion_tokens},\n    total_tokens       = {self.total_tokens})object at 0x1337>'''
    
    def __init__(self, response_dict: dict) -> None:
        
        self.response_dict  = response_dict
        self.id             = response_dict['id']
        self.object         = response_dict['object']
        self.created        = response_dict['created']
        self.model          = response_dict['model']
        self.completion     = self.Completion(response_dict['choices'])
        self.usage          = self.Usage(response_dict['usage'])

    def json(self) -> dict:
        return self.response_dict


class Search:
    def create(prompt: str, actualSearch: bool = True, language: str = 'en') -> dict: # None = no search
        if user_agent == '':
            raise ValueError('user_agent must be set, refer to documentation')
        if cf_clearance == '' :
            raise ValueError('cf_clearance must be set, refer to documentation')
        
        if not actualSearch:
            return {
                '_type': 'SearchResponse',
                'queryContext': {
                    'originalQuery': prompt
                },
                'webPages': {
                    'webSearchUrl': f'https://www.bing.com/search?q={quote(prompt)}',
                    'totalEstimatedMatches': 0,
                    'value': []
                },
                'rankingResponse': {
                    'mainline': {
                        'items': []
                    }
                }
            }
        
        headers = {
            'authority': 'www.phind.com',
            'accept': '*/*',
            'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
            'cookie': f'cf_clearance={cf_clearance}',
            'origin': 'https://www.phind.com',
            'referer': 'https://www.phind.com/search?q=hi&c=&source=searchbox&init=true',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': user_agent
        }
        
        return post('https://www.phind.com/api/bing/search', headers = headers, json = { 
            'q': prompt,
            'userRankList': {},
            'browserLanguage': language}).json()['rawBingResults']


class Completion:
    def create(
        model = 'gpt-4', 
        prompt: str = '', 
        results: dict = None, 
        creative: bool = False, 
        detailed: bool = False, 
        codeContext: str = '',
        language: str = 'en') -> PhindResponse:
        
        if user_agent == '' :
            raise ValueError('user_agent must be set, refer to documentation')

        if cf_clearance == '' :
            raise ValueError('cf_clearance must be set, refer to documentation')
        
        if results is None:
            results = Search.create(prompt, actualSearch = True)
        
        if len(codeContext) > 2999:
            raise ValueError('codeContext must be less than 3000 characters')
        
        models = {
            'gpt-4' : 'expert',
            'gpt-3.5-turbo' : 'intermediate',
            'gpt-3.5': 'intermediate',
        }
        
        json_data = {
            'question'    : prompt,
            'bingResults' : results, #response.json()['rawBingResults'],
            'codeContext' : codeContext,
            'options': {
                'skill'   : models[model],
                'date'    : datetime.now().strftime("%d/%m/%Y"),
                'language': language,
                'detailed': detailed,
                'creative': creative
            }
        }
        
        headers = {
            'authority': 'www.phind.com',
            'accept': '*/*',
            'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
            'content-type': 'application/json',
            'cookie': f'cf_clearance={cf_clearance}',
            'origin': 'https://www.phind.com',
            'referer': 'https://www.phind.com/search?q=hi&c=&source=searchbox&init=true',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': user_agent
        }
        
        completion = ''
        response   = post('https://www.phind.com/api/infer/answer', headers = headers, json = json_data, timeout=99999, impersonate='chrome110')
        for line in response.text.split('\r\n\r\n'):
            completion += (line.replace('data: ', ''))
        
        return PhindResponse({
            'id'     : f'cmpl-1337-{int(time())}', 
            'object' : 'text_completion', 
            'created': int(time()), 
            'model'  : models[model], 
            'choices': [{
                    'text'          : completion, 
                    'index'         : 0, 
                    'logprobs'      : None, 
                    'finish_reason' : 'stop'
            }], 
            'usage': {
                'prompt_tokens'     : len(prompt), 
                'completion_tokens' : len(completion), 
                'total_tokens'      : len(prompt) + len(completion)
            }
        })
        

class StreamingCompletion:
    message_queue    = Queue()
    stream_completed = False
    
    def request(model, prompt, results, creative, detailed, codeContext, language) -> None:
        
        models = {
            'gpt-4' : 'expert',
            'gpt-3.5-turbo' : 'intermediate',
            'gpt-3.5': 'intermediate',
        }

        json_data = {
            'question'    : prompt,
            'bingResults' : results,
            'codeContext' : codeContext,
            'options': {
                'skill'   : models[model],
                'date'    : datetime.now().strftime("%d/%m/%Y"),
                'language': language,
                'detailed': detailed,
                'creative': creative
            }
        }

        headers = {
            'authority': 'www.phind.com',
            'accept': '*/*',
            'accept-language': 'en,fr-FR;q=0.9,fr;q=0.8,es-ES;q=0.7,es;q=0.6,en-US;q=0.5,am;q=0.4,de;q=0.3',
            'content-type': 'application/json',
            'cookie': f'cf_clearance={cf_clearance}',
            'origin': 'https://www.phind.com',
            'referer': 'https://www.phind.com/search?q=hi&c=&source=searchbox&init=true',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': user_agent
        }
        
        response   = post('https://www.phind.com/api/infer/answer', 
            headers = headers, json = json_data, timeout=99999, impersonate='chrome110', content_callback=StreamingCompletion.handle_stream_response)


        StreamingCompletion.stream_completed = True

    @staticmethod
    def create(
        model       : str = 'gpt-4', 
        prompt      : str = '', 
        results     : dict = None, 
        creative    : bool = False, 
        detailed    : bool = False, 
        codeContext : str = '',
        language    : str = 'en'):
        
        if user_agent == '':
            raise ValueError('user_agent must be set, refer to documentation')
        if cf_clearance == '' :
            raise ValueError('cf_clearance must be set, refer to documentation')
        
        if results is None:
            results = Search.create(prompt, actualSearch = True)
        
        if len(codeContext) > 2999:
            raise ValueError('codeContext must be less than 3000 characters')
        
        Thread(target = StreamingCompletion.request, args = [
            model, prompt, results, creative, detailed, codeContext, language]).start()
        
        while StreamingCompletion.stream_completed != True or not StreamingCompletion.message_queue.empty():
            try:
                chunk = StreamingCompletion.message_queue.get(timeout=0)

                if chunk == b'data:  \r\ndata: \r\ndata: \r\n\r\n':
                    chunk = b'data:  \n\n\r\n\r\n'
                
                chunk = chunk.decode()
                
                chunk = chunk.replace('data: \r\n\r\ndata: ', 'data: \n')
                chunk = chunk.replace('\r\ndata: \r\ndata: \r\n\r\n', '\n\n\r\n\r\n')
                chunk = chunk.replace('data: ', '').replace('\r\n\r\n', '')
                
                yield PhindResponse({
                    'id'     : f'cmpl-1337-{int(time())}', 
                    'object' : 'text_completion', 
                    'created': int(time()), 
                    'model'  : model, 
                    'choices': [{
                            'text'          : chunk, 
                            'index'         : 0, 
                            'logprobs'      : None, 
                            'finish_reason' : 'stop'
                    }], 
                    'usage': {
                        'prompt_tokens'     : len(prompt), 
                        'completion_tokens' : len(chunk), 
                        'total_tokens'      : len(prompt) + len(chunk)
                    }
                })

            except Empty:
                pass

    @staticmethod
    def handle_stream_response(response):
        StreamingCompletion.message_queue.put(response)

#Main functions

def ask(prompt : str, api_key : str, internet : bool = False):
    if api_key=="vanshshah1029384756":
        if internet==False:
          retry, max_retries = 0, 10
          client = Client()
          params = {
                  "maximumLength": 16000
                  }
          while retry < max_retries:
              try:
                  result=""
                  for chunk in client.generate("openai:gpt-3.5-turbo-16k", f"Your name is n.e.r.d., an AI language model trained by Neurum. {prompt}", params=params):
                      result += chunk
                  return result
              except:
                  retry += 1
                  if retry == max_retries:
                      raise
                  continue  
        elif internet==True: 
            
            result = Completion.create(
                model  = 'gpt-4',
                prompt = prompt,
                results     = Search.create(prompt, actualSearch = False), # create search (set actualSearch to False to disable internet)
                creative    = False,
                detailed    = False,
                codeContext = '') # up to 3000 chars of code

            response=result.completion.choices[0].text
            return response
    else:
        return "invalid api key!"
    
def ask_image(prompt : str, reference_image : str, api_key : str):
    if api_key=="vanshshah1029384756":
        net=Ask_Internet("aAgDyPFygA0nhJGaIYy1wDaixFjkw0BMXJeZCvwiFWmyfSaF2pUFWjw6GQk_QdrO8QWOKA.")
        ans=net.ask_about_image(prompt, image=open(reference_image, 'rb').read())['content']
        return ans
    else:
        return "invalid api key!"