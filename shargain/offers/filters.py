from django_filters import rest_framework as filters


class ScrappingTargetFilterSet(filters.FilterSet):
    domain = filters.CharFilter(lookup_expr="icontains", field_name="scrapingurl__url")
    include_inactive_urls = filters.BooleanFilter(method="filter_include_inactive_urls")

    @staticmethod
    def filter_include_inactive_urls(queryset, name, value):
        if not value:
            queryset = queryset.prefetch_related("scrapingurl_set").filter(scrapingurl__is_active=True)
        return queryset
