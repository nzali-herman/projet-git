from django.shortcuts import redirect, render
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic
from .models import User , Book, Chat, DeleteRequest, Feedback 
from django.contrib import messages
from django.db.models import Sum
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, ListView
from .forms import ChatForm, BookForm , UserForm 
from . import models
import operator
import itertools
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, logout
from django.contrib import auth, messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
# Create your views here.


def home(request):
   return render(request, 'Bookstor/addandshow.html')

#page service
def services(request):
    return render(request ,'Bookstor/service.html')
# page a propos
def  apropos(request):
    return render(request ,'Bookstor/apropos.html')
#shared views
def login_form(request):
    return render(request, 'Bookstor/login.html')

def logoutView(request):
    logout(request)
    return redirect('homeac')
    
def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            if user.is_admin or user.is_superuser:
                return redirect('dashboard')
            elif user.is_consultant:
                return redirect('librarian')

            else:
                return redirect('publisher')
            
        else:
            messages.info(request, "Invalid username or password")
            return redirect('home')
        




def register_form(request):
    return render(request, 'Bookstor/register.html')
         
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)
        a =  User(username=username, email=email, password=password)
        a.save()
        messages.success(request, 'Votre compte a été créé avec succès.')
        return redirect('home')
    else:
        messages.error(request, 'Veuillez créer votre compte')   
        return redirect('regform')

#piblisher views

@login_required

def publisher(request):
    return render(request, 'publisher/home.html')   


@login_required
def uabook_form(request):
    return render(request, 'publisher/add_book.html')

@login_required
def request_form(request):
    return render(request, 'publisher/delete_request.html')

@login_required
def feedback_form(request):
    return render(request, 'publisher/send_feedback.html')



@login_required
def about(request):
    return render(request, 'publisher/about.html')



@login_required
def usearch(request):
    query = request.GET['query']
    print(type(query))


    #data = query.split()
    data = query
    print(len(data))
    if( len(data) == 0):
        return redirect('publisher')
    else:
                a = data

                # Searching for It
                qs5 =models.Book.objects.filter(id__iexact=a).distinct()
                qs6 =models.Book.objects.filter(id__exact=a).distinct()

                qs7 =models.Book.objects.all().filter(id__contains=a)
                qs8 =models.Book.objects.select_related().filter(id__contains=a).distinct()
                qs9 =models.Book.objects.filter(id__startswith=a).distinct()
                qs10 =models.Book.objects.filter(id__endswith=a).distinct()
                qs11 =models.Book.objects.filter(id__istartswith=a).distinct()
                qs12 =models.Book.objects.all().filter(id__icontains=a)
                qs13 =models.Book.objects.filter(id__iendswith=a).distinct()




                files = itertools.chain(qs5, qs6, qs7, qs8, qs9, qs10, qs11, qs12, qs13)

                res = []
                for i in files:
                    if i not in res:
                        res.append(i)


                # word variable will be shown in html when user click on search button
                word="Searched Result :"
                print("Result")

                print(res)
                files = res




                page = request.GET.get('page', 1)
                paginator = Paginator(files, 10)
                try:
                    files = paginator.page(page)
                except PageNotAnInteger:
                    files = paginator.page(1)
                except EmptyPage:
                    files = paginator.page(paginator.num_pages)
   


                if files:
                    return render(request,'publisher/result.html',{'files':files,'word':word})
                return render(request,'publisher/result.html',{'files':files,'word':word})





@login_required
def delete_request(request):
	if request.method == 'POST':
		book_id = request.POST['delete_request']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username
		user_request = username + " veut que le dossier avec l'ID  " + book_id + " soit supprimé."

		a = DeleteRequest(delete_request=user_request)
		a.save()
		messages.success(request, 'La demande a été envoyée')
		return redirect('request_form')
	else:
	    messages.error(request, 'La demande na pas été envoyée.')
	    return redirect('request_form')





