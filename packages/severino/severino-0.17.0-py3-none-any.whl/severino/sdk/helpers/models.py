import errno
import os
import re
import uuid

from severino.sdk import MailCarrier, MailCarrierTemplate


# Helper class to work with templates classes in code
class MailTemplate:
    _template_name: str
    _html_path: os.path
    _connection: uuid

    def __init__(self) -> None:
        self.mail_carrier = MailCarrier()
        self.mail_carrier_template = MailCarrierTemplate()

    @property
    def connection(self) -> uuid:
        return self._connection

    @connection.setter
    def connection(self, value: uuid):
        self._connection = value

    @property
    def html_path(self) -> os.path:
        return self._html_path

    @html_path.setter
    def html_path(self, value: os.path):
        if not os.path.exists(value):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), value)

        self._html_path = value

    @property
    def template_name(self) -> str:
        return self._template_name

    @template_name.setter
    def template_name(self, value: str):
        if not re.match(r"^[a-z_-]+$", value):
            raise Exception(f"'{value}' is not a valid name for template.")

        self._template_name = value

    def mail_migrate(self) -> None:
        """Update or Create email in Severino server if not exist"""
        self.mail_carrier_template.update(
            template_name=self.template_name,
            template_path=self.html_path,
        )

    def delete_remote(self) -> None:
        """Delete self template in Severino server"""
        self.mail_carrier_template.delete(template_name=self.template_name)

    def mail_preview(self, context_vars: dict = None) -> None:
        """Make preview email in your localhost
        Args:
            context_vars (dict, optional): dictionary with template variables
        """
        self.mail_carrier_template.test_template(
            template_path=self.html_path, context_vars=context_vars
        )

    def send_email(
        self,
        subject: str,
        to_email: list[str],
        bcc: list[str] = None,
        cc: list[str] = None,
        reply_to: list = None,
        context_vars: dict = None,
        files: list = [],
        tag: str = None,
    ):
        """Send email using this template.
        Args:
            subject (str, mandatory): The subject line of the email.
            to_email (list): A list of recipient addresses. Recipients are the audience of the message.
            bcc (list, optional): A list of addresses used in the “Bcc” header when sending the email. Recipients are those being discreetly or surreptitiously informed of the communication and cannot be seen by any of the other addressees. P.s: It is common practice to use the BCC: field when addressing a very long list of recipients, or a list of recipients that should not (necessarily) know each other, e.g. in mailing lists.
            cc (list, optional): A list of recipient addresses. Recipients are others whom the author wishes to publicly inform of the message (carbon copy)
            reply_to (list, optional): A list of recipient addresses used in the “Reply-To” header when sending the email.
            context_vars (dict, optional): An object containing key and values ​​that will be used by the template.
            files (list, optional): A list containing the files that will be sent together to the email. E.g: [{"name": "file.pdf", "file": "PCFkb2N0eXBlIGh0bWw+..."}]
            tag (str, optional): You can add a tag to find this email in the future.
        """
        print("test")
        return self.mail_carrier.send(
            from_connection=self._connection,
            template_name=self.template_name,
            to_email=to_email,
            bcc=bcc,
            cc=cc,
            reply_to=reply_to,
            subject=subject,
            context_vars=context_vars,
            files=files,
            tag=tag,
        )
