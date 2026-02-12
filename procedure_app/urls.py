from django.urls import path
from . import views

urlpatterns = [
   
    path('register/', views.register_page, name='register_page'),
    path('', views.login_page, name='login_page'),
    path('register_view/', views.register_view, name='register_view'),
    path('dashboard_administrateur/', views.dashboard_administrateur, name='dashboard_administrateur'),
    path('dashboard_consultant/', views.dashboard_consultant, name='dashboard_consultant'),
    path('dashboard_clien/', views.dashboard_client, name='dashboard_client'),
    path('login_view/', views.login_view, name= 'login_view'),
    path('logout/', views.logout_view, name= 'logout'),
    
    # urls  administrateur#
    path('admin_view_liste_clients/', views.admin_view_liste_clients.as_view(), name='admin_view_liste_clients'),
    path('create_user_form/', views.create_user_form, name='create_user_form'),
    path('admin_create_user/', views.admin_create_user, name='admin_create_user'),
    path('admin_view_detail_user/<int:pk>', views.admin_view_detail_user.as_view(), name='admin_view_detail_user'),
    path('admin_edit_user/<int:pk>', views.admin_edit_user.as_view(), name='admin_edit_user'),
    path('admin_delete_user/<int:pk>', views.admin_delete_user.as_view(), name='admin_delete_user'),
    path('admin_view_avis/', views.admin_view_avis.as_view(), name='admin_view_avis'),
    
    path('admin_view_list_dossiers_clients/', views.admin_view_list_dossiers_clients.as_view(), name ='admin_view_list_dossiers_clients'),
    path('admin_namage_dossier/', views.admin_namage_dossier.as_view(), name='admin_namage_dossier'),
    
    path('voir_detail_dossier/<int:dossier_id>/', views.voir_detail_dossier, name='voir_detail_dossier'),

    path('admin_edit_dossier/<int:pk>', views.admin_edit_dossier.as_view(), name='admin_edit_dossier'),
    path('admin_view_feedback_client/', views.admin_view_feedback_client.as_view(), name='admin_view_feedback_client'),
    path('admin_view_delete_request', views.admin_view_delete_request.as_view(), name='admin_view_delete_request'),
    path('dashboard-admin/dossier/<int:dossier_id>/chat/', views.admin_dossier_chat, name='admin_dossier_chat'),
    path('AdminConversationList', views.AdminConversationList.as_view(), name='AdminConversationList'),
    path('piece-jointe/supprimer/<int:pk>/', views.supprimer_piece_jointe, name='supprimer_piece_jointe'),
    path('dossier/supprimer/<int:pk>/', views.supprimer_dossier_client, name='supprimer_dossier_client'),
    path('chat/supprimer/<int:pk>/', views.supprimer_chat_client, name='supprimer_chat_client'),
    path('chat/<int:pk>/modifier/', views.modifier_chat_client, name='modifier_chat_client'),
    
    
    # urls client #
    
    path('client_view_page_dossier_form/', views.client_view_page_dossier_form, name="client_view_page_dossier_form"),
    path('client_ajout_dossier/', views.client_ajout_dossier, name="client_ajout_dossier"),
    path('client_view_list_dossier/', views.client_view_list_dossier.as_view(), name="client_view_list_dossier"),
    path('dossier/<int:dossier_id>/ajouter-pieces/',views.ajouter_pieces_jointes,name='ajouter_pieces_jointes'),
   
    
    path('dossier/<int:dossier_id>/piece-jointe/ajouter/', views.ajouter_piece_jointe, name='ajouter_piece_jointe'),
    path('client_send_feedback_form/', views.client_send_feedback_form, name='client_send_feedback_form'),
    path('client_send_feedback/', views.client_send_feedback, name='client_send_feedback'),
    path('client_create_chat/<int:dossier_id>/', views.client_create_chat, name='client_create_chat'),

    path('client_view_liste_chat/', views.client_view_liste_chat.as_view(), name='client_view_liste_chat'),
   
   
 
    path('delete_request/', views.delete_request, name='delete_request'),
   
   

 # ia #
   path('analyse-ia/<int:pk>/', views.vue_analyse_ia, name='analyse_ia'),
   path('chatbot-api/', views.chatbot_api, name='chatbot_api'),


   # Vos URLs existantes...
    
    
    # Nouveaux endpoints pour l'IA
    path('dossier/<int:dossier_id>/analyser/', views.analyser_dossier_ia, name='analyser_dossier_ia'),
    path('dossier/<int:dossier_id>/analyse/', views.voir_analyse_juridique, name='voir_analyse_juridique'),
    path('analyse/<int:analyse_id>/chat/', views.chat_analyse, name='chat_analyse'),
    
  
]
