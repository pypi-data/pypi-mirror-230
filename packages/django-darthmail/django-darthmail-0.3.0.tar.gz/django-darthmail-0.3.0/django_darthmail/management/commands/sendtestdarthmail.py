from django.utils import timezone

from herocentral.core.management.base import DevCommand
from django_darthmail.message import EmailMultiAlternatives


class Command(DevCommand):
    help = 'test darthmail'

    def handle(self, *args, **options):
        em = EmailMultiAlternatives(
            subject='darthmail test via HC %s' % timezone.now(),
            body='test email via HC %s' % timezone.now(),
            from_email='HeroCentral@regiohelden.de',
            to=['foo@regiohelden.de', 'bar@regiohelden.de'],
            cc=[],
            bcc=['baz@regiohelden.de'],
            reply_to=['noreply@regiohelden.de'],
            headers={'X-Test': 'true'},
            attachments=[],
            metadata={
                'test': 'true',
                'id': 42,
            },
        )
        em.send()
