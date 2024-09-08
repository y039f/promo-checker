import          os
import          json, time, httpx, sys, threading, ctypes, random, string, concurrent.futures, requests
from            colorama import Fore, init, Style
from            pystyle import Write, System, Colors, Colorate
from            threading import Lock, Thread, Timer
from            datetime import datetime
from            os.path import isfile, join
from            tls_client import Session
from            pystyle import Write, Colors, Colorate, Center
import          sys



required_modules = ["httpx", "requests", "pystyle", "tls_client", "colorama"]



if sys.version_info < (3, 8):
    print(f"{Fore.RED}Error: This script requires Python 3.8 or higher!{Style.RESET_ALL}")
    sys.exit()
    
    
def check_required_files():
    required_files = ["promos.txt", "proxies.txt"]
    missing_files = [file for file in required_files if not os.path.exists(file)]

    if missing_files:
        for file in missing_files:
            with open(file, "w") as f:
                pass  # Create empty files as placeholders
        print(f"{Fore.YELLOW}Created missing files: {', '.join(missing_files)}. Please fill them with appropriate data.{Style.RESET_ALL}")



def check_modules():
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"{Fore.RED}Missing modules: {', '.join(missing_modules)}{Style.RESET_ALL}")
        install = input(f"{Fore.WHITE} [?] {Fore.LIGHTBLACK_EX} Would you like to install them now? (y/n): {Style.RESET_ALL}").lower()
        if install == 'y':
            os.system(f'pip install {" ".join(missing_modules)}')
            print(f"{Fore.GREEN}Modules installed! Please restart the script.{Style.RESET_ALL}")
            sys.exit()
        else:
            print(f"{Fore.RED}Please install the required modules to continue!{Style.RESET_ALL}")
            sys.exit()
            
            
            
            
            
            
            
            
            
            
            
            

output_lock = threading.Lock()
red = Fore.RED
yellow = Fore.YELLOW
green = Fore.GREEN
blue = Fore.BLUE
orange = Fore.RED + Fore.YELLOW
pretty = Fore.LIGHTMAGENTA_EX + Fore.LIGHTCYAN_EX
magenta = Fore.MAGENTA
lightblue = Fore.LIGHTBLUE_EX
cyan = Fore.CYAN
gray = Fore.LIGHTBLACK_EX + Fore.WHITE
reset = Fore.RESET
pink = Fore.LIGHTGREEN_EX + Fore.LIGHTMAGENTA_EX
dark_green = Fore.GREEN + Style.BRIGHT

init()

