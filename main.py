#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        self.render("frontpage.html")


class NewPost(Handler):
    def render_front(self, title ="", body="", error=""):
        #blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("newpost.html", title = title, body = body, error = error)

    def get(self):
        self.render_front()
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            blog = Blog(title = title, body = body)
            blog.put()
            blog = blog.key().id()

            self.redirect('/blog/%s' % (blog))
        else:
            error = "We need both a title and some content!"
            self.render_front(title, body, error)

class Blogs(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("blog.html", blogs=blogs)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        #bid = Blog.key().id()
        #bid = self.request.get("blog")
        blog = Blog.get_by_id(int(id))
        #self.render("blog.html", bl = bl)
        t = jinja_env.get_template("permalink.html")
        response = t.render(blog = blog)
        self.response.write(response)
        if not blog:
             self.error(404)
             return
app = webapp2.WSGIApplication([('/', MainPage),('/newpost',NewPost),('/blog', Blogs),
                   webapp2.Route('/blog/<id:\d+>', ViewPostHandler)], debug = True)
