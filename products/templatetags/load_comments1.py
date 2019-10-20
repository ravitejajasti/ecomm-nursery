# from django import template

# register = template.Library()

# from products.models import Comment

# @register.inclusion_tag('products/comments-loader.html')
# def load_comments(url):
#     qs = Comment.objects.filter(url=url)
#     return {'comments':qs}