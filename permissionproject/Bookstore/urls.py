from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    #general ruls
    path('',views.home, name='homeac'),
    path('login_form',views.login_form, name='home'),
    path('services/',views.services, name = 'services'),
    path('apropos/',views.apropos, name = 'apropos'),
    path('login/',views.loginView, name='login'),
    path('logout/',views.logoutView, name='logout'),
    path('register_form/',views.register_form, name='regform'),
    path('register/',views.register_view, name='register'),
    path('librarian/',views.librarian, name='librarian'),
    path('uechat/<int:pk>',views.UEditchat.as_view(), name='uechat'),
    path('udchat/<int:pk>',views.uDeletechatview.as_view(), name='udchat'),
    
   #librarian urls
    path('librarian/',views.librarian, name='librarian'),
    path('labook_form/',views.labook_form, name='labook_form'),
    path('labook/',views.labook, name='labook'),
  
    path('llbook/',views.LBookListView.as_view(), name='llbook'),
    
   
   
    
    path('lcchat/',views.LcreateChat.as_view(), name='lcchat'),
    path('llchat/',views.LlistChat.as_view(), name='llchat'),

    
    

    
    path('lechat/<int:pk>',views.LEditchat.as_view(), name='lechat'),
    path('ldchat/<int:pk>',views.LDeletechatview.as_view(), name='ldchat'),
    path('lluser/',views.LListUserView.as_view(), name='lluser'),
    path('lfeedback/',views.LFeedback.as_view(), name='lfeedback'),
    #publisher urls
   
    path('publisher/',views.UBookListView.as_view(), name='publisher'),
    path('uabook_form/',views.uabook_form, name='uabook_form'),
    path('uabook/',views.uabook, name='uabook'),
    path('ucchat/',views.UcreateChat.as_view(), name='ucchat'),
    path('ulchat/',views.UlistChat.as_view(), name='ulchat'),
    path('request_form/',views.request_form, name='request_form'),
    path('delete_request/',views.delete_request, name='delete_request'),
  
    path('feedback_form/',views.feedback_form, name='feedback_form'),
    path('send_feedback/',views.send_feedback, name='send_feedback'),
    path('send_feedback/',views.send_feedback, name='send_feedback'),
   

    path('about/',views.about, name='about'),
    path('usearch/',views.usearch, name='usearch'),

    #admin urls
    path('dashboard/', views.dashboard, name='dashboard'),
     path('acchat/',views.AcreateChat.as_view(), name='acchat'),
    path('alchat/',views.AlistChat.as_view(), name='alchat'),
    path('aabook_form/',views.aabook_form, name='aabook_form'),
    path('aabook/',views.aabook, name='aabook'),
    path('albook/',views.ABookListView.as_view(), name='albook'),
    path('ambook/',views.AManageBook.as_view(), name='ambook'),
    path('adbook/<int:pk>',views.ADeleteBook.as_view(), name='adbook'),
    path('avbook/<int:pk>',views.AViewBook.as_view(), name='avbook'),
   
    path('aebook/<int:pk>',views.AEditView.as_view(), name='aebook'),
    path('adrequest/',views.ADeleteRequest.as_view(), name='adrequest'),
    path('adrequestview/<int:pk>',views.ADeleteRequestview.as_view(), name='adrequestview'),
    path('afeedback/',views.AFeedback.as_view(), name='afeedback'),
    path('asearch/',views.asearch, name='asearch'),
    path('adbookk/<int:pk>',views.ADeleteBook.as_view(), name='adbookk'),
    path('create_user_form/',views.create_user_form, name='create_user_form'),
    path('aluser/',views.ListUserView.as_view(), name='aluser'),
    path('create_user/',views.create_user, name='create_user'),
    path('alvuser/<int:pk>',views.AlViewUser.as_view(), name='alvuser'),
    path('aeuser/<int:pk>',views.AEditUser.as_view(), name='aeuser'),
    path('aduser/<int:pk>',views.ADeleteUser.as_view(), name='aduser'),
    path('aechat/<int:pk>',views.AEditchat.as_view(), name='aechat'),
    path('adchat/<int:pk>',views.ADeletechatview.as_view(), name='adchat'),
]   