@login_required
def send_feedback(request):
	if request.method == 'POST':
		feedback = request.POST['feedback']
		current_user = request.user
		user_id = current_user.id
		username = current_user.username
		feedback = username + " "+ " dit  " + feedback 

		a = Feedback(feedback=feedback)
		a.save()
		messages.success(request, 'Les commentaires ont été envoyés')
		return redirect('feedback_form')
	else:
	    messages.error(request, 'Les commentaires n ont pas été envoyés.')
	    return redirect('feedback_form')

    # users views   
@login_required
def uabook(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        year = request.POST['year']
        publisher = request.POST['publisher']
        desc = request.POST['desc']
        cover = request.FILES['cover']
        pdf1 = request.FILES['pdf1']
        pdf2 = request.FILES['pdf2']
        
        curent_user = request.user
        user_id = curent_user.id
        username = curent_user.username

        a = Book(title=title, author=author, year=year, publisher=publisher, 
            desc=desc, cover=cover, pdf1=pdf1, pdf2=pdf2, uploaded_by=username, user_id=user_id)
        a.save()
        messages.success(request, 'Le dossier a été téléchargé avec succès.')
        return redirect('publisher')
    else:
        messages.error(request, 'Le dossier n a pas été téléchargé avec succès.')
        return redirect('uabook_form')
    

        
        
class UcreateChat(LoginRequiredMixin, CreateView):
    form_class = ChatForm
    model = Chat
    template_name = 'publisher/chat_form.html'
    success_url = reverse_lazy('ulchat')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)
    

