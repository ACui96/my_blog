from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import ArticlePostForms
from .models import ArticlePost,ArticleColumn
from django.contrib.auth.models import User
import markdown
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from comment.models import Comment
from comment.forms import CommentForm
from notifications.models import Notification
from django.views import View

def article_list(request):
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')

    #初始化数据集
    article_list = ArticlePost.objects.all()
    #用户搜索逻辑
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) | Q(body__icontains=search)
        )
    else:
        search = ''
    
    #栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)
    
    #标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    if order == 'total_views':
        article_list = article_list.order_by('-total_views')
    else:
        pass


    page_num = 3 #每页显示的文章数
    paginator = Paginator(article_list, page_num)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = {
        'articles': articles, 
        'order': order, 
        'search': search,
        'column': column,
        'tag': tag
        }

    return render(request, 'article/list.html', context)

def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    comments = Comment.objects.filter(article=id)
    #引入评论表单
    comment_form = CommentForm()
    #浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 将markdown语法渲染成html样式
    md = markdown.Markdown(
        extensions=[
        # 包含 缩写、表格等常用扩展
        'markdown.extensions.extra',
        # 语法高亮扩展
        'markdown.extensions.codehilite',
        #目录扩展
        'markdown.extensions.toc',
        ]
    )
    
    article.body = md.convert(article.body)
    context = { 
        'article': article, 
        'toc':md.toc, 
        'comments': comments,
        'comment_form': comment_form
        }
    return render(request, 'article/detail.html', context)
#写文章的视图
def article_create(request):
    if request.method == "POST":
        article_post_form = ArticlePostForms(request.POST, request.FILES)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            #保存tags的对多对关系
            article_post_form.save_m2m()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForms()
        columns = ArticleColumn.objects.all()
        context = { 'article_post_form': article_post_form,'columns': columns }
        return render(request, 'article/create.html', context)

#删除文章的视图
@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    #过滤非作者用户
    if request.user !=article.author:
        return HttpResponse('抱歉，你无权删除这篇文章！')
    article.delete()
    return redirect("article:article_list")

#安全删除文章
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        #过滤非作者用户
        if request.user !=article.author:
            return HttpResponse('抱歉，你无权删除这篇文章！')
        Notification.objects.filter(target_object_id=id).delete()
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求！")

#修改文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    '''
    更新文章的视图函数
    通过POST方法提交表单，更新title、body字段
    GET方法进入初试表单界面
    id： 文章的 id
    '''

    article = ArticlePost.objects.get(id=id)
    #过滤非作者用户
    if request.user !=article.author:
        return HttpResponse('抱歉，你无权修改这篇文章！')
    if request.method == "POST":
        article_post_form = ArticlePostForms(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column  = None
            
            if request.FILES.get('avatar'):
                article.avtar = request.FILES.get('avatar')
            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForms()
        columns = ArticleColumn.objects.all()
        context = { 
            'article': article, 
            'article_post_form': article_post_form, 
            'columns': columns,
            'tags':','.join([x for x in article.tags.names()]),
            }
        return render(request, 'article/update.html', context)

class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')