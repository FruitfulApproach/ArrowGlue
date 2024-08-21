from ArrowGlue.settings import MAX_DB_TEXT_LENGTH, MAX_USERNAME_LENGTH
# Create your models here.
from neomodel import *

class Arrow(StructuredRel):
    sketch_src_index = IntegerProperty(default=-1)
    sketch_dst_index = IntegerProperty(default=-1)

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
        fmt = [self.sketch_src_index, self.sketch_dst_index]
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
    

class ObjectArrow(StructuredNode):
    text = StringProperty(max_length=MAX_DB_TEXT_LENGTH, default='')  
    var_regex = StringProperty(max_length=2 * MAX_DB_TEXT_LENGTH)
    
    # For quiver editor:
    sketch_index = IntegerProperty(default=-1)
    prop_id = StringProperty(default='')
    
    # H,S,L,A:
    color = JSONProperty(default=[0.0, 0.0, 0.0, 1.0])
    # Node-only:
    node_pos = JSONProperty(default=[0, 0])
    
    # To support arrot2arrow arrow2node conns we blended Arrow with Node.
    is_arrow = BooleanProperty(default=False)
    
    QUANTIFIERS = {0: 'forall', 1: 'exists', 2: 'bound',}
    quantifier = BooleanProperty(choices=QUANTIFIERS, default=0)
    
    # This is treated as a ZeroOrMore for Arrows.
    arrows_out = RelationshipTo('ArrowNode', 'ARROWS_TO', cardinality=ZeroOrMore,
                            model=Arrow)
    
    def from_quiver_format(self, fmt, index):
        self.sketch_index = index        
        pure_style = [fmt[0], fmt[1]]        
        self.pure_styling_info = pure_style
        
        if len(fmt) > 2:
            self.text = fmt[2]
            
        if len(fmt) > 3:
            self.color = fmt[3]
        
        self.save()
        
    def to_quiver_format(self):
        pure_style = self.pure_styling_info        
        return [pure_style[0], pure_style[1], self.text, self.color]
    
                
class Prop(StructuredNode):
    # Inherits text already    
    uid = UniqueIdProperty()
    
    maintainer = StringProperty(max_length=MAX_USERNAME_LENGTH)
    creation_datetime = DateTimeProperty(default_now=True)
    datetime_edited = DateTimeProperty(default_now=True)
    
    left_grouping = RelationshipTo('Prop', 'GROUPS', cardinality=ZeroOrOne)
    # Right-associative =>:
    right_assoc_implies = RelationshipTo('Prop', 'IMPLIES', cardinality=ZeroOrOne)
    
    logic_negated = BooleanProperty(default=False)

    diagram_commutes = BooleanProperty(default=False)
    equivalents = RelationshipTo('Prop', 'EQUIV', cardinality=ZeroOrMore)
    
    def from_quiver_format(self, fmt):
        objects = []
        vertices = fmt[2:2 + fmt[1]]
        
        for k,v in enumerate(vertices):
            o = ObjectArrow(sketch_index=k)
            o.from_quiver_format(v, k)
            o.save()            
            objects.append(o)
        
        arrows = fmt[2 + fmt[1]:]
            
        for k,e in enumerate(arrows):
            if k < len(objects):
                A = objects[e[0]]
                B = objects[e[1]]
            else:
                
                F = ObjectArrow(sketch_index=k)
                F.is_arrow = True
                F.save()
                
                f = A.arrows_out.connect(F)
                F.domain.connect(A)
                f.from_quiver_format(e)
                A.save()
                
                f.save()
                F.codomain.connect(B)
                F.save()
                
                
        self.add_objects(objects)               
    
    def to_quiver_format(self):
        edges = []
        vertices = []
        
        objects = self.objects()
        objects.sort(key=lambda x: x.sketch_index)        
        
        for o in objects:
            vertices.append(o.to_quiver_format())
            for f in o.arrows_out.all():
                edges.append(f.arrow_to_quiver_format())
                    
        fmt = [0, len(vertices)]
        fmt += vertices
        fmt += edges
        
        return fmt        
        
    def left(self):
        return self.prop_grouping.get()
    
    def right(self):
        return self.implies_prop.get()
    
    def objects(self):
        query = f'''
        MATCH (X:ObjectArrow)
        WHERE X.prop_uid={self.uid}
        RETURN X
        '''        
        results = db.cypher_query(query)        
        results = [ObjectArrow.inflate(row[0]) for row in results]
        return results
    
    