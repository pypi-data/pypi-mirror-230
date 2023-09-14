# Copyright (c) 2022-2023, Ora Lassila & So Many Aircraft
# All rights reserved.
#
# See LICENSE for licensing information
#

import string
import re
import urllib.parse
from rdflib import Literal, URIRef, BNode, Graph, RDF, Namespace

RR = Namespace("http://www.w3.org/ns/r2rml#")
RRE = Namespace("https://somanyaircraft.com/data/schemata/tinyrml/1/core#")

FALSE = Literal(False)

class URITemplateFormatter(string.Formatter):
    def get_value(self, key, args, kwargs):
        return urllib.parse.quote(super().get_value(key, args, kwargs))

def one(content):
    values, stuff = content
    if len(values) == 1:
        return values[0], stuff
    else:
        raise ValueError("Exactly one value required")

class Node:
    def __init__(self, node, mapper):
        self.node = node
        self.mapper = mapper

    def values(self, predicate):
        # The return value gets reused, so make sure it is not a generator
        return list(self.mapper.graph.objects(self.node, predicate))

    def value(self, predicate, default=None, interpret_literals=True):
        v = next(self.mapper.graph.objects(self.node, predicate), default)
        return str(v) if v and interpret_literals and isinstance(v, Literal) else v

class Template:
    def __init__(self, template_string, ignore_field_keys=None, empty_string_is_none=True):
        self.template_string = template_string
        self.empty_string_is_none = empty_string_is_none
        self.fields = [f for _, f, _, _ in self.uri_formatter.parse(template_string)]
        self.candidate_field = None
        for f in self.fields:
            if f not in ignore_field_keys or {}:
                self.candidate_field = f
                break
        if self.candidate_field is None:
            self.candidate_field = self.fields[0]

    uri_formatter = URITemplateFormatter()
    literal_formatter = string.Formatter()

    splitter = re.compile("[,;]+")

    def expand(self, data, term_type, role, expand_as_list=False):
        value = data[self.candidate_field]
        if value is None or (self.empty_string_is_none and value == ""):
            # If there is no value (None or potentially an empty string), we return None, except if
            # we are expanding for a subject map: in that case we must return a blank node, or there
            # would be no subject at all...
            return BNode() if role == RR.subjectMap else None
        elif isinstance(value, list):
            results = list()
            data2 = dict(data)
            for v in value:
                data2[self.candidate_field] = v
                results.append(self.expand(data2, term_type, role))
            return results
        elif expand_as_list:
            data2 = dict(data)
            data2[self.candidate_field] = [v.strip() for v in self.splitter.split(value)]
            return self.expand(data2, term_type, role, expand_as_list=False)
        else:
            formatter = self.uri_formatter if term_type == RR.IRI else self.literal_formatter
            return formatter.format(self.template_string, **data)

class TermMap(Node):
    def __init__(self, node, mapper, role, constant=None):
        super().__init__(node, mapper)
        self.role = role
        self.column = None
        self.template = None
        self.expression = None
        self.globals = mapper.globals
        self.term_type = RR.Literal
        self.datatype = None
        self.language = None
        if constant is None:
            constant = self.value(RR.constant, interpret_literals=False)
        if constant:
            self.constant = constant
        else:
            self.constant = None
            self.column = self.value(RR.column)
            if self.column is None:
                template_string = self.value(RR.template)
                if template_string:
                    self.template = Template(template_string,
                                             ignore_field_keys=mapper.ignore_field_keys,
                                             empty_string_is_none=mapper.empty_string_is_none)
                    self.expand_as_list = \
                        self.value(RRE.expandAsList, default=FALSE, interpret_literals=False).value
                else:
                    expression = self.value(RRE.expression)
                    if expression:
                        if mapper.allow_expressions:
                            self.expression = compile(expression, mapper.source_file, mode="eval")
                        else:
                            raise ValueError("No rre:expression allowed")
                    else:
                        raise ValueError("Specify rr:column, rr:template, or rre:expression")
        if self.node:
            self.classes = self.values(RR["class"])
            self.term_type = self.determineTermType()
            self.language = self.value(RR.language)
            self.datatype = self.value(RR.datatype)

    def determineTermType(self):
        term_type = self.value(RR.termType)
        if term_type is None:
            if self.role == RR.objectMap:
                term_type = RR.Literal if self.column or self.language or self.datatype else RR.IRI
            else:
                term_type = RR.IRI
        return term_type

    def process(self, data):
        if self.constant:
            terms = [self.constant]
        elif self.column:
            terms = self.termContent2term(data[self.column])
        elif self.template:
            terms = self.termContent2term(self.template.expand(data, self.term_type, self.role,
                                                               self.expand_as_list))
        elif self.expression:
            terms = self.termContent2term(eval(self.expression, self.globals, data))
        else:
            terms = [BNode()]
        if self.role == RR.subjectMap:
            type_statements = list()
            for term in terms:
                type_statements += [(term, RDF.type, c) for c in self.classes]
        else:
            type_statements = []
        return terms, type_statements

    def termContent2term(self, content):
        if content is None:
            return []
        elif isinstance(content, list):
            terms = list()
            for v in content:
                terms += self.termContent2term(v)
            return terms
        elif self.term_type == RR.IRI:
            return [content] if isinstance(content, BNode) else [URIRef(content)]
        elif self.term_type == RR.Literal:
            return [Literal(content, datatype=self.datatype, lang=self.language)]
        else:
            raise ValueError("Cannot use rr:template when creating an rr:BlankNode")

