import traceback
from textwrap import dedent

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connections
from urlid_graph import settings as urlid_graph_settings
from urlid_graph.log import IndexObjectsLogger
from urlid_graph.models import ObjectModelMixin, ObjectRepository
from urlid_graph.utils import random_name


class Command(BaseCommand):
    help = "Index objects from a specific model"

    def add_arguments(self, parser):
        parser.add_argument("--start-id", type=int)
        parser.add_argument("--batch-size", type=int, default=100_000)
        parser.add_argument("--no-delete", action="store_true")
        parser.add_argument("--only-missing", action="store_true")
        parser.add_argument("app_name")
        parser.add_argument("model")

    def handle(self, *args, **options):
        app_name = options["app_name"]
        batch_size = options["batch_size"]
        model = options["model"]
        only_missing = options["only_missing"]
        should_delete = not options["no_delete"] and not only_missing
        start_id = options["start_id"]

        Model = apps.get_model(app_name, model)
        if not issubclass(Model, ObjectModelMixin):
            raise ValueError("Model '{}' doesn't inherit from `ObjectModelMixin`".format(model))
        elif only_missing is True and start_id is not None:
            raise ValueError("--only-missing and --start-id are exclusive options")

        self.logger = IndexObjectsLogger(description=f"{app_name}.{model}")
        print(f"Starting job {self.logger.job.id}")

        ok = True
        try:
            if should_delete:
                self.logger.start_step("delete-objects")
                result = ObjectRepository.objects.filter(entity_id=Model._meta.entity_uuid).delete()
                self.logger.finish_step("delete-objects", message=f"{result[0]} objects deleted")

            self.logger.start_step("index")
            self.index(
                Model,
                only_missing=only_missing,
                start_id=start_id,
                batch_size=batch_size,
                callback=self.logger.progress,
            )
            self.logger.finish_step("index")

        except:  # noqa
            self.logger.error(traceback.format_exc())
            ok = False

        else:
            self.logger.finish()

        return str(ok)  # Used by import_data when calling this command programatically

    def index(
        self, Model, only_missing=False, start_id=None, lang="pg_catalog.portuguese", batch_size=10000, callback=None
    ):
        """Update the FTS index using objects from `Model`"""
        table_name = Model._meta.db_table
        temp_table_name = "urlid_tmp_fts_" + random_name(16)
        if only_missing:
            objrepo_table_name = ObjectRepository._meta.db_table
            select_uuids_sql = dedent(
                f"""
                SELECT
                  "m"."object_uuid" AS "uuid"
                FROM "{table_name}" AS "m"
                  LEFT JOIN "{objrepo_table_name}" AS "o"
                    ON "m"."object_uuid" = "o"."uuid"
                WHERE "o"."uuid" IS NULL;
            """
            ).strip()
            uuids_args = []
        else:
            select_uuids_sql = f"""
                SELECT DISTINCT object_uuid FROM "{table_name}" WHERE id >= %s
            """.strip()
            uuids_args = [start_id or 0]
        create_temp_table_sqls = [
            (
                f'CREATE TEMPORARY TABLE "{temp_table_name}" ("id" SERIAL, "uuid" UUID)',
                [],
            ),
            (
                dedent(
                    f"""
                    INSERT INTO "{temp_table_name}" ("uuid")
                    {select_uuids_sql}
                    """
                ).strip(),
                uuids_args,
            ),
            (
                f'CREATE INDEX "idx_{random_name(20)}" ON "{temp_table_name}" ("id", "uuid")',
                [],
            ),
        ]
        row_count = []
        with connections[urlid_graph_settings.DJANGO_DATABASE].cursor() as cursor:
            for sql, args in create_temp_table_sqls:
                cursor.execute(sql, args)
                row_count.append(cursor.rowcount)
        total_objects = row_count[1]

        string_agg = " || ' ' || ".join(
            f"COALESCE(STRING_AGG({field_name}, ' '), '')" for field_name in Model._meta.search_fields
        )
        insert_sql = dedent(
            f"""
            INSERT INTO "{ObjectRepository._meta.db_table}" (uuid, entity_id, search_data)
                SELECT
                    object_uuid,
                    %s::uuid,
                    to_tsvector(
                        %s,
                        {string_agg}
                    )
                FROM "{table_name}"
                WHERE object_uuid IN (
                    SELECT "uuid"
                    FROM "{temp_table_name}"
                    WHERE id >= %s AND id < %s
                )
                GROUP BY object_uuid
            ON CONFLICT (uuid) DO UPDATE SET search_data = EXCLUDED.search_data
            """
        ).strip()

        counter = 0
        for object_id in range(1, total_objects + 1, batch_size):
            args = (Model._meta.entity_uuid, lang, object_id, object_id + batch_size)
            with connections[urlid_graph_settings.DJANGO_DATABASE].cursor() as cursor:
                cursor.execute(insert_sql, args)
                counter += cursor.rowcount
                if callback is not None:
                    callback(done=counter, total=total_objects)

        drop_temp_table_sql = f'DROP TABLE "{temp_table_name}"'
        with connections[urlid_graph_settings.DJANGO_DATABASE].cursor() as cursor:
            cursor.execute(drop_temp_table_sql)

        return counter
