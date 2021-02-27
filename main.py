# -*- coding: utf-8 -*-
import os
import sys
import threading
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from smtplib import SMTP_SSL
import ssl
import smtplib
from PyQt5.QtWidgets import QFileDialog
from ui import Ui_MainWindow
from PyQt5 import QtWidgets
from utils import split_list

mail_server =  'smtp.gmail.com'	#  smtp.yandex.ru
mail_server_port = 587  #587 # 465

class MailSender(QtWidgets.QMainWindow):
    def __init__(self):
        super(MailSender, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_UI()

    def init_UI(self):
        self.ui.file_1_btn.clicked.connect(self.load_first_file_path)
        self.ui.file_2_btn.clicked.connect(self.load_second_file_path)
        self.ui.file_3_btn.clicked.connect(self.load_third_file_path)
        self.ui.file_4_btn.clicked.connect(self.load_forth_file_path)
        self.ui.start_work.clicked.connect(self.start_work)
        self.ui.start_work.clicked.connect(lambda: self.start_work(stop=True))

    def load_sender_list(self):
        sender = self.ui.send_from.toPlainText().split('\n')
        return sender

    def load_receiver_list(self):
        receiver = self.ui.send_to.toPlainText().replace(' ', '').split('\n')
        return receiver

    def load_first_file_path(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open file')
        self.ui.file_1.setText(file_name)

    def load_second_file_path(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open file')
        self.ui.file_2.setText(file_name)

    def load_third_file_path(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open file')
        self.ui.file_3.setText(file_name)

    def load_forth_file_path(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open file')
        self.ui.file_4.setText(file_name)

    def get_file_names(self):
        files = []
        if self.ui.file_1.text() == '':
            pass
        else:
            files.append(self.ui.file_1.text())

        if self.ui.file_2.text() == '':
            pass
        else:
            files.append(self.ui.file_2.text())

        if self.ui.file_3.text() == '':
            pass
        else:
            files.append(self.ui.file_3.text())

        if self.ui.file_4.text() == '':
            pass
        else:
            files.append(self.ui.file_4.text())

        for i in files:
            if '.' not in i:
                self.write_logs('Похоже где-то не указано разрешение файла..', 'info')
        return files

    def send_email(self, addr_from, addr_to, subject, text, password, attachment_files):
        #s = SMTP_SSL(mail_server, mail_server_port)
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.set_debuglevel(False)

        s.ehlo()
        #s.starttls()
        s.login(addr_from, password)

        message = MIMEMultipart()
        message['From'] = addr_from
        message['To'] = addr_to
        #subject = 'Проверка МТС-отчётов к сведению сотрудников'
        message['Subject'] = subject
        messageText = MIMEText(text, 'plain', 'utf-8')
        message.attach(messageText)

        if len(attachment_files) > 0:
            for file in attachment_files:
                try:
                    with open(file, "rb") as fh:
                        data = fh.read()
                    attachment = MIMEBase('application', "octet-stream")
                    attachment.set_payload(data)
                    encoders.encode_base64(attachment)
                    attachment.add_header('Content-Disposition',
                                          "attachment; filename= %s" % os.path.basename(file))
                    message.attach(attachment)
                except IOError:
                    print("Error opening attachment file %s" % file)

        s.sendmail(addr_from, addr_to, message.as_string())
        s.quit()
        #  отобразим информацию о кол-ве спаршенных товарах
        total_send = self.ui.total_mail_send.text()
        total_send = int(total_send)
        total_send += 1
        self.ui.total_mail_send.setText(str(total_send))
        #self.ui.logs.appendPlainText(f"Отправили с: {addr_from} на: {addr_to}")

    def stop(self):
        return True

    def main(self, stop):
        """ Собираем данные с полей """
        senders = self.load_sender_list()  # загружаем список аккаунтов откуда будем отправлять письма
        receiver = self.load_receiver_list() #  загружаем список почт куда слать
        data_list = split_list(receiver, len(senders), senders)  # список со вложенными емайлами
        attachment_files = self.get_file_names()  # читаем файлы вложения
        subject = self.ui.subject.text()  # тема сообщений
        email_text = self.ui.email_text.toPlainText()  # текст сообщений
        password = self.ui.default_password.text()  #  стандартный пароль для почт отправителей
        #self.ui.work_status.setText("<font color='green' style='font-weight:bold;'>Отправляем письма</font>")
        for email, items in data_list.items():
            #self.ui.logs.appendPlainText(f"Отправляем с: {email}")
            for item in items:
                self.ui.logs.appendPlainText(f"Отправили на: {item}")
                self.send_email(email, item, subject, email_text, password, attachment_files)

    def start_work(self, stop=False):
        global stop_send
        if stop:
            stop_send = True
            self.ui.start_work.setEnabled(True)
            self.ui.start_work.show()
        else:
            self.ui.start_work.hide()
            self.ui.stop_work.show()
            stop_send = False
            parser_thread = threading.Thread(target=self.main, name='parse_thread', args=(lambda: stop_send,))
            parser_thread.daemon = True
            parser_thread.start()



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    application = MailSender()
    application.show()
    sys.exit(app.exec_())