class PromoChecker:
    def __init__(self, num_threads=5, proxy_type="proxyless"):
        self.total = 0
        self.valid = 0
        self.invalid = 0
        self.redeemed = 0
        self.num_threads = num_threads
        self.proxy_type = proxy_type

        self.results_dir = self.create_results_directory()

        ctypes.windll.kernel32.SetConsoleTitleW(f'[ Discord Promo Checker ] By @y039f | github.com/y039f')

    def create_results_directory(self):
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
        results_dir = os.path.join("Results", current_time)
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        return results_dir

    def get_time_rn(self):
        date = datetime.now()
        hour = date.hour
        minute = date.minute
        second = date.second
        timee = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
        return timee

    def update_title(self):
        ctypes.windll.kernel32.SetConsoleTitleW(f'[ Discord Promo Checker ] | Valid : {self.valid} | Invalid : {self.invalid} | Redeemed : {self.redeemed} | Working Rate : {round(self.valid/self.total*100,2)}%')

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def save_proxies(self, proxies):
        with open(os.path.join(self.results_dir, "proxies.txt"), "w") as file:
            file.write("\n".join(proxies))

    def get_proxies(self):
        proxies_file = "proxies.txt"
        if os.path.exists(proxies_file):
            with open(proxies_file, 'r', encoding='utf-8') as f:
                proxies = f.read().splitlines()
            return proxies if proxies else []
        return []

    def random_headers(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.1.2 Safari/602.3.12",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
        ]
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def check_promo(self, promo, proxy=None, attempt=1, max_attempts=3):
        """Sprawdza kod promocyjny"""
        final_status = None  

        if attempt > max_attempts:
            return  

        session = Session(
            client_identifier="chrome_112",
            random_tls_extension_order=True
        )

        headers = self.random_headers()

        if self.proxy_type != "proxyless" and proxy:
            if ":" in proxy and len(proxy.split(":")) == 4:
                ip, port, user, pw = proxy.split(":")
                proxy_string = f"http://{user}:{pw}@{ip}:{port}"
            else:
                ip, port = proxy.split(":")
                proxy_string = f"http://{ip}:{port}"

            session.proxies = {
                "http": proxy_string,
                "https": proxy_string
            }

        try:
            time.sleep(random.uniform(1, 3))

            r = session.get(
                f"https://discord.com/api/v9/entitlements/gift-codes/{promo}?country_code=ES&with_application=false&with_subscription_plan=true",
                headers=headers
            )

            if "You are being rate limited." in r.text:
                time.sleep(2)  
                self.check_promo(promo, proxy, attempt + 1)
            elif r.status_code != 200 or "Unknown Gift Code" in r.text:
                final_status = "invalid"  
            else:
                r_json = r.json()
                check_redeemed = r_json['redeemed']
                if not check_redeemed:
                    subscription_trial = r_json.get('subscription_trial', {})
                    interval = subscription_trial.get('interval', None)
                    interval_count = subscription_trial.get('interval_count', None)

                    max_uses, uses = r_json['max_uses'], r_json['uses']
                    if max_uses != uses:
                        final_status = "valid" 

                        interval_text = f"{interval_count}m" if interval_count else "N/A"

                        if interval == 1:
                            with open(os.path.join(self.results_dir, "promos_1m.txt"), "a+", encoding='utf-8') as f:
                                f.write(f"PromoCode ---> {promo}, Interval: {interval_text}\n")
                        elif interval == 3:
                            with open(os.path.join(self.results_dir, "promos_3m.txt"), "a+", encoding='utf-8') as f:
                                f.write(f"PromoCode ---> {promo}, Interval: {interval_text}\n")

                        with open(os.path.join(self.results_dir, "valid_promo.txt"), "a+", encoding='utf-8') as f:
                            f.write(f"Valid Promo ---> https://promos.discord.gg/{promo}, Interval: {interval_text}\n")
                    else:
                        final_status = "redeemed" 

            if final_status: 
                time_rn = self.get_time_rn()
                if final_status == "valid":
                    interval_text = f"{interval_count}m" if interval_count else "N/A"
                    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({green}+{gray}) {pretty}Valid {gray}| Interval: {green}{interval_text}{gray} |{pink} https://promos.discord.gg/{reset}{promo}")
                    self.valid += 1
                elif final_status == "invalid":
                    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({red}-{gray}) {pretty}Invalid {gray}|{pink} https://promos.discord.gg/{reset}{promo}")
                    self.invalid += 1
                elif final_status == "redeemed":
                    print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({yellow}/{gray}) {pretty}Redeemed {gray}|{pink} https://promos.discord.gg/{reset}{promo}")
                    self.redeemed += 1

                self.total += 1
                self.update_title()

        except Exception as e:
            time_rn = self.get_time_rn()
            print(f"{reset}[ {cyan}{time_rn}{reset} ] {gray}({yellow}!{gray}) {pretty}Retry {gray}| Retrying to connect... Attempt {attempt}/{max_attempts}")
            self.check_promo(promo, proxy, attempt + 1)

    def run(self):
        """Uruchamia sprawdzanie promocji"""
        try:
            with open("promos.txt", "r") as f:
                lines = f.readlines()
                promos = []
                for line in lines:
                    index = line.find(".gg/")
                    if index != -1:
                        promo = line[index + 4:].strip()
                        promos.append(promo)

            proxies = self.get_proxies() if self.proxy_type != "proxyless" else None
            if self.proxy_type != "proxyless" and not proxies:
                print(f"{red}No proxies available!{reset}")
                return

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                future_to_promo = {executor.submit(self.check_promo, promo, random.choice(proxies) if proxies else None): promo for promo in promos}

                for future in concurrent.futures.as_completed(future_to_promo):
                    try:
                        future.result()  
                    except Exception as exc:
                        print(f'{red}Generated an exception: {exc}{reset}')
            
            executor.shutdown(wait=True)

        except FileNotFoundError:
            print(f"{red}promos.txt file not found!{reset}")
        except Exception as e:
            raise

if __name__ == "__main__":
    check_modules()
    check_required_files()
    
    
    promo_checker = None

    try:
        ctypes.windll.kernel32.SetConsoleTitleW("Promo Checker") 
        System.Clear()

        ascii_art = f"""
_________ .__                   __                 
\_   ___ \|  |__   ____   ____ |  | __ ___________ 
/    \  \/|  |  \_/ __ \_/ ___\|  |/ // __ \_  __ |
\     \___|   Y  \  ___/\  \___|    <\  ___/|  | \/
 \______  /___|  /\___  >\___  >__|_  \___  >__|   
        \/     \/     \/     \/     \/    \/       
        """

        centered_ascii = Center.XCenter(ascii_art)
        info = """
         discord.gg/sDBr6fa3Rb 
         telegram: @pasjonatyk

        """
        gradient_ascii = Colorate.Horizontal(Colors.white_to_black, centered_ascii)
        informations = Colorate.Vertical(Colors.white_to_black, info)

        print(gradient_ascii)
        print(informations  )

        num_threads = int(input(f"{Fore.WHITE} [?] {Fore.LIGHTBLACK_EX} Enter the number of threads: {Style.RESET_ALL}"))

        proxy_type = input(f"{Fore.WHITE} [?] {Fore.LIGHTBLACK_EX} Choose proxy type{Fore.WHITE} (proxyless/http/socks4/socks5): {Style.RESET_ALL}").lower()

        if proxy_type not in ["proxyless", "http", "socks4", "socks5"]:
            print(f"{Fore.RED}Invalid proxy type! Defaulting to proxyless.{Style.RESET_ALL}")
            proxy_type = "proxyless"

        promo_checker = PromoChecker(num_threads=num_threads, proxy_type=proxy_type)
        promo_checker.run()
    except ValueError:
        print(f"{Fore.RED}Invalid input! Please enter a valid number for threads.{Style.RESET_ALL}")