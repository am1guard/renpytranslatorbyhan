import ttkbootstrap as ttk
import os
os.environ["LC_ALL"] = "C"
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
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

        # 1- Dil Seçimi (Çeviri için)
        self.target_language = tk.StringVar(value='İngilizce')
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

        # 2- Arayüz Dili Seçimi (GUI metinlerinin yerelleştirilmesi)
        self.interface_language = tk.StringVar(value="English")
        self.interface_language_codes = {
            "Turkish": "tr",
            "English": "en",
            "German": "de",
            "French": "fr",
            "Spanish": "es",
            "Italiano": "it",
            "Russian": "ru"
        }
        self.interface_texts = {
            "tr": {
                "target_label": "Hedef Dil:",
                "proxy_list_label": "Proxy Listesi:",
                "load_proxy_button": "Yükle",
                "active_proxy_label": "Aktif Proxy: Yok",
                "folder_button": "Klasör Seç",
                "folder_label": "Seçilen Klasör: Yok",
                "start_translation_button": "ÇEVİRİYİ BAŞLAT",
                "tree_column_file": "Dosya Adı",
                "tree_column_status": "Durum",
                "tree_column_progress": "İlerleme",
                "made_by": "Made by HAN",
                "interface_lang_label": "Arayüz Dili:"
            },
            "en": {
                "target_label": "Target Language:",
                "proxy_list_label": "Proxy List:",
                "load_proxy_button": "Load",
                "active_proxy_label": "Active Proxy: None",
                "folder_button": "Select Folder",
                "folder_label": "Selected Folder: None",
                "start_translation_button": "START TRANSLATION",
                "tree_column_file": "File Name",
                "tree_column_status": "Status",
                "tree_column_progress": "Progress",
                "made_by": "Made by HAN",
                "interface_lang_label": "Interface Language:"
            },
            "de": {
                "target_label": "Zielsprache:",
                "proxy_list_label": "Proxy-Liste:",
                "load_proxy_button": "Laden",
                "active_proxy_label": "Aktiver Proxy: Keiner",
                "folder_button": "Ordner auswählen",
                "folder_label": "Ausgewählter Ordner: Keiner",
                "start_translation_button": "ÜBERSETZUNG STARTEN",
                "tree_column_file": "Dateiname",
                "tree_column_status": "Status",
                "tree_column_progress": "Fortschritt",
                "made_by": "Gemacht von HAN",
                "interface_lang_label": "Oberflächensprache:"
            },
            "fr": {
                "target_label": "Langue cible:",
                "proxy_list_label": "Liste de Proxy:",
                "load_proxy_button": "Charger",
                "active_proxy_label": "Proxy actif: Aucun",
                "folder_button": "Sélectionner le dossier",
                "folder_label": "Dossier sélectionné: Aucun",
                "start_translation_button": "DÉMARRER LA TRADUCTION",
                "tree_column_file": "Nom de fichier",
                "tree_column_status": "Statut",
                "tree_column_progress": "Progression",
                "made_by": "Créé par HAN",
                "interface_lang_label": "Langue de l'interface:"
            },
            "es": {
                "target_label": "Idioma objetivo:",
                "proxy_list_label": "Lista de Proxy:",
                "load_proxy_button": "Cargar",
                "active_proxy_label": "Proxy activo: Ninguno",
                "folder_button": "Seleccionar carpeta",
                "folder_label": "Carpeta seleccionada: Ninguna",
                "start_translation_button": "INICIAR TRADUCCIÓN",
                "tree_column_file": "Nombre de archivo",
                "tree_column_status": "Estado",
                "tree_column_progress": "Progreso",
                "made_by": "Hecho por HAN",
                "interface_lang_label": "Idioma de la interfaz:"
            },
            "it": {
                "target_label": "Lingua di destinazione:",
                "proxy_list_label": "Elenco Proxy:",
                "load_proxy_button": "Carica",
                "active_proxy_label": "Proxy attivo: Nessuno",
                "folder_button": "Seleziona cartella",
                "folder_label": "Cartella selezionata: Nessuna",
                "start_translation_button": "AVVIA TRADUZIONE",
                "tree_column_file": "Nome file",
                "tree_column_status": "Stato",
                "tree_column_progress": "Progresso",
                "made_by": "Fatto da HAN",
                "interface_lang_label": "Lingua interfaccia:"
            },
            "ru": {
                "target_label": "Целевой язык:",
                "proxy_list_label": "Список Proxy:",
                "load_proxy_button": "Загрузить",
                "active_proxy_label": "Активный Proxy: Нет",
                "folder_button": "Выбрать папку",
                "folder_label": "Выбранная папка: Нет",
                "start_translation_button": "НАЧАТЬ ПЕРЕВОД",
                "tree_column_file": "Имя файла",
                "tree_column_status": "Статус",
                "tree_column_progress": "Прогресс",
                "made_by": "Сделано HAN",
                "interface_lang_label": "Язык интерфейса:"
            }
        }

        self.cache_file = 'translation_cache.json'
        self.translation_cache = self.load_cache()

        self.proxy_list = []
        self.good_proxies = []
        self.bad_proxies = []
        self.proxy_cycle = None
        self.max_workers = os.cpu_count() * 8

        self.setup_ui()
        self.setup_styles()
        self.root.after(50, self.update_progress)
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

        # Arayüz dili seçimi
        interface_frame = ttk.Frame(control_frame)
        interface_frame.pack(side='left', padx=5)
        self.interface_lang_label = ttk.Label(
            interface_frame, 
            text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["interface_lang_label"]
        )
        self.interface_lang_label.pack(side="left")
        self.interface_lang_combo = ttk.Combobox(
            interface_frame,
            textvariable=self.interface_language,
            values=list(self.interface_language_codes.keys()),
            state="readonly",
            width=15
        )
        self.interface_lang_combo.pack(side="left", padx=5)
        self.interface_lang_combo.bind("<<ComboboxSelected>>", self.update_interface_texts)

        # Çeviri hedef dili seçimi
        lang_frame = ttk.Frame(control_frame)
        lang_frame.pack(side='left', padx=5)
        self.target_label = ttk.Label(
            lang_frame, 
            text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["target_label"]
        )
        self.target_label.pack(side='left')
        self.lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.target_language,
            values=list(self.languages.keys()),
            state='readonly',
            width=15
        )
        self.lang_combo.pack(side='left', padx=5)

        # Proxy bölümü
        proxy_frame = ttk.Frame(control_frame)
        proxy_frame.pack(side='left', padx=5)
        self.proxy_list_label = ttk.Label(
            proxy_frame, 
            text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["proxy_list_label"]
        )
        self.proxy_list_label.pack(side='left')
        self.proxy_text = scrolledtext.ScrolledText(proxy_frame, height=3, width=30)
        self.proxy_text.pack(side='left', padx=5)
        self.load_proxy_button = ttk.Button(
            proxy_frame, 
            text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["load_proxy_button"],
            command=self.load_proxies
        )
        self.load_proxy_button.pack(side='left', padx=5)
        self.active_proxy_label = ttk.Label(
            proxy_frame, 
            text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["active_proxy_label"]
        )
        self.active_proxy_label.pack(side='left', padx=5)

        # Klasör seçimi
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(side='left', padx=5)
        self.folder_button = ttk.Button(
            file_frame, 
            text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["folder_button"],
            command=self.select_folder
        )
        self.folder_button.pack()
        self.folder_label = ttk.Label(
            file_frame, 
            text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["folder_label"]
        )
        self.folder_label.pack()

        # Dosya listesi (Treeview)
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True, pady=5)
        self.tree = ttk.Treeview(tree_frame, columns=('Dosya', 'Durum', 'İlerleme'), show='headings')
        self.tree.heading('Dosya', text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["tree_column_file"])
        self.tree.heading('Durum', text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["tree_column_status"])
        self.tree.heading('İlerleme', text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["tree_column_progress"])
        self.tree.column('Dosya', width=400)
        self.tree.column('Durum', width=150)
        self.tree.column('İlerleme', width=100)
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        tree_scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        # Konsol alanı
        self.console = scrolledtext.ScrolledText(main_frame, height=10, bg='#000000', fg='#00FFFF')
        self.console.pack(fill='both', expand=True, pady=5)

        # Çeviriyi başlat butonu
        self.start_translation_button = ttk.Button(
            main_frame, 
            text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["start_translation_button"],
            command=self.start_translation_thread
        )
        self.start_translation_button.pack(pady=10)
        self.made_by_label = ttk.Label(
            main_frame, 
            text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["made_by"]
        )
        self.made_by_label.pack(side="right", padx=(10, 0))

    def update_interface_texts(self, event=None):
        lang_code = self.interface_language_codes[self.interface_language.get()]
        texts = self.interface_texts[lang_code]
        self.interface_lang_label.config(text=texts["interface_lang_label"])
        self.target_label.config(text=texts["target_label"])
        self.proxy_list_label.config(text=texts["proxy_list_label"])
        self.load_proxy_button.config(text=texts["load_proxy_button"])
        self.active_proxy_label.config(text=texts["active_proxy_label"])
        self.folder_button.config(text=texts["folder_button"])
        self.folder_label.config(text=texts["folder_label"])
        self.start_translation_button.config(text=texts["start_translation_button"])
        self.tree.heading('Dosya', text=texts["tree_column_file"])
        self.tree.heading('Durum', text=texts["tree_column_status"])
        self.tree.heading('İlerleme', text=texts["tree_column_progress"])
        self.made_by_label.config(text=texts["made_by"])

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('cyborg')
        self.root.config(bg="#000000")
        style.configure('TButton', foreground='#00FFFF', background='#000000', font=('Helvetica', 10, 'bold'))
        style.map('TButton', background=[('active', '#1a1a1a')])
        style.configure('TLabel', background='#000000', foreground='#00FFFF', font=('Helvetica', 10))
        style.configure('Treeview', background='#000000', fieldbackground='#000000', foreground='#00FFFF', font=('Helvetica', 10))

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
        self.folder_label.config(text=self.interface_texts[self.interface_language_codes[self.interface_language.get()]]["folder_label"].replace("Yok", self.folder_path if self.folder_path else "Yok"))
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
        return text

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
            translated_folder = os.path.join(self.folder_path, "translated")
            os.makedirs(translated_folder, exist_ok=True)
            output_path = os.path.join(translated_folder, file_name)
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(output)
            self.progress_queue.put(('progress', (file_name, 100, 'Tamamlandı')))
            return f"Başarıyla çevrildi: {file_name}"
        except Exception as e:
            return f"Hata: {os.path.basename(file_path)} - {str(e)}"

    def translate_and_cache(self, processed: str, replacements: Dict, original: str):
        special_characters = ["⬆", "⬇"]
        if any(char in processed for char in special_characters):
            return (processed, original, original)
        translated = self.translate_text(processed)
        if translated is None:
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
        self.root.after(0, lambda: messagebox.showinfo("Bilgi", "Çeviri Bitti"))

    def process_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            total_lines = len(lines)
            tasks = []
            translated_data = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as prep_executor:
                for line_num, line in enumerate(lines):
                    if line.strip().startswith(('old', '#')) or not line.strip():
                        translated_data.append((line_num, line))
                        continue
                    modified_line = line
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
                    if futures:
                        tasks.append((line_num, modified_line, futures))
                    else:
                        translated_data.append((line_num, modified_line))
                    if futures:
                        tasks.append((line_num, line, futures))
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
            translated_data.sort(key=lambda x: x[0])
            output_content = ''.join([line for _, line in translated_data])
            output_content = textwrap.dedent(output_content)
            output_content = output_content.lstrip()
            translated_folder = os.path.join(self.folder_path, "translated")
            os.makedirs(translated_folder, exist_ok=True)
            output_path = os.path.join(translated_folder, os.path.basename(file_path))
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
    root = ttk.Window(themename="cyborg")
    app = RenPyTranslator(root)
    root.mainloop()
