from django.db import models
from django.contrib.auth.models import User#django内置的简单账户系统
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image

class ArticleColumn(models.Model):
    '''
    文章栏目的 Model
    '''
    title = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

class ArticlePost(models.Model):
    '''
    文章
    '''
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    #文章标签
    tags = TaggableManager(blank=True)
    #文章栏目的‘一对多’外键关联
    column = models.ForeignKey(
        ArticleColumn,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='article'
    )
    #文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d', blank=True)
    #浏览量
    total_views = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)
    
    

    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return self.title
    
    #获取文章地址
    def get_absolute_url(self):
        return reverse("article:article_detail", args=[self.id])
    #保存时处理图片
    def save(self, *args, **kwargs):
        article = super(ArticlePost, self).save(*args, **kwargs) # Call the real save() method
       
        #固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 400
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x,new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        
        return article

    #供测试的错误方法    
    def was_created_recently(self):
        # 若文章是"最近"发表的，则返回 True
        diff = timezone.now() - self.created
        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            return True
        else:
            return False