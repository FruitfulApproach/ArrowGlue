from ArrowGlue.settings import MAX_DB_TEXT_LENGTH
# Create your models here.
from neomodel import *
from datetime import datetime
import base64
import json
from bidict import bidict

class AuthoredContent:
    uid = UniqueIdProperty()
    title = StringProperty(max_length=MAX_DB_TEXT_LENGTH)
    maintainer = StringProperty(max_length=MAX_DB_TEXT_LENGTH, default='ArrowGlue')
    creation_datetime = DateTimeProperty(default_now=True)
    datetime_edited = DateTimeProperty(default_now=True)

class CommonMixin:
    label = StringProperty(max_length=MAX_DB_TEXT_LENGTH, default='')
    label_subst_regex = StringProperty(max_length=2 * MAX_DB_TEXT_LENGTH)
    
    # For quiver editor:
    sketch_index = IntegerProperty(default=-1)
    sketch_id = StringProperty(default='')
    
    # H,S,L,A:
    color = JSONProperty(default=[0.0, 0.0, 0.0, 1.0])
    
    QUANTIFIERS = {0: 'forall', 1: 'exists', 2: 'bound',}
    quantifier = IntegerProperty(choices=QUANTIFIERS, default=0)


class Arrow(StructuredRel, CommonMixin):    
    sketch_src_index = IntegerProperty(default=-1)
    sketch_dst_index = IntegerProperty(default=-1)
    
    domain = RelationshipFrom('Node', 'ARROWS_TO', cardinality=ZeroOrOne)
    codomain = RelationshipTo('Node', 'ARROWS_TO', cardinality=ZeroOrOne)

    NUM_LINES = bidict({1: 'one', 2: 'two', 3: 'three', 4: 'four',})
    TAIL_STYLE = bidict({0:'none', 1:'mono', 2:'hook', 3:'arrowhead', 4:'CONNECTS_TO'})
    HEAD_STYLE = bidict({0:'none', 1:'arrowhead', 2:'epi', 3:'harpoon'})
    BODY_STYLE = bidict({0:'solid', 1:'none', 2:'dashed', 3:'dotted', 4:'squiggly', 5:'barred'})
    
    # Both mathematically significant and style fields:
    num_lines = IntegerProperty(choices=NUM_LINES, default=1)
    tail_style = IntegerProperty(choices=TAIL_STYLE, default=0)
    head_style = IntegerProperty(choices=HEAD_STYLE, default=1)
    body_style = IntegerProperty(choices=BODY_STYLE, default=0)
    
    ALIGNMENT = bidict({0: 'l', 1: 'ctr', 2: 'r', 3: 'ovr',})
    SIDE = bidict({0: 'no', 1: 't', 2: 'b',})    
    
    DEFAULT_PURE_STYLE = {
        'algmt' : 0,
        'lblpos' : 50,
        'lbloff': 0,
        'curve': 0,
        'tltrim': 0,
        'hdtrim': 0,
        'tailsd': 0,
        'headsd': 0,
    }
    # Style-only fields put into JSON property for Neo4j ultimate speed    
    pure_styling_info = JSONProperty(default=DEFAULT_PURE_STYLE)
        
    def from_quiver_format(self, fmt, index):
        self.sketch_src_index = fmt[0]
        self.sketch_dst_index = fmt[1]
        self.sketch_index = index
        
        if len(fmt) > 2:
            self.label = fmt[2]
        
        pure_style = self.DEFAULT_PURE_STYLE
        
        if len(fmt) > 3:
            pure_style['algmt'] = fmt[3]
            
        if len(fmt) <= 4:
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
                        self.head_style = self.BODY_STYLE.inv[body['name']]
                    
            if 'tail' in style:
                tail = style['tail']
                
                if 'name' in tail:
                    self.tail_style = self.TAIL_STYLE.inv[tail['name']]
                    
                if 'side' in tail:
                    pure_style['tailsd'] = self.SIDE.inv[tail['side']]
                    
            if 'head' in style:
                head = style['head']
                
                if 'name' in head:
                    self.head_style = self.HEAD_STYLE.inv[head['name']]
                
                if 'side' in head:
                    pure_style['headsd'] = self.SIDE.inv[head['side']]
            
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
        fmt.append(self.label if self.label is not None else '')
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

    
class Object(StructuredNode, CommonMixin):
    # Node-only:
    node_pos = JSONProperty(default=[0, 0])
    arrows_to = RelationshipTo('Object', 'ARROWS_TO', cardinality=ZeroOrMore, model=Arrow)
        
    def from_quiver_format(self, fmt, index):
        self.sketch_index = index        
        pos = [fmt[0], fmt[1]]        
        self.node_pos = pos
        
        if len(fmt) > 2:
            self.label = fmt[2]
            
        if len(fmt) > 3:
            self.color = fmt[3]
        
        self.save()
        
    def to_quiver_format(self):
        node_pos = self.node_pos
        return [node_pos[0], node_pos[1], self.label, self.color]
    



