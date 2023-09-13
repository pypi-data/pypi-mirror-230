import requests
import json
from importlib import import_module

from django.conf import settings
from django.utils import timezone

from zs_utils.exceptions import CustomException
from zs_utils.api.services import ApiRequestLogService
from zs_utils.email import default_html_templates


class EmailServiceException(CustomException):
    pass


class EmailService:
    """
    Статика: https://cloud.digitalocean.com/spaces/zonesmart-production?i=e47403&path=zonesmart_production%2Femail_static%2F
    Сервис для работы с email-уведомлениями (EmailSubscription)
    """

    @classmethod
    def get_html_template(cls, name: str) -> str:
        if getattr(settings, "EMAIL_TEMPLATE_MODULE", None):
            email_templates = import_module(name=settings.EMAIL_TEMPLATE_MODULE)
            if hasattr(email_templates, name):
                return getattr(email_templates, name)

        if not hasattr(default_html_templates, name):
            raise ValueError(f"HTML-шаблон '{name}' не найден.")

        return getattr(default_html_templates, name)

    @staticmethod
    def format_date(date: timezone.datetime) -> str:
        """
        Конвертация timezone.datetime в строку формата: '%a, %d %b %Y %H:%M:%S 0000'
        """
        return date.strftime("%a, %d %b %Y %H:%M:%S 0000")

    @classmethod
    def send_email(
        cls,
        sender: str,
        receivers: list,
        subject: str,
        text: str = None,
        files: dict = None,
        html: str = None,
        template: str = None,
        template_params: dict = None,
        delivery_time: timezone.datetime = None,
        tags: list = None,
        **kwargs,
    ) -> dict:
        """
        Отправка email-уведомления на пользовательские email адреса
        """

        data = {
            "from": sender,
            "to": receivers,
            "subject": subject,
            "text": text,
            "html": html,
            "template": template,
            "o:tag": tags,
        }
        if delivery_time:
            data["o:deliverytime"] = cls.format_date(delivery_time)
        if template_params:
            data["h:X-Mailgun-Variables"] = json.dumps(template_params)
        data = {key: value for key, value in data.items() if value}

        response = requests.post(
            url=f"{settings.MAILGUN_API_URL}/messages",
            auth=("api", settings.MAILGUN_API_KEY),
            data=data,
            files=files,
        )
        ApiRequestLogService.save_api_request_log_by_response(
            response=response,
            save_if_is_success=False,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_social_media_icon_urls(cls) -> dict:
        """
        Получение данных об иконках соц. сетей для формирования шаблона email-уведомления
        """
        file_names = {
            "facebook_icon_url": "facebook-icon.png",
            "instagram_icon_url": "instagram-icon.png",
            "linkedin_icon_url": "linkedin-icon.png",
            "youtube_icon_url": "youtube-icon.png",
            "twitter_icon_url": "twitter-icon.png",
            "tg_icon_url": "tg_icon.png",
        }
        return {key: f"{settings.EMAIL_STATIC_FOLDER_URL}{value}" for key, value in file_names.items()}

    @classmethod
    def send_email_using_standard_template(
        cls,
        sender: str,
        receivers: list,
        subject: str,
        title: str,
        body_content: str,
        cheers_content: str,
        email_icon_path: str = None,
        email_icon_url: str = None,
        files: dict = None,
        footer_extra_content: str = None,
        extra_template_params: dict = None,
        mailgun_template_name: str = "blank_template",
        **kwargs,
    ) -> dict:
        """
        Отправка email-уведомлений с использованием стандартного шаблона
        """
        if title:
            title_html = cls.get_html_template(name="title").format(title=title)
        else:
            title_html = ""

        if not email_icon_url:
            if email_icon_path:
                email_icon_url = f"{settings.EMAIL_STATIC_FOLDER_URL}{email_icon_path}"
            else:
                email_icon_url = f"{settings.EMAIL_STATIC_FOLDER_URL}icon_email.png"

        template_params = {
            "title": title_html,
            "body": body_content,
            "logo_url": f"{settings.EMAIL_STATIC_FOLDER_URL}logo-1.png",
            "email_icon_url": email_icon_url,
            "cheers_text": cheers_content,
        }

        if footer_extra_content:
            template_params["footer_text"] = footer_extra_content

        template_params.update(cls.get_social_media_icon_urls())

        if extra_template_params:
            template_params.update(extra_template_params)

        return cls.send_email(
            sender=sender,
            receivers=receivers,
            subject=subject,
            template=mailgun_template_name,
            template_params=template_params,
            files=files,
            **kwargs,
        )

    @classmethod
    def send_standard_team_email(
        cls,
        receivers: list,
        subject: str,
        title: str,
        body_content: str,
        email_icon_path: str = None,
        files: dict = None,
        footer_extra_content: str = None,
        extra_template_params: dict = None,
        **kwargs,
    ):
        """
        Отправка email-уведомлений с использованием командного шаблона (от лица команды Zonesmart)
        """
        return cls.send_email_using_standard_template(
            sender="Команда Zonesmart info@zonesmart.ru",
            receivers=receivers,
            subject=subject,
            title=title,
            body_content=body_content,
            email_icon_path=email_icon_path,
            cheers_content=cls.get_html_template(name="team_cheers"),
            files=files,
            footer_extra_content=footer_extra_content,
            extra_template_params=extra_template_params,
            **kwargs,
        )
