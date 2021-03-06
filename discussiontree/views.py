from discussiontree.models import NodeType, NodeSubType, DiscussionNode, NodeTypeConnectivity
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render
import ujson as json
import logging
logger = logging.getLogger('')

def dump_refutations(request):
    page = "<html>"
    for subtype in NodeSubType.objects.filter(super_type__name="Refutation").order_by('pk'):
        page += "Refutation type: %s<br/>" % subtype.name
        page += "Explanation: %s<br/>" % subtype.explanation
        page += "<br/>"
    page += "</html>"
    return HttpResponse(page)
        
def about(request):
    return render(request, 'about.html')

def index(request):
    return render(request, 'index.html')

def tree_index(request):
    context = {"user":request.user}
    #context['claims'] = DiscussionNode.objects.filter(node_subtype__super_type__name="Claim")
    context['roots'] = DiscussionNode.objects.filter(parent__isnull=True)
    return render(request, 'tree_index.html', context)

def view_node(request, node_id):
    node = DiscussionNode.objects.get(pk=int(node_id))
    child_connectivity = NodeTypeConnectivity.objects.filter(parent=node.node_type)
    child_types = [connectivity.child for connectivity in child_connectivity]
    node_children = DiscussionNode.objects.filter(parent=node)
    context = {
        "node": node,
        "child_types":child_types,
        "node_children":node_children,
        "user":request.user
    }
    return render(request, 'view_node.html', context)

def create_node(request):
    if request.method == "GET":
        context = {"parent": None, "user":request.user}
        parent_id =  request.GET.get('parent_id')
        if parent_id:
            context['parent'] = DiscussionNode.objects.get(pk=int(parent_id))

        node_type_id = request.GET.get('node_type')
        if not node_type_id:
            return HttpResponse(json.dumps({"success": False, "error": "The node_type field is compulsory"}))
        node_type = NodeType.objects.get(pk=int(node_type_id))
        context['node_type'] = node_type
        subtypes = NodeSubType.objects.filter(super_type=node_type)
        subtype_dict = {}

        for subtype in subtypes:
            subtype_dict[subtype.pk] = {
                "id": subtype.pk,
                "template": subtype.template,
                "name": subtype.name,
                "explanation": subtype.explanation
            }
        context['subtypes'] = json.dumps(subtype_dict)

        return render(request, 'create_node.html', context)
    elif request.method == "POST":
        create_kwargs = {}
        for field in ['title', 'body']:
            if field not in request.POST:
                return HttpResponse(json.dumps({"success":False, "error": "The %s field is compulsory" % field}))
            create_kwargs[field] = request.POST[field]
        subtype = NodeSubType.objects.get(pk=int(request.POST['node_subtype']))
        create_kwargs['node_subtype'] = subtype
        if request.POST.get('body'):
            create_kwargs['body'] = ' '.join(request.POST.getlist('body'))
        if request.POST.get('parent_id'):
            create_kwargs['parent_id'] = int(request.POST.get('parent_id'))
        node = DiscussionNode.objects.create(**create_kwargs)
        #return HttpResponse(json.dumps({"success": True, "node_id":node.pk}))
        return HttpResponseRedirect(reverse(view_node, args=(node.pk,)))

def create_proposition(request):
    claim_type = NodeType.objects.get(name="Proposition")
    return HttpResponseRedirect(reverse(create_node) + "?node_type=%s" % claim_type.pk)

def create_question(request):
    claim_type = NodeType.objects.get(name="Question")
    return HttpResponseRedirect(reverse(create_node) + "?node_type=%s" % claim_type.pk)

def create_user(request):
    context = {"user":request.user}
    if request.method == "GET":
        return render(request, 'create_user.html', context)
    elif request.method == "POST":
        username = request.POST.get('username')
        if not username:
            context['error'] = "You must supply a username"
            return render(request, 'create_user.html', context)
        if User.objects.filter(username=username).exists():
            context['error'] = "That username is taken"
            return render(request, 'create_user.html', context)
        user = User.objects.create(username=request.POST.get('username'))
        user.set_password('password')
        auth_login(request, user)
        context['user'] = user
    return render(request, 'user_created.html', context)

def login(request):
    context = {"user":request.user}
    if request.method == "GET":
        return render(request, 'login.html', context)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request=request, username=username, password=password)
        else:
            return HttpResponse(json.dumps({"success":False, "error": "Username and password are both required"}))

        if user is not None:
            auth_login(request, user)
            return HttpResponseRedirect(request.POST.get('redirect', '/'))

        return HttpResponse(json.dumps({"success":False, "error": "Invalid login"}))