class RightAssocImplies(Arrow):
    def __init__(*args, **kwargs):
        if 'num_lines' not in kwargs:
            kwargs['num_lines'] = 2
        super().__init__(*args, **kwargs)

        
class Proposition(Object, AuthoredContent):
    logic_negated = BooleanProperty(default=False)

    @property
    def preview_base64(self):
        raise NotImplementedError
    
    @staticmethod
    def factory_inflate(node):
        if 'Sketch' in node.labels:
            return Sketch.inflate(node)
        else:
            return Definition.inflate(node)
        
        
class Proof(Object, AuthoredContent):
    pass

class Definition(Proposition):
    start_prop = RelationshipTo('Proposition', 'STARTS_WITH', cardinality=ZeroOrOne)
    
    @property
    def title(self):
        return self.label
    
    @title.setter
    def title(self, new_title: str):
        self.label = new_title
        
    @property
    def preview_base64(self):
        rightmost = self.right_most_prop()
        return rightmost.preview_base64()
    
    def right_most_prop(self):
        start = self.start_prop.single()
        
        if not start:
            return None
        
        query = f"""
        MATCH p=(P:Proposition)-[A:ARROWS_TO*]->(Q:Proposition)
        WHERE P.uid='{start.uid}'
        RETURN Q ORDER BY length(p) DESC LIMIT 1
        """
        result, _ = db.cypher_query(query, resolve_objects=True)

        if not result:
            return start
        
        prop = result[0][0]
        
        if isinstance(prop, Definition):
            return prop.right_most_prop()
        
        return prop
        

    
class Sketch(Proposition):
    in_category = StringProperty(max_length=MAX_DB_TEXT_LENGTH, default='')
    commutes = BooleanProperty(default=False)
    
    def delete_content(self):
        nodes = Object.nodes.filter(sketch_id=self.uid)        
    
        for node in nodes:
            node.delete()               
    
    def from_quiver_format(self, fmt):
        objects = []
        vertices = fmt[2:2 + fmt[1]]
        
        for k,v in enumerate(vertices):
            o = Object(sketch_index=k, sketch_id=self.uid)
            o.from_quiver_format(v, k)            
            objects.append(o)
        
        arrows = fmt[2 + fmt[1]:]
            
        #for k,e in enumerate(arrows):
            #F = sketch_id=self.uid, sketch_index=k + len(objects))
            #F.from_quiver_format(fmt=e, index=k +len(objects))
            #arrows[k] = (F, e)
            
        for k, e in enumerate(arrows):
            assert max(e[0], e[1]) < len(objects) #TODO add in support for
            # Other connection types
            A = objects[e[0]]
            B = objects[e[1]]
            f = A.arrows_to.connect(B, {'sketch_id': self.uid})
            f.from_quiver_format(fmt=e, index=k)
            
        self.datetime_edited = datetime.now()
        self.save()
    
    def to_quiver_format(self):
        edges = []
        vertices = []
        
        objects = self.objects()
        objects.sort(key=lambda x: x[0].sketch_index)        
        
        for o in objects:
            vertices.append(o[0].to_quiver_format())
            
            for cod in o[0].arrows_to:
                f = o[0].arrows_to.relationship(cod)
                fmt = f.to_quiver_format()
                edges.append(fmt)
                    
        fmt = [0, len(vertices)]
        fmt += vertices
        fmt += edges
        
        return fmt        
    
    def objects(self):
        query = f'''
        MATCH (X:Object)
        WHERE X.sketch_id='{self.uid}'
        RETURN X
        '''        
        results,_ = db.cypher_query(query, resolve_objects=True)
        return results

    @property
    def preview_base64(self):
        json_data = self.to_quiver_format()
        json_data = json.dumps(json_data)
        res = base64.b64encode(json_data.encode(encoding='ascii'))
        res = res.decode('ascii')
        return res
