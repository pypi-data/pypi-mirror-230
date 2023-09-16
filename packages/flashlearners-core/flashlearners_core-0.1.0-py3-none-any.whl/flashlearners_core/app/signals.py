# from django.db.models.signals import post_delete, post_save
# from django.dispatch import receiver
#
# from flashlearners_core.app.models import Versioning, Subject, FlashCard, \
#     Topic, Option, Question, Novel, NovelChapter
#
#
# def update_versioning(attr):
#     try:
#         version = Versioning.objects.first()
#     except Versioning.DoesNotExist:
#         version = Versioning()
#     setattr(version, attr, getattr(version, attr) + 1)
#     version.save()
#
#
# @receiver(post_delete, sender=Subject)
# @receiver(post_save, sender=Subject)
# def subject_update_hook(sender, instance, **kwargs):
#     update_versioning('subject')
#
#
# @receiver(post_delete, sender=Topic)
# @receiver(post_save, sender=Topic)
# def topic_update_hook(sender, instance, **kwargs):
#     update_versioning('topic')
#
#
# @receiver(post_delete, sender=FlashCard)
# @receiver(post_save, sender=FlashCard)
# def flashcard_update_hook(sender, instance, **kwargs):
#     update_versioning('flashcard')
#
#
# @receiver(post_delete, sender=Question)
# @receiver(post_save, sender=Question)
# def question_update_hook(sender, instance, **kwargs):
#     update_versioning('question')
#
#
# @receiver(post_delete, sender=Option)
# @receiver(post_save, sender=Option)
# def option_update_hook(sender, instance, **kwargs):
#     update_versioning('option')
#
#
# @receiver(post_delete, sender=Novel)
# @receiver(post_save, sender=Novel)
# def novel_update_hook(sender, instance, **kwargs):
#     update_versioning('novel')
#
#
# @receiver(post_delete, sender=NovelChapter)
# @receiver(post_save, sender=NovelChapter)
# def novel_chapter_update_hook(sender, instance, **kwargs):
#     update_versioning('novel_chapter')
#
