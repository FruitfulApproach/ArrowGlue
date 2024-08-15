import db.views as views
from django.urls import path

urlpatterns = [
    path("define/", views.define, name="define"), 
    path("", views.index, name="db_index"), 
    path("delete-content/<str:content_id>", views.delete_content, name="delete_content"), 
    path("edit-text-content/<str:content_id>", views.edit_text_content, name="edit_text_content"), 
    path("error/<str:error_txt>", views.error_page, name="error"), 
    path("test1/", views.test1, name='test1'),
    path("edit-statement/<str:statement_id>", views.edit_statement, name='edit_statement'),
    path("new-statement/", views.new_statement, name='new_statement'), 
    path("edit-proof/<str:proof_id>", views.edit_proof, name='edit_proof'), 
    path("new-proof/", views.new_proof, name='new_proof')
]
