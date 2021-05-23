from django import forms

from .models import Comment, Post, Group


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'description', 'slug']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
        }
