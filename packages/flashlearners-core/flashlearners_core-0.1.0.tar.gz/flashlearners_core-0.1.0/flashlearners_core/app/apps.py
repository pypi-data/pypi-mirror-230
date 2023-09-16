from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'flashlearners_core.app'

    # def ready(self):
    #     from .signals import (
    #         subject_update_hook, topic_update_hook,
    #         flashcard_update_hook, question_update_hook, option_update_hook,
    #         novel_update_hook, novel_chapter_update_hook
    #     ) # noqa
