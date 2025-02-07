import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import re
import concurrent.futures
import queue
import threading
import textwrap
from deep_translator import GoogleTranslator
from itertools import cycle
import json
from typing import Dict

class RenPyTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Ren'Py Turbo Translator v2")
        self.root.geometry("1200x800")
        self.running = False
        self.placeholder_counter = 0
        
        # Dil desteği
        self.target_language = tk.StringVar(value='tr')
        self.languages = {
            'Türkçe': 'tr',
            'español': 'es',
            'English': 'en',
            'Afrikaans': 'af',
            'shqip': 'sq',
            'አማርኛ': 'am',
            'العربية': 'ar',
            'հայերեն': 'hy',
            'azərbaycan dili': 'az',
            'euskara': 'eu',
            'беларуская': 'be',
            'বাংলা': 'bn',
            'bosanski': 'bs',
            'български': 'bg',
            'català': 'ca',
            'Sinugbuanong Binisaya': 'ceb',
            'Chichewa': 'ny',
            '简体中文': 'zh-CN',
            '繁體中文': 'zh-TW',
            'corsu': 'co',
            'hrvatski': 'hr',
            'čeština': 'cs',
            'dansk': 'da',
            'Nederlands': 'nl',
            'Esperanto': 'eo',
            'eesti': 'et',
            'Filipino': 'tl',
            'suomi': 'fi',
            'français': 'fr',
            'Frysk': 'fy',
            'galego': 'gl',
            'ქართული': 'ka',
            'Deutsch': 'de',
            'Ελληνικά': 'el',
            'ગુજરાતી': 'gu',
            'Kreyòl ayisyen': 'ht',
            'Hausa': 'ha',
            'ʻŌlelo Hawaiʻi': 'haw',
            'עברית': 'he',
            'हिन्दी': 'hi',
            'Hmoob': 'hmn',
            'magyar': 'hu',
            'íslenska': 'is',
            'Igbo': 'ig',
            'Bahasa Indonesia': 'id',
            'Gaeilge': 'ga',
            'Italiano': 'it',
            '日本語': 'ja',
            'Basa Jawa': 'jw',
            'ಕನ್ನಡ': 'kn',
            'қазақ тілі': 'kk',
            'ខ្មែរ': 'km',
            '한국어': 'ko',
            'кыргызча': 'ky',
            'ພາສາລາວ': 'lo',
            'Latina': 'la',
            'latviešu': 'lv',
            'lietuvių': 'lt',
            'Lëtzebuergesch': 'lb',
            'македонски': 'mk',
            'Malagasy': 'mg',
            'Bahasa Melayu': 'ms',
            'മലയാളം': 'ml',
            'Malti': 'mt',
            'Māori': 'mi',
            'मराठी': 'mr',
            'Монгол': 'mn',
            'မြန်မာဘာသာ': 'my',
            'नेपाली': 'ne',
            'norsk': 'no',
            'پښتو': 'ps',
            'فارسی': 'fa',
            'polski': 'pl',
            'português': 'pt',
            'ਪੰਜਾਬੀ': 'pa',
            'română': 'ro',
            'русский': 'ru',
            'Gagana Samoa': 'sm',
            'Gàidhlig': 'gd',
            'српски': 'sr',
            'Sesotho': 'st',
            'chiShona': 'sn',
            'سنڌي': 'sd',
            'සිංහල': 'si',
            'slovenčina': 'sk',
            'slovenščina': 'sl',
            'Soomaali': 'so',
            'Basa Sunda': 'su',
            'Kiswahili': 'sw',
            'svenska': 'sv',
            'тоҷикӣ': 'tg',
            'தமிழ்': 'ta',
            'తెలుగు': 'te',
            'ไทย': 'th',
            'українська': 'uk',
            'اردو': 'ur',
            'O‘zbek': 'uz',
            'Tiếng Việt': 'vi',
            'Cymraeg': 'cy',
            'isiXhosa': 'xh',
            'ייִדיש': 'yi',
            'Yorùbá': 'yo',
            'isiZulu': 'zu'
        }
        
        # Çeviri önbelleği
        self.cache_file = 'translation_cache.json'
        self.translation_cache = self.load_cache()
        
        self.proxy_list = []
        self.good_proxies = []
        self.bad_proxies = []
        self.proxy_cycle = None  # Proxy döngüsü, proxy yüklendikten sonra ayarlanacak.
        self.max_workers = os.cpu_count() * 8
        
        # GUI bileşenleri ve stil
        self.setup_ui()
        self.setup_styles()
        self.root.after(50, self.update_progress)  # progress güncellemesi için
        
        # Kod desenleri
        self.code_patterns = [
            r'(\[.*?\])', r'(\{.*?\})', r'(<.*?>)',
            r'(@\d+)', r'(\b\w+_\w+\b)', r'\b\w+\.(png|jpg|mp3|ogg)\b',
            r'\\"'
        ]
        self.placeholder_cycle = cycle([f"§{i}§" for i in range(1000)])
        self.progress_queue = queue.Queue()
        self.active_proxy = "Proxy Yok"
        self.file_status = {}

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=10, pady=10, fill='both', expand=True)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=5)

        lang_frame = ttk.Frame(control_frame)
        lang_frame.pack(side='left', padx=5)
        ttk.Label(lang_frame, text="Hedef Dil:").pack(side='left')
        self.lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.target_language,
            values=list(self.languages.keys()),
            state='readonly',
            width=15
        )
        self.lang_combo.pack(side='left', padx=5)
        self.lang_combo.current(0)
        
        proxy_frame = ttk.Frame(control_frame)
        proxy_frame.pack(side='left', padx=5)
        ttk.Label(proxy_frame, text="Proxy Listesi:").pack(side='left')
        self.proxy_text = scrolledtext.ScrolledText(proxy_frame, height=3, width=30)
        self.proxy_text.pack(side='left', padx=5)
        ttk.Button(proxy_frame, text="Yükle", command=self.load_proxies).pack(side='left', padx=5)
        self.proxy_status = ttk.Label(proxy_frame, text="Aktif Proxy: Yok")
        self.proxy_status.pack(side='left', padx=5)

        file_frame = ttk.Frame(control_frame)
        file_frame.pack(side='left', padx=5)
        ttk.Button(file_frame, text="Klasör Seç", command=self.select_folder).pack()
        self.folder_label = ttk.Label(file_frame, text="Seçilen Klasör: Yok")
        self.folder_label.pack()

        # Treeview ve sağa yerleştirilmiş scrollbar
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=('Dosya', 'Durum', 'İlerleme'), show='headings')
        self.tree.heading('Dosya', text='Dosya Adı')
        self.tree.heading('Durum', text='Durum')
        self.tree.heading('İlerleme', text='İlerleme')
        self.tree.column('Dosya', width=400)
        self.tree.column('Durum', width=150)
        self.tree.column('İlerleme', width=100)
        self.tree.pack(side='left', fill='both', expand=True)

        tree_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        tree_scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        self.console = scrolledtext.ScrolledText(main_frame, height=10, bg='#34495e', fg='#ecf0f1')
        self.console.pack(fill='both', expand=True, pady=5)

        ttk.Button(main_frame, text="ÇEVİRİYİ BAŞLAT", command=self.start_translation_thread).pack(pady=10)
        label = tk.Label(main_frame, text="Made by HAN")
        label.pack(side="right", padx=(10, 0))
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        colors = {
            'primary': '#3498db', 
            'secondary': '#2980b9',
            'background': '#2c3e50',
            'text': '#ecf0f1'
        }
        self.root.config(bg=colors['background'])
        style.configure('TButton', foreground=colors['text'], background=colors['primary'])
        style.configure('TLabel', background=colors['background'], foreground=colors['text'])
        style.configure('Treeview', background='#34495e', fieldbackground='#34495e', foreground='white')
        style.map('TButton', background=[('active', colors['secondary'])])

    def load_proxies(self):
        try:
            with open("proxies.txt", "r") as f:
                self.proxy_list = [line.strip() for line in f if line.strip()]
            
            if self.proxy_list:
                self.good_proxies = self.proxy_list.copy()
                self.bad_proxies = []
                self.proxy_cycle = self.get_proxy_cycle()
                self.log(f"Yüklendi: {len(self.proxy_list)} proxy")
            else:
                self.log("Proxy bulunamadı! Direkt bağlantı kullanılacak")
        except Exception as e:
            self.log(f"Proxy yükleme hatası: {str(e)}")

    def get_proxy(self):
        while self.good_proxies:
            proxy = self.good_proxies.pop(0)
            if proxy not in self.bad_proxies:
                return proxy
        return None

    def get_proxy_cycle(self):
        while True:
            for proxy in self.good_proxies:
                if proxy not in self.bad_proxies:
                    yield proxy
            if not self.good_proxies:
                yield None

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        self.folder_label.config(text=f"Seçilen Klasör: {self.folder_path}")
        self.populate_file_tree()

    def populate_file_tree(self):
        self.tree.delete(*self.tree.get_children())
        for root_dir, _, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith('.rpy'):
                    self.tree.insert('', 'end', values=(file, 'Bekliyor', '%0'))
                    self.file_status[file] = {'status': 'Bekliyor', 'progress': 0}

    def log(self, message):
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)

    # Sürekli her 50ms çalışarak kuyruğu kontrol eder
    def update_progress(self):
        try:
            while not self.progress_queue.empty():
                msg_type, content = self.progress_queue.get_nowait()
                if msg_type == 'progress':
                    file_name, progress, status = content
                    self.update_file_status(file_name, progress, status)
                elif msg_type == 'log':
                    self.log(content)
                elif msg_type == 'error':
                    self.log(f"Kritik Hata: {content}")
        except queue.Empty:
            pass
        self.root.after(50, self.update_progress)

    def process_text(self, text):
        replacements = {}
        for pattern in self.code_patterns:
            for match in re.finditer(pattern, text):
                placeholder = next(self.placeholder_cycle)
                replacements[placeholder] = match.group(0)
                text = text.replace(match.group(0), placeholder, 1)
        return text, replacements

    def translate_text(self, text: str) -> str:
        target_lang = self.languages[self.target_language.get()]
        retries = 3
        
        for attempt in range(retries):
            proxy = next(self.proxy_cycle) if self.proxy_cycle else None
            try:
                translator = GoogleTranslator(
                    source='auto',
                    target=target_lang,
                    proxies={'http': proxy, 'https': proxy} if proxy else None,
                    timeout=10
                )
                translated = translator.translate(text)
                
                # Başarılı proxy'i listenin başına al
                if proxy and proxy in self.good_proxies:
                    self.good_proxies.remove(proxy)
                    self.good_proxies.insert(0, proxy)
                return translated
            except Exception as e:
                if proxy:
                    self.bad_proxies.append(proxy)
                    if proxy in self.good_proxies:
                        self.good_proxies.remove(proxy)
                self.log(f"Çeviri hatası (deneme {attempt+1}/ {retries}): {str(e)}")
        
        return text  # Fallback

    def load_cache(self) -> Dict:
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.translation_cache, f, ensure_ascii=False, indent=2)

    def translate_file(self, file_path):
        try:
            file_name = os.path.basename(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            target_lang = self.languages[self.target_language.get()]
            output = []
            total_lines = len(lines)
            processed_lines = 0
            for line in lines:
                if line.strip().startswith(('old', '#')) or not line.strip():
                    output.append(line)
                else:
                    quote_pattern = re.compile(r"(?<!\\)((['\"])(.*?)(?<!\\)\2)")
                    translations = {}
                    for match in quote_pattern.finditer(line):
                        original = match.group(1)
                        text_to_translate = match.group(3)
                        processed_text, replacements = self.process_text(text_to_translate)
                        if processed_text in self.translation_cache:
                            translated_text = self.translation_cache[processed_text]
                        else:
                            proxy = next(self.proxy_cycle) if self.proxy_cycle else None
                            translator = GoogleTranslator(
                                source='auto', 
                                target=target_lang, 
                                proxies={'http': proxy, 'https': proxy} if proxy else None,
                                timeout=15
                            )
                            translated_text = translator.translate(processed_text)
                            self.translation_cache[processed_text] = translated_text
                        translated_text = self.restore_code(translated_text, replacements)
                        translations[original] = f'"{translated_text}"'
                    for orig, trans in translations.items():
                        line = line.replace(orig, trans)
                    output.append(line)
                processed_lines += 1
                self.progress_queue.put(('progress', (file_name, (processed_lines/total_lines)*100, 'İşleniyor')))
            output_path = file_path.replace('.rpy', '_translated.rpy')
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(output)
            self.progress_queue.put(('progress', (file_name, 100, 'Tamamlandı')))
            return f"Başarıyla çevrildi: {file_name}"
        except Exception as e:
            return f"Hata: {os.path.basename(file_path)} - {str(e)}"

    def translate_and_cache(self, processed: str, replacements: Dict, original: str):
        # Özel karakterleri koruma listesi
        special_characters = ["⬆", "⬇"]
        
        # Eğer metin özel karakterlerden birini içeriyorsa, çeviri yapmadan orijinal metni döndür
        if any(char in processed for char in special_characters):
            return (processed, original, original)
        
        translated = self.translate_text(processed)
        if translated is None:
            # Eğer çeviri None dönerse, orijinal metni kullan
            translated = original
        restored = self.restore_code(translated, replacements)
        return (processed, original, restored)

    def run_translation_tasks(self, rpy_files):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                futures = {executor.submit(self.translate_file, file): file for file in rpy_files}
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        self.progress_queue.put(('log', result))
                    except Exception as e:
                        self.progress_queue.put(('error', str(e)))
        finally:
            self.running = False

    def restore_code(self, translated_text, replacements):
        if translated_text is None:
            translated_text = ""
        for placeholder, code in replacements.items():
            translated_text = translated_text.replace(placeholder, code)
        # Çift tırnakları tek tırnaklara çevir
        translated_text = translated_text.replace('"', "")
        return translated_text

    def update_file_status(self, file_name, progress, status):
        for item in self.tree.get_children():
            if self.tree.item(item, 'values')[0] == file_name:
                self.tree.item(item, values=(file_name, status, f"%{int(progress)}"))
                break

    def start_translation(self):
        if not hasattr(self, 'folder_path') or not self.folder_path:
            self.log("Lütfen önce bir klasör seçin!")
            return
        self.running = True
        if self.good_proxies and not self.proxy_cycle:
            self.proxy_cycle = cycle(self.good_proxies)
        files = [os.path.join(root, f)
                 for root, _, files in os.walk(self.folder_path)
                 for f in files if f.endswith('.rpy')]
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_file, file): file for file in files}
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.progress_queue.put(('error', str(e)))
        self.running = False
        self.save_cache()
        # Çeviri tamamlandığında kullanıcıya bilgi veren uyarı kutusu
        self.root.after(0, lambda: messagebox.showinfo("Bilgi", "Çeviri Bitti"))

    # DÜZELTİLMİŞ: process_file metodu artık sınıf içinde tanımlandı.
    def process_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            tasks = []
            translated_data = []
            
            # 1. Aşama: Tüm metinleri topla ve önbelleği kontrol et
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as prep_executor:
                for line_num, line in enumerate(lines):
                    if line.strip().startswith(('old', '#')) or not line.strip():
                        translated_data.append((line_num, line))
                        continue

                    modified_line = line  # Satırdaki değişiklikleri burada toplayacağız.
                    futures = []
                    for match in re.finditer(r'(?<!\\)(["\'])(.*?)(?<!\\)\1', line):
                        original = match.group(0)
                        text_inside = match.group(2)
                        processed, replacements = self.process_text(text_inside)

                        if processed in self.translation_cache:
                            restored = self.restore_code(self.translation_cache[processed], replacements)
                            modified_line = modified_line.replace(original, f'"{restored}"')
                        else:
                            futures.append((original, processed, replacements))
                    
                    # Eğer çeviri yapılacak hiçbir alıntı bulunamadıysa veya tümü cache'de varsa,
                    # modified_line zaten düzenlenmiş durumda; aksi halde futures dolu ise tasks'e ekliyoruz.
                    if futures:
                        tasks.append((line_num, modified_line, futures))
                    else:
                        translated_data.append((line_num, modified_line))

                    
                    if futures:
                        tasks.append((line_num, line, futures))
            
            # 2. Aşama: Tüm çevirileri paralel yap
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as translate_executor:
                all_futures = []
                
                for line_num, original_line, futures in tasks:
                    line_futures = []
                    for original, processed, replacements in futures:
                        future = translate_executor.submit(
                            self.translate_and_cache, 
                            processed, 
                            replacements,
                            original
                        )
                        line_futures.append((future, original))
                    all_futures.append((line_num, original_line, line_futures))
                
                # 3. Aşama: Sonuçları işle
                for line_num, original_line, line_futures in all_futures:
                    modified_line = original_line
                    for future, original in line_futures:
                        try:
                            processed_key, orig, restored = future.result(timeout=20)
                            modified_line = modified_line.replace(original, f'"{restored}"')
                            self.translation_cache[processed_key] = restored
                        except Exception as e:
                            self.log(f"Hata: {str(e)} - Orijinal metin kullanılıyor")
                    
                    translated_data.append((line_num, modified_line))
                    self.progress_queue.put(('progress', (
                        os.path.basename(file_path),
                        ((line_num+1) / total_lines) * 100,
                        'İşleniyor'
                    )))
            
            # 4. Aşama: Sıralı çıktıyı oluştur ve ortak girintiyi kaldır
            translated_data.sort(key=lambda x: x[0])
            output_content = ''.join([line for _, line in translated_data])
            output_content = textwrap.dedent(output_content)  # Ortak girinti kaldırılıyor.
            output_content = output_content.lstrip()           # Dosyanın en başındaki gereksiz boşluklar kaldırılıyor.

            output_path = file_path.replace('.rpy', '_translated.rpy')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            
            self.progress_queue.put(('progress', (os.path.basename(file_path), 100, 'Tamamlandı')))
            return True
        
        except Exception as e:
            self.progress_queue.put(('error', f"Hata: {os.path.basename(file_path)} - {str(e)}"))
            return False

    def start_translation_thread(self):
        threading.Thread(target=self.start_translation, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = RenPyTranslator(root)
    root.mainloop()
