from django.shortcuts import render, reverse, redirect
from django.http import HttpResponseRedirect, JsonResponse
from .models import *
from .forms import *
from neomodel.exceptions import *
import base64
import json
from django.contrib import messages
from django.template.loader import render_to_string
import traceback


def save_sketch_title(request):
    try:
        if request.method == 'POST':
            json_data = request.POST['json']
            json_data = json.loads(json_data)
            title = json_data['title']
            
            if len(title) > MAX_DB_TEXT_LENGTH:
                msg = f"The max DB text length was exceeded. Your title will be truncated to length {MAX_DB_TEXT_LENGTH} chars."
                messages.warning(request, message=msg)
                title = title[:MAX_DB_TEXT_LENGTH]
                
            sketch_id = json_data['sketch_id']            
            sketch = Sketch.nodes.get_or_none(uid=sketch_id)
            
            if sketch is None:
                raise f"Definition with UID {sketch_id} not found in the database. 😭"
            
            sketch.title = title
            sketch.save()
            
            data = f"Successfully set Sketch's title to {title}."
            
        else:            
            raise "Incorrect AJAX send method (needs to be POST)."
        
    except Exception as e:
        if __debug__:
            raise e
        data = str(e)
        messages.error(request, message=data)
        
    return JsonResponse(data, safe=False)



def save_definition_title(request):
    try:
        if request.method == 'POST':
            json_data = request.POST['json']
            json_data = json.loads(json_data)
            title = json_data['title']
            
            if len(title) > MAX_DB_TEXT_LENGTH:
                msg = f"The max. DB text length was exceeded. Your title will be truncated to length {MAX_DB_TEXT_LENGTH} chars."
                messages.warning(request, message=msg)
                title = title[:MAX_DB_TEXT_LENGTH]
                
            definition_id = json_data['definition_id']            
            definition = Definition.nodes.get_or_none(uid=definition_id)
            
            if definition is None:
                raise f"Definition with UID {definition_id} not found in the database. 😭"
            
            definition.title = title
            definition.save()
            
            data = f"Successfully set Definition's title to {title}."
            
        else:            
            raise "Incorrect AJAX send method (needs to be POST)."
        
    except Exception as e:
        if __debug__:
            raise e
        data = str(e)
        messages.error(request, message=data)
        
    return JsonResponse(data, safe=False)
            
        
def save_sketch(request):
    try:            
        if request.method == "POST":
            json_data = request.POST['json']
            json_data = json.loads(json_data)            
            sketch_id = json_data['sketch_id']            
            json_data = json_data['json_data']
            
            if json_data:
                json_data = base64.b64decode(json_data)
                json_data = json.loads(json_data)
            
            sketch = Sketch.nodes.get_or_none(uid=sketch_id)
            
            if sketch is None:
                data = f"Sketch with UID {sketch_id} not found in the database. 😭"
                messages.error(request, message=data)
            else:
                sketch.delete_content()
                sketch.from_quiver_format(json_data)
                data = "Proposition saved to database. 😎"
                messages.success(request, message=data)

        else:
            data = "Incorrect AJAX send method (needs to be POST)."
            messages.error(request, message=data)
    except Exception as e:
        if __debug__:
            raise e
        else:
            data = str(e)
        messages.error(request, messages=data)    
            
    return JsonResponse(data, safe=False)


def done_editing_sketch(request, sketch_id: str):
    try:
        done_url = pop_editing_referer(request, Sketch, sketch_id)            
        return redirect(done_url)
        
    except Exception as e:
        if __debug__:
            raise e
        return error(error_txt=traceback.format_exc())
    

def sketch_editor(request, sketch_id: str):
    try:            
        sketch = Sketch.nodes.get_or_none(uid=sketch_id)
        
        if sketch is None:
            raise Exception(f"Sketch with UID {sketch_id} doesn't exist in the database.")
        
        push_editing_referer(request, Sketch, sketch_id)
        
        sketch.save()
        quiver_base64 = sketch.to_quiver_format()
        quiver_base64 = json.dumps(quiver_base64)
        quiver_base64 = quiver_base64.encode(encoding='ascii')
        quiver_base64 = base64.b64encode(quiver_base64)
        quiver_base64 = quiver_base64.decode(encoding='ascii')      # 😅 many steps lol
                
        data = {
            'sketch' : sketch,
            'quiver_base64' : quiver_base64,
        }
        
        messages.success(request, message='Successfully loaded sketch from the database.')
        return render(request, 'db/sketch_editor.html', context=data)
    
    except Exception as e:
        if __debug__:
            raise e
        return error(error_txt=traceback.format_exc())
        

def push_editing_referer(request, cls, db_id):
    if not isinstance(cls, str):
        cls = cls.__name__
        
    referer = request.META.get('HTTP_REFERER', None)
    
    if referer is None:
        referer = reverse('home')
        
    session = request.session
    
    editing = session.get('editing', None)
    
    if not editing:
        editing = session['editing'] = {}
    
    if cls not in editing:
        editing[cls] = {}
        
    items = editing[cls]
        
    if db_id not in items:
        items[db_id] = referer
        
    request.session.modified = True
        
        
