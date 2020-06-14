from django.db import models
from django.contrib.auth.models import User
from article.models import ArticlePost
from ckeditor.fields import RichTextField
from mptt.models import MPTTModel, TreeForeignKey

#博文的评论
class Comment(MPTTModel):
    article = models.ForeignKey(
        ArticlePost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    body = RichTextField()
    created = models.DateTimeField(auto_now_add=True)

    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='children'
    )
    #记录二级评论回复给谁， str
    reply_to = models.ForeignKey(
        User,
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='replyers'
    )

    class MPTTMeta:
        oreder_insertion_by = ('created',)
    
    def __str__(self):
        return self.body[:20]