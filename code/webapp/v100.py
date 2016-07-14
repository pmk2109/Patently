VERSION_STR = 'v1.0.0'

import sys
import requests
import numpy as np
from error import Error
from flask import Blueprint, request, jsonify

sys.path.append('../')

# run build model on a weekly basis so that patents can be stored
# in a compressed format (this part is the time consuming part)
# After this, run use_model to unload pickles/msgpacks and run
# scoring function to return the appropriate object.

import use_model

df, abstracts_tfidf, tfidf = use_model.unpickle()
# user_text -- how to generate/store this?
 #-- think about how this may be implemented (NOT NECESSARY AT THE MOMENT)



blueprint = Blueprint(VERSION_STR, __name__)
@blueprint.route('/return_patent_similarity', methods=['GET'])
def return_patent_similarity():
    '''
    Use this endpoint to give you a list of patents similar to the user generated text.
    ---
    tags:
     - v1.0.0

    responses:
     200:
       description: Returns a dictionary with 1 key (response) with a corresponding value as a list of dictionaries all containing keys (document number, date issued, title, abstract, description, claims, scores) and values corresponding
     default:
       description: Unexpected error
       schema:
         $ref: '#/definitions/Error'

    parameters:
     - name: q
       in: query
       description: User generated text
       required: true
       type: string

    consumes:
     - multipart/form-data
     - application/x-www-form-urlencoded
    '''

    user_text = [request.args['q']]
    num_results = 5

    results = use_model.assemble_results(user_text, num_results, tfidf,
                                     abstracts_tfidf, df)

    '''
    EXAMPLE RESULTS:
    d = {'results' : [  {'doc_number': '123456',
                    'date' : '20160713',
                    'title' : 'toilet seat light',
                    'abstract' : 'a paragraph of text will go here',
                    'description' : 'many paragraphs of text will go here',
                    'claims' : 'a couple paragraphs of text will go here',
                    'scores' : [decimal point number]
                    },
                    {'doc_number': '123457',
                    'date' : '20160714',
                    'title' : 'toilet seat cushion',
                    'abstract' : 'a paragraph of text will go here',
                    'description' : 'many paragraphs of text will go here',
                    'claims' : 'a couple paragraphs of text will go here'
                    'scores' : [decimal point number]
                    },
                    {'doc_number': '123458',
                    'date' : '20160715',
                    'title' : 'under seat light',
                    'abstract' : 'a paragraph of text will go here',
                    'description' : 'many paragraphs of text will go here',
                    'claims' : 'a couple paragraphs of text will go here'
                    'scores' : [decimal point number]
                    },
                    {'doc_number': '123459',
                    'date' : '20160716',
                    'title' : 'toilet light',
                    'abstract' : 'a paragraph of text will go here',
                    'description' : 'many paragraphs of text will go here',
                    'claims' : 'a couple paragraphs of text will go here'
                    'scores' : [decimal point number]
                    },
                    { 'doc_number': '123460',
                    'date' : '20160717',
                    'title' : 'under sink light',
                    'abstract' : 'a paragraph of text will go here',
                    'description' : 'many paragraphs of text will go here',
                    'claims' : 'a couple paragraphs of text will go here'
                    'scores' : [decimal point number]
                    }
                ]
        }
        '''

    d = {'results' : results}

    return jsonify(d)




from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
