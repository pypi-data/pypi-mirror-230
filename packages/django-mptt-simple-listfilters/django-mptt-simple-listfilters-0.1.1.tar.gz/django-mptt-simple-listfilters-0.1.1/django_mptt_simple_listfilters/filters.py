import re
from mptt.admin import TreeRelatedFieldListFilter


class ListFilterIgnoreLeafNodes(TreeRelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        results = []
        nodes = super().field_choices(field, request, model_admin)
        if not nodes:
            return []
        this_value = int(re.findall("(\d+)", nodes[0][2])[0])
        for index in range(len(nodes) - 1):
            this_node = nodes[index]
            next_node = nodes[index + 1]
            next_value = int(re.findall("(\d+)", next_node[2])[0])
            if this_value < next_value:
                results.append(this_node)
            this_value = next_value
        return results

class ListFilterLimitDepth(TreeRelatedFieldListFilter):
    max_depth = 1
    def field_choices(self, field, request, model_admin):
        results = []
        mptt_level_indent = getattr(model_admin, 'mptt_level_indent', self.mptt_level_indent)
        max_indent = mptt_level_indent * (self.max_depth - 1)
        for node in super().field_choices(field, request, model_admin):
            this_indent = int(re.findall("(\d+)", node[2])[0])
            if this_indent <= max_indent:
                results.append(node)
        return results

class ListFilterLimitDepth2(ListFilterLimitDepth):
    max_depth = 2

class ListFilterLimitDepth3(ListFilterLimitDepth):
    max_depth = 3

class ListFilterLimitDepth4(ListFilterLimitDepth):
    max_depth = 4
