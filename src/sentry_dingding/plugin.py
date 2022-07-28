# coding: utf-8

import json

import requests
from sentry.plugins.bases.notify import NotificationPlugin

import sentry_dingding
from .forms import DingDingOptionsForm

DingTalk_API = "https://oapi.dingtalk.com/robot/send?access_token={token}"


class DingDingPlugin(NotificationPlugin):
    """
    Sentry plugin to send error counts to DingDing.
    """
    author = 'steven'
    author_url = 'https://github.com/stevenQiang/sentry-dingding-vibranium'
    version = sentry_dingding.VERSION
    description = 'Send error counts to DingDing.'
    resource_links = [
        ('Source', 'https://github.com/stevenQiang/sentry-dingding-vibranium'),
        ('Bug Tracker', 'https://github.com/stevenQiang/sentry-dingding-vibranium/issues'),
        ('README', 'https://github.com/stevenQiang/sentry-dingding-vibranium/blob/master/README.md'),
    ]

    slug = 'DingDingVibranium'
    title = 'DingDingVibranium'
    conf_key = slug
    conf_title = title
    project_conf_form = DingDingOptionsForm

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('access_token', project))

    def notify_users(self, group, event, triggering_rules, fail_silently=False, **kwargs):
        if self.should_notify(group, event):
            self.logger.info('send msg to dingtalk robot yes')
            self.post_process(group, event, triggering_rules, **kwargs)
        else:
            self.logger.info('send msg to dingtalk robot no')
            return

    def post_process(self, group, event, triggering_rules, **kwargs):
        """
        Process error.
        """
        if not self.is_configured(group.project):
            return

        if group.is_ignored():
            return

        access_token = self.get_option('access_token', group.project)
        send_url = DingTalk_API.format(token=access_token)
        title = u'【%s】【%s】的项目异常' % (event.get_tag("level"), event.project.slug)

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": u"#### {title} \n\n > {message} \n\n >告警规则：{triggering_rules} \n\n > 环境：{environment} \n\n [详细信息]({url})".format(
                    title=title,
                    message=event.title or event.message,
                    triggering_rules=triggering_rules,
                    #release=event.get_tag("release"),
                    environment=event.get_tag("environment"),
                    url=u"{}events/{}/".format(group.get_absolute_url(), event.event_id),
                )
            }
        }
        requests.post(
            url=send_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data).encode("utf-8")
        )
