from ArrowGlue.settings import MAX_DB_TEXT_LENGTH, MAX_USERNAME_LENGTH
# Create your models here.
from neomodel import *
from bidict import bidict


class AbstrBase(StructuredNode):
    text = StringProperty(max_length=MAX_DB_TEXT_LENGTH, default='')  
    var_regex = StringProperty(max_length=2 * MAX_DB_TEXT_LENGTH)
    
    DERIVED_TYPES = {
        'undefined': 'Undefined', 
        'object': 'Object',
        'arrow': 'Arrow',
        'diagram': 'DiagramSketch',
        'text': 'PureTextLang',
        'statement': 'Statement',        
    }
    type = StringProperty(choices=DERIVED_TYPES, default='undefined')
    
    @staticmethod
    def factory(uninflated):
        base_inflate = AbstrBase.inflate(uninflated)        
        return eval(f'{base_inflate.type}.inflate(uninflated)')    
    
        

class AbstrNode(AbstrBase):    
    sketch_index = IntegerProperty(default=-1)
    sketch_uid = StringProperty(default='')          
    color = JSONProperty(default={'h': 0, 's': 0, 'l' : 0, 'a': 1,})
    
    QUANTIFIERS = {0: 'forall', 1: 'exists', 2: 'bound',}
    quantifier = BooleanProperty(choices=QUANTIFIERS, default=0)
    
    
class Connection(StructuredRel):
    pass

   
class Object(AbstrNode):
    sourced_arrows = RelationshipTo('Arrow', 'CONNECTS', cardinality=ZeroOrMore, model=Connection)
    
    pure_styling_info = JSONProperty(
        default={
            'x': 0, 'y': 0
        })    
    
    def __init__(self, *args, **kwargs):
        self.type = 'object'
        super().__init__(*args, **kwargs)
        
    
    def from_quiver_format(self, fmt, index):
        self.parent_index = index
        
        pure_style = {
            'x' : fmt[0],
            'y' : fmt[1],
        }
        
        self.pure_styling_info = pure_style
        
        if len(fmt) > 2:
            self.text = fmt[2]
            
        if len(fmt) > 3:
            self.color = fmt[3]
        
        self.save()
        
    def to_quiver_format(self):
        pure_style = self.pure_styling_info        
        return [pure_style['x'], pure_style['y'], self.text, self.color] 
            
                
                
class Arrow(AbstrNode):
    src = RelationshipTo('AbstrNode', 'FROM', cardinality=One, model=Connection)
    dst = RelationshipTo('AbstrNode', 'CONNECTS', cardinality=One, model=Connection)
    
    NUM_LINES = {1: 'one', 2: 'two', 3: 'three', 4: 'four',}
    TAIL_STYLE = {0:'none', 1:'mono', 2:'hook', 3:'arrowhead', 4:'CONNECTS_TO'} 
    HEAD_STYLE = {0:'none', 1:'arrowhead', 2:'epi', 3:'harpoon'}
    BODY_STYLE = {0:'solid', 1:'none', 2:'dashed', 3:'dotted', 4:'squiggly', 5:'barred'}  
    
    # Both mathematically significant and style fields:
    num_lines = IntegerProperty(choices=NUM_LINES, default=1)
    tail_style = IntegerProperty(choices=TAIL_STYLE, default=0)
    head_style = IntegerProperty(choices=HEAD_STYLE, default=1)
    body_style = IntegerProperty(choices=BODY_STYLE, default=0)
    
    ALIGNMENT = {0: 'l', 1: 'ctr', 2: 'r', 3: 'ovr',}    
    SIDE = {0: 'no', 1: 't', 2: 'b',}    
    
    # Style-only fields put into JSON property for Neo4j ultimate speed    
    pure_styling_info = JSONProperty(
        default={
            'algmt' : 0,
            'lblpos' : 50,
            'lbloff': 0,
            'curve': 0,
            'tltrim': 0,
            'hdtrim': 0,
            'tailsd': 0,
            'headsd': 0,
        })
    

    def __init__(self, *args, **kwargs):
        self.type = 'arrow' 
        super().__init__(*args, **kwargs)
         
    
    def from_quiver_format(self, fmt, index):
        self.parent_index = index
        
        if len(fmt) > 2:
            self.text = fmt[2]
        
        pure_style = self.pure_styling_info.default_value()
        
        if len(3) > 3:
            pure_style['algmt'] = fmt[3]
            
        if len(fmt) <= 3:
            self.save()
            return
        
        opts = fmt[4]
            
        if 'label_position' in opts:
            pure_style['lblpos'] = opts['label_position']
        
        if 'offset' in opts:
            pure_style['lbloff'] = opts['offset']
            
        if 'curve' in opts:
            pure_style['curve'] = opts['curve']
            
        if 'shorten' in opts:
            shorten = opts['shorten']
            if 'source' in shorten:
                pure_style['tltrim'] = shorten['source']
            if 'target' in shorten:
                pure_style['hdtrim'] = shorten['target']
                
        if 'level' in opts:
            self.num_lines = opts['level']
            
        if 'style' in opts:
            style = opts['style']
            
            if 'body' in style:
                body = style['body']
                
                if 'name' in body:
                    self.head_style = body['name']
                    
            if 'tail' in style:
                tail = style['tail']
                
                if 'name' in tail:
                    self.tail_style = tail['name']
                    
                if 'side' in tail:
                    pure_style['tailsd'] = tail['side']
                    
            if 'head' in style:
                head = style['head']
                
                if 'name' in head:
                    self.head_style = head['name']
                
                if 'side' in head:
                    pure_style['headsd'] = head['side']
            
        color = None
        
        if len(fmt) > 5:
            color = fmt[5]
            
        elif 'colour' in opts:
            color = opts['colour']
            
        if color is not None:
            self.color = color
            
        self.pure_styling_info = pure_style            
        self.save()
                
    def to_quiver_format(self):
        fmt = [self.src.parent_index, self.dest.parent_index]
        fmt.append(self.text if self.text is not None else '')
        pure_style = self.pure_styling_info        
        fmt.append(pure_style['algmt'])
        
        opts = {
            #'colour' : [self.color_hue, self.color_sat, self.color_lum, self.color_alph],
            'label_position': pure_style['lblpos'], 
            'offset' : pure_style['lbloff'],
            'curve' : pure_style['curve'],
            'shorten' : {
                'source' : pure_style['tltrim'], 
                'target' : pure_style['hdtrim'],
            },
            'level' : self.num_lines,
            'style' : {
                'tail': {
                    'name' : self.TAIL_STYLE[self.tail_style],
                    'side' : self.SIDE[pure_style['tailsd']],
                },
                'head': {
                    'name' : self.HEAD_STYLE[self.head_style],
                    'side' : self.SIDE[pure_style['headsd']], 
                },
                'body': {
                    'name' : self.BODY_STYLE[self.body_style],
                }                    
            },
            'colour' : self.color,
        }
        
        fmt.append(opts)
        fmt.append(self.color)
        
        return fmt    
    
