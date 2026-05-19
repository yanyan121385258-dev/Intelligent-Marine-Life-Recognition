from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("studio_django_wiki", "0002_alter_wiki_table_alter_wikiarticle_table"),
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
    ]