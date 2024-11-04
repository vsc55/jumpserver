from itertools import islice

from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from common.const import Trigger
from orgs.mixins.models import JMSOrgBaseModel
from .base import AccountBaseAutomation
from ...const import AutomationTypes

__all__ = ['AccountCheckAutomation', 'AccountRisk', 'RiskChoice']


class AccountCheckAutomation(AccountBaseAutomation):

    def get_register_task(self):
        from ...tasks import check_accounts_task
        name = "check_accounts_task_period_{}".format(str(self.id)[:8])
        task = check_accounts_task.name
        args = (str(self.id), Trigger.timing)
        kwargs = {}
        return name, task, args, kwargs

    def to_attr_json(self):
        attr_json = super().to_attr_json()
        attr_json.update({
        })
        return attr_json

    def save(self, *args, **kwargs):
        self.type = AutomationTypes.check_account
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Gather account automation')


class RiskChoice(TextChoices):
    zombie = 'zombie', _('Long time no login')  # 好久没登录的账号
    ghost = 'ghost', _('Not managed')  # 未被纳管的账号
    long_time_password = 'long_time_password', _('Long time no change')
    weak_password = 'weak_password', _('Weak password')
    password_error = 'password_error', _('Password error')
    password_expired = 'password_expired', _('Password expired')
    group_changed = 'group_changed', _('Group change')
    sudo_changed = 'sudo_changed', _('Sudo changed')
    account_deleted = 'account_deleted', _('Account delete')
    no_admin_account = 'no_admin_account', _('No admin account')  # 为什么不叫 No privileged 呢，是因为有 privileged，但是不可用
    other = 'others', _('Others')


class AccountRisk(JMSOrgBaseModel):
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='risks', verbose_name=_('Asset'))
    username = models.CharField(max_length=32, verbose_name=_('Username'))
    risk = models.CharField(max_length=128, verbose_name=_('Risk'), choices=RiskChoice.choices)
    confirmed = models.BooleanField(default=False, verbose_name=_('Confirmed'))

    class Meta:
        verbose_name = _('Account risk')

    def __str__(self):
        return f"{self.username}@{self.asset} - {self.risk}"

    @classmethod
    def gen_fake_data(cls, count=1000, batch_size=50):
        from assets.models import Asset
        from accounts.models import Account

        assets = Asset.objects.all()
        accounts = Account.objects.all()

        counter = iter(range(count))
        while True:
            batch = list(islice(counter, batch_size))
            if not batch:
                break

            to_create = []
            for i in batch:
                asset = assets[i % len(assets)]
                account = accounts[i % len(accounts)]
                risk = RiskChoice.choices[i % len(RiskChoice.choices)][0]
                to_create.append(cls(asset=asset, username=account.username, risk=risk))

            cls.objects.bulk_create(to_create)


