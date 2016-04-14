"""
This module contains handlers that are called by taskqueue and/orcronjobs.
"""
import logging

import webapp2
from google.appengine.api import mail, app_identity

from services import users


class NotifyUserOfTurn(webapp2.RequestHandler):
    def post(self):
        """Send an email to a user to notify them of their turn"""
        app_id = app_identity.get_application_id()
        user = users.get_by_name(self.request.get('user'))
        
        if user:
            if user.email:
                subject = 'This is a reminder!'
                body = 'Hello {}, thanks for playing Memory - it is now your turn!'.format(user.name)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.format(app_id),
                           user.email,
                           subject,
                           body)
        else: #lets not throw an exception, just log the error
            logging.debug("Unable to find user {0}".format(self.request.get('user')))
        

app = webapp2.WSGIApplication([
    ('/notify_user_of_turn', NotifyUserOfTurn),
], debug=True)