class UlistChat(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'publisher/chat_list.html'
    
    def get_queryset(self):
        return Chat.objects.filter(posted_at__lt=timezone.now()).order_by('-id')
    


class UEditchat(LoginRequiredMixin, UpdateView):
    model = Chat
    form_class = ChatForm
 
    template_name = 'publisher/editchat.html'
   
    success_url = reverse_lazy('ulchat')
    success_message = 'Date was update successfully'

class uDeletechatview(LoginRequiredMixin,DeleteView):
    model = Chat
    template_name = 'publisher/deletechat.html'
   
    success_url = reverse_lazy('ulchat')
    success_message = 'Date was delete successfully'     



class UBookListView(ListView):
    model = Book
    template_name = 'publisher/book_list.html'
    context_object_name = 'books'
    paginate_by = 4

    def get_queryset(self):
        # Filtrer les livres pour l'utilisateur actuellement connecté
        return Book.objects.filter(uploaded_by=self.request.user).order_by('-id')
    


   
#libtrarian views
@login_required
def librarian(request):
    book = Book.objects.all().count()
    user = User.objects.all().count()
    chat = Chat.objects.all().count()
    feedback = Feedback.objects.all().count()
    feed = DeleteRequest.objects.all().count()
     
    context = {'book':book, 'user':user, 'chat':chat, 'feedback':feedback, 'feed':feed} 
    return render(request, 'librarian/home.html', context)  
        

@login_required
def labook_form(request):
    
    return render(request, 'librarian/add_book.html', )  


@login_required
def labook(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        year = request.POST['year']
        publisher = request.POST['publisher']
        desc = request.POST['desc']
        cover = request.FILES['cover']
        
        pdf1 = request.FILES['pdf1']
        pdf2 = request.FILES['pdf2']
        
        
        curent_user = request.user
        user_id = curent_user.id
        username = curent_user.username

        a = Book(title=title, author=author, year=year, publisher=publisher, 
            desc=desc, cover=cover, pdf1=pdf1, pdf2=pdf2, uploaded_by=username, user_id=user_id)
        a.save()
        messages.success(request, 'Le dossier a été téléchargé avec succès')
        return redirect('llbook')
    else:
        messages.error(request, 'Le dossier n a pas été téléchargé avec succès')
        return redirect('llbook')
        
        


class LListUserView(generic.ListView):
    model = User
    template_name = 'librarian/list_users.html'
    context_object_name = 'users'
    paginate_by = 4

    def get_queryset(self):
        return User.objects.order_by('-id')



class LBookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'librarian/book_list.html'
    context_object_name = 'books'
    paginate_by = 3

    def get_queryset(self):
        return Book.objects.order_by('-id')
    





















class LcreateChat(LoginRequiredMixin, CreateView):
    form_class = ChatForm
    model = Chat
    template_name = 'librarian/chat_form.html'
    success_url = reverse_lazy('llchat')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)
    
class LEditchat(LoginRequiredMixin, UpdateView):
    model = Chat
    form_class = ChatForm
 
    template_name = 'librarian/editchat.html'
   
    success_url = reverse_lazy('llchat')
    success_message = 'Date was update successfully'

class LDeletechatview(LoginRequiredMixin,DeleteView):
    model = Chat
    template_name = 'librarian/deletechat.html'
   
    success_url = reverse_lazy('llchat')
    success_message = 'Date was delete successfully'         





class LlistChat(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'librarian/chat_list.html'

    def get_queryset(self):
        return Chat.objects.filter(posted_at__lt=timezone.now()).order_by('-id')
    

class LFeedback(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'librarian/Feedback.html'
    context_object_name = 'feedbacks'
    # paginate_by = 3

    def get_queryset(self):
        return Feedback.objects.order_by('-id')       
    

#admin views



class AcreateChat(LoginRequiredMixin, CreateView):
    form_class = ChatForm
    model = Chat
    template_name = 'dashboard/chat_form.html'
    success_url = reverse_lazy('alchat')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)
    

class AEditchat(LoginRequiredMixin, UpdateView):
    model = Chat
    form_class = ChatForm
 
    template_name = 'dashboard/editchat.html'
   
    success_url = reverse_lazy('alchat')
    success_message = 'Date was update successfully'

class ADeletechatview(LoginRequiredMixin,DeleteView):
    model = Chat
    template_name = 'dashboard/deletechat.html'
   
    success_url = reverse_lazy('alchat')
    success_message = 'Date was delete successfully'         



class AlistChat(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'dashboard/chat_list.html'

    def get_queryset(self):
        return Chat.objects.filter(posted_at__lt=timezone.now()).order_by('-id')
    
    
    
@login_required
def aabook_form(request):
    
    return render(request, 'dashboard/add_book.html')  


@login_required
def aabook(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        year = request.POST['year']
        publisher = request.POST['publisher']
        desc = request.POST['desc']
        cover = request.FILES['cover']
        
        pdf1 = request.FILES['pdf1']
        pdf2 = request.FILES['pdf2']
       
        
        curent_user = request.user
        user_id = curent_user.id
        username = curent_user.username

        a = Book(title=title, author=author, year=year, publisher=publisher, 
            desc=desc, cover=cover, pdf1=pdf1, pdf2=pdf2, uploaded_by=username, user_id=user_id)
        a.save()
        messages.success(request, 'Le dossier a été téléchargé avec succès')
        return redirect('albook')
    else:
        messages.error(request, 'Le dossier n a pas été téléchargé avec succès')
        return redirect('aabook_form')
        
        
class ABookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'dashboard/book_list.html'
    context_object_name = 'books'
    paginate_by = 3

    def get_queryset(self):
        return Book.objects.order_by('-id')

class AManageBook(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'dashboard/manage_books.html'
    context_object_name = 'books'
    paginate_by = 3

    def get_queryset(self):
        return Book.objects.order_by('-id')
    

   
    


class ADeleteBook(LoginRequiredMixin,DeleteView):
    model = Book
    template_name = 'dashboard/confirm_delete.html'
   
    success_url = reverse_lazy('dashboard')
    success_message = 'Date was delete successfully'    


class AViewBook(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'dashboard/book_detail.html'



class AEditView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'dashboard/edit_book.html'
   
    success_url = reverse_lazy('ambook')
    success_message = 'Date was update successfully'


class ADeleteRequest(LoginRequiredMixin, ListView):
    model = DeleteRequest
    template_name = 'dashboard/delete_request.html'
    context_object_name = 'feedbacks'
    

    def get_queryset(self):
        return DeleteRequest.objects.order_by('-id')  
    
    

class ADeleteRequestview(LoginRequiredMixin,DeleteView):
    model = DeleteRequest
    template_name = 'dashboard/supdelete.html'
   
    success_url = reverse_lazy('dashboard')
    success_message = 'Date was delete successfully'     
    


class AFeedback(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'dashboard/Feedback.html'
    context_object_name = 'feedbacks'
    # paginate_by = 3

    def get_queryset(self):
        return Feedback.objects.order_by('-id')       
    



@login_required
def asearch(request):
    query = request.GET['query']
    print(type(query))


    #data = query.split()
    data = query
    print(len(data))
    if( len(data) == 0):
        return redirect('publisher')
    else:
                a = data

                # Searching for It
                qs5 =models.Book.objects.filter(id__iexact=a).distinct()
                qs6 =models.Book.objects.filter(id__exact=a).distinct()

                qs7 =models.Book.objects.all().filter(id__contains=a)
                qs8 =models.Book.objects.select_related().filter(id__contains=a).distinct()
                qs9 =models.Book.objects.filter(id__startswith=a).distinct()
                qs10 =models.Book.objects.filter(id__endswith=a).distinct()
                qs11 =models.Book.objects.filter(id__istartswith=a).distinct()
                qs12 =models.Book.objects.all().filter(id__icontains=a)
                qs13 =models.Book.objects.filter(id__iendswith=a).distinct()




                files = itertools.chain(qs5, qs6, qs7, qs8, qs9, qs10, qs11, qs12, qs13)

                res = []
                for i in files:
                    if i not in res:
                        res.append(i)


                # word variable will be shown in html when user click on search button
                word="Searched Result :"
                print("Result")

                print(res)
                files = res




                page = request.GET.get('page', 1)
                paginator = Paginator(files, 10)
                try:
                    files = paginator.page(page)
                except PageNotAnInteger:
                    files = paginator.page(1)
                except EmptyPage:
                    files = paginator.page(paginator.num_pages)
   


                if files:
                    return render(request,'dashboard/result.html',{'files':files,'word':word})
                return render(request,'dashboard/result.html',{'files':files,'word':word})


#libtrarian views
@login_required
def dashboard(request):
    book = Book.objects.all().count()
    user = User.objects.all().count()
    chat = Chat.objects.all().count()
    feedback = Feedback.objects.all().count()
    feed = DeleteRequest.objects.all().count()
     
    context = {'book':book, 'user':user, 'chat':chat, 'feedback':feedback, 'feed':feed} 
    return render(request, 'dashboard/home.html', context)  
        

def create_user_form(request):
    choice = ['1', '0', 'utilisateur', 'Admin', 'consultant']
    choice = {'choice': choice}

    return render(request, 'dashboard/add_user.html', choice)  




class ADeleteUser(SuccessMessageMixin, DeleteView):
    model = User
    template_name='dashboard/confirm_delete3.html'
    success_url = reverse_lazy('aluser')
    success_message = "Données supprimées avec succès."



class AEditUser(SuccessMessageMixin, UpdateView): 
    model = User
    form_class = UserForm
    template_name = 'dashboard/edit_user.html'
    success_url = reverse_lazy('aluser')
    success_message = "Données mises à jour avec succès."

class ListUserView(generic.ListView):
    model = User
    template_name = 'dashboard/list_users.html'
    context_object_name = 'users'
    paginate_by = 4

    def get_queryset(self):
        return User.objects.order_by('-id')
    

def create_user(request):
    choice = ['1', '0', 'utilisateur', 'Admin', 'consultant']
    choice = {'choice': choice}
    if request.method == 'POST':
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            username=request.POST['username']
            userType=request.POST['userType']
            email=request.POST['email']
            password=request.POST['password']
            password = make_password(password)
            print("User Type")
            print(userType)
            if userType == "utilisateur":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_utilisateur=True)
                a.save()
                messages.success(request, 'cet utilisateur a été créé succès!')
                return redirect('aluser')
            elif userType == "Admin":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_admin=True)
                a.save()
                messages.success(request, 'cet utilisateur a été créé succès!')
                return redirect('aluser')
            elif userType == "consultant":
                a = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, is_consultant=True)
                a.save()
                messages.success(request, 'cet utilisateur a été créé succès!')
                return redirect('aluser')    
            else:
                messages.success(request, 'cet utilisateur n a pas été créé')
                return redirect('create_user_form')
    else:
        return redirect('create_user_form')


class AlViewUser(DetailView):
    model = User
    template_name = 'dashboard/user_detail.html'