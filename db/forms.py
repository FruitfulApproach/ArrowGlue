from django import forms
from ArrowGlue.settings import MAX_DB_TEXT_LENGTH

class NewProofForm(forms.Form):
    title = forms.CharField(label="Proof Title", max_length=MAX_DB_TEXT_LENGTH)
    
class NewStatementForm(forms.Form):
    title = forms.CharField(label="Statement Title", max_length=MAX_DB_TEXT_LENGTH)
    
class AddToStatementForm(forms.Form):
    kind = forms.ChoiceField(choices=(('text', 'Purely textual language'),('sketch', 'Diagram sketch')))
    
class EditTextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(), max_length=MAX_DB_TEXT_LENGTH)
    
    
