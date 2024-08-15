from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseRedirect, JsonResponse
from .models import *
from .forms import *
from neomodel.exceptions import * 

def test1(request):
    #sketch = DiagramSketch(maintainer='EnjoysMath')
    #sketch.save()
    #A = Object(text='A', parent_uid=sketch.uid, parent_index=0)
    #A.save()
    #B = Object(text='B', parent_uid=sketch.uid, parent_index=1)
    #B.save()
    #f = Arrow(text='f', parent_uid=sketch.uid, parent_index=2)
    #f.save()
    #A.sourced_arrows.connect(f)
    #A.save()
    #f.dest_node.connect(B)
    #f.save()
    
    return render(request, template_name='db/test1.html')


def new_proof(request):
    if request.method == 'POST':
        form = NewProofForm(request.POST)
        
        if form.is_valid():
            proof = Proof()
            proof.save()
            proof_id = proof.uid
            
            next_url = reverse('edit_proof', args=[proof_id])
        else:
            next_url = reverse('error', kwargs={'error_txt': "Form not valid.",})
            
        return redirect(next_url)  # TODO error page or messages popup
    else:
        form = NewProofForm()
        
    return render(request, 'db/new_proof.html', {'form': form,})


def new_statement(request):
    if request.method == 'POST':
        form = NewStatementForm(request.POST)
        
        if form.is_valid():
            statement = Statement()            
            statement_id = statement.uid
            statement.text = form.cleaned_data['title']
            statement.save()
            
            next_url = reverse('edit_statement', args=[statement_id])
            return redirect(next_url)
        else:
            return redirect(reverse('error', kwargs={'error_txt': "Form not valid.",}))
    else:
        form = NewStatementForm()
        
    return render(request, 'db/new_statement.html', {'form': form,})


def edit_proof(request, proof_id: str):
    proof = Proof.nodes.get(uid=proof_id)
    
    if proof is None:
        return redirect(reverse('error', kwargs={'error_txt': f"Proof with UID {uid} not found.",}))
    
    return render(request, 'db/edit_proof.html', {'proof': proof,})


def edit_statement(request, statement_id: str):
    try:
        statement = Statement.nodes.get(uid=statement_id)
        
        if statement is None:
            return redirect(reverse('error', kwargs={'error_txt': f"Statement with UID {uid} not found.",}))
        
        add_given_form = None
        add_goal_form = None
        
        if request.method == 'POST':
            form = AddToStatementForm(request.POST)
            
            if form.is_valid():
                kind = form.cleaned_data['kind']
                
                if kind in {'sketch', 'text'}:           
                    index = len(statement.given_indices) + len(statement.goal_indices)
                    content = Content(display_index=index, maintainer='Debug', text=f'(TODO) Test {index}')
                    content.save()
                    
                    if kind == 'sketch':                
                        sketch = DiagramSketch()
                        sketch.save()
                        content.sketch.connect(sketch)                       
                        content.save()
                    elif kind == 'text':
                        pass
                    else:
                        assert 0
                    
                    statement.content.connect(content)
                    
                    part = request.POST['statement_part']
                                    
                    if part == 'given':
                        statement.given_indices.append(index)
                        add_given_form = form
                    elif part == 'goal':
                        statement.goal_indices.append(index)
                        add_goal_form = form
                    else:
                        assert 0
                    
                    statement.save()
                else:
                    assert 0            
            else:
                assert 0
    
        if len(statement.content) > 0:
            results = statement.content.all()        
            givens = set(statement.given_indices)
            goals = set(statement.goal_indices)
            givens = list(filter(lambda c: c.display_index in givens, results))
            goals = list(filter(lambda c: c.display_index in goals, results))
        #except CardinalityViolation:
        else:
            givens = []
            goals = []
            
        if add_given_form is None:
            add_given_form = AddToStatementForm()
        if add_goal_form is None:
            add_goal_form = AddToStatementForm()
        
        context = {
            'statement': statement,
            'givens': givens,
            'goals': goals,
            'add_given_form' : add_given_form,
            'add_goal_form': add_goal_form,
        }
    
        return render(request, 'db/edit_statement.html', context)
    
    except Exception as e:
        if __debug__:
            raise e
        return redirect(reverse('error', kwargs={'error_txt': str(e),}))
    
    


def error_page(request, error_txt: str):    
    context = {
        'error_text' : error_txt,
    }
    
    return render(request, 'db/error.html', context)


def edit_text_content(request, content_id: str):
    content = Content.nodes.get(uid=content_id)
    
    if content is None:
        return error(f'Text content with UID {content_id} not found.')
    
    if request.method == "GET":
        context = {
            'form' : EditTextForm(initial={'text': content.text,}),
        }
        
        return render(request, 'db/edit_text_content.html', context)
    else:
        form = EditTextForm(request.POST)
        
        if form.is_valid():
            content.text = form.cleaned_data['text']
            content.save()
            
            next_url = request.POST.get('next', None)
            
            if next_url is None:
                return error(f"Programmer error at {__file__}:edit_text_content().")
            
            return redirect(next_url)
        else:
            return error("Form not valid.")
 

def error(error_txt: str):
    return redirect(reverse('errror', kwargs={'error_txt': error_txt,}))


def delete_content(request, content_id: str):
    content = Content.nodes.get(uid=content_id)
    
    if content is None:
        return error(f'Text content with UID {content_id} not found.')
    
    query = f"""
    MATCH (s:Statement)-[r:CONTAINS]->(c:Content)
    WHERE c.uid = '{content_id}'
    RETURN s
    """
    results = db.cypher_query(query)
    statement = Statement.inflate(results[0][0][0])
    
    next_url = request.GET.get("next", None)
        
    if next_url is None:
        return error(f"Programmer error at {__file__}:edit_text_content().")
    
    return redirect(next_url)


def index(request):
    return render(request, "db/index.html")

def define(request):
    return render(request, "db/define.html")