# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.utils.translation import ugettext as _
import json
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ValidationError

def get_field_verbose_name(object, field):
    try:
        return object.__class__._meta.get_field(fields[0]).verbose_name
    except:
        return field

def build_field_verbose_names(object, fields):
    if len(fields)==1:
        return get_field_verbose_name(object, fields[0])
    else:
        verbose_names = [get_field_verbose_name(object, x) for x in fields]
        return _(u'{0} and {1}').format(u','.join(verbose_names[:-1], verbose_names[-1]))


def build_object_perm(object):
    #Check the user can change this type of object
    ct=ContentType.objects.get_for_model(object.__class__)
    try:
        model_name = object.__class__._meta.verbose_name
    except:
        model_name = ct.model
    return '{ct.app_label}.change_{ct.model}'.format(ct=ct)

def process_object_edition(request, object, object_validator=None, perm=None):
    """
    This function must be called from a view
    It handles the object edition made with aloah javascript editor
    If the request is an ajax post, the calling view should return the result of this function
    If not, the calling view is in charge of returning the appropriate response
    """
    if request.method == 'POST' and request.is_ajax():
        old_values = {}
        try:
            for (field, value) in request.POST.items():
                if hasattr(object, field):
                    old_values[field] = getattr(object, field)
                    setattr(object, field, value)
            
            if perm==None:    
                perm = build_object_perm(object) 
            
            if perm and not request.user.has_perm(perm):
                raise PermissionDenied
            
            if old_values: #It means that the object has been modified
                #if callback is provided : call it to check the object is Ok before saving
                if object_validator: 
                    object_validator(object) #should raise ValidationError if something wrong
                    
                #Validate
                object.full_clean()
            
                #Save the object
                object.save()
                
                response = {'status': 'success', 'message': _(u'Updated successfully')}
            else:
                response = {'status': 'warning', 'message': _('Warning: It seems that nothing has been changed')}
        
        except PermissionDenied:
            response = {'status': 'error', 'message': _("You are not allowed to change this object")}
        except ValidationError, ex:
            response = {'status': 'error', 'message': u' - '.join(ex.messages)}
        except Exception, msg:
            response = {'status': 'error', 'message': _("An error occured")}
        
        if response["status"] != 'success':
            response["old_values"] = old_values
        
        #return the result as json object
        return HttpResponse(json.dumps(response), mimetype='application/json')

    #if not an ajax POST: don't return anything and let the calling view make the job
    return None

