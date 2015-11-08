"""Implementation of a Pygments Lexer for the AADL language.

This implementation is derived from AADLLexer.py written by Sam
Procter for the MDCF project,
https://github.com/santoslab/aadl-translator
"""

import sys
import re

from pygments.lexer import RegexLexer, include, bygroups
from pygments.token import Error, Punctuation, Literal, Token, \
     Text, Comment, Operator, Keyword, Name, String, Number, Generic, \
     Whitespace

class AADLLexer(RegexLexer):
    """
    Pygments parser for AADL models. See <http://www.aadl.info> for
    more details.
    """

    name = 'AADL'
    aliases = ['aadl']
    filenames = ['*.aadl']
    mimetypes = ['text/x-aadl']

    flags = re.MULTILINE | re.DOTALL

    iden_rex = r'[a-zA-Z_][a-zA-Z0-9_\.]*'
    class_iden_rex = r'(' + iden_rex + r')(::)('+ iden_rex + r')'
    definition_rex = r'(' + iden_rex + r')' +  r'(\s*:\s*)\b'
    keyword_rex = r'(device|system|port|connection|process|thread|data|subprogram|processor)'

    with_tuple = (r'(with)(\s+)', bygroups(Keyword.Namespace, Whitespace), 'with-list')
    text_tuple = (r'[^\S\n]+', Text)
    terminator_tuple = (r'(;)(\s+)', bygroups(Punctuation, Whitespace), '#pop')
    comment_tuple = (r'--.*?$', Comment.Single)
    comment_whitespace_tuple = (r'(--.*?$)(\s+)', bygroups(Comment.Single, Whitespace))

    tokens = {
        'packageOrSystem': [
             text_tuple,
             (r'(implementation)(\s+)(' + iden_rex + r')', bygroups(Name.Class, Whitespace, Name.Class), '#pop'),
             (iden_rex, Name.Class, '#pop'),
         ],
        'annex': [
             text_tuple,
             (r'(\s*)({\*\*)(\s+)', bygroups(Whitespace, Punctuation, Whitespace)),
             (r'(\*\*})(\s*)(;)?(\s+)', bygroups(Punctuation, Whitespace, Punctuation, Whitespace), '#pop'),
             (iden_rex, Name.Class),
         ],
        'with-list' : [
            (r'\s*(,)\s*', Punctuation),
            (r'[a-zA-Z_]\w*', Name.Namespace),
            terminator_tuple,
        ],
        'package-declaration' : [
            text_tuple,
            (r'(implementation)', Keyword.Declaration),
            (r'(' + iden_rex + r')(;)', bygroups(Name.Class, Punctuation), '#pop'),
            (iden_rex, Name.Class, '#pop'),
            (r'(extends)', Keyword.Declaration),
            (r'(' + class_iden_rex + r')(;)', bygroups(Name.Class, Punctuation), '#pop'),
            (iden_rex, Name.Class, '#pop'),
        ],
        'declaration' : [
            text_tuple,
            (r'(in|out|event|data)', Keyword.Type),
            (r'(flow|path|port|thread|subprogram)', Keyword.Type),
            (class_iden_rex, bygroups(Name.Class, Punctuation, Name.Entity)),
            (r'(' + iden_rex + r')(\s+)(->|<-|<->)(\s+)('+ iden_rex + r')', bygroups(Name.Variable, Whitespace, Operator, Whitespace, Name.Variable)),
            (iden_rex, Name.Function),
            (r'({)(\s+)', bygroups(Punctuation, Whitespace), 'property-constant-declaration'),
            (r'}', Punctuation),
            terminator_tuple,
        ],
        'applies-to' : [
            text_tuple,
            (r'\(', Punctuation),
            (r'\s*(,)\s*', Punctuation),
            (r'\s*(\*\*)\s*', Operator),
            (keyword_rex, Keyword.Type),
            (r'(\{)(' + iden_rex + r')(\})', bygroups(Punctuation, Name.Class, Punctuation)),
            (r'\)', Punctuation, '#pop:2'),
        ],
        'property-value' : [
            (r'[0-9]+', Number.Integer),
            (r'[0-9]+\.[0-9]*', Number.Float),
            (r'(reference)(\()(' + iden_rex + ')(\))', bygroups(Keyword.Declaration, Punctuation, Name.Variable.Instance, Punctuation)),
            (r'"[^"]*"', Literal.String.Double),
            (r'(\s*)(ms)(\s*)', bygroups(Whitespace, Literal, Whitespace)),
            (r'(\s*)(\.\.)(\s+)', bygroups(Whitespace, Operator, Whitespace)),
            (class_iden_rex, bygroups(Name.Class, Punctuation, Name.Constant)),
            (iden_rex, Name.Constant),
        ],
        'applies-to-property-value' : [
            (r'(\s*)(applies)(\s+)(to)(\s+)', bygroups(Whitespace, Keyword, Whitespace), 'applies-to'),
            include('property-value'),
        ],
        'property-section-property-value' : [
        	include('property-value'),
        	terminator_tuple,
        ],
        'property-constant-value' : [
            include('property-value'),
            (r'(;)(\s+)', bygroups(Punctuation, Whitespace), '#pop:2')
        ],
        'aggregate-property-constant-list' : [
	        (r'(' + iden_rex + r')(\s*)(=>)(\s*)', bygroups(Name.Class, Whitespace, Operator, Whitespace)),
        	include('property-value'),
            (r'\s*;\s*', Punctuation),
            (r'(\];)(\s+)', bygroups(Punctuation, Whitespace), '#pop:2'),
            (r'(\])(\s+)(applies)(\s+)(to)(\s+)(' + iden_rex +')(;)(\s+)', bygroups(Punctuation, Whitespace, Keyword.Declaration, Whitespace, Keyword.Declaration, Whitespace, Name.Variable.Instance, Punctuation, Whitespace), '#pop'),
        ],
        'property-declaration' : [
            text_tuple,
            (r'(' + iden_rex + r')(\s*)(=>)(\s*)', bygroups(Name.Class, Whitespace, Operator, Whitespace), 'applies-to-property-value'),
            terminator_tuple,
        ],
        'property-constant-declaration' : [
            text_tuple,
            (class_iden_rex + r'(\s*)(=>)(\s*)(\[)(\s*)', bygroups(Name.Class, Punctuation, Name.Constant, Whitespace, Operator, Whitespace, Punctuation, Whitespace), 'aggregate-property-constant-list'),
            (r'(' + iden_rex + r')(\s*)(=>)(\s*)(\[)(\s*)', bygroups(Name.Class, Whitespace, Operator, Whitespace, Punctuation, Whitespace), 'aggregate-property-constant-list'),
            (class_iden_rex + r'(\s*)(=>)(\s*)', bygroups(Name.Class, Punctuation, Name.Constant, Whitespace, Operator, Whitespace), 'property-constant-value'),
            (r'(' + iden_rex + r')(\s*)(=>)(\s*)', bygroups(Name.Class, Whitespace, Operator, Whitespace), 'property-constant-value'),
        ],
        'property-set' : [
            with_tuple,
            (r'(' + iden_rex + r')(\s+)(is)(\s+)', bygroups(Name.Class, Whitespace, Keyword.Namespace, Whitespace)),
            (definition_rex + r'(constant)', bygroups(Name.Variable.Global, Punctuation, Keyword), 'property-constant-declaration'),
            (definition_rex, bygroups(Name.Variable.Global, Punctuation), 'property-declaration'),
            (r'(end)(\s+)(' + iden_rex + r')(;)', bygroups(Keyword.Namespace, Whitespace, Name.Class, Punctuation)),
        ],
        'property-section' : [
            text_tuple,
            comment_whitespace_tuple,
            (class_iden_rex + r'(\s*)(=>)(\s*)(\[)(\s*)', bygroups(Name.Class, Punctuation, Name.Constant, Whitespace, Operator, Whitespace, Punctuation, Whitespace), 'aggregate-property-constant-list'),
            (class_iden_rex + r'(\s*)(=>)(\()(\s*)', bygroups(Name.Class, Punctuation, Name.Class, Whitespace, Operator, Whitespace), 'property-section-property-value'),
            (r'(' + iden_rex + r')(\s*)(=>)(\s*)', bygroups(Name.Class, Whitespace, Operator, Whitespace), 'property-section-property-value'),
            (r'(\*\*})(\s*)(;)', bygroups(Punctuation, Whitespace, Punctuation), '#pop'),
            (r'', Generic.Error, '#pop'),
        ],
        'call-section' : [
            text_tuple,
            comment_whitespace_tuple,
            (r'(' + iden_rex + r')(\s*)(:)(\s*)({)(\s*)', bygroups(Name.Class, Whitespace, Punctuation, Whitespace, Punctuation, Whitespace)),
            (definition_rex, bygroups(Name.Variable, Punctuation), 'declaration'),
            (r'}', Punctuation),
            terminator_tuple,
        ],
        'root': [
            (r'(\n\s*|\t)', Whitespace),
            comment_tuple,
            (r'(package)(\s+)', bygroups(Keyword.Namespace, Text), 'packageOrSystem'),
            (r'(public|private)', Keyword.Namespace),
            with_tuple,
            (r'(annex)(\s+)',  bygroups(Keyword.Namespace, Text), 'annex'),
            (keyword_rex + r'(\s+)', bygroups(Keyword.Type, Text), 'package-declaration'),
            (r'(calls)(\s+)',bygroups(Keyword.Namespace, Text),'call-section'),
            (r'(subcomponents|connections|features|flows)(\s+)', bygroups(Keyword.Namespace, Whitespace)),
            (definition_rex, bygroups(Name.Variable, Punctuation), 'declaration'),
            (r'(properties)(\s*)', bygroups(Keyword.Namespace, Whitespace), 'property-section'),
            (r'(end)(\s+)', bygroups(Keyword.Namespace, Whitespace), 'package-declaration'),
            (r'(property set)(\s+)', bygroups(Keyword.Namespace, Whitespace), 'property-set'),
        ]
    }
