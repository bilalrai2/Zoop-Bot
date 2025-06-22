from datetime import datetime
import time
from colorama import Fore
import requests
import random
from fake_useragent import UserAgent
import asyncio
import json
import gzip
import brotli
import zlib
import chardet
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class zoopapp:
    BASE_URL = "https://tgapi.zoop.com/api/"
    HEADERS = {
        "accept": "*/*",
        "accept-encoding": "br",
        "accept-language": "en-GB,en;q=0.9,en-US;q=0.8",
        "content-type": "application/json",
        "origin": "https://tgapp.zoop.com",
        "referer": "https://tgapp.zoop.com/",
        "sec-ch-ua": '"Microsoft Edge";v="134", "Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge WebView2";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
    }

    def __init__(self):
        self.config = self.load_config()
        self.query_list = self.load_query("query.txt")
        self.token = None
        self.userId = None
        self.session = self.sessions()
        self._original_requests = {
            "get": requests.get,
            "post": requests.post,
            "put": requests.put,
            "delete": requests.delete,
        }
        self.proxy_session = None

    def banner(self) -> None:
        """Displays the banner for the bot."""
        self.log("🎉 Zoop App Free Bot", Fore.CYAN)
        self.log("🚀 Created by BILAL STUDIO", Fore.CYAN)
        self.log("📢 Channel: https://t.me/BilalStudio3\n", Fore.CYAN)

    def log(self, message, color=Fore.RESET):
        safe_message = message.encode("utf-8", "backslashreplace").decode("utf-8")
        print(
            Fore.LIGHTBLACK_EX
            + datetime.now().strftime("[%Y:%m:%d ~ %H:%M:%S] |")
            + " "
            + color
            + safe_message
            + Fore.RESET
        )
    
    def sessions(self):
        session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504, 520]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    def decode_response(self, response):
        """
        Mendekode response dari server secara umum.

        Parameter:
            response: objek requests.Response

        Mengembalikan:
            - Jika Content-Type mengandung 'application/json', maka mengembalikan objek Python (dict atau list) hasil parsing JSON.
            - Jika bukan JSON, maka mengembalikan string hasil decode.
        """
        # Ambil header
        content_encoding = response.headers.get("Content-Encoding", "").lower()
        content_type = response.headers.get("Content-Type", "").lower()

        # Tentukan charset dari Content-Type, default ke utf-8
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=")[-1].split(";")[0].strip()

        # Ambil data mentah
        data = response.content

        # Dekompresi jika perlu
        try:
            if content_encoding == "gzip":
                data = gzip.decompress(data)
            elif content_encoding in ["br", "brotli"]:
                data = brotli.decompress(data)
            elif content_encoding in ["deflate", "zlib"]:
                data = zlib.decompress(data)
        except Exception:
            # Jika dekompresi gagal, lanjutkan dengan data asli
            pass

        # Coba decode menggunakan charset yang didapat
        try:
            text = data.decode(charset)
        except Exception:
            # Fallback: deteksi encoding dengan chardet
            detection = chardet.detect(data)
            detected_encoding = detection.get("encoding", "utf-8")
            text = data.decode(detected_encoding, errors="replace")

        # Jika konten berupa JSON, kembalikan hasil parsing JSON
        if "application/json" in content_type:
            try:
                return json.loads(text)
            except Exception:
                # Jika parsing JSON gagal, kembalikan string hasil decode
                return text
        else:
            return text

    def load_config(self) -> dict:
        """
        Loads configuration from config.json.

        Returns:
            dict: Configuration data or an empty dictionary if an error occurs.
        """
        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                self.log("✅ Configuration loaded successfully.", Fore.GREEN)
                return config
        except FileNotFoundError:
            self.log("❌ File not found: config.json", Fore.RED)
            return {}
        except json.JSONDecodeError:
            self.log(
                "❌ Failed to parse config.json. Please check the file format.",
                Fore.RED,
            )
            return {}

    def load_query(self, path_file: str = "query.txt") -> list:
        """
        Loads a list of queries from the specified file.

        Args:
            path_file (str): The path to the query file. Defaults to "query.txt".

        Returns:
            list: A list of queries or an empty list if an error occurs.
        """
        self.banner()

        try:
            with open(path_file, "r") as file:
                queries = [line.strip() for line in file if line.strip()]

            if not queries:
                self.log(f"⚠️ Warning: {path_file} is empty.", Fore.YELLOW)

            self.log(f"✅ Loaded {len(queries)} queries from {path_file}.", Fore.GREEN)
            return queries

        except FileNotFoundError:
            self.log(f"❌ File not found: {path_file}", Fore.RED)
            return []
        except Exception as e:
            self.log(f"❌ Unexpected error loading queries: {e}", Fore.RED)
            return []

    def login(self, index: int) -> None:
        self.log("🔐 Attempting to log in...", Fore.GREEN)

        if index >= len(self.query_list):
            self.log("❌ Invalid login index. Please check again.", Fore.RED)
            return

        token = self.query_list[index]
        self.log(
            f"📋 Using token: {token[:10]}... (truncated for security)",
            Fore.CYAN,
        )

        req_url = f"{self.BASE_URL}oauth/telegram"
        payload = {"initData": token}
        headers = self.HEADERS

        try:
            self.log("📡 Sending login request...", Fore.CYAN)
            response = requests.post(req_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            if "data" in data:
                data = data["data"]
                access_token = data.get("access_token")
                if not access_token:
                    self.log("❌ Access token not found in response.", Fore.RED)
                    return

                info = data.get("information", {})
                self.token = access_token  # Simpan access_token ke self.token
                self.userId = info.get("userId", "Unknow")

                username = info.get("username", "Unknown")
                year_join = info.get("yearJoin", "N/A")
                point = info.get("point", 0)
                spin = info.get("spin", 0)
                is_premium = info.get("isPremium", False)

                self.log("✅ Login successful!", Fore.GREEN)
                self.log(f"👤 Username: {username}", Fore.LIGHTGREEN_EX)
                self.log(f"🎂 Year Joined: {year_join}", Fore.CYAN)
                self.log(f"⭐ Premium: {is_premium}", Fore.CYAN)
                self.log(f"💎 Points: {point}", Fore.CYAN)
                self.log(f"🔄 Spins: {spin}", Fore.CYAN)
            else:
                self.log("⚠️ Unexpected response structure.", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to send login request: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error (possible JSON issue): {e}", Fore.RED)
        except KeyError as e:
            self.log(f"❌ Key error: {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)

    def spin(self) -> None:
        from datetime import datetime, UTC

        self.log("🎰 Starting spin process...", Fore.GREEN)

        headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}
        spin_url = f"{self.BASE_URL}users/spin"

        retry_limit = 3  # maksimal 3 percobaan saat gagal
        while True:
            current_date = datetime.now(UTC).isoformat().replace("+00:00", "Z")
            payload = {
                "userId": self.userId,
                "date": current_date
            }

            self.log("🎡 Attempting spin...", Fore.CYAN)

            retries = 0
            while retries < retry_limit:
                try:
                    response = requests.post(spin_url, headers=headers, json=payload, timeout=10)
                    response.raise_for_status()
                    spin_data = self.decode_response(response)

                    if "data" not in spin_data:
                        self.log("⚠️ No 'data' in response. Spin ended.", Fore.YELLOW)
                        return

                    result = spin_data["data"]
                    reward = result.get("circle", {}).get("name", "N/A")
                    self.log(f"✅ Spin successful! Reward: {reward}", Fore.GREEN)
                    break  # keluar dari retry loop dan lanjut spin berikutnya

                except requests.exceptions.Timeout:
                    retries += 1
                    self.log(f"⏳ Timeout occurred. Retry {retries}/{retry_limit}...", Fore.YELLOW)
                except Exception as e:
                    self.log(f"❌ Spin failed: {e}", Fore.RED)
                    return

            if retries >= retry_limit:
                self.log("❌ Maximum retries reached. Exiting spin.", Fore.RED)
                return
            
    def daily(self) -> None:
        self.log("🌞 Checking daily reward status...", Fore.GREEN)
        headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}

        try:
            # Ambil status daily dari endpoint baru
            get_url = f"{self.BASE_URL}tasks/{self.userId}"
            response = requests.get(get_url, headers=headers)
            response.raise_for_status()
            data = self.decode_response(response)

            if "data" in data:
                daily_info = data["data"]
                claimed = daily_info.get("claimed", True)
                daily_index = daily_info.get("dailyIndex", None)

                if not claimed:
                    self.log("🎁 Daily reward not yet claimed, attempting to claim...", Fore.CYAN)
                    
                    # Klaim daily reward jika belum diklaim
                    reward_url = f"{self.BASE_URL}tasks/rewardDaily/{self.userId}"
                    payload = {"index": daily_index}

                    reward_response = requests.post(reward_url, headers=headers, json=payload)
                    reward_response.raise_for_status()
                    reward_data = self.decode_response(reward_response)

                    if "data" in reward_data:
                        self.log("✅ Daily reward claimed successfully!", Fore.GREEN)
                    else:
                        self.log("⚠️ Unexpected response structure when claiming reward.", Fore.YELLOW)
                else:
                    self.log("✔️ Daily reward has already been claimed today.", Fore.YELLOW)
            else:
                self.log("⚠️ Unexpected response structure from task status API.", Fore.YELLOW)

        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to claim daily reward: {e}", Fore.RED)
        except ValueError as e:
            self.log(f"❌ Data error (possibly JSON): {e}", Fore.RED)
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", Fore.RED)

    def task(self) -> None:
        def fetch_tasks():
            self.log("🧩 [Phase 1] Fetching task list from server...", Fore.GREEN)
            headers = {**self.HEADERS, "Authorization": f"Bearer {self.token}"}
            url = f"{self.BASE_URL}social"
            try:
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                data = self.decode_response(resp)
                return data.get("data", [])
            except Exception as e:
                self.log(f"❌ Failed to fetch tasks: {e}", Fore.RED)
                return []

        # Ambil semua tugas
        tasks = fetch_tasks()
        if not tasks:
            self.log("⚠️ No tasks available.", Fore.YELLOW)
            return

        # Bagi tugas berdasarkan expired flag
        expired_tasks = [t for t in tasks if t.get("expired", False)]
        pending_tasks = [t for t in tasks if not t.get("expired", False)]

        # Ringkasan Phase 1
        self.log(f"📋 Total tasks: {len(tasks)} (Pending: {len(pending_tasks)}, Expired: {len(expired_tasks)})", Fore.BLUE)
        if expired_tasks:
            self.log("❌ Expired tasks:", Fore.YELLOW)
            for t in expired_tasks:
                self.log(f" - {t.get('title')}", Fore.YELLOW)
        if pending_tasks:
            self.log("⌛ Pending tasks:", Fore.CYAN)
            for t in pending_tasks:
                self.log(f" - {t.get('title')}", Fore.CYAN)
        else:
            self.log("🎯 No pending tasks to claim.", Fore.GREEN)
            return

        # Phase 2: klaim semua pending tasks
        self.log("⚙️ [Phase 2] Claiming pending tasks...", Fore.MAGENTA)
        claimed_ids = []
        for task in pending_tasks:
            try:
                task_id = task.get("_id")
                task_title = task.get("title", "Unknown")
                # Perbaiki URL klaim: gunakan tasks/verified/{userId}
                claim_url = f"{self.BASE_URL}tasks/verified/{self.userId}"
                payload = {
                    "point": task.get("point", 0),
                    "spin": task.get("spin", 0),
                    "type": task.get("type", "")
                }

                # Eksekusi klaim
                r = requests.post(
                    claim_url,
                    headers={**self.HEADERS, "Authorization": f"Bearer {self.token}"},
                    json=payload
                )
                r.raise_for_status()
                res = self.decode_response(r)
                if res.get("data"):
                    self.log(f"🎉 Claimed '{task_title}' successfully.", Fore.GREEN)
                    claimed_ids.append(task_id)
                else:
                    self.log(f"⚠️ Unexpected claim response for '{task_title}': {res}", Fore.YELLOW)
            except Exception as e:
                self.log(f"❌ Error during claim for '{task.get('title')}': {e}", Fore.RED)

        # Phase 3: update status lokal
        self.log("🔄 [Phase 3] Updating local status...", Fore.MAGENTA)
        new_expired = [t for t in pending_tasks if t.get('_id') in claimed_ids]
        still_pending = [t for t in pending_tasks if t.get('_id') not in claimed_ids]
        self.log(f"Pending: {len(still_pending)}, Claimed: {len(new_expired)}", Fore.BLUE)
        if new_expired:
            self.log("✅ Newly claimed tasks:", Fore.GREEN)
            for t in new_expired:
                self.log(f" - {t.get('title')}", Fore.GREEN)
        if still_pending:
            self.log("⌛ Still pending:", Fore.CYAN)
            for t in still_pending:
                self.log(f" - {t.get('title')}", Fore.CYAN)



    def load_proxies(self, filename="proxy.txt"):
        """
        Reads proxies from a file and returns them as a list.

        Args:
            filename (str): The path to the proxy file.

        Returns:
            list: A list of proxy addresses.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                proxies = [line.strip() for line in file if line.strip()]
            if not proxies:
                raise ValueError("Proxy file is empty.")
            return proxies
        except Exception as e:
            self.log(f"❌ Failed to load proxies: {e}", Fore.RED)
            return []

    def set_proxy_session(self, proxies: list) -> requests.Session:
        """
        Creates a requests session with a working proxy from the given list.

        If a chosen proxy fails the connectivity test, it will try another proxy
        until a working one is found. If no proxies work or the list is empty, it
        will return a session with a direct connection.

        Args:
            proxies (list): A list of proxy addresses (e.g., "http://proxy_address:port").

        Returns:
            requests.Session: A session object configured with a working proxy,
                            or a direct connection if none are available.
        """
        # If no proxies are provided, use a direct connection.
        if not proxies:
            self.log("⚠️ No proxies available. Using direct connection.", Fore.YELLOW)
            self.proxy_session = requests.Session()
            return self.proxy_session

        # Copy the list so that we can modify it without affecting the original.
        available_proxies = proxies.copy()

        while available_proxies:
            proxy_url = random.choice(available_proxies)
            self.proxy_session = requests.Session()
            self.proxy_session.proxies = {"http": proxy_url, "https": proxy_url}

            try:
                test_url = "https://httpbin.org/ip"
                response = self.proxy_session.get(test_url, timeout=5)
                response.raise_for_status()
                origin_ip = response.json().get("origin", "Unknown IP")
                self.log(
                    f"✅ Using Proxy: {proxy_url} | Your IP: {origin_ip}", Fore.GREEN
                )
                return self.proxy_session
            except requests.RequestException as e:
                self.log(f"❌ Proxy failed: {proxy_url} | Error: {e}", Fore.RED)
                # Remove the failed proxy and try again.
                available_proxies.remove(proxy_url)

        # If none of the proxies worked, use a direct connection.
        self.log("⚠️ All proxies failed. Using direct connection.", Fore.YELLOW)
        self.proxy_session = requests.Session()
        return self.proxy_session

    def override_requests(self):
        """Override requests functions globally when proxy is enabled."""
        if self.config.get("proxy", False):
            self.log("[CONFIG] 🛡️ Proxy: ✅ Enabled", Fore.YELLOW)
            proxies = self.load_proxies()
            self.set_proxy_session(proxies)

            # Override request methods
            requests.get = self.proxy_session.get
            requests.post = self.proxy_session.post
            requests.put = self.proxy_session.put
            requests.delete = self.proxy_session.delete
        else:
            self.log("[CONFIG] proxy: ❌ Disabled", Fore.RED)
            # Restore original functions if proxy is disabled
            requests.get = self._original_requests["get"]
            requests.post = self._original_requests["post"]
            requests.put = self._original_requests["put"]
            requests.delete = self._original_requests["delete"]


async def process_account(account, original_index, account_label, zoop, config):

    ua = UserAgent()
    zoop.HEADERS["user-agent"] = ua.random

    # Menampilkan informasi akun
    display_account = account[:10] + "..." if len(account) > 10 else account
    zoop.log(f"👤 Processing {account_label}: {display_account}", Fore.YELLOW)

    # Override proxy jika diaktifkan
    if config.get("proxy", False):
        zoop.override_requests()
    else:
        zoop.log("[CONFIG] Proxy: ❌ Disabled", Fore.RED)

    # Login (fungsi blocking, dijalankan di thread terpisah) dengan menggunakan index asli (integer)
    await asyncio.to_thread(zoop.login, original_index)

    zoop.log("🛠️ Starting task execution...", Fore.CYAN)
    tasks_config = {
        "daily": "Automatically claim your daily reward! 🌞",
        "task": "Automatically complete your tasks! ✅",
        "spin": "Automatically spin the wheel! 🎰"
    }

    for task_key, task_name in tasks_config.items():
        task_status = config.get(task_key, False)
        color = Fore.YELLOW if task_status else Fore.RED
        zoop.log(
            f"[CONFIG] {task_name}: {'✅ Enabled' if task_status else '❌ Disabled'}",
            color,
        )
        if task_status:
            zoop.log(f"🔄 Executing {task_name}...", Fore.CYAN)
            await asyncio.to_thread(getattr(zoop, task_key))

    delay_switch = config.get("delay_account_switch", 10)
    zoop.log(
        f"➡️ Finished processing {account_label}. Waiting {Fore.WHITE}{delay_switch}{Fore.CYAN} seconds before next account.",
        Fore.CYAN,
    )
    await asyncio.sleep(delay_switch)


async def worker(worker_id, zoop, config, queue):
    """
    Setiap worker akan mengambil satu akun dari antrian dan memprosesnya secara berurutan.
    Worker tidak akan mengambil akun baru sebelum akun sebelumnya selesai diproses.
    """
    while True:
        try:
            original_index, account = queue.get_nowait()
        except asyncio.QueueEmpty:
            break
        account_label = f"Worker-{worker_id} Account-{original_index+1}"
        await process_account(account, original_index, account_label, zoop, config)
        queue.task_done()
    zoop.log(f"Worker-{worker_id} finished processing all assigned accounts.", Fore.CYAN)


async def main():
    zoop = zoopapp() 
    config = zoop.load_config()
    all_accounts = zoop.query_list
    num_threads = config.get("thread", 1)  # Jumlah worker sesuai konfigurasi

    if config.get("proxy", False):
        proxies = zoop.load_proxies()

    zoop.log(
        "🎉 [LIVEXORDS] === Welcome to Zoop App Automation === [LIVEXORDS]", Fore.YELLOW
    )
    zoop.log(f"📂 Loaded {len(all_accounts)} accounts from query list.", Fore.YELLOW)

    while True:
        # Buat queue baru dan masukkan semua akun (dengan index asli)
        queue = asyncio.Queue()
        for idx, account in enumerate(all_accounts):
            queue.put_nowait((idx, account))

        # Buat task worker sesuai dengan jumlah thread yang diinginkan
        workers = [
            asyncio.create_task(worker(i + 1, zoop, config, queue))
            for i in range(num_threads)
        ]

        # Tunggu hingga semua akun di queue telah diproses
        await queue.join()

        # Opsional: batalkan task worker (agar tidak terjadi tumpang tindih)
        for w in workers:
            w.cancel()

        zoop.log("🔁 All accounts processed. Restarting loop.", Fore.CYAN)
        delay_loop = config.get("delay_loop", 30)
        zoop.log(
            f"⏳ Sleeping for {Fore.WHITE}{delay_loop}{Fore.CYAN} seconds before restarting.",
            Fore.CYAN,
        )
        await asyncio.sleep(delay_loop)


if __name__ == "__main__":
    asyncio.run(main())