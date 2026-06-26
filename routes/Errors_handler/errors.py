from flask import render_template

def register_error_handlers(app):
    def render_error(error):
        
        code = getattr(error, 'code', 500)
        
      
        messages = {
            400: "The server couldn't understand that request. Check your form data.",
            401: "You need to be logged in to access this page.",
            403: "Access Denied. You don't have permission to see this.",
            404: "We looked everywhere, but we couldn't find that page.",
            405: "That action (Method) isn't allowed here.",
            429: "Whoa there! You're sending requests too fast. Slow down.",
            500: "Our server is having a bit of a crisis. We're on it!",
            503: "The site is currently overbooked. Please try again in a moment."
        }
        
        message = messages.get(code, "An unexpected error occurred.")
        return render_template('errors/master_error.html', 
                               code=code, 
                               message=message), code

    # Register the same function for all codes
    for code in [400, 401, 403, 404, 405, 429, 500, 503]:
        app.errorhandler(code)(render_error)