class Content(AbstrBase):
    # Inherits text already    
    uid = UniqueIdProperty()
    
    maintainer = StringProperty(max_length=MAX_USERNAME_LENGTH, required=True)
    creation_datetime = DateTimeProperty(default_now=True)
    datetime_edited = DateTimeProperty(default_now=True)
    
    display_index = IntegerProperty(required=True)    
    sketch = RelationshipTo('DiagramSketch', "DRAWN_AS", cardinality=ZeroOrOne)
    
    @property
    def is_pure_text(self):
        #query = f"""
        #MATCH (c:Content)-[r:DRAWN_AS]->(d:DiagramSketch)
        #WHERE c.uid = {self.uid}
        #RETURN count(r)
        #"""
        #results = db.cypher_query(query)
        
        #print("IS PURE TEXT (results):", results)
        
        #return results[0] == 0
        
        return len(self.sketch) == 0
        
    
class DiagramSketch(AbstrBase):
    associated_rule = RelationshipTo('Statement', 'NOTATION', cardinality=ZeroOrOne)
        
    def __init__(self, *args, **kwargs):
        self.type = 'diagram' 
        super().__init__(*args, **kwargs)       

class PureTextLang(AbstrBase):
    def __init__(self, *args, **kwargs):
        self.type = 'text'
        super().__init__(*args, **kwargs)
        

class Contains(StructuredRel):
    pass
    
class Statement(AbstrBase):
    uid = UniqueIdProperty()
    content = RelationshipTo('Content', 'CONTAINS', cardinality=OneOrMore)
    given_indices = JSONProperty(default=[])
    goal_indices = JSONProperty(default=[])    

    def __init__(self, *args, **kwargs):
        self.type = 'statement'
        super().__init__(*args, **kwargs)
        
class Prop(AbstrBase):
    uid = UniqueIdProperty()
        
class Proposition(AbstrBase):
    content = RelationshipTo('Content', 'CONTAINS', cardinality=One)

class RightAssoc(Proposition):
    pass
    

class Definition(Statement):
    pass

class Conjecture(Statement):
    pass


class Theorem(Statement):
    proof = RelationshipTo('Proof', 'PROVEN_BY', cardinality=OneOrMore)
    

    
    
    
    
    
class Proof(AbstrBase):
    uid = UniqueIdProperty()
    statement = RelationshipTo('Statement', 'PROVES', cardinality=One)
    
    def __init__(self, *args, **kwargs):
        self.type = 'proof'
        super().__init__(*args, **kwargs)

    
#class WordDefinition(Proof):
    #binding_words = RelationshipTo('PureTextLang', 'WORD', cardinality=One)
    #expansion = RelationshipTo('AbstrBase', 'EXPAND', cardinality=OneOrMore, model=ProofOrder)
    
    
    