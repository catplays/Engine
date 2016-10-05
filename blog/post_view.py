# encoding=utf-8
import cgi

from flask import abort, render_template, request, session
from flask import redirect
from flask import url_for

from blog import post
from blog import pagination
from blog import app

postClass = post.Post(app.config)


@app.template_filter('formatdate')
def format_datetime_filter(input_value, format_="%a, %d %b %Y"):
    return input_value.strftime(format_)


@app.route('/', defaults={'page': 1})
@app.route('/page/<int:page>')
def index(page):
    skip = int(app.config['PAGE_SIZE']) * (page - 1)
    posts = postClass.get_posts(int(app.config['PAGE_SIZE']), skip)
    count = postClass.get_total_count()
    pag = pagination.Pagination(page, int(app.config['PAGE_SIZE']), count)
    return render_template('index.html', posts=posts['data'], pager=pag)


@app.route('/tag/<tag>', defaults={'page': 1})
@app.route('/tag/<tag>/<int:page>')
def posts_by_tag(tag, page):
    skip = int(app.config['PAGE_SIZE']) * (page - 1)
    posts = postClass.get_posts(int(app.config['PAGE_SIZE']), skip, tag=tag)
    count = postClass.get_total_count(tag=tag)
    pag = pagination.Pagination(page, int(app.config['PAGE_SIZE']), count)
    if not post['data']:
        abort(404)
    return render_template('index.html', posts=posts['data'], pager=pag)


@app.route('/post/<id>')
def show_post(id):
    post = postClass.get_post_by_id(id)
    if not post['data']:
        abort(404)
    return render_template('one_post.html', post=post['data'])


@app.route('/new_post', methods=['POST', 'GET'])
def new_post():
    error = False
    error_msg = 'form is not fill out completely!'
    if request.method == 'POST':
        title = request.form.get('title', None)
        preview = request.form.get('short-text', None)
        body = request.form.get('full-text', None)

        if not title or not preview or not body:
            error = True
        else:
            tags = cgi.escape(request.form.get('tags'))
            tag_array = extract_tags(tags)

            post_data = {
                'title': title,
                'preview': preview,
                'body': body,
                'author': session['user'],
                'tags': tag_array
            }
            post-id = request.form.get('post-id')
            if post-id:
                post = postClass.update_post(post_data,post-id)
            else:
                post = postClass.add_new_post(post_data)
            if post['error']:
                error = True
                error_msg = post['error']
            else:
                return redirect(url_for('show_post', id=post['data']))

    return render_template('new_post.html', error=error,error_msg=error_msg)


@app.route('/edit_post', methods='GET')
def edit_post():
    return render_template('edit_post.html')


@app.route('/s/<query>', defaults={'page': 1})
@app.route('/s/<query>/<int:page>')
def search(query, page):
    pass


def extract_tags(tags):
    whitespace = re.compile('\s')
    nowhite = whitespace.sub("", tags)
    tags_array = nowhite.split(',')

    cleaned = []
    for tag in tags_array:
        if tag not in cleaned and tag != "":
            cleaned.append(tag)

    return cleaned
'''
# 错误处理器 关联abort函数，当错误发生时，错误被当做参数传进来
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

'''