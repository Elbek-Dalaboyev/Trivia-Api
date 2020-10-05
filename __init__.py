from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from models import Question, Category, setup_db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # paginating questions
    def paginate_tests(request, selection):
        request = request.args.get('page', 1, type=int)
        start = (request - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        tests = [test.format() for test in selection]
        current_tests = tests[start:end]

        return current_tests

    # return categories using format()
    def current_category(categories):
        category = [category.format1() for category in categories]
        return category

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')

        return response

    # question list
    @app.route('/categories', methods=['GET'])
    def get_categories():
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        categories = Category.query.all()
        formatted_categories = {category.id: category.type for category in categories}
        return jsonify({
            'success': True,
            'categories': formatted_categories,
        })

    @app.route('/questions')
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * 10
            end = start + 10
            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]
            categories = Category.query.all()
            formatted_categories = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_questions': len(formatted_questions),
                'categories': formatted_categories,
                'current_category': None
            })
        except:
            abort(404)

    @app.route('/questions/<int:test_id>')
    def question_by_id(test_id):
        questions = Question.query.filter(Question.id == test_id).all()
        question = [question.format() for question in questions]
        return jsonify({
            'success': True,
            'questions': question
        })

    # delete function to delete from question list
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        try:
            # get the question by id
            question = Question.query.filter_by(id=id).one_or_none()
            if question == '' and question is None:
                abort(404)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': id
            })
        except:
            abort(422)

    # inserting new question
    @app.route('/questions', methods=['POST'])
    def add_new_question():
        data = request.get_json()

        question = data.get('question', '')
        answer = data.get('answer', '')
        difficulty = data.get('difficulty', '')
        category = data.get('category', '')

        if ((question == '') or (answer == '') or (difficulty == '') or (category == '')):
            abort(422)

        # return error if one of variables is empty
        try:
            question = Question(question=question, answer=answer, difficulty=difficulty, category=category)

            question.insert()

            return jsonify({
                'success': True,
                'message': 'Successfully Created'
            }), 201

        except:
            abort(422)

    # searching questions
    @app.route('/questions/search', methods=['POST'])
    def search_question():
        data = request.get_json()
        search_answer = data.get('searchTerm', '')
        if search_answer == '':
                abort(404)
        try:
            questions = Question.query.filter(Question.question.ilike(f'%{search_answer}%')).all()

            if len(questions) == 0:
                abort(404)
            paginate_test = paginate_tests(request, questions)
            categories = Category.query.all()
            formatted_categories = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'questions': paginate_test,
                'total_questions': len(questions),
                'current_category': formatted_categories
            })
        except:
            abort(404)

    # finding questions by their categories
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_by_category(category_id):

        try:
            questions = Question.query.filter(Question.category == str(category_id)).all()

            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:
            abort(404)

    # play quiz
    @app.route('/quiz', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            p_question = body['previous_questions']
            category_id = body["quiz_category"]["id"]
            category_type = body["quiz_category"]["type"]
            if category_id == 0 and category_type:
                questions = Question.query.all()
            elif p_question is not None:
                questions = Question.query.filter(Question.id.notin_(p_question), Question.category == category_id).all()
            else:
                questions = Question.query.all()
            next_question = random.choice(questions).format()
            if next_question is None:
                next_question = False
            return jsonify({
                'success': True,
                'question': next_question
            })
        except:
            abort(422)

    # error handlers
    @app.errorhandler
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400

    @app.errorhandler
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Request'
        }), 422

    @app.errorhandler
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Method Not Allowed'
        }), 500

    return app
