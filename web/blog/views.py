from django.shortcuts import render,get_object_or_404,redirect
from . import models
from blog.models import Post,Comment,UserProfileInfo
from blog.forms import CommentForm,PostForm,userform
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView,DeleteView,UpdateView,CreateView,DetailView,ListView
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse

# Create your views here.


class AboutView(TemplateView):
    template_name = 'blog/about.html'


class PostListView(ListView):
    model = Post
    
    #def post_list(self,request):
     #   posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
      #  return render(request, 'blog/post_list.html', {'postss':posts})
    
    def get_queryset(request):
       return Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')


class PostDetailView(DetailView):
    model = Post
    redirect_field_name = 'blog/post_detail.html'




class CreatePostView(LoginRequiredMixin,CreateView):

    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post


class PostUpdateView(LoginRequiredMixin,UpdateView):
    
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostDeleateView(LoginRequiredMixin,DeleteView):

    model = Post
    success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin,ListView):
    login = '/login/'
    redirect_field_name = 'blog/post_list.html'
    model = Post

    #def get_queryset(self):
     #   return Post.objects.filter(published_date__isnull=True).order_by('created_date')
    def draft_list(self,request):
        drafts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
        return render(request, 'blog/post_draft_list.html', {'draft':drafts})


#############################################

@login_required
def post_publish(request,pk):

    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('post_detail',pk=pk)



@login_required
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post,pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail',pk=post.pk)
    else:
        form = CommentForm
    return render(request,'blog/comment_form.html',{'form':form})

@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect('post_detail',pk=comment.post.pk)


@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail',pk=post_pk)



@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('post_list'))



def register(request):

    registered = False

    if request.method == 'POST':

        user_form = userform(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            registered = True

        else:
            print(user_form.errors)

    else:
        user_form = userform()

    return render(request,'registration/register.html',{'user_form':user_form,'registered':registered})



def user_login(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')


        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('post_list'))

            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")

        else:
            print("someone tried to login and failed")
            print("Username: {} and Password: {}".format(username,password))
            return HttpResponse("invalid login details supplied")
    
    else:
        return render(request,'registration/login.html',{})

