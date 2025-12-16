import tkinter as tk
from tkinter import ttk
import smtplib
import dns.resolver
from email_validator import validate_email, EmailNotValidError


class EmailVerifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Verificador de E-mail")
        self.root.geometry("420x200")
        self.root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Digite o e-mail:", font=("Segoe UI", 11)).pack(anchor="w")

        self.email_entry = ttk.Entry(frame, width=45)
        self.email_entry.pack(pady=8)

        self.verify_button = ttk.Button(
            frame, text="Verificar", command=self.verify_email
        )
        self.verify_button.pack(pady=10)

        self.result_label = ttk.Label(frame, text="", font=("Segoe UI", 11, "bold"))
        self.result_label.pack(pady=10)

    def verify_email(self):
        email = self.email_entry.get().strip()
        self.result_label.config(text="", foreground="black")

        if not email:
            self.show_error("Informe um e-mail")
            return

        # 1️⃣ Validação de formato
        try:
            validation = validate_email(email)
            email = validation.email
            domain = email.split("@")[1]
        except EmailNotValidError:
            self.show_error("Email inválido")
            return

        # 2️⃣ Verificação de MX
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
            mx_host = str(mx_records[0].exchange)
        except Exception:
            self.show_error("Domínio não recebe e-mails")
            return

        # 3️⃣ Verificação SMTP (best effort)
        if self.smtp_check(mx_host, email):
            self.show_success("OK ✔ Email existe")
        else:
            self.show_error("Email não existe")

    def smtp_check(self, mx_host, email):
        try:
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_host)
            server.helo("verificador.local")
            server.mail("verificador@local.com")
            code, _ = server.rcpt(email)
            server.quit()

            return code in (250, 251)
        except Exception:
            return False

    def show_success(self, message):
        self.result_label.config(text=message, foreground="green")

    def show_error(self, message):
        self.result_label.config(text=message, foreground="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = EmailVerifierApp(root)
    root.mainloop()
