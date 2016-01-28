#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config_import as ci
import log_control
import smtplib
from email.mime.text import MIMEText
import traceback


class MailSend:

    def __init__(self):
        try:
            self.smtp_host = ci.smtp_host
            self.smtp_port = ci.smtp_port
            self.local_host = ci.local_host
            self.auth_id = ci.smtpauth_id
            self.auth_pass = ci.smtpauth_pass
            self.from_addr = ci.from_addr
            self.to_addr = ci.to_addr
            self.mail_title = ci.mail_title
        except:
            err = "Read config failed.\n"
            log_control.logging.error(err + traceback.format_exc())
            raise

    def mail_send(self, mail_body):

        # SMTPのコネクション確立(SMTPAUTH有り)
        smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
        smtp.ehlo(self.local_host)
        smtp.login(self.auth_id, self.auth_pass)
        mail_body = MIMEText(mail_body)
        mail_body['Subject'] = self.mail_title

        try:
            smtp.sendmail(self.from_addr, self.to_addr, mail_body.as_string())
            smtp.quit()
            return
        except:
            # メール送信に失敗した場合にのみエラーメッセージを返す
            err_msg = "[ERROR] mal_send: メール送信失敗"
            smtp.quit()
            return err_msg
