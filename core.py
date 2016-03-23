'''
Created on 18/03/2016

Encapsulation module used for interacting with the google app engine ndb.model classes

@author: thurstonemerson
'''
import logging
from google.appengine.ext import ndb
import endpoints

class Service(object):
    """A :class:`Service` instance encapsulates common ndb.Model 
    operations in the context of a Google app engine application.
    Adapted from SQLAlchemy/Flask service module found in 
    https://github.com/mattupstate/overholt
    """
    __model__ = None

    def _isinstance(self, model, raise_error=True):
        """Checks if the specified model instance matches the service's model.
        By default this method will raise a `ValueError` if the model is not the
        expected type.
        :param model: the model instance to check
        :param raise_error: flag to raise an error on a mismatch
        """
        rv = isinstance(model, self.__model__)
        if not rv and raise_error:
            raise ValueError('%s is not of type %s' % (model, self.__model__))
        return rv
    
    def get_by_urlsafe(self, urlsafe):
        """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind.
        :param urlsafe: A urlsafe key string
        """
        try:
            key = ndb.Key(urlsafe=urlsafe)
        except TypeError:
            raise endpoints.BadRequestException('Invalid Key')
        except Exception, e:
            if e.__class__.__name__ == 'ProtocolBufferDecodeError':
                raise endpoints.BadRequestException('Invalid Key')
            else:
                raise
        

        model = key.get()
        if not model:
            return None
        
        self._isinstance(model)
        
        return model
    
    def get_by_name(self, model_name):
        """Returns an instance of the service's model with the specified model name.
        Returns `None` if an instance with the specified model name does not exist.
        :param model_name: the name of the model to find
        """
        return self.__model__.query(self.__model__.name == model_name).get()

    def save(self, model):
        """Commits the model to the database and returns the model
        :param model: the model to save
        """
        self._isinstance(model)
        model.put()
        return model
    
    def new(self, request=None):
        """Returns a new, unsaved instance of the service's model class. Initialise
        the instance with the instance parameters if any are specified.
        :param request: instance parameters
        """
        if request is None:
            return self.__model__()
        
        data = {field.name: getattr(request, field.name) for field in request.all_fields()}
        logging.info("data is {0}".format(data))
    
        return self.__model__(**data)
    
    def create(self, request):
        """Returns a new, saved instance of the service's model class.
        :param **kwargs: instance parameters
        """
    
        return self.save(self.new(request))
    
    def update(self, model, **kwargs):
        """Returns an updated instance of the service's model class.
        :param model: the model to update
        :param **kwargs: update parameters
        """
        self._isinstance(model)
        for k, v in kwargs.items():
            setattr(model, k, v)
        self.save(model)
        return model

    
