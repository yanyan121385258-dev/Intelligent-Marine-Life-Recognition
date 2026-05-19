from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("studio_django_wiki", "0003_drop_hetrz_knowledge_tables"),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS hetrz_knowledge;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS hetrz_knowledge_article;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS hertz_knowledge;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS hertz_knowledge_article;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]