def pop_editing_referer(request, cls, db_id):
    if not isinstance(cls, str):
        cls = cls.__name__
        
    session = request.session
    editing = session.get('editing', None)    
    done_url = None
    
    if editing:
        if cls in editing:                    
            defs = editing[cls]
            
            if db_id in defs:
                done_url = defs[db_id]
                del defs[db_id]
            else:
                defs.clear()
                
            request.session.modified = True                
        
    if done_url is None:    
        done_url = reverse('home')
        
    return done_url


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
        return error(error_txt=traceback.format_exc())
    
    


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
    return redirect(reverse('error', kwargs={'error_txt': error_txt,}))


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


def add_sketch_to_def(request):
    try:            
        if request.method == "POST":
            json_data = request.POST['json']
            json_data = json.loads(json_data)                     
    
            definition_id = json_data['definition_id']
            definition = Definition.nodes.get_or_none(uid=definition_id)
            
            if definition is None:
                raise f"Definition with UID {definition_id} does not exist in the database. (╯‵□′)╯︵┻━┻"
            
            sketch = Sketch()
            sketch.title = 'Title 😎?'
            sketch.save()
            end = definition.right_most_prop()
            
            if end:
                end.arrows_to.connect(sketch)
                end.save()
            else:
                definition.start_prop.connect(sketch)
                definition.save()
            
            context = {
                'prop' : sketch,                    
            }
            
            card_content =  render_to_string(template_name='db/quiver_preview_include.html', context=context)
            
            data = {
                'prop_id': sketch.uid,
                'card_content': card_content, 
            }
        
        else:
            raise "Incorrect AJAX send method (needs to be POST)"
            
    except Exception as e:
        if __debug__:
            raise e
        else:
            data = str(e)
        messages.error(request, messages=data)    
            
    return JsonResponse(data, safe=False)


def remove_prop_from_def(request):
    try:            
        if request.method == "POST":
            json_data = request.POST['json']
            json_data = json.loads(json_data)                     

            prop_id = json_data['prop_id']
            
            query = f"""
            MATCH (P:Proposition)-[r:ARROWS_TO]->(Q:Proposition)
            WHERE Q.uid='{prop_id}'
            RETURN P,Q
            """
            
            results,_ = db.cypher_query(query, resolve_objects=True)
            
            if results:
                results = results[0]                
                P, Q = results               
                codQ = Q.arrows_to.single()
                P.arrows_to.disconnect(Q)
                
                if codQ:
                    Q.arrows_to.disconnect(codQ)
                    P.arrows_to.connect(codQ)
                
                Q.delete()
            else:
                Q = Proposition.nodes.get_or_none(uid=prop_id)
                
                if Q:
                    Q.delete()
                else:
                    msg = f"Proposition with UID {prop_id} does not exist in the database. 😢"
                    messages.warning(request, message=msg)
                
            msg = "Successfully deleted the proposition from the definition. 😎"
            messages.success(request, message=msg)
            data = ""
        else:
            raise "Incorrect AJAX send method (needs to be POST)"
            
    except Exception as e:
        #if __debug__:            #raise e
        
        data = str(e)
        messages.error(request, messages=data)    
            
    return JsonResponse(data, safe=False)    
    


def define(request):
    definition = Definition()
    definition.title = 'Title 🤓?'
    definition.save()
    
    url = reverse('edit_definition', args=(definition.uid, ))

    return redirect(url)


def done_editing_def(request, definition_id: str):
    try:
        done_url = pop_editing_referer(request, Definition, definition_id)            
        return redirect(done_url)
        
    except Exception as e:
        if __debug__:
            raise e
        return error(error_txt=traceback.format_exc())         


def edit_definition(request, definition_id: str):
    try:            
        definition = Definition.nodes.get_or_none(uid=definition_id)
        if definition is None:
            raise f"Definition with UID {definition_id} does not exist in the database." + \
                  "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻"    

        push_editing_referer(request, Definition, definition_id)
        
        start = definition.start_prop.single()
        implication_chain = []        
        
        if start:
            query = f"""
            MATCH p=(P:Proposition)-[A:ARROWS_TO*]->(Q:Proposition)
            WHERE P.uid='{start.uid}'
            RETURN p ORDER BY length(p) DESC LIMIT 1
            """
            paths,_ = db.cypher_query(query, resolve_objects=True)
            
            if paths:
                paths = paths[0]
                
                for path in paths:
                    for node in path.nodes:
                        implication_chain.append(node)
                    break
            else:
                implication_chain = [start]
                
        context = {
            'definition' : definition,
            'implication_chain': implication_chain,
        }
        
        return render(request, "db/define.html", context)
    
    except Exception as e:
        if __debug__:
            raise e
        return error(error_txt=traceback.format_exc())
    


