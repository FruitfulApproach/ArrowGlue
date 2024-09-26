import db.views as views
from django.urls import path

urlpatterns = [
    path("save-sketch-title/", views.save_sketch_title, name="save_sketch_title"), 
    path("save-definition-title/", views.save_definition_title, name="save_definition_title"),
    path("add-sketch-to-def/", views.add_sketch_to_def, name="add_sketch_to_def"),
    path("delete-prop-from-def/", views.remove_prop_from_def, name="remove_prop_from_def"), 
    path("save-sketch/", views.save_sketch, name="save_sketch"), 
    path("edit-sketch/<str:sketch_id>", views.sketch_editor, name="sketch_editor"),
    path("done-editing-sketch/<str:sketch_id>", views.done_editing_sketch, name='done_editing_sketch'), 
    path("edit-definition/<str:definition_id>", views.edit_definition, name="edit_definition"),
    path("done-editing-def/<str:definition_id>", views.done_editing_def, name='done_editing_def'), 
    path("define/", views.define, name='define'), 
    path("", views.index, name="home"), 
    path("delete-content/<str:content_id>", views.delete_content, name="delete_content"), 
    path("edit-text-content/<str:content_id>", views.edit_text_content, name="edit_text_content"), 
    path("error/<str:error_txt>", views.error_page, name="error"), 
    path("edit-statement/<str:statement_id>", views.edit_statement, name='edit_statement'),
    path("new-statement/", views.new_statement, name='new_statement'), 
    path("edit-proof/<str:proof_id>", views.edit_proof, name='edit_proof'), 
    path("new-proof/", views.new_proof, name='new_proof')
]
