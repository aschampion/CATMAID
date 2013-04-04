import json

from django.http import HttpResponse

from catmaid.models import *
from catmaid.control.authentication import *
from catmaid.control.common import *


@requires_user_role(UserRole.Annotate)
def list_notifications(request, project_id = None):
    # In the future there may be other kinds of notifications, but for now there are just change requests.
    requestType = request.POST.get('sSearch_1', '')
    if requestType == '0':
        change_requests = ChangeRequest.objects.filter(recipient = request.user, status = ChangeRequest.OPEN)
    elif requestType == '1':
        change_requests = ChangeRequest.objects.filter(recipient = request.user, status = ChangeRequest.APPROVED)
    elif requestType == '2':
        change_requests = ChangeRequest.objects.filter(recipient = request.user, status = ChangeRequest.REJECTED)
    elif requestType == '3':
        change_requests = ChangeRequest.objects.filter(recipient = request.user, status = ChangeRequest.INVALID)
    else:
        change_requests = ChangeRequest.objects.filter(recipient = request.user)
    
    # TODO: iDisplayStart = starting record #, iDisplayLength = # of records to return
    range_start = request.POST.get('iDisplayStart', '')
    if range_start == '':
        range_start = 0
    else:
        range_start = int(range_start)
    range_length = request.POST.get('iDisplayLength', '')
    if range_length == '' or int(range_length) < 0:
        range_end = len(change_requests)
    else:
        range_end = range_start + int(range_length)
    
    print >> sys.stderr, 'Range: ' + str(range_start) + ':' + str(range_end)
    
    change_request_list = [[cr.id, cr.type, cr.description, cr.status_name(), cr.location.x, cr.location.y, cr.location.z, 
                            (cr.treenode if cr.treenode else cr.connector).id, cr.treenode.skeleton.id if cr.treenode else 'null', 
                            cr.user.get_full_name(), cr.creation_time.strftime('%Y-%m-%d %I:%M %p')] for cr in change_requests[range_start:range_end]]
    
    return HttpResponse(json.dumps({'iTotalRecords': len(change_request_list), 'iTotalDisplayRecords': len(change_request_list), 'aaData': change_request_list}))


@requires_user_role(UserRole.Annotate)
def approve_change_request(request, project_id = None):
    change_request_id = int(request.POST.get('id', -1))
    
    if change_request_id == -1:
        raise Exception('Missing arguments to approve_change_request')
    
    # TODO: make sure request.user has permission to approve the request
    
    change_request = ChangeRequest.objects.get(pk = change_request_id)
    change_request.approve()
    
    return HttpResponse(json.dumps({'change_request_id': change_request_id}))


@requires_user_role(UserRole.Annotate)
def reject_change_request(request, project_id = None):
    change_request_id = int(request.POST.get('id', -1))
    
    if change_request_id == -1:
        raise Exception('Missing arguments to reject_change_request')
    
    # TODO: make sure request.user has permission to reject the request
    
    change_request = ChangeRequest.objects.get(pk = change_request_id)
    change_request.reject()
    
    return HttpResponse(json.dumps({'change_request_id': change_request_id}))
