from djangoldp.serializers import LDPSerializer
from djangoldp.views import LDPViewSet

from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from ..models import Booklet, BookletContributor
from ..permissions import BookletPermissions

def get_booklet_user_pk(user, pk):
    qs = qs_booklet_user(user)
    return get_object_or_404(qs, pk=pk)

def qs_booklet_user(user):
    if user.is_anonymous:
        return Booklet.objects.filter(accessibility_public=True)

    return Booklet.objects.filter(Q(contributors__user=user)
                                  | Q(accessibility_public=True)
                                  | (Q(collaboration_allowed=True) & Q(annotations__creator=user))
                                  ).distinct()

class BookletSerializer(LDPSerializer):
    def validate(self, attrs):
        # Bypass custom validation for creation
        if self.instance is None:
            return attrs

        currrent_user = self.context['request'].user
        try:
            booklet_contributor = self.instance.contributors.filter(user=currrent_user).get()
        except:
            booklet_contributor = None

        if 'annotations' in attrs and len(attrs) == 1:
            old_annotations = self.instance.annotations.all()
            old_annotations_ids = list(map(lambda annotation: annotation.pk, old_annotations))
            new_annotations = attrs['annotations']
            new_annotations_id = list(map(lambda annotation: int(annotation['pk']), new_annotations))
            for old_annotation in old_annotations:
                if booklet_contributor is None or booklet_contributor.role == BookletContributor.ROLE_VISIT or booklet_contributor.role == BookletContributor.ROLE_CONTRIBUTOR:
                    if old_annotation.pk not in new_annotations_id and old_annotation.creator != currrent_user:
                        raise ValidationError('Cannot remove annotation not creator')

            for new_annotation_id in new_annotations_id:
                if new_annotation_id not in old_annotations_ids:
                    if self.instance.collaboration_allowed == False and (booklet_contributor is None or booklet_contributor.role == BookletContributor.ROLE_VISIT):
                        raise ValidationError('Cannot add annotation to not collaboration booklet when contributor')
        else:
            if booklet_contributor is None or not booklet_contributor.role in [BookletContributor.ROLE_ADMIN, BookletContributor.ROLE_OWNER]:
                raise ValidationError('Edition of other fields than only annotation reserved for admins')

        return attrs

    @property
    def with_cache(self):
        return False


class BookletViewset(LDPViewSet):
    serializer_class = BookletSerializer
    permission_classes = [BookletPermissions]
    fields = [
        '@id',
        'annotations',
        'title',
        'abstract',
        'accessibility_public',
        'collaboration_allowed',
        'tags',
        'cover'
    ]

    def perform_create(self, serializer, **kwargs):
        booklet = super().perform_create(serializer, **kwargs)
        contributor = BookletContributor(
            user=self.request.user,
            role=BookletContributor.ROLE_OWNER,
            booklet=booklet
        )
        contributor.save()

        return booklet

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)

        if response.status_code == 200:
            booklet = Booklet.objects.get(pk=kwargs['pk'])
            # User added annotation and is not contributor, adding it
            if booklet.collaboration_allowed == True and BookletContributor.objects.filter(booklet=booklet, user=request.user).count() == 0:
                contributor = BookletContributor(booklet=booklet, user=request.user, role=BookletContributor.ROLE_VISIT)
                contributor.save()

        return response

    def get_queryset(self, *args, **kwargs):
        return qs_booklet_user(self.request.user)


    def get_object(self):
        obj = get_booklet_user_pk(self.request.user, pk=self.kwargs['pk'])

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