class PredicateObjectMap(Node):
    def __init__(self, node, mapper):
        super().__init__(node, mapper)
        pred = self.value(RR.predicate)
        if pred:
            self.predicate_map = TermMap(None, mapper, constant=pred, role=RR.predicateMap)
        else:
            self.predicate_map = TermMap(self.value(RR.predicateMap), mapper, role=RR.predicateMap)
        obj = self.value(RR.object, interpret_literals=False)
        if obj:
            self.object_map = TermMap(None, mapper, constant=obj, role=RR.objectMap)
        else:
            self.object_map = TermMap(self.value(RR.objectMap), mapper, role=RR.objectMap)

    def process(self, subject, data):
        pred, type_statements1 = one(self.predicate_map.process(data))
        objs, type_statements2 = self.object_map.process(data)
        return [(subject, pred, obj) for obj in objs] + type_statements1 + type_statements2

class TriplesMap(Node):
    def __init__(self, node, mapper):
        super().__init__(node, mapper)
        self.subject_map = TermMap(self.value(RR.subjectMap), mapper, RR.subjectMap)
        self.predicate_object_maps = [PredicateObjectMap(pom, mapper)
                                      for pom in self.values(RR.predicateObjectMap)]

    def process(self, rows, result_graph=None):
        if result_graph is None:
            result_graph = Graph()
        for data in rows:
            subject, type_statements = one(self.subject_map.process(data))
            result_graph += type_statements
            for pom in self.predicate_object_maps:
                result_graph += pom.process(subject, data)
        return result_graph

class Mapper:
    def __init__(self, mapping,
                 triples_map_uri=None, ignore_field_keys=None, empty_string_is_none=True,
                 allow_expressions=True, global_bindings=None):
        if global_bindings is None:
            global_bindings = dict()
        if isinstance(mapping, Graph):
            graph = mapping
            self.source_file = "<unknown>"
        else:
            graph = Graph()
            self.source_file = mapping
            graph.parse(mapping)
        if triples_map_uri is None:
            for u in graph.subjects(RDF.type, RR.TriplesMap):
                triples_map_uri = u
                break
            if triples_map_uri is None:
                raise ValueError("No rr:TriplesMap found")
        self.graph = graph
        self.ignore_field_keys = ignore_field_keys or {}
        self.empty_string_is_none = empty_string_is_none
        self.allow_expressions = allow_expressions
        self.globals = (global_bindings
                        if global_bindings.get("__builtins__", None)
                        else {"__builtins__": __builtins__, **global_bindings})
        self.triples_map = TriplesMap(triples_map_uri, self)

    def query(self, database, filter_expr=None, result_graph=None):
        rows = database.query(filter_expr=filter_expr)
        return self.process(rows, result_graph=result_graph)

    def process(self, rows, result_graph=None):
        return self.triples_map.process(rows, result_graph=result_graph)
