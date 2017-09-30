from django.db import models
from django.contrib.postgres.fields import JSONField

class NodeType(models.Model):
    # eg. "Claim", "Evidence", "Refutation" etc
    name = models.TextField()
    # How much this nodes credibility impacts its parents credibility
    credibility_factor = models.IntegerField(default=1)

    # Whether this node impacts the credibility of its parents owner.
    # Set to false when circumstances prone to change should affect node
    # credibility, but not its owner (such as citations being added not
    # penalising the author of a citation needed node, etc)
    affects_parent_owner_cred = models.BooleanField(default=True)

class NodeSubType(models.Model):
    super_type = models.ForeignKey(NodeType)
    name = models.TextField()
    explanation = models.TextField()
    template = JSONField()

class DiscussionNode(models.Model):
    parent = models.ForeignKey('self', null=True)
    node_subtype = models.ForeignKey(NodeSubType)
    title = models.TextField()
    body = models.TextField()

    # Accessor only.
    @property
    def node_type(self):
        return self.node_subtype.super_type

# Signifies which nodes can have which children
class NodeTypeConnectivity(models.Model):
    parent = models.ForeignKey(NodeType, related_name='+')
    child = models.ForeignKey(NodeType, related_name='+')
