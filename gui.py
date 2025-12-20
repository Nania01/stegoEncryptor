import customtkinter as ctk
from tkinter import filedialog
import engine

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class StegoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("StegoPic")
        self.geometry("600x600")
        self.resizable(False, False)

        self.current_img_path_enc = ""
        self.current_img_path_dec = ""
        self.placeholder_text = "Введите текст, который хотите зашифровать..."

        self.tabview = ctk.CTkTabview(self, width=560, height=560)
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

        self.entry_text = ctk.CTkTextbox(frame, width=450, height=150, border_width=2, corner_radius=10)
        self.entry_text.pack(pady=20)

        self.entry_text.insert("0.0", self.placeholder_text)
        self.entry_text.configure(text_color="gray", font=("Arial", 14, "italic"))

        self.entry_text.bind("<FocusIn>", self.on_text_focus_in)
        self.entry_text.bind("<FocusOut>", self.on_text_focus_out)

        self.btn_run_enc = ctk.CTkButton(frame, text="ЗАШИФРОВАТЬ", fg_color="#228B22", hover_color="#3CB371",
                                         width=200, height=40, font=("Arial", 14, "bold"), command=self.run_encrypt)
        self.btn_run_enc.pack(pady=20)

        self.result_frame = ctk.CTkFrame(frame, fg_color="transparent")

        self.lbl_key_info = ctk.CTkLabel(self.result_frame, text="✅ Готово! Ваш ключ:", font=("Arial", 14, "bold"),
                                         text_color="#228B22")
        self.entry_key_result = ctk.CTkEntry(self.result_frame, width=300, justify="center", font=("Consolas", 14))

    def setup_decrypt_tab(self):
        frame = self.tab_decrypt

        self.btn_select_img_dec = ctk.CTkButton(frame, text="Выбрать файл", command=self.select_image_dec, width=200)
        self.btn_select_img_dec.pack(pady=(20, 10))

        self.lbl_file_dec = ctk.CTkLabel(frame, text="Файл не выбран", text_color="gray", font=("Arial", 12))
        self.lbl_file_dec.pack(pady=5)

        self.entry_key_input = ctk.CTkEntry(frame, width=300, placeholder_text="Вставьте ключ сюда", justify="center")
        self.entry_key_input.pack(pady=20)

        self.btn_run_dec = ctk.CTkButton(frame, text="РАСШИФРОВАТЬ", fg_color="#B22222", hover_color="#DC143C",
                                         width=200, height=40, font=("Arial", 14, "bold"), command=self.run_decrypt)
        self.btn_run_dec.pack(pady=20)

        self.text_result = ctk.CTkTextbox(frame, width=450, height=150, corner_radius=10)
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

    def run_encrypt(self):
        if not self.current_img_path_enc:
            return

        text = self.entry_text.get("0.0", "end-1c")
        if text == self.placeholder_text or not text.strip():
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG file", "*.png")])

        if save_path:
            key = engine.save_encrypted_image(self.current_img_path_enc, text, save_path)

            self.result_frame.pack(pady=10, fill="x")
            self.lbl_key_info.pack(pady=(0, 5))
            self.entry_key_result.pack(pady=5)

            self.entry_key_result.delete(0, "end")
            if key:
                self.entry_key_result.insert(0, key)
            else:
                self.entry_key_result.insert(0, "Ошибка размера")

    def run_decrypt(self):
        if not self.current_img_path_dec:
            return

        key = self.entry_key_input.get()
        result_text = engine.get_decrypted_text(self.current_img_path_dec, key)

        self.text_result.delete("0.0", "end")
        self.text_result.insert("0.0", result_text)