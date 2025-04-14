from django.db import models, transaction, connections


class AdspressoManager(models.Manager):
    def bulk_update_or_create(self, objects, batch_size=100):
        """
        Создает или обновляет объекты батчем.

        Для корректного использования нужно в модели также прописать поля
        conflict_fields: например ('id',)
        update_fields: например ('age', 'name')

        :param objects: Список объектов модели
        :param batch_size: размер батча.
        """
        if not objects:
            return

        table = self.model._meta.db_table
        conflict_fields = getattr(self.model, "conflict_fields", None)
        update_fields = getattr(self.model, "update_fields", None)
        fields = [field.name for field in self.model._meta.fields]

        if not conflict_fields:
            raise ValueError(f"Необходимо указать conflict_fields (например, ['id']) в {self.model.__name__}")
        if not update_fields:
            update_fields = [field for field in fields if field not in conflict_fields]

        values_sql = ', '.join([f'%({field})s' for field in fields])
        conflict_target = ', '.join(conflict_fields)
        update_sql = ', '.join([f'{field} = EXCLUDED.{field}' for field in update_fields])

        sql = f"""
            INSERT INTO {table} ({', '.join(fields)})
            VALUES ({values_sql})
            ON CONFLICT ({conflict_target}) 
            DO UPDATE SET {update_sql};
        """

        with connections[self.db].cursor() as cursor:
            for batch in range(0, len(objects), batch_size):
                batch_objs = objects[batch:batch + batch_size]
                params = [obj.__dict__ for obj in batch_objs]
                cursor.executemany(sql, params)
