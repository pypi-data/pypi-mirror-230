import time
from multiprocessing import Process
from django.db import transaction
from django import db
import sys
from django.contrib.postgres.search import SearchVector
import traceback


class RebuildWikiConfigs:
    def run(self):
        from torque import models

        config = models.WikiConfig.objects.filter(cache_dirty=True).first()
        if config:
            # We do this outside of the transaction, because if someone comes
            # along and dirties it again while we're rebuilding, we want to
            # rebuild it after we're done rebuilding it.
            config.cache_dirty = False
            config.save()

            print(
                "Populating unbuilt template caches for %s in %s"
                % (config.group, config.wiki.wiki_key)
            )
            for view_template in models.Template.objects.filter(
                type="View", wiki=config.wiki
            ):
                config.populate_template_cache(view_template)

            for search_template in models.Template.objects.filter(
                type="Search", wiki=config.wiki
            ):
                config.populate_template_cache(search_template, True)

            print(
                "Rebuilding search index for %s: %s"
                % (config.wiki.wiki_key, config.group)
            )
            with transaction.atomic():
                config.rebuild_search_index()

            return True


class PropagateTemplateDirty:
    """When a template gets dirty, we need to update all the caches that depend on it"""

    def run(self):
        from torque import models

        for template in models.Template.objects.filter(dirty=True).all():
            template.dirty = False
            template.save()

            models.TemplateCacheDocument.objects.filter(template=template).update(
                dirty=True
            )

            if template.type == "TOC":
                models.TableOfContentsCache.objects.filter(
                    toc__in=template.collection.tables_of_contents.all()
                ).update(dirty=True)


class RebuildTOCs:
    def run(self):
        from torque import models

        toc_cache = models.TableOfContentsCache.objects.filter(dirty=True).first()
        if toc_cache:
            # As above, we do this outside of the transaction, because if someone comes
            # along and dirties it again while we're rebuilding, we want to
            # rebuild it after we're done rebuilding it.
            print(
                "Rebuilding toc %s (%s): %s..."
                % (
                    toc_cache.toc.collection.name,
                    toc_cache.wiki_config.group,
                    toc_cache.toc.name,
                ),
                end="",
            )
            toc_cache.dirty = False
            toc_cache.save()
            with transaction.atomic():
                toc_cache.rebuild()
            print("Rebuilt")
            return True


class RebuildSearchCacheDocuments:
    def run(self):
        from torque import models

        num = models.SearchCacheDocument.objects.filter(dirty=True).count()
        if num > 0:
            print("Rebuilding %s search cache documents" % num)

        for cache_document in models.SearchCacheDocument.objects.filter(dirty=True):
            collection = cache_document.document.collection
            for config in collection.configs.all():
                document_dict = cache_document.document.to_dict(config)
                cache_document.data = " ".join(list(map(str, document_dict.values())))
                cache_document.dirty = False
                cache_document.save()
                models.SearchCacheDocument.objects.filter(id=cache_document.id).update(
                    data_vector=SearchVector("data")
                )


class RebuildTemplateCacheDocuments:
    def run(self):
        from torque import models

        template_cache = models.TemplateCacheDocument.objects.filter(dirty=True).first()
        if template_cache:
            print(
                "Rebuilding template cache for (%s: %s), %s left"
                % (
                    template_cache.document_dict.wiki_config.wiki.wiki_key,
                    template_cache.document_dict.document.key,
                    models.TemplateCacheDocument.objects.filter(dirty=True).count(),
                )
            )

            for tc in models.TemplateCacheDocument.objects.filter(
                document_dict=template_cache.document_dict, dirty=True
            ):
                template_cache.rebuild()

            return True


class CreateUnbuiltDocumentDicts:
    def run(self):
        from torque import models

        for wiki_config in models.WikiConfig.objects.all():
            if (
                wiki_config.valid_ids.count()
                != models.DocumentDictCache.objects.filter(
                    document__in=wiki_config.valid_ids.all(), wiki_config=wiki_config
                ).count()
            ):
                print(
                    "Add unbuilt document dictionaries for %s in %s"
                    % (wiki_config.group, wiki_config.wiki.wiki_key)
                )
                wiki_config.rebuild_document_dict_cache()
                return True


class RebuildDocumentDicts:
    def run(self):
        from torque import models

        ddcs = models.DocumentDictCache.objects.filter(dirty=True).all()
        if len(ddcs) > 0:
            print("Rebuilding %s Document Dicts" % len(ddcs))
            for ddc in ddcs:
                ddc.document.rebuild_cache(ddc.wiki_config)
            return True


class CacheRebuilder(Process):
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        db.connections.close_all()

        while True:
            try:
                # We always want to do the dictionary caches if they exist,
                # and for the rest of the caches, they shouldn't do very many just
                # in case there's new document dict cache invalidation that's happened
                (
                    CreateUnbuiltDocumentDicts().run()
                    or RebuildDocumentDicts().run()
                    or PropagateTemplateDirty().run()
                    or RebuildWikiConfigs().run()
                    or RebuildSearchCacheDocuments().run()
                    or RebuildTOCs().run()
                    or RebuildTemplateCacheDocuments().run()
                    or time.sleep(5)
                )
            except:
                print("Rebuilder failed a loop due to %s" % sys.exc_info()[0])
                print(traceback.format_exc())
