from typing import Optional

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from onesignal_sdk.client import Client
from onesignal_sdk.error import OneSignalHTTPError

from core_models import settings, constants
from core_models.utils import log_exception, MailAttachment


class NotificationManager:
    client = Client(app_id=settings.ONE_SIGNAL_APP_ID,
                    rest_api_key=settings.ONE_SIGNAL_REST_API_KEY,
                    user_auth_key=settings.ONE_SIGNAL_USER_AUTH_KEY)

    def profile_application_notification(self, application, pwd=None):
        print(f"Sending Profile Request update mail to {application.email}")
        self.send_mail(
            subject='Liquify Profile Request',
            template_dir='request-update',
            to=[application.email],
            context_dict={"req": application, "pwd": pwd},
            request=None,
        )
        print(f"Profile Request update mail sent to {application.email}")

    @staticmethod
    def save_invoice_notification(invoice):
        from core_models.app.models import Notification
        notifications = []
        if invoice.status in [constants.NEW_INVOICE_STATUS]:
            notice_type = constants.NEW_INVOICE_NOTIF_TYPE
            notifications.append(
                Notification(
                    object_id=invoice.id,
                    notice_type=notice_type,
                    created_by=invoice.seller
                )
            )
        elif invoice.status in [constants.WITHDRAWN_INVOICE_STATUS]:
            notice_type = constants.INVOICE_WITHDRAWN_NOTIF_TYPE
            notifications.append(
                Notification(
                    object_id=invoice.id,
                    notice_type=notice_type,
                    created_by=invoice.buyer
                )
            )
            if invoice.financier:
                notifications.append(
                    Notification(
                        object_id=invoice.id,
                        notice_type=notice_type,
                        created_by=invoice.financier
                    )
                )
        elif invoice.status in [constants.COMPLETED_INVOICE_STATUS]:
            notice_type = constants.INVOICE_REPAID_NOTIF_TYPE
            notifications.append(Notification(
                object_id=invoice.id,
                notice_type=notice_type,
                created_by=invoice.financier
            ))
            notifications.append(Notification(
                object_id=invoice.id,
                notice_type=notice_type,
                created_by=invoice.seller
            ))
        elif invoice.status in [constants.FUNDED_INVOICE_STATUS]:
            notice_type = constants.INVOICE_FUNDED_NOTIF_TYPE
            notifications.append(Notification(
                object_id=invoice.id,
                notice_type=notice_type,
                created_by=invoice.buyer
            ))
            notifications.append(Notification(
                object_id=invoice.id,
                notice_type=notice_type,
                created_by=invoice.seller
            ))
        elif invoice.status in [constants.VALIDATED_INVOICE_STATUS,
                                constants.AWAITING_PAYMENT_INVOICE_STATUS,
                                constants.AMEND_INVOICE_STATUS,
                                constants.OVERDUE_INVOICE_STATUS,
                                constants.REJECTED_INVOICE_STATUS]:
            dct = {
                constants.VALIDATED_INVOICE_STATUS: constants.INVOICE_VALIDATED_NOTIF_TYPE,
                constants.AWAITING_PAYMENT_INVOICE_STATUS: constants.INVOICE_AWAITING_PAYMENT_NOTIF_TYPE,
                constants.AMEND_INVOICE_STATUS: constants.AMEND_INVOICE_NOTIF_TYPE,
                constants.OVERDUE_INVOICE_STATUS: constants.INVOICE_OVERDUE_NOTIF_TYPE,
                constants.REJECTED_INVOICE_STATUS: constants.INVOICE_REJECTED_NOTIF_TYPE,
            }
            notice_type = dct[invoice.status]
            notifications.append(Notification(
                object_id=invoice.id,
                notice_type=notice_type,
                created_by=invoice.seller
            ))
        Notification.objects.bulk_create(notifications, ignore_conflicts=True)

    def send_mail(
            self, subject='', template_dir='', to=None,
            bcc=None, from_email=None, context_dict=None,
            file: Optional[MailAttachment] = None,
            request=None
    ):
        body_html = render_to_string(f'{template_dir}/mail.html', context_dict or {}, request=request)
        body_txt = render_to_string(f'{template_dir}/mail.txt', context_dict or {}, request=request)

        msg = EmailMultiAlternatives(
            subject=subject, body=body_txt, to=to or [],
            bcc=bcc or [], from_email=from_email
        )
        msg.attach_alternative(body_html, "text/html")
        if file is not None:
            msg.attach(
                filename=file.name,
                content=file.content,
                mimetype=file.mime
            )
        sent = msg.send(fail_silently=True)
        print(f"Mail sent: {sent}")
        return sent

    def send_push(self, notification):
        """
        For sending push notification to all user devices
        by passing either uid or user object
        :param notification:
        :return:
        """
        try:
            include_player_ids = notification.created_by.notification_tokens
            if bool(include_player_ids):
                notification_body = {
                    'contents': {'en': notification.text},
                    'data': {
                        "id": notification.id,
                        "object_id": notification.object_id,
                        "notice_type": notification.notice_type,
                        "seen": notification.seen,
                    },
                    'include_player_ids': include_player_ids
                }

                # Make a request to OneSignal and parse response
                response = self.client.send_notification(notification_body)
                print("---------PushNotificationManager-------------")
                print(response.body)  # JSON parsed response
                print("---------/PushNotificationManager/-------------")

        except OneSignalHTTPError as e:  # An exception is raised if
            # response.status_code != 2xx
            log_exception("PushNotificationManager", e)
        except Exception as e:
            log_exception("PushNotificationManager", e)
