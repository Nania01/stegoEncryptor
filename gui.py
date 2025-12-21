import customtkinter as ctk
from tkinter import filedialog
import engine

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class StegoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("StegoPic v5.0")
        self.geometry("600x650")
        self.resizable(False, False)

        self.current_img_path_enc = ""
        self.current_img_path_dec = ""
        self.placeholder_text = "Введите текст, который хотите зашифровать..."

        self.tabview = ctk.CTkTabview(self, width=560, height=600)
        self.tabview.pack(padx=20, pady=20)

        self.tab_encrypt = self.tabview.add("Зашифровать")
        self.tab_decrypt = self.tabview.add("Расшифровать")

        self.setup_encrypt_tab()
        self.setup_decrypt_tab()

    def setup_encrypt_tab(self):
        frame = self.tab_encrypt

        self.btn_select_img_enc = ctk.CTkButton(frame, text="Выбрать картинку", command=self.select_image_enc,
                                                width=200)
        self.btn_select_img_enc.pack(pady=(20, 10))

        self.lbl_file_enc = ctk.CTkLabel(frame, text="Файл не выбран", text_color="gray", font=("Arial", 12))
        self.lbl_file_enc.pack(pady=5)

        self.lbl_method_enc = ctk.CTkLabel(frame, text="Выберите метод шифрования:", font=("Arial", 12, "bold"))
        self.lbl_method_enc.pack(pady=(10, 0))

        self.combo_method_enc = ctk.CTkComboBox(frame,
            values=["LSB (Red)", "LSB (Green)", "LSB (Blue)", "LSB (Multi)", "EOF (Скрытие в конце)"],
            width=250, state="readonly")
        self.combo_method_enc.pack(pady=5)
        self.combo_method_enc.set("LSB (Multi)")

        self.lbl_pass_enc = ctk.CTkLabel(frame, text="Придумайте пароль (обязательно):", font=("Arial", 12, "bold"))
        self.lbl_pass_enc.pack(pady=(10, 0))
        self.entry_pass_enc = ctk.CTkEntry(frame, width=250, placeholder_text="Ваш секретный пароль", show="*")
        self.entry_pass_enc.pack(pady=5)

        self.entry_text = ctk.CTkTextbox(frame, width=450, height=100, border_width=2, corner_radius=10)
        self.entry_text.pack(pady=15)
        self.entry_text.insert("0.0", self.placeholder_text)
        self.entry_text.configure(text_color="gray", font=("Arial", 14, "italic"))
        self.entry_text.bind("<FocusIn>", self.on_text_focus_in)
        self.entry_text.bind("<FocusOut>", self.on_text_focus_out)

        self.btn_run_enc = ctk.CTkButton(frame, text="ЗАШИФРОВАТЬ", fg_color="#228B22", hover_color="#3CB371",
                                         width=200, height=40, font=("Arial", 14, "bold"), command=self.run_encrypt)
        self.btn_run_enc.pack(pady=10)

        self.result_frame = ctk.CTkFrame(frame, fg_color="transparent")

        self.lbl_key_info = ctk.CTkLabel(self.result_frame, text="✅ Готово! Ваш ключ:", font=("Arial", 14, "bold"),
                                         text_color="#228B22")

        self.key_container = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.entry_key_result = ctk.CTkEntry(self.key_container, width=230, justify="center", font=("Consolas", 13))
        self.entry_key_result.pack(side="left", padx=5)

        self.btn_copy = ctk.CTkButton(self.key_container, text="Копировать", width=80,
                                      command=self.copy_key_to_clipboard)
        self.btn_copy.pack(side="left")

    def setup_decrypt_tab(self):
        frame = self.tab_decrypt

        self.btn_select_img_dec = ctk.CTkButton(frame, text="Выбрать файл", command=self.select_image_dec, width=200)
        self.btn_select_img_dec.pack(pady=(20, 10))

        self.lbl_file_dec = ctk.CTkLabel(frame, text="Файл не выбран", text_color="gray", font=("Arial", 12))
        self.lbl_file_dec.pack(pady=5)

        self.lbl_key_dec = ctk.CTkLabel(frame, text="Вставьте полученный ключ:", font=("Arial", 12, "bold"))
        self.lbl_key_dec.pack(pady=(20, 0))

        self.key_input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.key_input_frame.pack(pady=10)
        self.entry_key_input = ctk.CTkEntry(self.key_input_frame, width=230, placeholder_text="Base64 ключ...", justify="center")
        self.entry_key_input.pack(side="left", padx=5)

        self.btn_paste = ctk.CTkButton(self.key_input_frame, text="Вставить", width=80,
                                       command=self.paste_key_from_clipboard)
        self.btn_paste.pack(side="left")

        self.lbl_pass_dec = ctk.CTkLabel(frame, text="Введите пароль:", font=("Arial", 12, "bold"))
        self.lbl_pass_dec.pack(pady=(10, 0))
        self.entry_pass_dec = ctk.CTkEntry(frame, width=250, placeholder_text="Пароль от этого файла", show="*")
        self.entry_pass_dec.pack(pady=5)

        self.btn_run_dec = ctk.CTkButton(frame, text="РАСШИФРОВАТЬ", fg_color="#B22222", hover_color="#DC143C",
                                         width=200, height=40, font=("Arial", 14, "bold"), command=self.run_decrypt)
        self.btn_run_dec.pack(pady=20)

        self.text_result = ctk.CTkTextbox(frame, width=450, height=120, corner_radius=10)
        self.text_result.pack(pady=10)

    def on_text_focus_in(self, event):
        if self.entry_text.get("0.0", "end-1c") == self.placeholder_text:
            self.entry_text.delete("0.0", "end")
            self.entry_text.configure(text_color=("black", "white"), font=("Arial", 14))

    def on_text_focus_out(self, event):
        if self.entry_text.get("0.0", "end-1c").strip() == "":
            self.entry_text.insert("0.0", self.placeholder_text)
            self.entry_text.configure(text_color="gray", font=("Arial", 14, "italic"))

    def select_image_enc(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.bmp")])
        if path:
            self.lbl_file_enc.configure(text=path.split("/")[-1])
            self.current_img_path_enc = path

    def select_image_dec(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.bmp")])
        if path:
            self.lbl_file_dec.configure(text=path.split("/")[-1])
            self.current_img_path_dec = path

    def copy_key_to_clipboard(self):
        key = self.entry_key_result.get()
        if key:
            self.clipboard_clear()
            self.clipboard_append(key)
            self.update()
            self.btn_copy.configure(text="Скопировано!")
            self.after(2000, lambda: self.btn_copy.configure(text="Копировать"))

    def paste_key_from_clipboard(self):
        try:
            text = self.clipboard_get()
            self.entry_key_input.delete(0, "end")
            self.entry_key_input.insert(0, text)
        except:
            pass

    def run_encrypt(self):
        if not self.current_img_path_enc: return
        
        text = self.entry_text.get("0.0", "end-1c")
        password = self.entry_pass_enc.get()
        
        if text == self.placeholder_text or not text.strip(): return
        if not password: 
            self.entry_pass_enc.configure(border_color="red")
            return
        else:
            self.entry_pass_enc.configure(border_color="gray")

        method = self.combo_method_enc.get()
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png")])

        if save_path:
            if "EOF" in method:
                length = engine._encrypt_eof(self.current_img_path_enc, text, save_path, password)
                key = engine._generate_smart_key("eof", length)
            else:
                key = engine.encrypt(self.current_img_path_enc, text, password, save_path, method)

            self.result_frame.pack(pady=10, fill="x")
            self.lbl_key_info.pack(pady=(0, 5))
            self.key_container.pack(pady=5)
            self.entry_key_result.delete(0, "end")

            if key == "TooLarge":
                self.entry_key_result.insert(0, "Текст слишком большой!")
            elif key:
                self.entry_key_result.insert(0, key)
            else:
                self.entry_key_result.insert(0, "Ошибка")

    def run_decrypt(self):
        if not self.current_img_path_dec: return

        key = self.entry_key_input.get()
        password = self.entry_pass_dec.get()
        
        if not key or not password: return

        method_code, length = engine._parse_smart_key(key)
        
        if method_code == "eof":
            result_text = engine._decrypt_eof(self.current_img_path_dec, length, password)
        else:
            result_text = engine.decrypt(self.current_img_path_dec, key, password)

        self.text_result.delete("0.0", "end")
        self.text_result.insert("0.0", result_text)