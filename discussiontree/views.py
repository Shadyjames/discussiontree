from discussiontree.models import NodeType, NodeSubType, DiscussionNode
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
import ujson as json

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

def claim_index(request):
    context = {}
    context['claims'] = DiscussionNode.objects.filter(node_subtype__super_type__name="Claim")
    return render(request, 'claim_index.html', context)

def view_node(request, node_id):
    context = {"node": DiscussionNode.objects.get(pk=int(node_id))}
    return render(request, 'view_node.html', context)

def create_node(request):
    if request.method == "GET":
        context = {"parent": None}
        parent_id =  request.GET.get('parent')
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
        subtype_id = NodeSubType.objects.get(pk=int(request.POST['node_subtype']))
        create_kwargs['node_subtype'] = DiscussionNode.objects.create(pk=subtype_id)
        node = DiscussionNode.objects.create(**create_kwargs)
        return render(json.dumps({"success": True, "node_id":node.pk}))

def create_proposition(request):
    claim_type = NodeType.objects.get(name="Proposition")
    return HttpResponseRedirect(reverse(create_node) + "?node_type=%s" % claim_type.pk)

def create_question(request):
    claim_type = NodeType.objects.get(name="Question")
    return HttpResponseRedirect(reverse(create_node) + "?node_type=%s" % claim_type.pk)
