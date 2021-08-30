from django_filters import rest_framework as filters


class ScrappingTargetFilterSet(filters.FilterSet):
    domain = filters.CharFilter(lookup_expr="contains", field_name="url")
